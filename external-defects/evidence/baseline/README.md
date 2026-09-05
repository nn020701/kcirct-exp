# 历史成功基线与当前服务

历史正式成功批次使用 `circt-semantics` 的 `d6bde7971eb3d07035d6f43c3c9a3153c6744288`，同时包含未提交的语义/API 修复。裸历史 HEAD 不能复现本轮结果。原始 [service.patch](service.patch) 从 `.runs/batch-final-01/service.patch` 按字节保存，5833 字节，SHA256 为 `54a7053789eebda3e68c824b4f3c8515f5f517602ca09de19a69458bccbb57a9`。

补丁包含 `seq.to_clock` 单比特语义、同宽二态 `ceq/cne` 比较和多个命名端口共享信号时的读取别名支持。[baseline.json](baseline.json) 提取原版本、工具版本、语义/API/definition/parser 哈希，并关联原记录哈希；它是可移植摘要，完整原版本日志仍在 `.runs`。

当前可用服务提交 `85bb13fa52a54b94e2ab5dc933ccc3ef378e9064` 已包含所需修复，迁移验证时其语义文件与 API 哈希与本次 prepare 相同。使用这个或包含相同修复的服务即可；不要再次将历史补丁叠加到已修复服务。若需精确还原历史基线，应在独立干净 checkout 检出历史 HEAD，先检查补丁适用性再应用，并核对 baseline 中的语义及 API 哈希。

历史工具版本为 K/pyk 7.1.323、CIRCT firtool-1.147.0（LLVM 23.0.0git）、Verilator 5.048；具体构建版本以摘要和原记录为准。实验仓库的操作测试迁移是独立维护层面，不能替代必要语义，也不能仅凭当前测试数证明另一工具链复现成功。
