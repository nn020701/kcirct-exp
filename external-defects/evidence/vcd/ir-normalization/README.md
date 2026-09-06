# 常量初始化转换的独立对照证据

这里验证受限初始化转换是否保留原 RTL 行为：将持久化 MLIR 经官方 CIRCT 转换导出 SV，
再分别用 Verilator 执行原 RTL 与导出 SV，以同一输入比较全部顶层端口的完整 VCD。
这些是转换验证，独立于 Kimulator 的正式批次，不增加缺陷案例、变体或正式事件数量。

| 验证 | 输入与范围 | 实际结果 |
|---|---|---|
| S2 正常组 | 原始 RTL 与 `initial-register-v1` 导出 SV，同一 45 行输入展开的 89 events / 7 ports | 全部 VCD 一致 |
| S2 缺陷组 | 原始缺陷 RTL 与对应导出 SV，同一 89 events / 7 ports | 全部 VCD 一致 |
| 非零初值小例 | `q` 为 i4、初值 5，7 events / 3 ports | 全部 VCD 一致；低电平序列为 `[5, 0, 9, 2]` |

S2 的原始记录见 [results.json](initial-roundtrip/results.json)，波形可直接打开：

- 正常组：[原 RTL](initial-roundtrip/golden/original/trace.vcd)、[导出 SV](initial-roundtrip/golden/exported/trace.vcd)。
- 缺陷组：[原 RTL](initial-roundtrip/buggy/original/trace.vcd)、[导出 SV](initial-roundtrip/buggy/exported/trace.vcd)。
- 非零小例：[原始记录](nonzero-initial-roundtrip/results.json)、[原 RTL](nonzero-initial-roundtrip/original/trace.vcd)、[导出 SV](nonzero-initial-roundtrip/exported/trace.vcd)。

S2 两组的 `inputs/` 保存实际被验证的最终 MLIR、pre-LLHD/HW 双输入、
初始化转换输出、审计、源码映射、provenance 和原 RTL。
非零小例额外保存[原 RTL](nonzero-initial-roundtrip/inputs/rtl/initial-block.sv)、
[LLHD generic](nonzero-initial-roundtrip/llhd.generic.mlir)、[HW generic](nonzero-initial-roundtrip/hw.generic.mlir)、
[转换审计](nonzero-initial-roundtrip/normalization.json)与[导出 SV](nonzero-initial-roundtrip/normalized.sv)。
驱动、输入事件、工具命令、stdout/stderr、VCD 预检及外部 diffvcd 日志均随各组保存；
`obj`、`obj_dir`、二进制模型等构建缓存没有复制。

初次使用 `circt-translate` 导出失败的命令仍保留在
[commands.json](initial-roundtrip/commands.json)，[原 stderr](initial-roundtrip/golden/export.stderr.log)
保持原字节。后续成功采用 `circt-opt --export-verilog`，其命令和输出另存，没有回写首次失败。

## 索引与结论边界

[index.json](index.json) 逐文件记录实际来源、持久化路径、SHA256 与字节数。
这里复制了 203 个精选工件；所有原 JSON、日志、源码和波形保持原字节，绝对路径表示历史来源。
查找这些来源的可分享副本时，使用索引中的 `path`，不依赖本机 `.work` 目录。
`tools/` 还保存与生成记录哈希匹配的转换脚本，以及真实比较所用的 diffvcd。

[独立 IR 审计](ir-audit.json) 另行记录两版新工件哈希、RTL 初始化的逐项证明、
转换重放及源码映射核验，并与历史运行快照核对旧输入未改变。历史输入尚未存在于
该仓库 HEAD 中的情况已在原审计记录说明，未将其写成 Git 基线验证。

比较记录复用了通用助手的字段名：其中 `kimulator_vcd` 实际指向**导出 SV 的 Verilator 波形**，
`native_vcd` 指向原始 RTL 的 Verilator 波形。本目录没有因此声称这些验证调用了 Kimulator；
索引显式记录了这两个角色。真实 K/Verilator 结果另见[正式报告](../../../VCD_RUNS.md)。

这些结果覆盖给定输入、参数、二态默认零初始化及已证明的常量初值。
非零小例补充检查默认零值不能替代显式初值的情况，不能推广为任意 LLHD 过程转换的证明。
转换条件与用户流程见[实验说明](../../../README.md#一次常量初始化的受限转换)。
