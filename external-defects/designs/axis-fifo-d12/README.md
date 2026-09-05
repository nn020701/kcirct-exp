# D12：AXI Stream 帧 FIFO

缓存满时丢弃帧的状态变化及异常输出。

正常对照组由 `original/axis_fifo.v` 组成，顶层为 `axis_fifo`。缺陷组只将下表中的原文件替换为对应变体文件，其余依赖共用正常组文件。

| 变体 | 原文件 | 缺陷替换文件 | 输入与参考输出 | 样本数 | 执行配置 |
| --- | --- | --- | --- | ---: | --- |
| `d12` | `original/axis_fifo.v` | `variants/d12/axis_fifo_bug_d12.v` | `testbench/tb.csv` | 16 | [manifest](../../manifests/d12.json) |

CSV 的输入列用于固定轨迹回放，输出列用于正常组的逐单元格 oracle 比较；缺陷组使用同一输入。端口宽度、参数、初始化、时钟、允许的掩码与采样阶段均由 manifest 明确规定。

`testbench/tb.v` 是按字节保留的上游适配 TB，用于独立验证原始激励或失败判据；它与 runner 生成的固定 CSV 回放适配器有不同作用。

ADDR_WIDTH=2、DATA_WIDTH=8、FRAME_FIFO=1、DROP_WHEN_FULL=1。CSV 只含 8 个 oracle 输出；status_overflow/status_bad_frame/status_good_frame 仍属于完整端口比较范围。原 TB 需要外部时钟且可能提前结束。

`provenance/project.toml`、`provenance/to_btor2.ys` 和 `provenance/origin/` 保留上游配置、辅助脚本与来源说明的原始字节。原配置中的相对路径通过 [layout.json](provenance/layout.json) 映射到当前目录，不能直接按迁移前工作目录运行辅助脚本。

[来源目录](../../catalog/upstream.json) 固定仓库 commit 和归档 SHA256。上游文件保留原许可头；此目录调整不增加或替换许可。manifest 同时校验源文件和 layout 的 SHA256。

本页说明设计与输入契约，执行结果见实验根目录的 `results/`，历史完整运行留存在 `.runs/`。
