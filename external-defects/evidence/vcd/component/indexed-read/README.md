# 共享参数 indexed read 语义补丁

[indexed-read.patch](indexed-read.patch) 是第五份组件补丁，只修改 `hardware/hardware.md`。它先按原参数顺序求值全部依赖，再按相同顺序读取结果；通过 `L[I]` 构造临时单元素列表，继续调用原求值与 READ_DIRECT 规则，保留 Bits、memory Map、寄存器 history/preset 等路径。共享的原参数 List 不再直接进入头尾解构。

本轮只在 K/CIRCT 语义层规避已观测的共享列表问题，没有修改 K 或 LLVM backend。此前 AutoConnect 修改引入的 S2 回归及 S3/D12 旧失败都保留原始证据；旧四份 patch 和说明不覆盖。

## 复现与身份

在组件基线 `3afaa5f93d8ed0cabeb08bdce1fd4c5f74a8a5a2` 上，先按[第四份补丁说明](../auto-connect-list-preservation/README.md)依次应用公开 CLI、数组、整数 preset、AutoConnect 四份 patch，再应用本补丁。配置自己的 `KCIRCT_ROOT` 与 `KCIRCT_EXP_ROOT`：

```sh
git -C "$KCIRCT_ROOT" apply --check   "$KCIRCT_EXP_ROOT/external-defects/evidence/vcd/component/indexed-read/indexed-read.patch"
git -C "$KCIRCT_ROOT" apply   "$KCIRCT_EXP_ROOT/external-defects/evidence/vcd/component/indexed-read/indexed-read.patch"
export KIMULATOR="$KCIRCT_ROOT/.venv/bin/kcirct"
make -C "$KCIRCT_EXP_ROOT" prepare PYTHON="$KCIRCT_EXP_ROOT/.venv/bin/python"
```

已从完整干净 `git archive` 独立完成五份 patch 的十次 `git apply --check` / `git apply`，全部返回 0；还原后的 52 份语义文件及 API/simulator/plugin 哈希与 complete-03 正式 prepared 一致。补丁 SHA256 为 `1535788f73bd21b7485f0fe86c7a72ed78d19ccdfddffcc4b736b9a286933867`，应用后的 hardware.md SHA256 为 `0acb587e5af1d219e6e27b3c81fc934ff61a1bd553cce6cd4ee88d9f87b506ef`。完整记录见 [identity.json](identity.json) 与 [原字节索引](index.json)。

正式 definition SHA256 为 `08ac54e383967aa9aa7ba218cd0148e2b4d3f19dea67ddab33f120d661854e2b`。独立候选构建使用相同 52 份源码，但 definition SHA256 为 `f198336d59b414b088c960a6a15af4b3f48bf275dc16f15e1457afb598064c16`；[构建对照](validation/build-comparison.json)发现 16 条 owise 生成排除条件的分支/变量排列变化，不能只解释为绝对路径差异，也不证明 binary 等价。三例原 prestate 重放和正式批次分别绑定各自构建。

## 验证范围

complete-03 的十个已配置变体、正常/缺陷两版全部 VCD 对照通过；每版 642 个事件、每事件两次求值。另有[完整状态审计](../../metadata-integrity/vcd-complete-03/README.md)确认 20 组全部 2,568 份状态的 whole connection 保持 setup，旧 complete-02 的九份 S2 异常仍被同一审计准确检出。

[覆盖复核](validation/coverage-review.md)按它形成时的真实状态保留，区分零参数、重复 SSA、memory Map、层级 alias、preset 与反馈。该历史复核写成时 operation 尚在运行；最终 operation 结果另存于本目录的 `operation-validation/`。operation 通用 README 仅作为[说明工件](validation/operation-README.md)保存，没有写入本轮结果。

这些观察支持本轮固定轨迹上的语义层规避有效；不证明底层 token/GC 根因已经修复，亦不扩展为任意列表共享或所有电路的证明。
