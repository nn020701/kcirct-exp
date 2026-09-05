# D4：带 wrapper 的 AXI Stream FIFO

FIFO 帧边界及状态输出的较长固定输入轨迹。

正常对照组由 `original/axis_fifo.v`, `original/axis_fifo_wrapper.v` 组成，顶层为 `axis_fifo_wrapper`。缺陷组只将下表中的原文件替换为对应变体文件，其余依赖共用正常组文件。

| 变体 | 原文件 | 缺陷替换文件 | 输入与参考输出 | 样本数 | 执行配置 |
| --- | --- | --- | --- | ---: | --- |
| `d4` | `original/axis_fifo.v` | `variants/d4/axis_fifo_bug_d4.v` | `testbench/tb.csv` | 185 | [manifest](../../manifests/d4.json) |

CSV 的输入列用于固定轨迹回放，输出列用于正常组的逐单元格 oracle 比较；缺陷组使用同一输入。端口宽度、参数、初始化、时钟、允许的掩码与采样阶段均由 manifest 明确规定。

上游适配项目没有可直接执行的 `tb.v`；`testbench/` 保留其 CSV。原生模拟器由 runner 生成 CSV 回放适配器。

顶层 axis_fifo_wrapper 使用 DATA_WIDTH=8、USER_WIDTH=1；内部 ADDR_WIDTH=5、FRAME_FIFO=1、DROP_BAD_FRAME=0、DROP_WHEN_FULL=0。保留缺少 timescale 的原 wrapper，通过 manifest frontend_args 指定 --timescale=1ns/1ps。

`provenance/project.toml`、`provenance/to_btor2.ys` 和 `provenance/origin/` 保留上游配置、辅助脚本与来源说明的原始字节。原配置中的相对路径通过 [layout.json](provenance/layout.json) 映射到当前目录，不能直接按迁移前工作目录运行辅助脚本。

[来源目录](../../catalog/upstream.json) 固定仓库 commit 和归档 SHA256。上游文件保留原许可头；此目录调整不增加或替换许可。manifest 同时校验源文件和 layout 的 SHA256。

本页说明设计与输入契约，执行结果见实验根目录的 `results/`，历史完整运行留存在 `.runs/`。
