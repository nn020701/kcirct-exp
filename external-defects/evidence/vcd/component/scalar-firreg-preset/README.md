# 整数寄存器 preset 补丁

[scalar-firreg-preset.patch](scalar-firreg-preset.patch) 在已有数组语义之上增加
signless 整数 `seq.firreg` 的显式初值处理。补丁只修改
`src/kcirct/kdist/circt_semantics/dialects/seq/seq.md`：
寄存器首次求值和首次反馈读取使用 `preset`，形成历史值后沿用普通保持、更新与同步复位。
没有 `preset` 的寄存器继续采用二态零初始化；数组 `preset` 与异步复位的未支持边界保留。

这是尚未提交的组件源码证据。它绑定 `vcd-complete-01` 的实际 `prepared.json` 身份，
该准备记录不表示全部案例已通过；正式结果另见 [VCD_RUNS.md](../../../../VCD_RUNS.md)。
既有 CLI 和数组补丁保持原字节。

## 应用顺序

先在基线 `3afaa5f93d8ed0cabeb08bdce1fd4c5f74a8a5a2` 的干净组件工作树上，
按[数组补丁说明](../packed-array-semantics/README.md)依次应用旧 CLI 与数组补丁。
将 `KCIRCT_ROOT` 和 `KCIRCT_EXP_ROOT` 设为自己的组件与实验仓库路径，再应用本补丁：

```sh
git -C "$KCIRCT_ROOT" apply --check \
  "$KCIRCT_EXP_ROOT/external-defects/evidence/vcd/component/scalar-firreg-preset/scalar-firreg-preset.patch"
git -C "$KCIRCT_ROOT" apply \
  "$KCIRCT_EXP_ROOT/external-defects/evidence/vcd/component/scalar-firreg-preset/scalar-firreg-preset.patch"
export KIMULATOR="$KCIRCT_ROOT/.venv/bin/kcirct"
make -C "$KCIRCT_EXP_ROOT" prepare PYTHON="$KCIRCT_EXP_ROOT/.venv/bin/python"
```

`prepare` 按新源码重建并绑定定义与 parser。初值转换后的持久化 IR 和原始 RTL
仍须使用相同输入进行外部 VCD 对照，不能用补丁应用成功替代实验结论。
转换的范围与来源说明见 [实验 README](../../../../README.md#一次常量初始化的受限转换)。

## 已执行的源码验证

从完整 `git archive` 基线开始，在独立临时目录实际依次检查并应用 CLI、数组、preset
三个补丁，六次 `git apply --check` / `git apply` 退出码均为 `0`。
最后一步恰好改变一个 `seq.md` 文件；应用后的全部 52 份语义文件、API、simulator 与
kdist 插件哈希均匹配已保存的准备记录。服务文件未改动，临时验证目录已清理；本次验证没有重复编译或仿真。

[identity.json](identity.json) 保存补丁依赖哈希、单文件前后哈希、完整源码身份、
实际应用命令与输出及编译准备身份。可以复用数组补丁说明中的 Python 核验命令，
将输入 identity 文件改成本目录的 `identity.json`，核对全部源码。

补丁 SHA256：`5ef3aff5969d6fbd50436d7e082fd6984cfdd1bab5b9a0fc3236050319f241dd`。
