MR 标题：按索引分阶段读取 operation 参数，避免仿真中的连接表变化

部分真实设计在 LLVM 执行中出现了 `connection` 内 operation 的 SSA 参数列表变化，例如 mux 的条件参数丢失、末尾参数重复。这个问题可能使后续求值卡住，也可能在短轨迹的 VCD 仍一致时留下错误连接。

将 `HARDWARE#READ` 改为两个按索引推进的 continuation：先按原顺序求值全部依赖，再按原顺序读取全部结果。原参数列表只参与长度查询和索引访问；现有求值与 `READ_DIRECT` 规则只接收新建的单元素列表，继续复用寄存器 history、显式 preset 和内存 Map 的读取逻辑。保留现有 AutoConnect 整表匹配，以及同一输入执行两次后 dump 的实验协议。本修改只调整 K/CIRCT 语义，K 和 LLVM backend 保持原版本。

验证：

- LLVM、Haskell、LLVM library 三个 target 均编译通过，构建快照与冻结的 52 个语义文件哈希一致。
- S3、D12、S2 从各自原始事件 prestate 连续执行到结束，完整 `connection` 保持不变，全部 current 正常清空。
- 标准 operation 的 13 组求值及 13 组 VCD 比较共 26 项通过，覆盖数组、层级 alias、时钟、寄存器、preset 和内存读写。26 份末态快照全部正常结束且连接表不变；67 个输入与参考资产的前后哈希一致。
- `vcd-complete-03` 的 10 个配置、正常/缺陷两版共 20 组 VCD 对照全部通过，逐事件核对 18,310 个端口值。独立审计检查全部 2,568 份求值状态，完整 `connection` 均与各自 setup 一致，变化数与未绑定命令输出哈希数均为 0。

这是在既有后端上对已观察问题的语义层规避。原始失败证据保留；三例事件重放与正式批次分别绑定各自重新构建的定义，不将有限轨迹上的通过解释为底层缺陷已普遍修复。

稳定证据：[补丁、构建身份与 operation 验证](/Users/bytedance/cym/cymProject/k-circt-top-repo/services/kcirct-exp/external-defects/evidence/vcd/component/indexed-read/README.md)，[完整状态和波形审计](/Users/bytedance/cym/cymProject/k-circt-top-repo/services/kcirct-exp/external-defects/evidence/vcd/metadata-integrity/vcd-complete-03/README.md)。
