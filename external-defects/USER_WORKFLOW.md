# 将 Kimulator 作为完整外部组件使用

用户提供 generic MLIR、顶层模块名和输入事件 JSON，调用一次 `kcirct simulate`，即可得到 VCD、退出码和诊断目录。实验程序不需要导入 Python API，也不需要了解 Kore 状态如何编译、推进或读取。这里使用新增的可执行 `simulate` 接口；原有 `generate` 占位接口不承担本流程。

## 输入与一条模拟命令

前提是已在独立环境安装含 `simulate` 的 Kimulator，匹配的 K 工具在该环境 `PATH` 中，且通过该环境的 `kdist build circt-semantics.llvm` 准备过语义定义。`kcirct simulate --describe` 可查看安装身份和工具版本。首次模拟需要的 parser 在工作目录自动生成，也可显式传入已准备的 parser。

本轮 CLI 尚未提交到组件仓库；基线 `3afaa5f93d8ed0cabeb08bdce1fd4c5f74a8a5a2` 本身不含 `simulate`。独立复现请使用[组件源码补丁与身份记录](evidence/vcd/component/README.md)，其中保存应用方法、完整补丁和文件哈希，不能只检出裸基线提交。

需要一维整数数组语义时，再应用[数组补丁](evidence/vcd/component/packed-array-semantics/README.md)；
需要整数寄存器显式初值时，继续应用 [preset 补丁](evidence/vcd/component/scalar-firreg-preset/README.md)。
当前 complete-03 完整案例集继续应用第四份 [AutoConnect 补丁](evidence/vcd/component/auto-connect-list-preservation/README.md)及第五份 [indexed read 补丁](evidence/vcd/component/indexed-read/README.md)。五份补丁按顺序应用并重新准备定义和 parser。第四补丁引入的 S2 内部连接回归保留为历史；第五补丁后全部 20 组、2,568 份状态的完整连接审计通过。该结果支持本轮有限轨迹的语义层规避，不表示修复了 K/LLVM backend。

以 D13 正常版为例，输入文件已纳入实验版本管理：

- [design.generic.mlir](designs/axis-frame-len-d13/mlir/d13/golden/design.generic.mlir)：实际仿真设计。
- [d13.events.json](designs/axis-frame-len-d13/testbench/d13.events.json)：11 个输入事件，来自原始 6 行 CSV；不包含预期输出。

在本实验仓库根目录运行下列命令，`kcirct` 使用其自己的安装环境：

```sh
kcirct simulate \
  external-defects/designs/axis-frame-len-d13/mlir/d13/golden/design.generic.mlir \
  --top-module axis_frame_len \
  --inputs external-defects/designs/axis-frame-len-d13/testbench/d13.events.json \
  --output external-defects/.runs/manual-d13/test.vcd \
  --work-dir external-defects/.runs/manual-d13/work \
  --evaluations-per-input 2
```

调用独立路径的安装命令也可以，无需把 Kimulator 装入调用方的 Python 环境。已有输出或工作目录会拒绝覆盖，重跑请更换目录名。定义默认从组件的 kdist 安装中选择；`--definition-dir`、`--parser` 可用于显式复用准备好的构建。

输入应使用所选组件能够执行的持久化 generic MLIR。实验 manifest 可以通过
`ir_baseline` 选择保留来源的独立 IR 版本，`ir_profile` 说明受限转换；这些属于实验准备，
不增加 `kcirct simulate` 的私有参数。若 RTL 含一次常量初值，可按
[初始化转换流程](README.md#一次常量初始化的受限转换) 保存证明、转换为整数寄存器 `preset`，
并选择支持该属性的组件版本。转换和组件语义都准备好后，仍使用上述同一条公开模拟命令。

## 事件和产物契约

事件 JSON 的结构为 `{"schema_version": 1, "timescale": "1ns", "events": [...]}`，每个事件包含整数 `time` 和完整 `inputs`。例如 `{"time": 1, "inputs": {"clk": 1, ...}}` 中省略号仅示意其他全部输入，实际文件必须提供顶层要求的每个输入及合法整数值。

同一事件的所有输入保持不变，组件连续执行两次状态推进后才 dump；第二次调用不改变时钟或 VCD 时间。D13 的 11 个事件对应 22 次状态推进，VCD 时间为 0 至 10 ns，包含全部顶层输入和输出。

| 用户可观察产物 | 用途 |
|---|---|
| `test.vcd` | 在波形查看器中调试，或交给其他仿真器的 VCD 比较工具 |
| `work/result.json` | 状态、失败阶段、完成事件数、调用次数、耗时及输入/VCD 哈希 |
| `work/commands.jsonl` 与错误日志 | 实际工具命令、退出码和诊断 |
| `work/inputs.json`、`work/design.generic.mlir` | 本次消费的输入快照 |

失败返回非零退出码并保存诊断。部分波形不算完成，调用方还可检查 `events_completed` 和 `simulation_calls`。需要内部状态证据时增加 `--keep-states`，普通 VCD 使用不要求读取这些文件。

## 从单组件运行到对照实验

将输入 MLIR 换成 [D13 缺陷版](designs/axis-frame-len-d13/mlir/d13/buggy/design.generic.mlir)，保持事件文件不变，即可得到缺陷版 VCD。批量 runner 负责将同一事件序列交给 Verilator，保存其真实 VCD，并调用外部 `diffvcd.py` 比较两版全部规定顶层端口。CSV 预期值只用于判断设计缺陷是否被触发，不传入 Kimulator。

额外内部信号可以不进入规定端口集合，但必需顶层端口缺失或采样不一致必须失败。仅一位标量与 `[0:0]` 的等价声明会生成附带映射和正文哈希的比较副本，原始波形不改写。批量运行在保存全部案例证据后，以退出码 `1` 表示存在未通过案例；这与单组件因模拟失败而返回非零退出码的边界不同。

[实验 README](README.md)提供 `make run` 和 `make report-vcd` 批量入口，[正式结果](VCD_RUNS.md)链接可直接查看的真实波形及错误证据。原流程直接引用 `KCIRCT` 内部读取与推进函数；新流程将边界收敛为公开命令、文件和退出码，组件内部仍合理复用自身 API。

正式 runner 全程通过外部进程调用组件；[S2 的独立 arc 调度诊断](evidence/vcd/metadata-integrity/vcd-complete-02/arc-protocol/index.json)直接使用生产 API，以区分 CLI 包装与语义执行原因。这个辅助诊断不是主实验入口：178 个状态与 CLI 逐字节相同，在旧 complete-02 身份下复现同一内部连接问题；当前 complete-03 的全状态审计另行保存。VCD 主协议通过与内部元数据完整性分别记录，见 [STATUS](STATUS.md)。

论文可据此描述：用户无需编写绑定内部 API 的 Python 驱动，即可对持久化 MLIR 施加显式输入轨迹并获得标准 VCD；实验通过独立进程和可核验产物复现这一接口路径。这支持可使用性与可复现接口的说明，不构成用户研究或完整 HDL 兼容性的结论。
