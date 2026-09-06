# 外部 Kimulator CLI 的组件补丁

正式实验 `vcd-standard-01` 使用了本轮尚未提交的 `kcirct simulate` 公开接口。
`circt-semantics` 的基线提交 `3afaa5f93d8ed0cabeb08bdce1fd4c5f74a8a5a2` 本身不含该命令；
复现者需要在这个基线上应用 [public-simulate.patch](public-simulate.patch)，再安装 Python 包。

补丁只包含四个文件：

- `README.md`：通用命令、输入协议与运行工件说明。
- `src/kcirct/__main__.py`：公开 `simulate` 子命令。
- `src/kcirct/_simulate.py`：独立仿真流程、双执行采样、VCD 和失败证据。
- `src/tests/unit/test_simulate.py`：输入校验、双执行采样及失败证据的回归测试。

端口别名修复及其 unit 测试已经包含在基线中。补丁不包含 `api.py`，也不改变 K 语义。

## 应用与确认

先将 `KCIRCT_ROOT` 设为上述基线的干净 `circt-semantics` 工作树，将 `KCIRCT_EXP_ROOT`
设为本实验仓库位置。先检查补丁，检查通过后再应用：

```bash
git -C "$KCIRCT_ROOT" rev-parse HEAD
git -C "$KCIRCT_ROOT" apply --check \
  "$KCIRCT_EXP_ROOT/external-defects/evidence/vcd/component/public-simulate.patch"
git -C "$KCIRCT_ROOT" apply \
  "$KCIRCT_EXP_ROOT/external-defects/evidence/vcd/component/public-simulate.patch"
make -C "$KCIRCT_ROOT" poetry-install
"$KCIRCT_ROOT/.venv/bin/kcirct" simulate --describe
```

`--describe` 的 `simulator_sha256` 应为 `7ad752d4c2137fc6fdf113bbbc6b2d73841929fdd10fa7694ffe1d01434cecc3`，
`api_sha256` 应为 `40e6b398d06f6dff1ecdba85819330b54006a0d46aedaa0474613ac451a211cd`。
完整基线、四份文件在应用前后的 SHA256、补丁 SHA256、正式运行组件身份和验证过程见
[identity.json](identity.json)。K 工具与 Python 依赖仍需按实验说明安装；该补丁不包含编译后的定义或 parser。
从已有 MLIR 和事件运行的具体操作见 [外部组件使用流程](../../../USER_WORKFLOW.md)。

## 已执行的补丁验证

使用 `git archive` 导出上述提交的完整树，在独立临时目录实际执行了
`git apply --check` 和 `git apply`，两者退出码均为 `0`。应用后的四个文件逐字节哈希
与正式实验所用工作树一致；基线 `api.py` 的哈希保持不变，服务工作树未被修改。
临时验证目录已清理。

补丁 SHA256：`daa7d2d20f1cd33b759d6e96e56f8c1cfcadb6d101d32bcb1b427ceb1f78ec90`。

该证据用于在接口尚未提交时明确复现版本；它不代表补丁已经提交或发布。
