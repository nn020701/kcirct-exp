# S3：AXI Stream 位宽适配器

64 位输入按有效字节拆成 8 位输出。

正常对照组由 `original/axis_adapter.v` 组成，顶层为 `axis_adapter`。缺陷组只将下表中的原文件替换为对应变体文件，其余依赖共用正常组文件。

| 变体 | 原文件 | 缺陷替换文件 | 输入与参考输出 | 样本数 | 执行配置 |
| --- | --- | --- | --- | ---: | --- |
| `s3` | `original/axis_adapter.v` | `variants/s3/axis_adapter_bug_s3.v` | `testbench/tb.csv` | 13 | [manifest](../../manifests/s3.json) |

CSV 的输入列用于固定轨迹回放，输出列用于正常组的逐单元格 oracle 比较；缺陷组使用同一输入。端口宽度、参数、初始化、时钟、允许的掩码与采样阶段均由 manifest 明确规定。

`testbench/tb.v` 是按字节保留的上游适配 TB，用于独立验证原始激励或失败判据；它与 runner 生成的固定 CSV 回放适配器有不同作用。

INPUT_DATA_WIDTH=64、INPUT_KEEP_WIDTH=8、OUTPUT_DATA_WIDTH=8、OUTPUT_KEEP_WIDTH=1。原 TB 在 posedge Active 阶段写出采样，驱动通过 NBA 更新；进程退出码本身不能判定 oracle。

`provenance/project.toml`、`provenance/to_btor2.ys` 和 `provenance/origin/` 保留上游配置、辅助脚本与来源说明的原始字节。原配置中的相对路径通过 [layout.json](provenance/layout.json) 映射到当前目录，不能直接按迁移前工作目录运行辅助脚本。

[来源目录](../../catalog/upstream.json) 固定仓库 commit 和归档 SHA256。上游文件保留原许可头；此目录调整不增加或替换许可。manifest 同时校验源文件和 layout 的 SHA256。

## MLIR 测试基线

以下文件纳入版本管理，对应本设计的正常组与缺陷组。三种形式的用途及刷新方式见[通用约定](../../README.md#mlir-测试基线)。

| 变体 / 对照组 | 可读 MLIR | K 输入 | 调试 MLIR | 源码映射 | 生成来源 |
|---|---|---|---|---|---|
| `s3` / 正常 | [design.mlir](mlir/s3/golden/design.mlir) | [generic](mlir/s3/golden/design.generic.mlir) | [debug generic](mlir/s3/golden/design.debug.generic.mlir) | [source-map](mlir/s3/golden/source-map.json) | [provenance](mlir/s3/golden/provenance.json) |
| `s3` / 缺陷 | [design.mlir](mlir/s3/buggy/design.mlir) | [generic](mlir/s3/buggy/design.generic.mlir) | [debug generic](mlir/s3/buggy/design.debug.generic.mlir) | [source-map](mlir/s3/buggy/source-map.json) | [provenance](mlir/s3/buggy/provenance.json) |

生成来源记录该组实际使用的 RTL、参数、工具版本和来源运行状态。历史 location 原样保留，按来源记录与 [layout.json](provenance/layout.json) 回查当前源码。

本页说明设计与输入契约，执行结果见实验根目录的 `results/`，历史完整运行留存在 `.runs/`。

## 外部组件输入事件

- [s3.events.json](testbench/s3.events.json)：对应原 CSV 的完整输入事件，只含时间与输入，不包含 oracle。

这些事件可直接传给 `kcirct simulate --inputs`，与上面的持久化 generic MLIR 配套使用。每个事件固定同一输入执行两次后 dump；全部 low/high VCD 对照流程见 [用户流程](../../USER_WORKFLOW.md)。
