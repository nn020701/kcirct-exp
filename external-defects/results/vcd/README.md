# VCD 主协议结果

`summary.json` 与 `cases/` 按 `selection.json` 选择各变体最新一次主协议结果；
`attempts.json` 保留六个正式批次的全部 47 次尝试。当前 10 个变体 / 9 个来源全部通过，
每版 326 行 CSV、642 个事件，两版合计 2,568 次 K 求值。

这里的 `pass` 表示完整规定顶层 VCD 与辅助 oracle 条件通过；内部不变量另行检查。
complete-03 的[独立全状态审计](../../evidence/vcd/metadata-integrity/vcd-complete-03/README.md)
确认 20 组全部 2,568 份状态的完整连接保持 setup。complete-02 的 S2 九份连接变化及其他历史失败
保持原始结果，见[当前结论与历史](../../STATUS.md)。本轮是语义层规避，不是 K/LLVM backend 修复。
