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

本页说明设计与输入契约，执行结果见实验根目录的 `results/`，历史完整运行留存在 `.runs/`。
