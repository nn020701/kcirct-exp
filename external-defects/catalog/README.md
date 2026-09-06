# 设计与来源目录

此目录保存可移植的来源身份和候选配置；外部组件双执行 VCD 结论见 `results/vcd/`，原 `results/` 根目录保存历史低电平 CSV 结论。

- [design-index.json](design-index.json)：9 个已配置项目、10 个缺陷变体，以及正常组、替换文件和 CSV 的路径映射。
- [ir-index.json](ir-index.json)：各变体正常版与缺陷版的持久化 MLIR、源码映射、生成来源及来源运行状态；可从这里定位语义输入和调试位置。
- [candidate-inventory.json](candidate-inventory.json)：短池配置与仍未展开的 SPI、D7 候选。`configuration_status` 表示存在完整配置，不表示仿真通过。
- [upstream.json](upstream.json)：上游仓库、固定 commit、归档 SHA256 和导入核查来源。
- [设计目录](../designs/README.md)：按正常组、缺陷变体、测试输入、MLIR 和来源材料组织的文件说明。

所有活动路径（包括 IR 索引和各组 `provenance.json` 中的产物、当前源码路径）相对实验根目录 `external-defects/`。`source_run` 的记录路径指向本地忽略的 `.runs/` 历史归档，干净检出无需取得归档即可阅读已保存的 IR 和生成来源。原 `project.toml` 保持字节不变，其项目相对路径由各自 `provenance/layout.json` 解析；manifest 的 `source_hashes` 同时固定源文件及 layout 的哈希。辅助 `to_btor2.ys` 作为原始来源保留，不承担当前 runner 的执行配置。

MLIR 基线的三种形式、来源核查及刷新约定见[实验说明](../README.md#mlir-测试基线)。IR 索引保留历史受阻输入及其生成来源，当前正式 VCD 状态另绑定 complete-03；文件存在本身不表示通过。10 个已配置变体的主协议与全部逐次状态连接审计均已完成，旧 S2 回归作为历史另存，见 [STATUS](../STATUS.md)。

当前 runner 校验来源与产物哈希后直接消费已保存的 generic MLIR，通过公开 `kcirct simulate` 命令执行。每个变体的输入事件位于其 `testbench/<variant>.events.json`，与 CSV 对应且不包含预期输出；[设计目录](../designs/README.md)提供导航。新协议每个事件同输入双执行后 dump，全 low/high VCD 对照与历史 CSV 观测分别报告。

迁移前自动生成的来源清单、静态核查报告与 manifest 快照保存在 `.work/migration/`。它们可能含旧绝对路径和早期运行状态，仅用于迁移审计；`.runs/` 中的历史运行证据也保持原始字节。
