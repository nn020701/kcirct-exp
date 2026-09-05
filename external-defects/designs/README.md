# 实验设计目录

正常组、缺陷替换文件和测试输入分别保存，多个变体共享依赖，保留全部上游文件原始字节。每个项目的 `provenance/layout.json` 将原项目相对路径映射到当前实验根目录相对路径。

| 案例 | 项目 | 顶层 | 变体 | CSV 样本数 |
| --- | --- | --- | --- | ---: |
| S1 | [axi-lite-s1](axi-lite-s1/README.md) | `xlnxdemo` | `s1b`, `s1r` | 10, 10 |
| S2 | [axi-stream-s2](axi-stream-s2/README.md) | `xlnxstream_2018_3` | `s2` | 45 |
| S3 | [axis-adapter-s3](axis-adapter-s3/README.md) | `axis_adapter` | `s3` | 13 |
| C4 | [axis-async-fifo-c4](axis-async-fifo-c4/README.md) | `axis_fifo_wrapper` | `c4` | 10 |
| D12 | [axis-fifo-d12](axis-fifo-d12/README.md) | `axis_fifo` | `d12` | 16 |
| D4 | [axis-fifo-d4](axis-fifo-d4/README.md) | `axis_fifo_wrapper` | `d4` | 185 |
| D11 | [axis-frame-fifo-d11](axis-frame-fifo-d11/README.md) | `axis_frame_fifo` | `d11` | 17 |
| D13 | [axis-frame-len-d13](axis-frame-len-d13/README.md) | `axis_frame_len` | `d13` | 6 |
| D8 | [axis-switch-d8](axis-switch-d8/README.md) | `axis_switch` | `d8` | 14 |

`original/` 是正常 RTL 及共用依赖；`variants/<id>/` 只包含该变体的缺陷替换文件；`testbench/` 保存原 CSV 与可用的适配 TB；`provenance/` 保存原 `project.toml`、辅助脚本及 `origin/` 材料。每个项目 README 解释其输入和对照关系。

执行配置位于 `../manifests/`，来源与候选目录位于 [catalog](../catalog/README.md)。当前配置覆盖 9 个来源案例、10 个变体，共 326 个 CSV 样本；执行通过与否由 `../results/` 的证据汇总给出。
