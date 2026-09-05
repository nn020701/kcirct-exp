# 外部 RTL 缺陷普通仿真实验

本实验使用公开设计、已知缺陷变体和独立测试输入，验证普通 Kimulator 能否与 Verilator 重现同一失败。正常版必须先满足外部 oracle；正常与缺陷两版还要分别通过 K/原生全观测比较，才能将缺陷轨迹作为后续 Error-trace 需求的依据。

[STATUS.md](STATUS.md) 只记录当前结论与卡点；[RUNS.md](RUNS.md) 列实际正式运行；[failure-analysis.md](failure-analysis.md) 分析已保存的 D13/D8/D4 失败；[error-trace-requirements.md](error-trace-requirements.md) 提出需求。本轮没有开发 Error-trace。

## 来源与目录

设计来自固定版本的 [RTLRepair](https://github.com/ekiwi/rtl-repair/tree/71e1afc0b9a2327d008b46acd415cf3f0343a938)，其中 bugbase 来源固定为 `7702e478f4ffdca477273d5a395992ecf006d70f`。提交、归档哈希和来源说明见 [catalog/upstream.json](catalog/upstream.json)。上游文件保持原字节，原许可和来源说明随设计保存；没有因复制实验资产而改变其许可。

| 路径 | 作用 |
|---|---|
| [designs/](designs/README.md) | 每项目的 `original/` 正常 RTL 与依赖、`variants/<id>/` 缺陷文件、`testbench/` CSV/TB、`provenance/` 来源与路径映射 |
| [manifests/](manifests) | 可执行配置：文件及哈希、参数、端口、CSV、采样协议、掩码和超时 |
| [catalog/](catalog/README.md) | 上游来源、候选池和设计索引；候选不等于已运行案例 |
| [results/](results/summary.json) | 指定正式批次的精简可移植结果与每案例摘要 |
| [evidence/](evidence/README.md) | 关键真实输出、状态窗口、IR、补丁及其来源/哈希索引 |
| `.runs/` | 完整命令、版本、构建/运行日志、每事件 Kore 状态和中间结果；本地忽略 |
| `../.build/external-defects/` | 实验专用 K definition/parser 构建；本地忽略 |

`designs/<project>/provenance/layout.json` 将原上游文件名映射到当前布局。源码哈希用于检查文件是否仍与固定来源一致。9 个项目、10 个 manifest 的 CSV 共 326 条。实际运行和通过数量由结果计算，详见 RUNS。

## 安装与选择工具

需要 Python 3.11+。从实验仓库根目录按[根 README](../README.md)安装所选服务及开发依赖。K 工具版本应匹配服务的 `kframework` 依赖；CIRCT 与 Verilator 需要可执行文件。历史版本及语义修复见 [baseline](evidence/baseline/README.md)，不能只检出未含修复的历史 HEAD。

| CLI 参数 | 环境变量 | 省略时 |
|---|---|---|
| `--kcirct-root` | `KCIRCT_ROOT` | 本仓库同级 `circt-semantics` |
| `--k-bin` | `K_BIN` | 从 `PATH` 找 `kompile`、`krun`、`kast` |
| `--circt-bin` | `CIRCT_BIN` | 从 `PATH` 找 `circt-verilog`、`circt-opt` |
| `--verilator` | `VERILATOR` | 从 `PATH` 找 `verilator` |

`--k-bin` 和 `--circt-bin` 指定工具目录，`--verilator` 指定程序。Python 运行时由 Makefile 的 `PYTHON` 或 `reproduce.sh` 的 `PYTHON` 环境变量控制；后者默认 `python3`。选定服务路径须与该 Python 实际导入的 API 和 kdist 插件路径一致。

## 运行与汇总

以下命令在实验仓库根目录执行。`prepare` 构建专用 definition/parser，`run` 保存完整普通仿真证据；已有运行目录不能覆盖。

```sh
make prepare PYTHON=.venv/bin/python
make run PYTHON=.venv/bin/python CASES=d13
make run PYTHON=.venv/bin/python CASES='s3 s1b s1r d8'
make run PYTHON=.venv/bin/python CASES='d12 d11 d4 s2 c4'
```

`CASES=all-short` 选择全部 10 个配置，包括目前仍受阻的配置。也可直接使用 CLI：

```sh
.venv/bin/python external-defects/runner.py prepare --kcirct-root ../circt-semantics
.venv/bin/python external-defects/runner.py run --cases d13 --run-id d13-check
```

省略 `--run-id` 时生成新目录名。运行结果固定保存在 `.runs/<run-id>`；准备记录在 `.runs/validation`。案例先检查 manifest 和源码哈希，再执行原生与 K；失败阶段同样保存命令与日志，后续案例继续保留自己的结果。

```sh
make report PYTHON=.venv/bin/python
make report PYTHON=.venv/bin/python REPORT_ARGS='--runs batch-first-01 batch-memory-01 batch-final-01'
```

`report.py` 重算需要所选批次的完整 `.runs` 归档。默认使用 [results/selection.json](results/selection.json)；显式 `--runs` 更新正式选择，按清单顺序为同一变体采用最后一次结果。没有选择文件时才扫描已有批次。迁移检查与临时验证不会自动扩大已有正式清单。干净副本可以直接阅读已发布的 `results/` 和 RUNS；如需重算历史汇总，须另行取得对应完整归档。改变选择时，`results/cases/` 同步为当前集合，历史尝试仍保存在 `.runs`。尚未导出关键证据的新批次不会链接到旧批次的 CSV。

## 比较与采样契约

每案例检查正常原生及正常 K 是否满足独立 CSV oracle，再比较两版全部 manifest 输出的 K/原生轨迹；缺陷两后端须保存相同首次 oracle 差异。`simulator_agrees_with_native` 和 `bug_detected_by_oracle` 分别记录这两件事。缺陷后端的 `oracle_mismatch` 可以是预期结果；构建失败、解析失败、超时和部分轨迹不能算案例通过。D12 的三个状态输出虽不在外部 oracle 列中，仍纳入两后端比较。

当前 CSV 驱动使用声明的二态零初始化：逐行设置输入和低时钟，执行 low eval 后读取输出；除最后一行外，再执行 high eval 提交上升沿。K 的低相位对应偶数事件；读取信号本身不触发推进。该观测契约经本池逐案例检查，不能据此推断任意 SV 调度或每个中间事件都与原生相同。特别是 D8，奇数事件内部寄存器更新与顶层端口再次传播存在边界，分析须保留事件相位。

D13 使用实际 UUT 默认的 `DATA_WIDTH=64, KEEP_WIDTH=8`，不能误用 TB 局部的宽度变量。S1 的两个变体使用各自 CSV。D11 仅掩去上游明确标为未知的那个 oracle 单元格，输入未知和其他未授权未知值会被拒绝。所有掩码、参数、列归一化和宽度均由 manifest 明示。

独立原 TB 对照覆盖 D13/S3 的完整原轨迹；D8 原 TB 在第 13 个上升沿结束，只覆盖完整 14 行 CSV 的前 13 条，末行由 CSV 驱动验证。相关原字节证据见 [evidence](evidence/README.md)。这些有限轨迹并非形式化证明，也没有证明四态未知值、任意测试平台、多时钟或全部参数组合的兼容性。

## 证据与解释

每后端记录命令、版本、驱动、初始化/采样契约、标准输出/错误、阶段耗时和输出 CSV。K 额外记录输入 IR、调试 location、源码映射、事件 metadata、压缩 Kore 状态和状态哈希。完整记录留在 `.runs`；共享证据以 [index.json](evidence/index.json) 标记原始来源、字节数和 SHA256。原日志中的历史绝对路径不改写为看似可执行的新路径。

结果耗时包括进程启动和 Kore I/O，历史并行运行的耗时不能直接充当公平的仿真性能倍率。人工读取保存状态得到的分析同样标注其来源；它不代表已经实现自动因果追踪。
