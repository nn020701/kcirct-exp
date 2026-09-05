# S2：AXI Stream 主接口

启动计数及输出握手轨迹。

正常对照组由 `original/xlnxstream_2018_3.v` 组成，顶层为 `xlnxstream_2018_3`。缺陷组只将下表中的原文件替换为对应变体文件，其余依赖共用正常组文件。

| 变体 | 原文件 | 缺陷替换文件 | 输入与参考输出 | 样本数 | 执行配置 |
| --- | --- | --- | --- | ---: | --- |
| `s2` | `original/xlnxstream_2018_3.v` | `variants/s2/xlnxstream_2018_3_bug_s2.v` | `testbench/tb.csv` | 45 | [manifest](../../manifests/s2.json) |

CSV 的输入列用于固定轨迹回放，输出列用于正常组的逐单元格 oracle 比较；缺陷组使用同一输入。端口宽度、参数、初始化、时钟、允许的掩码与采样阶段均由 manifest 明确规定。

上游适配项目没有可直接执行的 `tb.v`；`testbench/` 保留其 CSV。原生模拟器由 runner 生成 CSV 回放适配器。

C_M_AXIS_TDATA_WIDTH=32、C_M_START_COUNT=32；时钟 M_AXIS_ACLK，同步低有效复位 M_AXIS_ARESETN。适配项目无 tb.v；前端可能保留 LLHD 操作，必须依据实际运行证据分类。

`provenance/project.toml`、`provenance/to_btor2.ys` 和 `provenance/origin/` 保留上游配置、辅助脚本与来源说明的原始字节。原配置中的相对路径通过 [layout.json](provenance/layout.json) 映射到当前目录，不能直接按迁移前工作目录运行辅助脚本。

[来源目录](../../catalog/upstream.json) 固定仓库 commit 和归档 SHA256。上游文件保留原许可头；此目录调整不增加或替换许可。manifest 同时校验源文件和 layout 的 SHA256。

本页说明设计与输入契约，执行结果见实验根目录的 `results/`，历史完整运行留存在 `.runs/`。
