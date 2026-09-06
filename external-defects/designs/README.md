# 实验设计目录

正常组、缺陷替换文件和测试输入分别保存，多个变体共享依赖，保留全部上游文件原始字节。对应的 MLIR 测试基线按变体和正常/缺陷组持久化。每个项目的 `provenance/layout.json` 将原项目相对路径映射到当前实验根目录相对路径。

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

`mlir/<variant>/{golden,buggy}/` 保存三种 MLIR、`source-map.json` 和 `provenance.json`。先阅读 `design.mlir` 理解设计，再用 `design.generic.mlir` 检查 K 的 operation 输入；调试时用 `design.debug.generic.mlir` 与源码映射回查位置。各项目 README 提供两组的直接链接，完整路径与来源运行见 [IR 索引](../catalog/ir-index.json)。S1 的两个变体各有独立基线，保持其输入契约和来源运行的对应关系。

经过明确转换的新版本放在 `mlir/<variant>/<generation>/{golden,buggy}/`，由 manifest 的
`ir_baseline` 和 `ir_profile` 选择，原版本继续保留。一次常量初始化的受限 profile
额外保存前后端原始 IR、初始化转换审计及工具身份；生成过程和边界见
[受限转换说明](../README.md#一次常量初始化的受限转换)。生成成功与仿真通过分别记录。

这些文件纳入版本管理，后端受阻时也保留。runner 验证源码、参数与产物哈希后，直接把持久化 generic MLIR 传给外部 `kcirct simulate`；基线更新需独立核对前端工具和生成来源，详见[实验说明](../README.md#mlir-测试基线)。

每个变体的 `testbench/<variant>.events.json` 保存版控输入事件，只有时间和完整顶层输入，不包含 oracle。它与原 CSV 对应，由 `make inputs CASES=all-short` 生成，已有不同内容时拒绝覆盖。runner 检查事件与 CSV 一致，再用同一输入事件驱动两后端；Kimulator 每事件双执行后采样，全部 low/high 事件进入 VCD diff。各项目 README 提供事件文件入口。

执行配置位于 `../manifests/`，来源与候选目录位于 [catalog](../catalog/README.md)。当前配置覆盖 9 个来源案例、10 个变体，共 326 行 CSV / 642 个事件；新协议执行情况见 [VCD_RUNS](../VCD_RUNS.md) 与 `../results/vcd/`，历史 CSV 结果单独保留。
