# 正式运行结果

固定短池实际运行 **10 个缺陷变体 / 9 个原始案例**，共 326 条已知独立 CSV 采样（0 个变体样本数未知）；完整通过 **7 个变体 / 6 个原始案例**，共 254 条采样。

完整通过要求正常原生和正常 K 满足独立 oracle，正常/缺陷 K 分别与对应原生全部规定观测一致，并且缺陷两后端保留相同首次 oracle 差异。不同后端、正常/缺陷版本和重复运行不增加独立案例数。

| 原案例 | 变体 | 采样 | 正常原生/oracle | 正常 K/oracle | 缺陷 K/原生 | 缺陷首次 oracle 差异 | 当前状态 |
|---|---|---:|---|---|---|---|---|
| D13 | [d13](results/cases/d13.json) | 6 | 一致 | 一致 | 一致 | 5: frame_len 1 → 3 | pass |
| S3 | [s3](results/cases/s3.json) | 13 | 一致 | 一致 | 一致 | 8: input_axis_tready 1 → 0 | pass |
| S1 | [s1b](results/cases/s1b.json) | 10 | 一致 | 一致 | 一致 | 5: S_AXI_AWREADY 0 → 1 | pass |
| S1 | [s1r](results/cases/s1r.json) | 10 | 一致 | 一致 | 一致 | 5: S_AXI_ARREADY 0 → 1 | pass |
| D8 | [d8](results/cases/d8.json) | 14 | 一致 | 一致 | 一致 | 4: m_axis_tvalid 1 → 0 | pass |
| D12 | [d12](results/cases/d12.json) | 16 | 一致 | 一致 | 一致 | 13: m_axis_tdata 3 → 4 | pass |
| D11 | [d11](results/cases/d11.json) | 17 | 一致 | 未完成 | 未完成 | 13: drop_frame 0 → 1 | timeout |
| D4 | [d4](results/cases/d4.json) | 185 | 一致 | 一致 | 一致 | 67: s_axis_tready 0 → 1 | pass |
| S2 | [s2](results/cases/s2.json) | 45 | 一致 | 未完成 | 未完成 | 42: M_AXIS_TLAST 0 → 1 | execution_error |
| C4 | [c4](results/cases/c4.json) | 10 | 一致 | 未完成 | 未完成 | 4: input_axis_tready 0 → 1 | timeout |

未完成 K 执行的行，其首次差异来自已完成的缺陷原生运行，不能算作 K 重现成功。

## 统计来源

本表从 3 个指定正式批次、17 次批量案例尝试生成；同一变体选用清单中最后一次结果。正式批次选择保存在 [selection.json](results/selection.json)，迁移检查和其他验证不会自动进入已有正式清单。

| 批次 | 案例尝试数 | 原始结果 SHA256 |
|---|---:|---|
| batch-first-01 | 5 | `455fe2f346d0ddb6cae74c5dc9a570294dba85f3812b88eb1f579dd04a57b794` |
| batch-memory-01 | 5 | `2c9170139adf9791b2f879b67fba784b738acb5223081cf7cb61cab6ff814f5b` |
| batch-final-01 | 7 | `5e11e8e2665942a033a025763240203c834cf96d2386fd7b110b78faf6a5a525` |

精简机器表：[JSON](results/summary.json)、[CSV](results/summary.csv)；保留每次尝试的状态和首次差异：[attempts.json](results/attempts.json)。关键原始输出、状态窗口和来源哈希见 [evidence/index.json](evidence/index.json)。

## 结论的适用范围

这是固定配置、外部输入轨迹和独立检查依据下的有限仿真重现，不是形式化证明，也不表示无需驱动适配就兼容全部 SV/C++ 测试环境。D13/S3 完整原 TB 轨迹和 D8 的13条共有前缀另有对照；D8 的最后一条由完整外部 CSV 验证。

阶段耗时保留在机器结果中，包含进程启动及 Kore I/O；验证期间的并行运行成本不能用作公平性能倍率。本表只由实际案例结果计算，不将历史单元测试数量写成迁移后的验证结论。

当前卡点见 [STATUS.md](STATUS.md)，使用方法见 [README.md](README.md)，三例详细分析见 [failure-analysis.md](failure-analysis.md)。本轮未开发 Error-trace；后续功能需求见 [error-trace-requirements.md](error-trace-requirements.md)。
