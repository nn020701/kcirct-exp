# D8：AXI Stream 交换器

四输入、单输出配置中的索引错误。

正常对照组由 `original/arbiter.v`, `original/axis_register.v`, `original/axis_switch.v`, `original/priority_encoder.v` 组成，顶层为 `axis_switch`。缺陷组只将下表中的原文件替换为对应变体文件，其余依赖共用正常组文件。

| 变体 | 原文件 | 缺陷替换文件 | 输入与参考输出 | 样本数 | 执行配置 |
| --- | --- | --- | --- | ---: | --- |
| `d8` | `original/axis_switch.v` | `variants/d8/axis_switch_bug_d8.v` | `testbench/tb.csv` | 14 | [manifest](../../manifests/d8.json) |

CSV 的输入列用于固定轨迹回放，输出列用于正常组的逐单元格 oracle 比较；缺陷组使用同一输入。端口宽度、参数、初始化、时钟、允许的掩码与采样阶段均由 manifest 明确规定。

`testbench/tb.v` 是按字节保留的上游适配 TB，用于独立验证原始激励或失败判据；它与 runner 生成的固定 CSV 回放适配器有不同作用。

正常组依赖 arbiter、axis_register、priority_encoder。DUT 默认 S_COUNT=4、M_COUNT=1，M_TOP=1672；TB 参数覆盖块被注释。project.toml 要求二态仿真。原 TB 需要外部时钟且会先于完整 CSV 停止。

`provenance/project.toml`、`provenance/to_btor2.ys` 和 `provenance/origin/` 保留上游配置、辅助脚本与来源说明的原始字节。原配置中的相对路径通过 [layout.json](provenance/layout.json) 映射到当前目录，不能直接按迁移前工作目录运行辅助脚本。

[来源目录](../../catalog/upstream.json) 固定仓库 commit 和归档 SHA256。上游文件保留原许可头；此目录调整不增加或替换许可。manifest 同时校验源文件和 layout 的 SHA256。

## MLIR 测试基线

以下文件纳入版本管理，对应本设计的正常组与缺陷组。三种形式的用途及刷新方式见[通用约定](../../README.md#mlir-测试基线)。

| 变体 / 对照组 | 可读 MLIR | K 输入 | 调试 MLIR | 源码映射 | 生成来源 |
|---|---|---|---|---|---|
| `d8` / 正常 | [design.mlir](mlir/d8/golden/design.mlir) | [generic](mlir/d8/golden/design.generic.mlir) | [debug generic](mlir/d8/golden/design.debug.generic.mlir) | [source-map](mlir/d8/golden/source-map.json) | [provenance](mlir/d8/golden/provenance.json) |
| `d8` / 缺陷 | [design.mlir](mlir/d8/buggy/design.mlir) | [generic](mlir/d8/buggy/design.generic.mlir) | [debug generic](mlir/d8/buggy/design.debug.generic.mlir) | [source-map](mlir/d8/buggy/source-map.json) | [provenance](mlir/d8/buggy/provenance.json) |

生成来源记录该组实际使用的 RTL、参数、工具版本和来源运行状态。历史 location 原样保留，按来源记录与 [layout.json](provenance/layout.json) 回查当前源码。

本页说明设计与输入契约，执行结果见实验根目录的 `results/`，历史完整运行留存在 `.runs/`。

## 外部组件输入事件

- [d8.events.json](testbench/d8.events.json)：对应原 CSV 的完整输入事件，只含时间与输入，不包含 oracle。

这些事件可直接传给 `kcirct simulate --inputs`，与上面的持久化 generic MLIR 配套使用。每个事件固定同一输入执行两次后 dump；全部 low/high VCD 对照流程见 [用户流程](../../USER_WORKFLOW.md)。
