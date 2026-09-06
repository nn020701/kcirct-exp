# complete-03 全状态连接审计

本批次十个已配置变体、九个来源的主协议 VCD 全部通过；正常/缺陷两版各有 326 行 CSV 展开的 642 个 low/high 事件，每事件同输入执行两次。两版合计 2,568 次求值。

独立审计确认 **20 组全部 2,568 份逐次状态的完整 connection 与各自 setup 一致**。它重新读取每份 gzip，并同时核验 states.json、对应命令 stdout SHA、event/evaluation/time、source_path、setup、末态与磁盘快照集合。Map 按 key 精确比较并拒重复 key；递归 Map 的项顺序可以不同，所有 sort、inj 目标类型和 List 顺序保持。

- [完整 connection 审计](audit/vcd-complete-03-connection-audit.json)与[审计脚本](audit/audit_connections.py)。
- [完整波形与证据审计](audit/vcd-complete-03-audit.json)：逐事件全部规定端口、外部 CLI 调用、输入/组件身份、命令与压缩状态哈希。
- [旧 complete-02 反证](audit/previous-complete02-audit.json)：同一审计准确检出 S2 golden 原有九份变化，零哈希未绑定；[比较器边界检查](audit/auditor-checks.json)保留基于真实 setup 在内存中构造的六项比较器检查。
- [原字节来源与 SHA256](index.json)。

本目录保存全状态审计索引、每组 setup/末态、最后两份 gzip、全部命令和 states.json；其余逐次 gzip 仍在完整 `.runs/vcd-complete-03` 归档，压缩与解压 SHA 均已固定。顶层 VCD 和正式运行文件由[六批报告](../../../../VCD_RUNS.md)及新批次 evidence 单独索引。

第五份 [indexed read 语义补丁](../../component/indexed-read/README.md)后，历史 S2 异常在本轮轨迹中不再出现。complete-02 的 VCD pass 与九份 metadata 损坏同时是真实观察，旧证据不改写。本轮没有修改 K/LLVM backend，也不把有限轨迹的规避有效扩大为底层根因已彻底修复。
