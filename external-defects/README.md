# 外部 RTL 缺陷普通仿真实验

本实验使用公开设计、已知缺陷变体和独立测试输入，验证普通 Kimulator 能否与 Verilator 模拟同一正常与错误行为。当前协议为 `external-cli-double-eval-vcd-v1`：Kimulator 通过完整外部 CLI 执行，每个固定输入事件重复执行两次后 dump，以正常和缺陷两版全部顶层输入、输出的完整 low/high VCD diff 为主判据。CSV 的预期输出保留为辅助缺陷判据。

[STATUS.md](STATUS.md) 记录当前结论与卡点；[VCD_RUNS.md](VCD_RUNS.md) 列新协议正式结果；[USER_WORKFLOW.md](USER_WORKFLOW.md) 展示单用户外部组件流程。先前直接导入 API、各相位单次执行并比较低电平 CSV 的结果保留在 [RUNS.md](RUNS.md)，不计入新协议通过数量。[failure-analysis.md](failure-analysis.md) 和 [error-trace-requirements.md](error-trace-requirements.md) 继续解释其历史证据。本轮没有开发 Error-trace。

六批正式结果共 47 次尝试，最新 10 个变体 / 9 个来源的 VCD 主协议全部通过，每版 326 行 CSV / 642 个事件，两版合计 2,568 次 K 求值。第五份语义补丁后，[独立审计](evidence/vcd/metadata-integrity/vcd-complete-03/README.md)也确认全部 20 组、2,568 份逐次状态的完整 `connection` 保持 setup。VCD 与内部不变量分别验证；历史 S2 回归保留，本轮仅在语义层规避，没有修改 K/LLVM backend。

## 来源与目录

