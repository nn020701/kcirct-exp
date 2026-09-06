# kcirct-exp

这里保存 K/CIRCT 的可复现实验，包括设计与持久化 MLIR、驱动契约、比较方法、正式结果和关键证据。Kimulator 由独立安装的 `kcirct` 命令提供，实验仓库通过文件、参数和退出码调用它。

已配置的 10 个变体 / 9 个来源完成正式运行：VCD 主协议全部通过，每版 326 行 CSV / 642 个事件，两版合计 2,568 次 K 求值；第五份语义补丁改用索引读取共享参数列表后，20 组全部 2,568 份状态的完整连接审计也通过，见[当前结论](external-defects/STATUS.md)。历史回归证据保留；本轮没有修改 K/LLVM backend。

目前包含 [external-defects](external-defects/README.md)：使用公开 RTL 缺陷及原测试输入，先验证普通仿真器能重现真实失败，再据证据提出 Error-trace 需求。本轮没有开发 Error-trace。

- [使用方法与实验边界](external-defects/README.md)
- [外部组件用户流程](external-defects/USER_WORKFLOW.md)：MLIR 和事件 JSON → 单条模拟命令 → VCD 与诊断
- [设计与持久化 MLIR](external-defects/designs/README.md)：正常版、缺陷版及其生成来源
- [当前结论与卡点](external-defects/STATUS.md)
- [双执行 VCD 正式结果](external-defects/VCD_RUNS.md)与[历史低电平 CSV 结果](external-defects/RUNS.md)
- [三例失败分析](external-defects/failure-analysis.md)与[功能需求及优先级](external-defects/error-trace-requirements.md)

## 环境与最小运行

需要 Python 3.11+、独立安装并提供 `simulate` 的 Kimulator、与其 `kframework` 匹配的 K 工具，以及 Verilator。运行阶段直接使用持久化 generic MLIR，不依赖 CIRCT 前端。实验和组件可以使用不同虚拟环境。以下命令在本目录运行，组件路径仅展示同级 checkout 的一种布局：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
export KIMULATOR=../circt-semantics/.venv/bin/kcirct
make test PYTHON=.venv/bin/python
make prepare PYTHON=.venv/bin/python
make run PYTHON=.venv/bin/python CASES=d13 ARGS='--run-id example-d13'
make report-vcd PYTHON=.venv/bin/python REPORT_ARGS='--runs example-d13'
```

也可将安装后的 `kcirct` 放入 `PATH`，省略 `KIMULATOR`。`PYTHON` 选择实验解释器，`KIMULATOR` 选择完整外部组件。runner 通过公开 `kcirct simulate --describe` 查询组件身份与工具版本，不导入 `kcirct` / `pyk`。

`prepare` 保存组件与完整编译工件哈希，运行前再次核验。批次会完成全部所选案例并保存证据；任一案例未通过时，最终以非零退出码通知调用方，详细结论仍可汇总。

当前完整案例集使用基线 `3afaa5f93d8ed0cabeb08bdce1fd4c5f74a8a5a2` 加五份按顺序保存的补丁：[公开 CLI](external-defects/evidence/vcd/component/README.md)、[一维整数数组语义](external-defects/evidence/vcd/component/packed-array-semantics/README.md)、[整数 firreg preset](external-defects/evidence/vcd/component/scalar-firreg-preset/README.md)、[AutoConnect 整 List 表达](external-defects/evidence/vcd/component/auto-connect-list-preservation/README.md)、[共享参数索引读取](external-defects/evidence/vcd/component/indexed-read/README.md)。基线已有 `seq.to_clock`、同宽二态 `ceq/cne` 与端口别名修复；裸基线不含公开 `simulate`。补丁绑定实际身份并验证可应用，不表示已提交或全部内部问题已解决。

## 保存约定

`external-defects/designs/`、`manifests/`、`catalog/` 是可分享的实验输入。每个设计的 `mlir/<variant>/{golden,buggy}/` 持久化保存测试基线，包括可读 MLIR、Kimulator 输入的 generic MLIR、带 location 的调试 MLIR、源码映射和生成来源，纳入版本管理；独立版本使用 `mlir/<variant>/<generation>/{golden,buggy}/` 并由 manifest 选择，例如 S2 的 `initial-register-v1`，旧版本保留；入口见 [IR 索引](external-defects/catalog/ir-index.json)。

`results/vcd/` 与 `evidence/vcd/` 保存新协议的精简结果、原始 VCD、事件、CLI 诊断及哈希；原 `results/` 根目录及其他 `evidence/` 保留历史 CSV 证据。新运行完整写入 `external-defects/.runs/`，构建写入 `.build/external-defects/`，临时审计写入 `external-defects/.work/`，这三处忽略版本控制。runner 校验 RTL、参数和产物哈希后直接消费持久化 generic MLIR，按[更新约定](external-defects/README.md#mlir-测试基线)有意识地刷新。历史 location 和日志保持原字节，其中旧路径按来源记录解释。

本目录作为顶层工作区的独立 Git 子模块维护，远端为
`git@github.com:nn020701/kcirct-exp.git`。实验资产在本仓库提交；顶层仓库只记录子模块指针。
