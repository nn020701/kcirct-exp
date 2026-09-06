# S2：AXI Stream 主接口

启动计数及输出握手轨迹。

正常对照组由 `original/xlnxstream_2018_3.v` 组成，顶层为 `xlnxstream_2018_3`。缺陷组只将下表中的原文件替换为对应变体文件，其余依赖共用正常组文件。

| 变体 | 原文件 | 缺陷替换文件 | 输入与参考输出 | 样本数 | 执行配置 |
| --- | --- | --- | --- | ---: | --- |
| `s2` | `original/xlnxstream_2018_3.v` | `variants/s2/xlnxstream_2018_3_bug_s2.v` | `testbench/tb.csv` | 45 | [manifest](../../manifests/s2.json) |

CSV 的输入列用于固定轨迹回放，输出列用于正常组的逐单元格 oracle 比较；缺陷组使用同一输入。端口宽度、参数、初始化、时钟、允许的掩码与采样阶段均由 manifest 明确规定。

上游适配项目没有可直接执行的 `tb.v`；`testbench/` 保留其 CSV。原生模拟器由 runner 生成 CSV 回放适配器。

C_M_AXIS_TDATA_WIDTH=32、C_M_START_COUNT=32；时钟 M_AXIS_ACLK，同步低有效复位 M_AXIS_ARESETN。
原前端基线保留 LLHD 操作；独立版本通过受限初始化转换生成可供组件执行的 IR，两个版本分别保存。

`provenance/project.toml`、`provenance/to_btor2.ys` 和 `provenance/origin/` 保留上游配置、辅助脚本与来源说明的原始字节。原配置中的相对路径通过 [layout.json](provenance/layout.json) 映射到当前目录，不能直接按迁移前工作目录运行辅助脚本。

[来源目录](../../catalog/upstream.json) 固定仓库 commit 和归档 SHA256。上游文件保留原许可头；此目录调整不增加或替换许可。manifest 同时校验源文件和 layout 的 SHA256。

## MLIR 测试基线

当前 manifest 选择 `initial-register-v1` 目录，profile 为 `constant-initial-register-v1`。
以下文件纳入版本管理，对应本设计的正常组与缺陷组。三种形式的用途及刷新方式见[通用约定](../../README.md#mlir-测试基线)。

| 当前对照组 | 可读 MLIR | K 输入 | 调试 MLIR | 源码映射 | 生成来源与转换证明 |
|---|---|---|---|---|---|
| 正常 | [design.mlir](mlir/s2/initial-register-v1/golden/design.mlir) | [generic](mlir/s2/initial-register-v1/golden/design.generic.mlir) | [debug generic](mlir/s2/initial-register-v1/golden/design.debug.generic.mlir) | [source-map](mlir/s2/initial-register-v1/golden/source-map.json) | [provenance](mlir/s2/initial-register-v1/golden/provenance.json)、[初始化证明](mlir/s2/initial-register-v1/golden/initial-lowering.json) |
| 缺陷 | [design.mlir](mlir/s2/initial-register-v1/buggy/design.mlir) | [generic](mlir/s2/initial-register-v1/buggy/design.generic.mlir) | [debug generic](mlir/s2/initial-register-v1/buggy/design.debug.generic.mlir) | [source-map](mlir/s2/initial-register-v1/buggy/source-map.json) | [provenance](mlir/s2/initial-register-v1/buggy/provenance.json)、[初始化证明](mlir/s2/initial-register-v1/buggy/initial-lowering.json) |

该版本从同一 RTL、参数与前端分别保存 `frontend.pre-llhd.generic.mlir` 和
`frontend.hw.generic.mlir`。初始化证明逐一关联 `mst_exec_state`、`read_pointer`、`count`
的常量初始化与寄存器驱动，输出 `initialized.hw.generic.mlir`，随后由官方转换生成最终 IR。
更多边界见[受限转换流程](../../README.md#一次常量初始化的受限转换)。

[独立回导对照](../../evidence/vcd/ir-normalization/README.md) 保存了原 RTL 与转换后 SV 的
两组 Verilator 全事件比较，以及初值为 5 的小例。它核验转换行为，和 Kimulator 的正式运行结果分别记录。

最终 generic/debug 中四个顶层输出的 location 指向当时的
`.work/ir-preparation/initial-register-v1/s2/<golden或buggy>/design.mlir:5`。
它对应同组持久化的 `initial-register-v1/<golden或buggy>/design.mlir:5`，两份文件已经逐字节核对一致。
其余 RTL location 保留 `designs/...` 相对来源。为保留运行身份，不改写已运行 IR 内的 location；
干净检出时按此映射打开持久化文件即可。

原解析失败基线继续保留，以下路径不会被新版本覆盖：

| 变体 / 对照组 | 可读 MLIR | K 输入 | 调试 MLIR | 源码映射 | 生成来源 |
|---|---|---|---|---|---|
| `s2` / 正常 | [design.mlir](mlir/s2/golden/design.mlir) | [generic](mlir/s2/golden/design.generic.mlir) | [debug generic](mlir/s2/golden/design.debug.generic.mlir) | [source-map](mlir/s2/golden/source-map.json) | [provenance](mlir/s2/golden/provenance.json) |
| `s2` / 缺陷 | [design.mlir](mlir/s2/buggy/design.mlir) | [generic](mlir/s2/buggy/design.generic.mlir) | [debug generic](mlir/s2/buggy/design.debug.generic.mlir) | [source-map](mlir/s2/buggy/source-map.json) | [provenance](mlir/s2/buggy/provenance.json) |

生成来源记录该组实际使用的 RTL、参数、工具版本和来源运行状态。历史 location 原样保留，按来源记录与 [layout.json](provenance/layout.json) 回查当前源码。

历史基线保留 K 解析失败时的 LLHD，便于复核原始卡点。当前 initial-register-v1 两版在 complete-03 的 89 事件 VCD 对照及各 178 份逐次状态完整连接审计通过，见[正式案例](../../results/vcd/cases/s2.json)与[当前内部审计](../../evidence/vcd/metadata-integrity/vcd-complete-03/README.md)。complete-02 正常版曾从 event84/evaluation2 起出现九份连接变化；该 AutoConnect 回归保留[原始证据](../../evidence/vcd/metadata-integrity/vcd-complete-02/README.md)，第五补丁在语义层改用索引读取后本轮轨迹不再出现。两项判据仍分别报告。

本页说明设计与输入契约，执行结果见实验根目录的 `results/`，历史完整运行留存在 `.runs/`。

## 外部组件输入事件

- [s2.events.json](testbench/s2.events.json)：对应原 CSV 的完整输入事件，只含时间与输入，不包含 oracle。

这些事件可直接传给 `kcirct simulate --inputs`，与上面的持久化 generic MLIR 配套使用。每个事件固定同一输入执行两次后 dump；全部 low/high VCD 对照流程见 [用户流程](../../USER_WORKFLOW.md)。
