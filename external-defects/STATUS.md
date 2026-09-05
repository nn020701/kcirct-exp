# 当前结论与卡点

正式池实际运行 10 个缺陷变体、9 个原始案例，共 326 条 CSV 采样；7 个变体、6 个原始案例完整通过，共 254 条采样。完整清单及逐案例结果见 [RUNS.md](RUNS.md)。通过的是 d13、s3、s1b、s1r、d8、d12、d4：正常版满足外部 oracle，正常/缺陷 K 均与对应原生规定观测一致，缺陷保留同一首次 oracle 差异。

D13/D8/D4 的真实失败已保存输出、关键内部状态、generic SSA 和源码位置，详见 [failure-analysis.md](failure-analysis.md)。这些是人工核验的普通仿真证据。本轮未开发 Error-trace；[需求及优先级](error-trace-requirements.md)依据这些证据提出。

| 配置 | 当前阻塞 | 已完成部分 | 下一步需要解决什么 |
|---|---|---|---|
| d11 | 正常/缺陷 K 首事件均达到 120 秒超时 | 原生正常通过 oracle，缺陷已被检测；CIRCT 编译及导入完成 | 普通 K 执行的首事件成本/停滞诊断，尚无全轨迹一致性结论 |
| c4 | 正常/缺陷 K 首事件均达到 120 秒超时 | 原生正常通过 oracle，缺陷已被检测；CIRCT 编译及导入完成 | 同上，不能将超时当成设计缺陷定位成功 |
| s2 | LLHD 导入文本第 15 行解析失败：`unexpected <, expecting }` | 两版原生完成并符合预期；前端输出已保存 | 普通仿真的 IR/parser 支持缺口，尚未进入 K 事件执行 |

卡点来源、原始日志哈希及结构化摘要见 [evidence/blockers.json](evidence/blockers.json)。完整日志保存在本地 `.runs`。这三项是普通仿真的前置支持缺口，不应直接列为已验证的 Error-trace 功能缺陷。

S3/S1/D12 的早期比较或导入失败已在正式后续批次通过，早期结果保留于 [attempts.json](results/attempts.json)。D4 存储案例已通过完整 185 行端口轨迹比较，但内部存储因果分析目前仍是读取 K 保存状态后的人工核验。

候选目录中的其他项目尚未实际运行，不计入上述数量。迁移后的 prepare、D13 重跑和测试属于布局/接口验证，也不扩大正式历史清单。当前服务提交 `85bb13fa52a54b94e2ab5dc933ccc3ef378e9064` 含必要语义与 API 修复；历史基线及补丁记录见 [baseline](evidence/baseline/README.md)。
