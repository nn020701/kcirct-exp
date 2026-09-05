# 可分享的关键证据

此目录从完整 `.runs` 归档选择与验收、失败分析及回归检查直接相关的工件；[index.json](index.json) 逐份记录原始来源、目标路径、字节数与 SHA256。所列原始工件均按字节复制，压缩 Kore 保留原压缩字节。状态窗口中的事件 SHA256 则对应未压缩 Kore，两者不能混用。

- 各案例 `golden_native/buggy_native/golden_k/buggy_k/output.csv`：来自正式清单为该案例采用的批次。尚未完成 K 的配置只有原生 CSV。
- `d13/native-independent/`：独立原 TB 的两版完整输出和失败/采样窗口；两个 `output.csv` 同时是 native 适配器回归的可分享参考。
- `s3/original-tb/` 与 `d8/original-tb-prefix.json`：原 TB 对照；D8 只验证原 TB 实际执行的 13 条共有前缀，完整 CSV 为 14 条。
- `d13/analysis/`、`d8/analysis/`、`d4/analysis/`：分析批次的两版 generic/debug IR、源码映射和选定事件状态。
- `analysis/`：从这些实际状态读取的寄存器、控制和存储窗口；D4 另保存地址 2 的历史有效写入记录。
- [baseline/](baseline/README.md)：历史服务补丁原字节及版本、语义哈希摘要。
- [blockers.json](blockers.json)：从原日志提取的结构化卡点摘要，显式标注为派生数据，并保存原日志来源与哈希；不是改写后的日志。

原始 IR、source-map 与状态窗口可能含旧 `sources/`、`results/` 或机器绝对路径。这是历史记录，不能作为当前程序路径解析输入。旧 `results/<批次>` 完整归档现位于 `.runs/<批次>`；共享工件通过索引的 `source` 关联，设计文件通过 `designs/<project>/provenance/layout.json` 和原哈希关联。为保持证据真实性，不替换原日志/IR 内部的路径；当前可执行 manifest 和正式精简结果使用新布局。

完整事件序列、命令、构建产物和含机器路径的原日志仍保存在忽略的 `.runs`，不随精简证据全部复制。仅凭这些选定窗口可以复核文档列出的局部值；若要重新枚举所有事件或重算完整历史报告，需要对应完整归档。人工状态读取未增加新的 Error-trace 功能。
