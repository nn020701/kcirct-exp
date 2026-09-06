# D11：AXI Stream 帧 FIFO

丢帧状态与队列输出轨迹。

正常对照组由 `original/axis_frame_fifo.v` 组成，顶层为 `axis_frame_fifo`。缺陷组只将下表中的原文件替换为对应变体文件，其余依赖共用正常组文件。

| 变体 | 原文件 | 缺陷替换文件 | 输入与参考输出 | 样本数 | 执行配置 |
| --- | --- | --- | --- | ---: | --- |
| `d11` | `original/axis_frame_fifo.v` | `variants/d11/axis_frame_fifo_bug_d11.v` | `testbench/tb.csv` | 17 | [manifest](../../manifests/d11.json) |

CSV 的输入列用于固定轨迹回放，输出列用于正常组的逐单元格 oracle 比较；缺陷组使用同一输入。端口宽度、参数、初始化、时钟、允许的掩码与采样阶段均由 manifest 明确规定。

`testbench/tb.v` 是按字节保留的上游适配 TB，用于独立验证原始激励或失败判据；它与 runner 生成的固定 CSV 回放适配器有不同作用。

ADDR_WIDTH=2、DATA_WIDTH=8、DROP_WHEN_FULL=1。唯一 oracle 掩码是 sample_index=0 的 drop_frame=x，不能扩展到其他单元格。原 TB 可能在 cycle=13 提前结束。原来源 README 的修复链接指向 D13，应以现存配对源码为准。

`provenance/project.toml`、`provenance/to_btor2.ys` 和 `provenance/origin/` 保留上游配置、辅助脚本与来源说明的原始字节。原配置中的相对路径通过 [layout.json](provenance/layout.json) 映射到当前目录，不能直接按迁移前工作目录运行辅助脚本。

[来源目录](../../catalog/upstream.json) 固定仓库 commit 和归档 SHA256。上游文件保留原许可头；此目录调整不增加或替换许可。manifest 同时校验源文件和 layout 的 SHA256。

## MLIR 测试基线

以下文件纳入版本管理，对应本设计的正常组与缺陷组。三种形式的用途及刷新方式见[通用约定](../../README.md#mlir-测试基线)。

| 变体 / 对照组 | 可读 MLIR | K 输入 | 调试 MLIR | 源码映射 | 生成来源 |
|---|---|---|---|---|---|
| `d11` / 正常 | [design.mlir](mlir/d11/golden/design.mlir) | [generic](mlir/d11/golden/design.generic.mlir) | [debug generic](mlir/d11/golden/design.debug.generic.mlir) | [source-map](mlir/d11/golden/source-map.json) | [provenance](mlir/d11/golden/provenance.json) |
| `d11` / 缺陷 | [design.mlir](mlir/d11/buggy/design.mlir) | [generic](mlir/d11/buggy/design.generic.mlir) | [debug generic](mlir/d11/buggy/design.debug.generic.mlir) | [source-map](mlir/d11/buggy/source-map.json) | [provenance](mlir/d11/buggy/provenance.json) |

生成来源记录该组实际使用的 RTL、参数、工具版本和来源运行状态。历史 location 原样保留，按来源记录与 [layout.json](provenance/layout.json) 回查当前源码。

此处 IR 同时对应历史首事件超时证据与补充一维数组语义后的实际运行，原字节保持不变。`d11` 已在 `vcd-array-bits-02` 及后续 complete-03 完成主协议 VCD 对照；当前结果见[正式案例](../../results/vcd/cases/d11.json)，历史超时仍保留。

本页说明设计与输入契约，当前 VCD 结果见实验根目录的 `results/vcd/`，旧 `results/` 为历史 CSV 结果，历史完整运行留存在 `.runs/`。

## 外部组件输入事件

- [d11.events.json](testbench/d11.events.json)：对应原 CSV 的完整输入事件，只含时间与输入，不包含 oracle。

这些事件可直接传给 `kcirct simulate --inputs`，与上面的持久化 generic MLIR 配套使用。每个事件固定同一输入执行两次后 dump；全部 low/high VCD 对照流程见 [用户流程](../../USER_WORKFLOW.md)。
