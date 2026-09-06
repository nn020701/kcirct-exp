# 外部组件双执行 VCD 正式结果

协议：`external-cli-double-eval-vcd-v1`。实际尝试 10 个变体 / 9 个来源案例，完整通过 10 个变体 / 9 个来源案例。

输入共 326 条 CSV 行，展开为 642 个 low/high 事件；通过案例覆盖 642 个事件。每个事件的 Kimulator 调用在同一输入下执行两次后 dump，Verilator eval 完成后 dump；两版各自比较全部顶层输入和输出。事件数不重复乘以设计版本或后端数量。

完整通过还要求正常两后端满足低电平 CSV oracle，缺陷两后端触发同一首次 oracle 差异。缺陷版 oracle_mismatch 可以是预期结果；超时、解析失败、部分波形及 VCD 不一致均不能通过。

本页 pass 仅表示上述 VCD 与 oracle 协议通过。内部状态不变性等额外检查及未解决问题见 [STATUS.md](STATUS.md)，不能由波形一致推定内部状态完整性通过。

| 案例 | 变体 | CSV / 事件 | 正常 VCD | 缺陷 VCD | 状态 | 首个波形差异或阻塞 |
|---|---|---:|---|---|---|---|
| D13 | [d13](results/vcd/cases/d13.json) | 6 / 11 | 一致 · [K](evidence/vcd/vcd-complete-03/d13/golden/kimulator/test.vcd) / [Verilator](evidence/vcd/vcd-complete-03/d13/golden/native/trace.vcd) | 一致 · [K](evidence/vcd/vcd-complete-03/d13/buggy/kimulator/test.vcd) / [Verilator](evidence/vcd/vcd-complete-03/d13/buggy/native/trace.vcd) | pass | 无 |
| S3 | [s3](results/vcd/cases/s3.json) | 13 / 25 | 一致 · [K](evidence/vcd/vcd-complete-03/s3/golden/kimulator/test.vcd) / [Verilator](evidence/vcd/vcd-complete-03/s3/golden/native/trace.vcd) | 一致 · [K](evidence/vcd/vcd-complete-03/s3/buggy/kimulator/test.vcd) / [Verilator](evidence/vcd/vcd-complete-03/s3/buggy/native/trace.vcd) | pass | 无 |
| S1 | [s1b](results/vcd/cases/s1b.json) | 10 / 19 | 一致 · [K](evidence/vcd/vcd-complete-03/s1b/golden/kimulator/test.vcd) / [Verilator](evidence/vcd/vcd-complete-03/s1b/golden/native/trace.vcd) | 一致 · [K](evidence/vcd/vcd-complete-03/s1b/buggy/kimulator/test.vcd) / [Verilator](evidence/vcd/vcd-complete-03/s1b/buggy/native/trace.vcd) | pass | 无 |
| S1 | [s1r](results/vcd/cases/s1r.json) | 10 / 19 | 一致 · [K](evidence/vcd/vcd-complete-03/s1r/golden/kimulator/test.vcd) / [Verilator](evidence/vcd/vcd-complete-03/s1r/golden/native/trace.vcd) | 一致 · [K](evidence/vcd/vcd-complete-03/s1r/buggy/kimulator/test.vcd) / [Verilator](evidence/vcd/vcd-complete-03/s1r/buggy/native/trace.vcd) | pass | 无 |
| D8 | [d8](results/vcd/cases/d8.json) | 14 / 27 | 一致 · [K](evidence/vcd/vcd-complete-03/d8/golden/kimulator/test.vcd) / [Verilator](evidence/vcd/vcd-complete-03/d8/golden/native/trace.vcd) | 一致 · [K](evidence/vcd/vcd-complete-03/d8/buggy/kimulator/test.vcd) / [Verilator](evidence/vcd/vcd-complete-03/d8/buggy/native/trace.vcd) | pass | 无 |
| D12 | [d12](results/vcd/cases/d12.json) | 16 / 31 | 一致 · [K](evidence/vcd/vcd-complete-03/d12/golden/kimulator/test.vcd) / [Verilator](evidence/vcd/vcd-complete-03/d12/golden/native/trace.vcd) | 一致 · [K](evidence/vcd/vcd-complete-03/d12/buggy/kimulator/test.vcd) / [Verilator](evidence/vcd/vcd-complete-03/d12/buggy/native/trace.vcd) | pass | 无 |
| D11 | [d11](results/vcd/cases/d11.json) | 17 / 33 | 一致 · [K](evidence/vcd/vcd-complete-03/d11/golden/kimulator/test.vcd) / [Verilator](evidence/vcd/vcd-complete-03/d11/golden/native/trace.vcd) | 一致 · [K](evidence/vcd/vcd-complete-03/d11/buggy/kimulator/test.vcd) / [Verilator](evidence/vcd/vcd-complete-03/d11/buggy/native/trace.vcd) | pass | 无 |
| D4 | [d4](results/vcd/cases/d4.json) | 185 / 369 | 一致 · [K](evidence/vcd/vcd-complete-03/d4/golden/kimulator/test.vcd) / [Verilator](evidence/vcd/vcd-complete-03/d4/golden/native/trace.vcd) | 一致 · [K](evidence/vcd/vcd-complete-03/d4/buggy/kimulator/test.vcd) / [Verilator](evidence/vcd/vcd-complete-03/d4/buggy/native/trace.vcd) | pass | 无 |
| S2 | [s2](results/vcd/cases/s2.json) | 45 / 89 | 一致 · [K](evidence/vcd/vcd-complete-03/s2/golden/kimulator/test.vcd) / [Verilator](evidence/vcd/vcd-complete-03/s2/golden/native/trace.vcd) | 一致 · [K](evidence/vcd/vcd-complete-03/s2/buggy/kimulator/test.vcd) / [Verilator](evidence/vcd/vcd-complete-03/s2/buggy/native/trace.vcd) | pass | 无 |
| C4 | [c4](results/vcd/cases/c4.json) | 10 / 19 | 一致 · [K](evidence/vcd/vcd-complete-03/c4/golden/kimulator/test.vcd) / [Verilator](evidence/vcd/vcd-complete-03/c4/golden/native/trace.vcd) | 一致 · [K](evidence/vcd/vcd-complete-03/c4/buggy/kimulator/test.vcd) / [Verilator](evidence/vcd/vcd-complete-03/c4/buggy/native/trace.vcd) | pass | 无 |

