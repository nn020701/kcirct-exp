# kcirct-exp

这里集中保存 K/CIRCT 的可复现实验，包括外部设计、驱动契约、比较方法、正式结果和关键证据。语义实现仍由独立的 `circt-semantics` 服务提供；实验仓库可与它并列放置，也可显式选择其他安装位置。

目前包含 [external-defects](external-defects/README.md)：使用公开 RTL 缺陷及原测试输入，先验证普通仿真器能重现真实失败，再据证据提出 Error-trace 需求。本轮没有开发 Error-trace。

- [使用方法与实验边界](external-defects/README.md)
- [当前结论与卡点](external-defects/STATUS.md)
- [正式运行案例](external-defects/RUNS.md)
- [三例失败分析](external-defects/failure-analysis.md)与[功能需求及优先级](external-defects/error-trace-requirements.md)

## 环境与最小运行

需要 Python 3.11+、所选 `circt-semantics` 的 Python 包及其依赖、匹配该服务 `kframework` 版本的 K 工具、CIRCT 和 Verilator。默认从 `PATH` 查找工具。以下命令在本目录运行，假定服务位于同级目录：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e ../circt-semantics -r requirements-dev.txt
make test PYTHON=.venv/bin/python
make prepare PYTHON=.venv/bin/python
make run PYTHON=.venv/bin/python CASES=d13
```

也可以通过 `PYTHON` 使用已安装所选服务的现有虚拟环境。runner 会校验实际导入的 API 和 kdist 插件是否来自指定服务，避免混用其他 checkout。

当前服务提交 `85bb13fa52a54b94e2ab5dc933ccc3ef378e9064` 已包含实验所需的 `seq.to_clock`、同宽二态 `ceq/cne` 与端口读取别名修复。历史正式成功基线是 `d6bde7971eb3d07035d6f43c3c9a3153c6744288` 加工作树补丁，裸历史 HEAD 不能复现；还原依据见 [baseline](external-defects/evidence/baseline/README.md)。操作测试的目录迁移属于维护工作，不替代这些语义要求。

## 保存约定

`external-defects/designs/`、`manifests/`、`catalog/` 是可分享的实验输入；`results/` 是精简正式结果；`evidence/` 保存经索引和哈希校验的关键原始证据。新运行完整写入 `external-defects/.runs/`，构建写入 `.build/external-defects/`，临时审计写入 `external-defects/.work/`。后三者均忽略版本控制。历史运行归档保留原字节，迁移不会改写其中的旧机器路径。

本目录作为顶层工作区的独立 Git 子模块维护，远端为
`git@github.com:nn020701/kcirct-exp.git`。实验资产在本仓库提交；顶层仓库只记录子模块指针。