设计来自固定版本的 [RTLRepair](https://github.com/ekiwi/rtl-repair/tree/71e1afc0b9a2327d008b46acd415cf3f0343a938)，其中 bugbase 来源固定为 `7702e478f4ffdca477273d5a395992ecf006d70f`。提交、归档哈希和来源说明见 [catalog/upstream.json](catalog/upstream.json)。上游文件保持原字节，原许可和来源说明随设计保存；没有因复制实验资产而改变其许可。

| 路径 | 作用 |
|---|---|
| [designs/](designs/README.md) | 每项目的 `original/` 正常 RTL 与依赖、`variants/<id>/` 缺陷文件、`testbench/` CSV/TB、`mlir/` 测试基线、`provenance/` 来源与路径映射 |
| [manifests/](manifests) | 可执行配置：文件及哈希、参数、端口、CSV、采样协议、掩码和超时 |
| [catalog/](catalog/README.md) | 上游来源、候选池和设计索引；候选不等于已运行案例 |
| [results/vcd/](results/vcd/summary.json) | 新协议正式批次、全部尝试及每案例结果 |
| [evidence/vcd/](evidence/vcd/index.json) | 新协议原始 VCD、事件输入、CLI 结果、比较日志及哈希 |
| [results/](results/summary.json) | 历史低电平 CSV 的精简结果 |
| [evidence/](evidence/README.md) | 关键真实输出、状态窗口、IR、补丁及其来源/哈希索引 |
| `.runs/` | 完整命令、版本、构建/运行日志、每事件 Kore 状态和中间结果；本地忽略 |
| `../.build/external-defects/` | 实验专用 K definition/parser 构建；本地忽略 |

`designs/<project>/provenance/layout.json` 将上游文件名映射到当前布局。9 个项目、10 个 manifest 的 CSV 共 326 行，展开为 642 个独立 low/high 事件。每个设计的 `testbench/<variant>.events.json` 是版控激励，只含输入与时间，不含 oracle。全部配置已执行；当前主协议通过数量由 [summary.json](results/vcd/summary.json) 给出，额外内部审计另见 [STATUS](STATUS.md)。

## MLIR 测试基线

MLIR 是 Kimulator 的直接测试输入，按 `designs/<project>/mlir/<variant>/{golden,buggy}/` 纳入版本管理，分别对应正常组和缺陷组。需要独立转换版本时，在变体目录下新增 `<generation>/{golden,buggy}/`，通过 manifest 的 `ir_baseline` 选择该版本、`ir_profile` 声明转换约定；没有这两个字段时沿用原目录。[设计目录](designs/README.md)提供阅读入口，[catalog/ir-index.json](catalog/ir-index.json)提供每组文件与来源运行的机器可读索引。

| 文件 | 用途 |
|---|---|
| `design.mlir` | 前端生成或经声明转换后保存的可读形式，用于理解模块与运算 |
| `design.generic.mlir` | 供 Kimulator 编译的 generic 形式，用于检查 operation、类型、属性及语义覆盖 |
| `design.debug.generic.mlir` | 同一 IR 带 location 的 generic 形式，用于回查 RTL 源码位置 |
| `source-map.json` | 固定执行版与调试版哈希，记录 operation 行号对应与 location 别名 |
| `provenance.json` | 记录来源运行、生成命令、顶层及参数、工具版本、RTL 路径与哈希、产物哈希及运行状态 |

基线保留实际运行产物的原始字节。历史 location 中的旧源码路径，通过 `provenance.json` 的 `rtl_sources` 和项目 `provenance/layout.json` 对应到当前 RTL；其中指向当时生成文件的路径用于识别来源，不作为当前可执行路径。不要直接替换 IR 内的路径，否则原哈希与映射也会失效。

runner 验证 provenance 中的顶层、参数、前端配置、RTL 顺序以及源码与产物 SHA256 后，直接将持久化 `design.generic.mlir` 交给外部组件，运行阶段不调用 CIRCT 前端。刷新基线需在独立生成过程中选择工具版本、核对源码及参数，再一并更新三种 MLIR、映射、来源与 IR 索引，并审阅差异。保存 IR 本身不表示仿真通过；历史受阻输入同样保留，即使当前已选择新版本；执行结论见 [STATUS.md](STATUS.md) 与 [VCD_RUNS.md](VCD_RUNS.md)。

来源记录区分案例结论与单个后端状态：缺陷版的 `backend_status=oracle_mismatch` 可以是预期缺陷差异，同时案例为 `case_status=pass`；这不是 K 执行错误，判定条件见[比较与采样契约](#比较与采样契约)。

`evidence/` 中用于失败分析的 IR 快照绑定各自历史批次，继续保留其来源，不随设计基线刷新而替换。

### 一次常量初始化的受限转换

`constant-initial-register-v1` 用于保留 RTL 的一次常量初始化。工具
[prepare_ir.py](prepare_ir.py) 从同一 RTL、参数和 CIRCT 工具生成 pre-LLHD 与 HW 两个阶段，
再调用 [initial_lowering.py](initial_lowering.py) 核对初始化来源。它只把已证明的一次、
无条件、零物理延迟常量驱动转为同名、同宽整数寄存器的 `seq.firreg preset`；
随后由官方 `llhd-sig2reg`、canonicalize 和 verifier 完成转换。

该转换要求 manifest 明确采用 `rtl_initial_plus_two_state_zero`。不匹配的非零初值、
动态或延迟初始化、多驱动歧义及不支持的 LLHD 结构会失败；最终仍含 LLHD 时不会发布新版本。
这是一项有边界的前端转换，不表示 Kimulator 已实现通用 LLHD 执行。

以下命令从实验仓库根目录运行，使用 `PATH` 中的 CIRCT 工具；也可通过 `CIRCT_BIN`
或 `--circt-bin` 指定工具目录：

```sh
.venv/bin/python external-defects/prepare_ir.py \
  --cases s2 --generation initial-register-example
```

两版转换成功后，新目录保存三种最终 MLIR、两个前端阶段的原始 generic IR、
`initialized.hw.generic.mlir`、`initial-lowering.json`、源码映射与 provenance。
审计记录关联被移除的初始化驱动、寄存器、初值、位宽及输入/输出哈希。
命令和日志的完整工作目录位于忽略的 `.work/ir-preparation/`。

默认只生成版本，不切换 manifest。审阅后将 `ir_baseline` 指向新目录，并设置
`ir_profile` 为 `constant-initial-register-v1`；也可在首次生成命令增加 `--activate`，
让工具在两版生成和基线校验完成后切换。已有版本不会覆盖，重试使用新的 generation 名称。
生成记录中的 `generated_not_simulated` 只表示 IR 已生成；能否完成普通仿真仍须通过
独立组件、完整输入事件和两版 Verilator VCD 对照确认。

## 安装与选择工具

需要 Python 3.11+。实验环境按[根 README](../README.md)只安装 `requirements-dev.txt`；组件独立安装提供 `kcirct simulate` 的版本及其依赖。K 工具须匹配组件声明的 `kframework`，另需 Verilator。当前运行不要求 CIRCT，更新持久化 IR 时才使用相应前端。当前完整案例集需按顺序应用 CLI、数组、preset、AutoConnect、indexed read 五份组件补丁，完整身份和顺序见 [STATUS](STATUS.md#组件身份与独立进程边界)。

| CLI 参数 | 环境变量 | 省略时 |
|---|---|---|
| `--kimulator` | `KIMULATOR` | 从 `PATH` 找安装后的 `kcirct` |
| `--k-bin` | `K_BIN` | 组件继承的 `PATH` 中的 K 工具 |
| `--verilator` | `VERILATOR` | 从 `PATH` 找 `verilator` |
| `--diffvcd` | `DIFFVCD` | 选定服务目录下的 `scripts/diffvcd.py` |
| `--kcirct-root` | `KCIRCT_ROOT` | 同级 `circt-semantics`，只用于默认定位 diffvcd |
| `prepare_ir.py --circt-bin` | `CIRCT_BIN` | 从 `PATH` 查找 `circt-verilog` 与 `circt-opt`，仅用于更新 IR |

`PYTHON` 选择实验解释器，`KIMULATOR` 选择独立组件命令，二者可属于不同虚拟环境。runner 用公开 `kcirct simulate --describe` 查询包、语义哈希及工具身份。`--diffvcd` 可选择独立比较脚本，解除默认服务目录布局的依赖。组件内部复用自身 API；实验端只启动进程、传文件与公开参数、读取退出码及产物，不导入 `kcirct` / `pyk`，不修改内部方法。

## 运行与汇总

以下命令在实验仓库根目录执行。`prepare` 构建专用 definition/parser，`run` 保存完整普通仿真证据；已有运行目录不能覆盖。

准备记录绑定组件语义与 kdist 插件身份、K 版本、parser，以及 `definition.kore`、`compiled.bin`、`backend.txt`、`interpreter` 四个完整构建工件的 SHA256。运行前再次核验；组件或构建内容变化时须重新 `prepare`，不能混用旧缓存。

```sh
make prepare PYTHON=.venv/bin/python
make inputs PYTHON=.venv/bin/python CASES=all-short
make run PYTHON=.venv/bin/python CASES=d13 ARGS='--run-id example-d13'
make run PYTHON=.venv/bin/python CASES=all-short ARGS='--run-id example-all'
```

`CASES=all-short` 选择全部 10 个已配置变体。也可直接使用 CLI：

```sh
.venv/bin/python external-defects/runner.py prepare --kcirct-root ../circt-semantics
.venv/bin/python external-defects/runner.py run --cases d13 --run-id d13-check
```

`inputs` 只从上游 CSV 生成版控事件 JSON，已有不同内容时拒绝覆盖；文件已随设计保存，普通运行无需重复生成。省略 `--run-id` 时生成新名称。完整运行结果保存在 `.runs/<run-id>`；准备记录在 `.runs/validation`。案例检查来源、基线和事件一致性后执行两后端，失败保留阶段与日志，后续案例继续执行。

批次在全部所选案例结束并保存证据后返回：所有案例通过时退出 `0`，任一案例未通过时退出 `1`。因此 `make run` 的非零退出不表示后续案例被放弃；查看该批次 `results.json` 获取逐案例结论。汇总应在批次结束后执行。

```sh
make report-vcd PYTHON=.venv/bin/python REPORT_ARGS='--runs example-all'
.venv/bin/python external-defects/report.py --protocol vcd --runs example-d13
```

VCD 报告首次必须显式 `--runs`，后续省略时只读取 `results/vcd/selection.json`。同一变体采用清单中最后一次尝试，全部入选尝试保存在 `attempts.json`。报告验证精确协议、完整双执行和两组 VCD 证据，拒绝旧 CSV 批次；导出到 `results/vcd/`、`VCD_RUNS.md` 与 `evidence/vcd/<run-id>/`。原字节与 SHA256 一起保存，同名证据内容变化时拒绝覆盖。干净副本可直接看 VCD、JSON 与日志；重算仍需要完整 `.runs` 归档。旧 CSV 汇总保留 `make report REPORT_ARGS='--runs batch-first-01 batch-memory-01 batch-final-01'` 入口，新报告不改历史根目录结果。

## 比较与采样契约

CSV 第 `i` 行的非时钟输入固定不变：在 `2*i ns` 驱动 `clock=0`；除最后一行外，在 `2*i+1 ns` 驱动 `clock=1`。两个后端实际输入事件必须一致，VCD 时基为 `1ns`，本适配器面向无延迟 DUT。

| 后端 | 每个事件的执行 |
|---|---|
| Kimulator | 固定全部输入 → simulate → 同一输入从前次状态 simulate → 在该事件时间 dump |
| Verilator | 固定全部输入 → eval 完成本次组合与寄存器更新 → 在该事件时间 trace dump |

Kimulator 第二次调用不翻转时钟、不新增事件或时间点，沿用现有语义要求的传播协议。low 和 high 都双执行后采样，再比较全部事件。比较先检查必需顶层端口、位宽、完整时间窗口和确定值，再调用外部 `diffvcd.py`。两侧额外内部信号不参加规定端口集合；规定端口缺失不能用 `skip_missing` 或 `--ignore-missing-signals` 隐藏。

`read_ports_fast(skip_missing=True)` 是组件内部读取端口时跳过尚无信号值的条目，随后 `simulate` 仍检查全部必需顶层输入、输出。通用 `diffvcd` 可以只比较同名信号交集，适应额外声明的数量差异；本实验先验证 manifest 规定端口完整，再选择它们比较。`--ignore-missing-signals` 进一步跳过有声明但无采样的信号，本实验未启用。上述选项都不是忽略已有信号值不一致的手段。

一位端口可能被一侧声明为标量 `q`、另一侧声明为 `q[0:0]`。在已确认同一顶层端口且双方位宽均为 1 后，比较器只为需要的一侧生成改写该声明的 VCD 副本，使用 `scalar-equals-i1-zero-range-v1` 映射后执行 diff。原始 VCD 保持不变，`normalization-map.json` 保存原/副本哈希、逐端口名称映射与波形正文哈希，证明正文未修改。其他名称或位宽差异仍报错；所有规定端口的每个 low/high 采样值仍参加比较。

通过要求：正常与缺陷两版分别 K/Verilator VCD 一致，正常两后端满足低电平 CSV oracle，缺陷两后端保留相同首次 oracle 差异。缺陷后端的 `oracle_mismatch` 可以是预期结果；构建/解析失败、超时、部分轨迹或任何规定端口波形差异不能通过。D12 三个无 CSV oracle 的状态输出也参加 VCD diff。使用声明的二态零初始化，保留 RTL 显式初值，不额外插入 reset。

D13 使用实际 UUT 默认的 `DATA_WIDTH=64, KEEP_WIDTH=8`，不能误用 TB 局部的宽度变量。S1 的两个变体使用各自 CSV。D11 仅掩去上游明确标为未知的那个 oracle 单元格，输入未知和其他未授权未知值会被拒绝。所有掩码、参数、列归一化和宽度均由 manifest 明示。

历史独立原 TB 对照覆盖 D13/S3 的完整原轨迹；D8 原 TB 在第 13 个上升沿结束，只覆盖完整 14 行 CSV 的前 13 条，末行由 CSV 驱动验证。相关原字节证据见 [evidence](evidence/README.md)。这些历史观测不替代新协议的完整 VCD 验证；有限轨迹也不证明四态未知值、任意测试平台、多时钟或全部参数组合的兼容性。

## 证据与解释

新批次保存 runner/native/waveform 快照、工具身份、协议与来源校验；每后端记录真实命令、VCD、驱动、退出码和错误。组件另有每次执行记录与可选压缩 Kore 状态。完整记录留在 `.runs`；新正式共享证据以 [VCD index](evidence/vcd/index.json) 保存原始 VCD、事件、CLI 结果、比较日志及 SHA256；旧证据仍由[原 index](evidence/index.json)索引。原日志绝对路径表示当时来源，不改写为看似可执行的新路径。

组件非空原始 `.stderr` 全部导出，包含 parser 的原始错误；成功调用产生的空 `.stderr` 只保留命令记录与内容哈希，避免重复保存过程空文件。比较器显式索引的日志仍按原字节全部保存。较大的 Kore 状态、模型构建与其他中间文件继续留在忽略的 `.runs`。

结果耗时包括进程启动和 Kore I/O，不能直接充当公平性能倍率。历史单执行低电平分析不自动转化为新协议结论，新差异须按事件相位解释。人工状态分析不代表自动因果追踪。外部 CLI 与独立安装的操作流程可用作接口复现证据，不能替代用户研究。
