# 当前结论与卡点

**全部 10 个已配置变体、9 个来源案例已完成：主协议 VCD 全部通过，独立检查的 20 组、2,568 份逐次状态也全部保持完整 `connection` 与 setup 一致。** 当前结果来自 `vcd-complete-03`。每版使用 326 行 CSV 展开的 642 个 low/high 事件，每事件同输入求值两次；两版合计 1,284 个完成事件、2,568 次 K 求值。

第五份语义补丁将共享参数列表改为按索引求值和读取，S2 的历史 P0 异常在本轮轨迹中不再出现。本轮没有修改 K/LLVM backend，也没有开发 Error-trace；这个结论不等于底层共享缺陷已根治或所有输入普遍正确。

## 当前判据与验证

runner 通过完整外部 `kcirct simulate` 进程消费持久化 generic MLIR 和版控事件。全部顶层输入、输出在每个 low/high 事件比较真实 VCD；正常版满足辅助 CSV oracle，缺陷版保留相同首次 oracle 差异。oracle 预期值不传给组件，必需信号缺失、未知值、错误位宽和不完整轨迹不能通过。

[VCD 正式报告](VCD_RUNS.md)与[完整证据审计](evidence/vcd/metadata-integrity/vcd-complete-03/audit/vcd-complete-03-audit.json)分别保留原始波形、命令和身份。[全状态连接审计](evidence/vcd/metadata-integrity/vcd-complete-03/README.md)重新读取全部快照，逐份绑定 gzip、索引和命令 stdout SHA，检查事件顺序、双执行、setup 和末态。比较递归 Map 的 key/value，保留所有 sort、inj 目标类型及 List 次序；仅 Map 序列化顺序变化不算内容损坏。旧 complete-02 的同一审计仍准确检出九份 S2 异常，说明比较器没有忽略真实参数顺序变化。

## 六批真实历史

[机器汇总](results/vcd/summary.json)和[全部尝试](results/vcd/attempts.json)保留六批共 **47 次案例尝试**，显式选择各变体最后一次主协议结果。历史重跑不增加当前配置的独立事件数。

| 正式批次 | 尝试数 | 当时真实结果 |
|---|---:|---|
| `vcd-standard-01` | 10 | 3 通过、4 VCD 声明预检差异、2 超时、1 执行错误 |
| `vcd-standard-02` | 5 | 4 通过、1 执行错误 |
| `vcd-array-bits-02` | 2 | D11、C4 通过 |
| `vcd-complete-01` | 10 | 8 通过、S3/D12 正常版执行错误 |
| `vcd-complete-02` | 10 | 10 个 VCD 通过；独立审计发现 S2 九份连接变化 |
| `vcd-complete-03` | 10 | 10 个 VCD 通过；20 组全部 2,568 份状态连接不变 |

complete-03 的 [runner/make](evidence/vcd/vcd-complete-03/run/batch-exit.json)均返回 0。旧 standard-01 在存在失败时仍返回 0、standard-02 返回 1、complete-01 runner/make 返回 1/2，均按各自原始记录保留；不追溯改写退出码或旧 VCD 通过观察。

## 已处理卡点与仍有的边界

- **D11/C4 数组形状**：历史首事件 120 秒超时最初只表明原因未知。静态检查确认缺少 `hw.array_inject` 及数组 mux/firreg 注册、初始化形状；补充限定的一维正长度整数数组、二态和有效索引语义后，原输入完成对照。不是一般性能结论或任意聚合支持。
- **S2 初值与 LLHD**：旧 LLHD generic IR 的 parser 失败保留原字节。当前选择 `initial-register-v1`，将已证明的一次常量初始化转为整数 firreg preset；[独立 RTL/SV 对照及来源证明](evidence/vcd/ir-normalization/README.md)支持该受限转换，不表示通用 LLHD 语义。
- **S3/D12 执行停驻**：[complete-01 失败](evidence/vcd/execution-failures/vcd-complete-01/README.md)中 krun 返回 0，但仍有 current/operation，CLI 报 `未清空 []` 并返回 1。三次原事件重放逐字节复现；严格 mux 检查暴露只读参数列表损坏。更早的 VCD 通过仍是真实观察。
- **S2 元数据回归**：[前后版本对照](evidence/vcd/metadata-integrity/vcd-complete-02/audit/s2-before-autoconnect-audit.json)确认：相同输入、IR、API、CLI、parser、setup 下，第四份 AutoConnect 补丁解决 S3/D12 路径的同时，在 S2 引入 event84/eval2 起九份连接变化。第五补丁后的本轮全状态审计通过；[旧失败与相邻状态](evidence/vcd/metadata-integrity/vcd-complete-02/README.md)不覆盖，也不改写其 VCD `pass`。

