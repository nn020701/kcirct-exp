# 独立接口验证证据

这里保存公开 Kimulator CLI 和外部实验驱动环境的独立验证。
它们用于检查用户使用流程与组件边界，不新增正式案例，也不计入正式批次的案例或事件总数。

## 最简 CLI 流程

[原始验证记录](public-cli-d13/validation.json) 保存实际命令和环境。输入是仓库长期保存的
D13 正常版 Generic MLIR 与 `d13.events.json`，命令只显式提供顶层名、输入事件、输出 VCD
和工作目录。未传 `--parser`、`--definition-dir` 或 `--evaluations-per-input`：

- 通过 `KDIST_DIR` 找到已构建定义，CLI 自动生成本次 parser。
- 默认同输入求值两次，共 11 个事件、22 次仿真、26 次外部命令。
- VCD 包含全部 8 个顶层端口，时间为 0 至 10 ns，最后 `frame_len=1`。
- 使用真实外部 diffvcd 对 `vcd-standard-01` 的 D13 正常版 Verilator VCD 比较，退出码为 `0`。

可直接查看 [VCD](public-cli-d13/test.vcd)、[CLI 结果](public-cli-d13/result.json)、
[原始命令日志](public-cli-d13/commands.jsonl) 和 [diffvcd 命令](public-cli-d13/diffvcd.command.json)。
CLI 和 diffvcd 的 stdout/stderr 均已保留；成功比较的输出日志为空，这是该工具的正常行为。

## 外部 runner 的独立环境

[环境验证记录](isolated-runner/isolated-runner-env.json) 保存虚拟环境创建和安装命令、
实际 Python 前缀、包清单、模块导入检查及测试命令。
环境仅安装实验 runner 的 `pytest`、`vcdvcd` 及其依赖；`kcirct` 与 `pyk` 均不可导入。
仿真通过明确指定的外部 `kcirct` 可执行文件完成。

在该环境中运行完整实验工具测试，结果为 **81 passed in 13.54s**；
[stdout](isolated-runner/isolated-runner-pytest.stdout.txt) 和
[stderr](isolated-runner/isolated-runner-pytest.stderr.txt) 保留实际输出。
这里验证的是实验驱动与仿真器进程的依赖边界，不意味着仿真器本身无需安装 K 或其 Python 依赖。

## 来源与复现

[index.json](index.json) 逐文件记录原始来源、SHA256 和字节数；原始 JSON 中的机器路径
作为历史记录保持不变，可通过索引找到这里的持久化副本。仅 diffvcd 命令记录由原
`validation.json` 明确提取，其来源哈希也已保存。没有复制 parser、Kore 或临时虚拟环境。

公开 CLI 尚未包含在基线提交中；复现前请按 [组件补丁说明](../component/README.md)
应用对应补丁。完整操作流程见 [USER_WORKFLOW.md](../../../USER_WORKFLOW.md)。
