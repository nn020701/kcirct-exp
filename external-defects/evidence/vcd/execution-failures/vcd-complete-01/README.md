# complete-01 的执行失败证据

本批次实际结果为 **8 个通过、2 个执行错误**。这里保存正式运行的原始工件、之后的独立定位，
以及新定义的定向重放；后续修复通过不改写这次失败。入口与 SHA256 见 [index.json](index.json)。

| 案例 | 正式失败位置 | 已完成事件 | 原始终态检查错误 |
|---|---|---:|---|
| S3 golden | 事件 0，第 2 次执行 | 0 / 25 | `simulated.1.kore，未清空 []` |
| D12 golden | 事件 9，第 1 次执行 | 9 / 31 | `simulated.0.kore，未清空 []` |

两处最后的 `krun` 进程均返回 `0`，但仍存在待执行状态，外部 CLI 因完整性检查返回 `1`。
批次 runner 返回 `1`，宿主 `make` 返回 `2`。因此进程正常退出不能单独证明一个事件完成，
`未清空 []` 也没有充分说明实际残留的 `current-info` 和 operation。

每案 `golden/kimulator/simulation/result.json` 保留 CLI 的原始错误；上层 `result.json` 的
`kimulator 退出码 1` 是 runner 汇总信息。失败输入、原始 generic MLIR、setup/last-state、
逐次压缩状态、命令和部分 VCD 均保留；`golden/native` 保存同输入的完整 Verilator 对照。

## 独立审计与定位

[audit/vcd-complete-01-audit.json](audit/vcd-complete-01-audit.json) 核对本批次 5,989 份非构建缓存工件，
解压并验证全部 2,477 个执行快照与对应命令 stdout SHA256。18 组完整 K/Verilator 波形及 D12
失败前的 9 个事件，共 17,498 个端口与事件组合，重新采样后均一致。审计通过表示证据完整，
不改变本批次的两项失败。

[diagnosis/s3](diagnosis/s3) 保存三次原始失败重放，以及事件 0 第 1 次执行中
`depth 1956 → 1957` 的相邻状态：`connection[%131]` 的参数由
`[%124, %28, %112]` 变成 `[%28, %112, %112]`，当时的 `current` 仍保持正确。
[diagnosis/d12/findings.json](diagnosis/d12/findings.json) 保存另案对应的
`depth 942 → 943` 首次变化；其早期只检查首个 `current` 的非单调搜索已弃用，没有作为边界证据导出。

新定义的定向重放保存在各案诊断目录中。它们验证完整只读 `connection` 保持不变且无剩余 `current`；
完整实验结论仍以[正式批次报告](../../../../VCD_RUNS.md)为准。
对应源码见[第四份组件补丁](../../component/auto-connect-list-preservation/README.md)。
修复采用语义等价的整 List 模式，未修改 K/LLVM backend，也未声明彻底解决所有共享问题。

早先 standard 批次的 VCD 通过仍是真实观测；complete-01 在更严格的 mux 检查下暴露了列表损坏。
不能把此次失败笼统归因于 preset，也不能倒推旧通过记录是伪造结果。