## 证据与统计范围

[selection.json](results/vcd/selection.json) 固定正式批次；同一变体采用清单中最后一次尝试。[summary.json](results/vcd/summary.json)、[summary.csv](results/vcd/summary.csv) 保存当前结果，[attempts.json](results/vcd/attempts.json) 保留全部入选尝试。

| 批次 | 案例尝试 | 批量原始结果 SHA256 |
|---|---:|---|
| vcd-standard-01 | 10 | `33e850d351ba429e2e024034b47c0c57f94b082f25e181d74983e759e53998bb` |
| vcd-standard-02 | 5 | `265cda91c161b3a4bd05da0a145e951d04f234af1c1b62a6d9ab846fccad4f37` |
| vcd-array-bits-02 | 2 | `b83075034919da7fb50cdb56b197b3c21e76e158c0bd1929db57fb0de8e0a20f` |
| vcd-complete-01 | 10 | `ec1ccdd90ff1544ae6074f27556f7d0e13da3091f2dd08d04e4880b7d966d77f` |
| vcd-complete-02 | 10 | `6c800ca260708ff0b72f17fa20ad27fa8635eeb974d43f2fdef359204f7c5b3d` |
| vcd-complete-03 | 10 | `41c192bf1c328cf104eb714db9598847f5c8108f3cd030c660b6d8c554a3ecd8` |

[evidence/vcd/index.json](evidence/vcd/index.json) 保存本报告原始 VCD、事件输入、CLI 结果、实际命令、工具版本、比较日志与错误诊断的路径和 SHA256。文件按原字节导出；日志中的绝对路径表示运行时来源，重新运行使用 [README](README.md) 的可配置命令。干净检出可直接打开波形并查看失败证据，无需本地 .runs；重新生成报告仍需要完整原始归档。

历史单执行低电平 CSV 结果保留在 [RUNS.md](RUNS.md)，不计入本表的 VCD 通过数量。当前结论与卡点见 [STATUS.md](STATUS.md)，单个用户的外部组件流程见 [USER_WORKFLOW.md](USER_WORKFLOW.md)。

这些结果验证固定输入、参数和二态初始化下的有限波形对照；不将接口可用性当作用户研究结论。未开发 Error-trace，保存的普通仿真状态仍需独立分析。
