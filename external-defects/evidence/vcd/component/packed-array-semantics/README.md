# 一维整数数组语义补丁

这里保存 `vcd-array-bits-02` 实际使用、尚未提交的数组语义源码，供独立复现实验。
[packed-array-semantics.patch](packed-array-semantics.patch) 在
`circt-semantics` 基线 `3afaa5f93d8ed0cabeb08bdce1fd4c5f74a8a5a2` 上使用，
并与上一层的 [公开 CLI 补丁](../README.md) 配合。
旧 CLI 补丁及其身份记录保持原字节；本目录不替换历史组件版本。

补丁只包含五个语义文件：

| 文件 | 内容 |
|---|---|
| `dialects/hw/hw-layout.md` | 静态打包位宽与数组索引位宽计算 |
| `hardware/bits.md` | 在打包 Bits 中替换指定元素的位区间 |
| `dialects/hw/hw.md` | 二态有效索引的 `hw.array_inject` |
| `dialects/comb/comb.md` | 相同静态类型和实际位宽的数组 `comb.mux` |
| `dialects/seq/seq.md` | 数组 `seq.firreg` 的注册、初始化与历史状态读取 |

表中路径均相对 `src/kcirct/kdist/circt_semantics/`。运行时数组使用打包 Bits，
MLIR 的数组类型仍保留；元素 0 位于最低位。验证范围是一维、正长度、正整数位宽、
二态值及有效索引；数组寄存器采用已有零初始化和同步复位策略。数组的显式 `preset`
和异步复位保留明确的未支持标记，不将嵌套数组、零位宽或四态行为列为已支持能力。
补丁不改变 `api.py`、CLI 或实验驱动，也不包含编译后的定义和 parser。

## 应用补丁

将 `KCIRCT_ROOT` 设为上述基线的干净组件工作树，`KCIRCT_EXP_ROOT` 设为实验仓库位置。
先按组件说明安装依赖，并让与 `kframework 7.1.323` 匹配的 K 工具位于组件环境中。
依次应用两个补丁：

```sh
git -C "$KCIRCT_ROOT" rev-parse HEAD
git -C "$KCIRCT_ROOT" apply --check \
  "$KCIRCT_EXP_ROOT/external-defects/evidence/vcd/component/public-simulate.patch"
git -C "$KCIRCT_ROOT" apply \
  "$KCIRCT_EXP_ROOT/external-defects/evidence/vcd/component/public-simulate.patch"
git -C "$KCIRCT_ROOT" apply --check \
  "$KCIRCT_EXP_ROOT/external-defects/evidence/vcd/component/packed-array-semantics/packed-array-semantics.patch"
git -C "$KCIRCT_ROOT" apply \
  "$KCIRCT_EXP_ROOT/external-defects/evidence/vcd/component/packed-array-semantics/packed-array-semantics.patch"
make -C "$KCIRCT_ROOT" poetry-install
```

若工作树已应用旧 CLI 补丁，从数组补丁的检查步骤继续。随后使用实验仓库的
`prepare` 重新构建定义和 parser，避免使用旧语义的构建缓存；以下命令按独立环境运行：

```sh
export KIMULATOR="$KCIRCT_ROOT/.venv/bin/kcirct"
make -C "$KCIRCT_EXP_ROOT" prepare PYTHON="$KCIRCT_EXP_ROOT/.venv/bin/python"
make -C "$KCIRCT_EXP_ROOT" run PYTHON="$KCIRCT_EXP_ROOT/.venv/bin/python" \
  CASES='d11 c4' ARGS='--run-id reproduce-array-bits'
```

实验环境依赖及完整操作见 [实验说明](../../../../README.md)。重跑使用新的批次名；
该命令不会覆盖 `vcd-array-bits-02` 的历史归档。

## 已执行的验证与身份核对

使用完整 `git archive` 基线，在独立临时目录依次实际执行两个补丁的
`git apply --check` 和 `git apply`，四次退出码均为 `0`。数组补丁应用前后的
文件差异恰好为上述五个文件；应用后全部 **52 份语义源文件**的路径集合和 SHA256
均与 `vcd-array-bits-02` 的组件身份一致。`api.py`、`_simulate.py` 和 kdist 插件
也与该批次一致。验证没有修改服务工作树，临时目录已清理；本次补丁验证未重复编译或仿真。

[identity.json](identity.json) 保存完整基线身份、两个补丁的依赖关系、五个文件的前后哈希、
全部语义哈希、实际应用命令与输出，以及原始 `versions.json`、`prepared.json`、
`results.json` 的来源和 SHA256。其中的编译工件哈希用于标识已执行批次，不要求不同机器
重新构建的二进制哈希完全相同。

补丁 SHA256：`53ed976ca70780c032bf7bb54b54b93d251cd8d2b5d88754663535d3e527fda0`。

在自己的组件工作树中可再次核对全部源码：

```sh
python3 - "$KCIRCT_ROOT" \
  "$KCIRCT_EXP_ROOT/external-defects/evidence/vcd/component/packed-array-semantics/identity.json" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
identity = json.loads(Path(sys.argv[2]).read_text())
checks = identity['verification']['semantics'] + identity['verification']['unchanged_api_simulator_plugin']
for record in checks:
    actual = hashlib.sha256((root / record['path']).read_bytes()).hexdigest()
    assert actual == record['sha256'], record['path']
print('全部语义与组件源码哈希一致')
PY
```

该证据明确保存未提交版本的复现方法，不表示补丁已经提交或发布。
