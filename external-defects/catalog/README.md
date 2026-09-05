# 设计与来源目录

此目录保存可移植的来源身份和候选配置；执行结论见实验根目录的 `results/`。

- [design-index.json](design-index.json)：9 个已配置项目、10 个缺陷变体，以及正常组、替换文件和 CSV 的路径映射。
- [candidate-inventory.json](candidate-inventory.json)：短池配置与仍未展开的 SPI、D7 候选。`configuration_status` 表示存在完整配置，不表示仿真通过。
- [upstream.json](upstream.json)：上游仓库、固定 commit、归档 SHA256 和导入核查来源。
- [设计目录](../designs/README.md)：按正常组、缺陷变体、测试输入和来源材料组织的文件说明。

所有活动路径相对实验根目录 `external-defects/`。原 `project.toml` 保持字节不变，其项目相对路径由各自 `provenance/layout.json` 解析；manifest 的 `source_hashes` 同时固定源文件及 layout 的哈希。辅助 `to_btor2.ys` 作为原始来源保留，不承担当前 runner 的执行配置。

迁移前自动生成的来源清单、静态核查报告与 manifest 快照保存在 `.work/migration/`。它们可能含旧绝对路径和早期运行状态，仅用于迁移审计；`.runs/` 中的历史运行证据也保持原始字节。
