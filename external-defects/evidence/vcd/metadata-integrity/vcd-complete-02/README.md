# complete-02 的波形通过与元数据审计

本批次 **10 个案例的完整 VCD 对照全部通过**，正常/缺陷两版各覆盖 642 个事件，
两版合计 2,568 次 K 求值；runner 与宿主 `make` 均返回 `0`。
随后独立检查全部内部 `connection`，发现 **S2 正常版从 event 84 / evaluation 2 起的 9 份状态发生真实内容变化**。
这两个观察同时保留，不能互相替代。证据来源、路径与 SHA256 见 [index.json](index.json)。

- [波形与工件审计](audit/vcd-complete-02-audit.json)：6,181 份工件哈希、2,568 份快照的解压哈希及命令绑定均一致；重新读取 20 组完整波形的 18,310 个端口与事件组合，全部一致。
- [完整 connection 审计](audit/vcd-complete-02-connection-audit.json)：20 组共 2,568 个执行状态，S2 正常版 9 份内容变化，其余 19 组均不变；差异不是 Map 序列化顺序变化。
- [精确变更](audit/s2-complete02-connection-change.json)：`%53` mux 的参数从 `[%51,%50,%54]` 变为 `[%50,%54,%54]`。
- `s2/golden` 保存正式执行命令、输入、状态、原生对照，以及变化前一份和随后九份压缩快照；两版原始 VCD 和比较记录同时保留。

该发现说明顶层波形通过和没有残留 `current`，仍不足以证明全部内部元数据保持不变。
原始 `results.json` 中的 `pass` 按实际 VCD 验收结果保留；额外完整性问题记录为独立审计结论。
后续规则定位与修复验证应追加新证据，不能覆盖本批工件或提前宣称全部工作完成。

[后续定位](diagnosis/findings.json)已将首次变化定位到普通 `hardware.md` 的 `READ_DIRECT` 规则附近，depth 1023→1024；只有 `connection[%53]` 改变，signals/history/register 保持不变。三次完整事件重放与正式状态相同，序列化单步重启未复现变化。所定位的规则不是 preset 分支；语义修复暂停，该 P0 隐患仍未解决。原字节工件与哈希见[诊断索引](diagnosis/index.json)。

[修改前后审计](audit/s2-before-autoconnect-audit.json)进一步确认：complete-01 的 S2 golden 全部178份状态连接不变，complete-02才出现9份变化；相同输入、MLIR、API、CLI、parser和setup，语义源码只差AutoConnect修改所在 `circt/circt.md`。这是本轮修改引入的元数据回归，P0仍未解决，不能笼统归为与本轮修改无关的既有问题。来源哈希见[历史对照索引](historical-comparison-index.json)。