[arc 调度的直接 API 诊断](evidence/vcd/metadata-integrity/vcd-complete-02/arc-protocol/index.json)与旧 CLI 的 178 个状态逐字节相同，排除了新包装/槽位轮换造成该差异。[proof-hint 诊断](evidence/vcd/proof-hint/README.md)确认命中 AutoConnect/READ_DIRECT；普通模式仍复现，追踪模式的连接损坏却消失。实际 runtime 源码和静态库确认 proof 参数序列化会额外 `kore_alloc`，但 GC token 复用和具体写入 hook 的底层根因仍未获得低扰动动态证明。语义层规避不能替代这项证明。

一位标量与 `[0:0]` 只通过严格等价 header 副本解决，原波形正文不改。当前结论仅覆盖给定参数、二态初始化、时钟连接及固定轨迹，不证明四态、多时钟、所有参数或任意内部不变量。SPI、D7 仍属未展开候选，不计入完成数量。

## 组件身份与用户流程

组件基线 `3afaa5f93d8ed0cabeb08bdce1fd4c5f74a8a5a2` 上依次应用五份尚未提交的源码补丁：

1. [公开 simulate CLI](evidence/vcd/component/README.md)。
2. [一维整数数组语义](evidence/vcd/component/packed-array-semantics/README.md)。
3. [整数 firreg preset](evidence/vcd/component/scalar-firreg-preset/README.md)。
4. [AutoConnect 整 List 表达](evidence/vcd/component/auto-connect-list-preservation/README.md)，保留其旧回归说明。
5. [共享参数 indexed read](evidence/vcd/component/indexed-read/README.md)，本轮规避与当前身份。

干净 archive 上五份补丁的十次检查/应用全部成功，最后仅修改 `hardware.md`；全部 52 份语义源码及 API/simulator/plugin 与正式准备身份匹配。正式定义 SHA256 为 `08ac54e383967aa9aa7ba218cd0148e2b4d3f19dea67ddab33f120d661854e2b`，见 [prepared](evidence/vcd/vcd-complete-03/run/prepared.json)。独立候选构建源码相同，但定义中 16 条 owise 生成排除条件有分支/变量排列差异，不能归结为绝对路径差异或宣称 binary 等价；各项验证绑定各自定义，见[构建对照](evidence/vcd/component/indexed-read/validation/build-comparison.json)。

[独立接口验证](evidence/vcd/interface/README.md)确认实验环境无法导入 `kcirct`/`pyk`，仍可从外部组件得到标准 VCD。正式 runner 始终只传文件、公开参数并读取进程退出码；离线 Kore/直接 API 审计是独立诊断，不混同为论文主流程。复现入口见 [USER_WORKFLOW.md](USER_WORKFLOW.md)。

[标准 operation 验证](evidence/vcd/component/indexed-read/operation-validation/index.json)的 13 组仿真与 VCDdiff 共 26 项通过（850.50 秒 / 4.21 秒）；独立核验 13 份 setup 与最后 26 份轮换状态全部连接不变且终态正常，67 份输入/参考资产前后哈希一致。这不等于 operation 的每个中间状态都保存并检查；正式批次的全部 2,568 份快照由另一审计覆盖。

现有[实验工具测试](evidence/vcd/validation/current-experiment-tests/index.json)保留 150 项通过的原始记录；测试不增加正式案例数。耗时包含进程启动及 Kore I/O，不能作为公平性能倍率或用户研究结果。

## 后续 Error-trace 需求

历史单执行 CSV 机制分析继续绑定 [RUNS.md](RUNS.md) 和 [failure-analysis.md](failure-analysis.md)。[需求与优先级](error-trace-requirements.md)据真实设计错误、执行停驻、元数据损坏及追踪扰动提出可信诊断能力；本轮没有开发或验收 Error-trace，也没有把需求文档当作实现完成。
