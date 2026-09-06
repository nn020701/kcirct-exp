# proof-hint 边界实际记录

使用本机 K 7.1.323 的 `pyk.kllvm.hints.prooftrace.LLVMRewriteTraceIterator` 流式读取六份 HINT v13 文件；未安装其他依赖。`full` 启用 instrumentation 与 debugging，`lite` 仅启用 instrumentation。这里只描述日志中的事件和普通输出对照，不推断根因。

下表的事件号从 0 开始，表示 hint 事件序号；它不是 K rewrite depth。rule ordinal 只在配套 `definition.kore` 中解释。每个源码位置都用官方 `llvm-kompile-compute-loc` 另行核对。

| 案例与普通输出边界 | 模式 | 全部事件数 | 最后规则事件号 | rule ordinal | 源码 location |
| --- | --- | ---: | ---: | ---: | --- |
| S2 1023→1024 | [full](s2/boundary-events.json) | 9388 | 9384 | 1277 | `hardware/hardware.md` `56:1:63:42` ([官方定位](s2/compute-loc.stdout)) |
| S2 1023→1024 | [lite](s2-lite/boundary-events.json) | 8365 | 8361 | 1277 | `hardware/hardware.md` `56:1:63:42` ([官方定位](s2-lite/compute-loc.stdout)) |
| D12 942→943 | [full](d12/boundary-events.json) | 7339 | 7334 | 1304 | `circt/circt.md` `136:1:140:11` ([官方定位](d12/compute-loc.stdout)) |
| D12 942→943 | [lite](d12-lite/boundary-events.json) | 6397 | 6392 | 1304 | `circt/circt.md` `136:1:140:11` ([官方定位](d12-lite/compute-loc.stdout)) |
| S3 1956→1957 | [full](s3/boundary-events.json) | 16414 | 16409 | 1304 | `circt/circt.md` `136:1:140:11` ([官方定位](s3/compute-loc.stdout)) |
| S3 1956→1957 | [lite](s3-lite/boundary-events.json) | 14458 | 14453 | 1304 | `circt/circt.md` `136:1:140:11` ([官方定位](s3-lite/compute-loc.stdout)) |

六份最后规则的关键绑定如下，full 和 lite 相同。SSA 前缀分别是 S2 的 `xlnxstream_2018_3/`、D12 的 `axis_fifo/`、S3 的 `axis_adapter/`。原始 KORE substitution 保存在表格链接的 `boundary-events.json`。

- S2：`Port=%51`、`L=[%50,%54]`、`Signal=bits(0,1)`；规则是普通 Bits `READ_DIRECT`。紧接最后规则的是 `LIST.concat` 和 `MAP.concat` hook 事件。
- D12：`Arg=%57`、`Args=[%65,%70]`；规则是 `AutoConnect`。紧接最后规则的是两条 `LIST.concat` 和一条 `MAP.concat` hook 事件。
- S3：`Arg=%124`、`Args=[%28,%112]`；规则同为 `AutoConnect`。紧接最后规则的 hook 种类和次序与 D12 相同。

| 目标 connection key | 普通 before | 普通 after | full/lite hint 解码终态 |
| --- | --- | --- | --- |
| S2 `%53` | `[%51,%50,%54]` | `[%50,%54,%54]` | `[%51,%50,%54]` |
| D12 `%69` | `[%57,%65,%70]` | `[%65,%70,%70]` | `[%57,%65,%70]` |
| S3 `%131` | `[%124,%28,%112]` | `[%28,%112,%112]` | `[%124,%28,%112]` |

S2 的 current `14214` 中，普通 after 的 mux 模板也已变为 `[%50,%54,%54]`；hint 解码终态仍是 `[%51,%50,%54]`。D12 current `1379` 和 S3 current `3` 的目标 mux 模板在这一步普通 before/after 都保留原列表，其连接表条目已经改变。完整 current KORE 保存在各 `terminal-comparison.json`。

三例中，full 和 lite 的解码终态逐字节相同。按 Map 项无序、List 有序展开结合表示，并忽略 `inj` 目标 sort 的值对照，六份 hint 的整个 connection 都等于普通 before，和普通 after 各差一个表中目标 key；这不是严格 KORE 类型相等的声明。严格 repr 比较及原始 KORE 都保留在各 `summary.json` 和 `final.kore`。

因此这些 hint 能提供实际命中的规则编号、源码位置和 substitution；它们没有复现普通输出中观察到的最终连接变化。当前记录不能确定差异来自输出模式改变运行行为还是编码/解码过程，不能据此否认普通运行异常。

六份完整日志均没有 `LIST.range` hook 事件。编译器用于 head/tail 匹配的 `hook_LIST_range_long` 不一定作为 K hook 事件写入 hint，因此缺少该事件不能证明函数未被调用，也不能直接据这份日志锁定这个函数。

解码器为 [decode_hint.py](decode_hint.py)，末尾完整事件在各目录的 `tail.json`；全程 `events.ndjson` 只记录事件种类、rule ordinal 和 hook/function 名称。大项 substitution/参数/结果独立保存在按 SHA256 命名的 `terms/*.kore`，没有省略后伪装成完整值。
