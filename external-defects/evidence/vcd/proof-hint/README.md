# 连接列表异常的 proof-hint 诊断

本次按用户要求启用 K 7.1.323 已有的 proof-hint，没有修改服务语义、生产 runner 或 LLVM runtime，也没有开发 Error-trace。旧语义与当前语义分别复制到独立目录，52 份源码逐一匹配 complete-01 / complete-02 的哈希。原始状态和正式 VCD 结果未改写。

**实际命中的规则已经确认，但开启 hint 输出后，三例都没有在原步数保留普通运行中的连接损坏。根因与修复仍未完成。**

## 实际结果

每个案例均从原始事件 prestate 连续执行到指定 depth。`full` 同时开启 `--llvm-proof-hint-instrumentation` 与 `--llvm-proof-hint-debugging`；`lite` 只开启前者。四个隔离定义构建均成功。十份普通模式的边界输出与原先保存的对应状态逐字节相同；六份 HINT v13 文件均返回 0，并通过现有 pyk 流式解码。

| 案例 | 普通模式的首次边界 | hint 最后命中的规则 | 普通输出的 connection 参数 | full / lite hint 终态参数 |
|---|---|---|---|---|
| S3 golden | 1956→1957 | ordinal 1304，Auto Connect | `[%28,%112,%112]` | `[%124,%28,%112]` |
| D12 golden | 942→943 | ordinal 1304，Auto Connect | `[%65,%70,%70]` | `[%57,%65,%70]` |
| S2 golden | 1023→1024 | ordinal 1277，普通 Bits READ_DIRECT | `[%50,%54,%54]` | `[%51,%50,%54]` |

depth 是 K 重写步数；ordinal 必须结合本次配套定义解释，不是跨版本稳定编号。规则源码位置另用官方 `llvm-kompile-compute-loc` 核实。三例 full/lite 解码终态各自逐字节相同；按 Map 项和有序 List 值比较，hint 的连接表保持原值，与普通模式末态各差一个目标 key。值比较处理了序列化结合形式与注入目标 sort 差异，不宣称严格 KORE 类型相等。

用户可直接阅读[实际规则与变量绑定](decoded/boundary-review.md)，其中包含六份日志的事件号、源码位置、关键参数和对应 JSON；[机器摘要](decoded/boundary-summary.json)提供同一结果。S3/D12 最后规则后记录两次 `LIST.concat`，S2 为一次 `LIST.concat`；这些日志均没有 `LIST.range` 事件。编译器用于模式匹配的 `hook_LIST_range_long` 不一定作为 K hook 事件写入 hint，因此不能据事件缺失断言该函数没有执行。

## 已确认的运行时事实与仍需验证的假设

本机实际 LLVM backend 为 0.1.139，来源由 Nix derivation、原始源码、安装头文件和静态库绑定，见[运行时身份](runtime/source-identity.json)。

- [列表实现](runtime/source-excerpts.txt)显示 `hook_LIST_range_long` 创建 transient，再调用 `drop` / `take`。Immer 在 `can_mutate` 为真时可以把叶子中的后续元素向前移动；对三元素列表丢弃首项，这种原地操作与 `[a,b,c]→[b,c,c]` 的形状吻合。
- 当前内存策略使用 `no_refcount_policy` 和 GC transience owner token。节点错误获准原地修改、以及 GC 后 token 地址复用，是具体待验证假设；尚未记录失败现场的叶子地址、owner token 或 GC 迁移，不能宣布已经确认根因。
- [proof 输出源码与库核验](runtime/proof-output-findings.json)确认：`serialize_term_to_proof_trace` 为记录参数、变量等调用 `kore_alloc` 分配临时包装对象。这会增加同一 K 堆中的分配。lite 仍记录这些值，因此减少配置 dump 没有消除这项影响。
- 所查 proof Map/List 序列化递归读取当前容器，未发现按 block 指针缓存旧内容；这不是排除整个系统所有编码/解码差异的证明。当前结果应保留为“普通模式与 hint 模式状态不同”，不能把 hint 的正确连接当作修复成功。

下一项有针对性的诊断应记录普通执行路径中 `hook_LIST_range_long` 的输入叶子、共享关系、owner token、`can_mutate` 判断及 GC 边界，并验证探针自身仍保留异常。本次未实施该探针或修改语义。

## 证据与复现

[selected-index.json](selected-index.json)绑定这里精选工件的来源与 SHA256；[raw-hints.json](raw-hints.json)绑定六份完整二进制日志、定义身份、事件数和本机存放位置。约 2 GB 的原始 hint、完整解码尾部与临时构建保留于忽略目录 `.work/complete-exp/proof-hint/`。这里持久化关键规则事件、终态对照、无损压缩的解码终态、构建/运行命令和运行时源码证据。

通用调用形式如下，路径由调用者指定：

```sh
kompile "$SEMANTICS_SOURCE/circt-core.k" \
  --backend llvm --main-module CIRCT-CORE --syntax-module CIRCT-CORE-SYNTAX \
  --llvm-proof-hint-instrumentation --llvm-proof-hint-debugging \
  --output-definition "$DIAGNOSTIC_DEFINITION"

krun "$ORIGINAL_PRESTATE" --definition "$DIAGNOSTIC_DEFINITION" \
  --parser cat --term --no-expand-macros --depth "$REWRITE_DEPTH" \
  --output kore > "$ORDINARY_STATE"

krun "$ORIGINAL_PRESTATE" --definition "$DIAGNOSTIC_DEFINITION" \
  --parser cat --term --no-expand-macros --depth "$REWRITE_DEPTH" \
  --proof-hint > "$PROOF_HINT"
```

lite 对照去掉构建参数 `--llvm-proof-hint-debugging`，使用另一个输出目录。实际命令、工具路径、原始 prestate 哈希和返回码以 `current/`、`old/` 中保存的记录为准。这些诊断不增加正式实验案例数，也不替代 VCD 主协议。
