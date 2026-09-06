# S1：AXI Lite 寄存器接口

同一正常设计对应 B 通道与 R 通道两个缺陷变体。

正常对照组由 `original/xlnxdemo.v` 组成，顶层为 `xlnxdemo`。缺陷组只将下表中的原文件替换为对应变体文件，其余依赖共用正常组文件。

| 变体 | 原文件 | 缺陷替换文件 | 输入与参考输出 | 样本数 | 执行配置 |
| --- | --- | --- | --- | ---: | --- |
| `s1b` | `original/xlnxdemo.v` | `variants/s1b/xlnxdemo_bug_s1b.v` | `testbench/tb0.csv` | 10 | [manifest](../../manifests/s1b.json) |
| `s1r` | `original/xlnxdemo.v` | `variants/s1r/xlnxdemo_bug_s1r.v` | `testbench/tb1.csv` | 10 | [manifest](../../manifests/s1r.json) |

CSV 的输入列用于固定轨迹回放，输出列用于正常组的逐单元格 oracle 比较；缺陷组使用同一输入。端口宽度、参数、初始化、时钟、允许的掩码与采样阶段均由 manifest 明确规定。

上游适配项目没有可直接执行的 `tb.v`；`testbench/` 保留其 CSV。原生模拟器由 runner 生成 CSV 回放适配器。

必须保持 project.toml 的 bugs 关联：s1b→tb0.csv，s1r→tb1.csv。两份 CSV 每行只允许一个已记录的尾随空字段。原 trace_tb0/trace_tb1 将 42 个 DUT 状态清零，但含 UUT.properties 引用，不能直接与去除 FORMAL 的适配 RTL 组合。

`provenance/project.toml`、`provenance/to_btor2.ys` 和 `provenance/origin/` 保留上游配置、辅助脚本与来源说明的原始字节。原配置中的相对路径通过 [layout.json](provenance/layout.json) 映射到当前目录，不能直接按迁移前工作目录运行辅助脚本。

[来源目录](../../catalog/upstream.json) 固定仓库 commit 和归档 SHA256。上游文件保留原许可头；此目录调整不增加或替换许可。manifest 同时校验源文件和 layout 的 SHA256。

## MLIR 测试基线

以下文件纳入版本管理，对应本设计的正常组与缺陷组。三种形式的用途及刷新方式见[通用约定](../../README.md#mlir-测试基线)。

| 变体 / 对照组 | 可读 MLIR | K 输入 | 调试 MLIR | 源码映射 | 生成来源 |
|---|---|---|---|---|---|
| `s1b` / 正常 | [design.mlir](mlir/s1b/golden/design.mlir) | [generic](mlir/s1b/golden/design.generic.mlir) | [debug generic](mlir/s1b/golden/design.debug.generic.mlir) | [source-map](mlir/s1b/golden/source-map.json) | [provenance](mlir/s1b/golden/provenance.json) |
| `s1b` / 缺陷 | [design.mlir](mlir/s1b/buggy/design.mlir) | [generic](mlir/s1b/buggy/design.generic.mlir) | [debug generic](mlir/s1b/buggy/design.debug.generic.mlir) | [source-map](mlir/s1b/buggy/source-map.json) | [provenance](mlir/s1b/buggy/provenance.json) |
| `s1r` / 正常 | [design.mlir](mlir/s1r/golden/design.mlir) | [generic](mlir/s1r/golden/design.generic.mlir) | [debug generic](mlir/s1r/golden/design.debug.generic.mlir) | [source-map](mlir/s1r/golden/source-map.json) | [provenance](mlir/s1r/golden/provenance.json) |
| `s1r` / 缺陷 | [design.mlir](mlir/s1r/buggy/design.mlir) | [generic](mlir/s1r/buggy/design.generic.mlir) | [debug generic](mlir/s1r/buggy/design.debug.generic.mlir) | [source-map](mlir/s1r/buggy/source-map.json) | [provenance](mlir/s1r/buggy/provenance.json) |

生成来源记录该组实际使用的 RTL、参数、工具版本和来源运行状态。历史 location 原样保留，按来源记录与 [layout.json](provenance/layout.json) 回查当前源码。

本页说明设计与输入契约，执行结果见实验根目录的 `results/`，历史完整运行留存在 `.runs/`。

## 外部组件输入事件

- [s1b.events.json](testbench/s1b.events.json)：对应原 CSV 的完整输入事件，只含时间与输入，不包含 oracle。
- [s1r.events.json](testbench/s1r.events.json)：对应原 CSV 的完整输入事件，只含时间与输入，不包含 oracle。

这些事件可直接传给 `kcirct simulate --inputs`，与上面的持久化 generic MLIR 配套使用。每个事件固定同一输入执行两次后 dump；全部 low/high VCD 对照流程见 [用户流程](../../USER_WORKFLOW.md)。
