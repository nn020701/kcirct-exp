# AutoConnect 参数列表保留补丁

[auto-connect-list-preservation.patch](auto-connect-list-preservation.patch) 只修改
`src/kcirct/kdist/circt_semantics/circt/circt.md` 的两条 `AutoConnect` 规则：
将参数列表整体绑定到 `Args`，再检查首元素的 `AutoConnect` 标记，避免在规则左侧拆分共享列表。
规则表达的连接行为保持不变；实验中已观察到旧表达导致只读 `connection` 的参数顺序改变，
本补丁消除 S3/D12 已复现路径中的改变，但在 S2 引入新的元数据回归。这里没有修改 K 或 LLVM backend，也不宣称所有 backend 共享问题均已解决。

这是独立保存的未提交组件源码证据。它绑定 `vcd-complete-02/prepared.json` 的实际身份，
准备成功不等于整批实验通过；运行结论见 [VCD_RUNS.md](../../../../VCD_RUNS.md)。
旧 CLI、数组和 preset 三份补丁保持原字节。

## 应用与验证

在组件基线 `3afaa5f93d8ed0cabeb08bdce1fd4c5f74a8a5a2` 的干净工作树中，先按
[preset 补丁说明](../scalar-firreg-preset/README.md)依次应用 CLI、数组和 preset 三份补丁。
将 `KCIRCT_ROOT` 和 `KCIRCT_EXP_ROOT` 配置为自己的组件与实验仓库路径，再执行：

```sh
git -C "$KCIRCT_ROOT" apply --check \
  "$KCIRCT_EXP_ROOT/external-defects/evidence/vcd/component/auto-connect-list-preservation/auto-connect-list-preservation.patch"
git -C "$KCIRCT_ROOT" apply \
  "$KCIRCT_EXP_ROOT/external-defects/evidence/vcd/component/auto-connect-list-preservation/auto-connect-list-preservation.patch"
export KIMULATOR="$KCIRCT_ROOT/.venv/bin/kcirct"
make -C "$KCIRCT_EXP_ROOT" prepare PYTHON="$KCIRCT_EXP_ROOT/.venv/bin/python"
```

已经从完整 `git archive` 基线独立执行四份补丁的八次 `git apply --check` / `git apply`，
退出码均为 `0`。最后一步恰改变一个 `circt.md`；应用后的全部 52 份语义文件、API、simulator
和 kdist 插件哈希与 `vcd-complete-02` 的准备记录一致。验证没有修改组件工作树，没有重复编译或仿真。

[identity.json](identity.json) 保存基线、依赖补丁、源码前后哈希、实际验证命令和准备身份。
补丁 SHA256：`b82c5e1d76d8f938c1a6c57827ce82ae016e93fa830190b1921f2ca7d24dfbc6`。

另保存[标准 operation 验证](operation-validation/index.json)的真实命令与输出：4 个案例各执行仿真与 VCDdiff，共 8 项通过；末态完整 `connection` 与 setup 一致。此记录不替代 S3/D12 原始大型输入的针对性反例。

## 已确认回归与暂停状态

[前后版本审计](../../metadata-integrity/vcd-complete-02/audit/s2-before-autoconnect-audit.json)保持相同输入、MLIR、API、CLI、parser 和 setup：补丁前 complete-01 的 S2 golden 全部178份状态连接不变；补丁后 complete-02 出现9份连接内容变化。两批语义源码只差本补丁的 `circt/circt.md`。因此这是本轮修改引入的已确认元数据回归，P0尚未解决；不能因两批S2顶层VCD均通过而宣称内部完整性通过。进一步语义修改暂停，当前补丁仅用于复现已记录组件身份，不是无已知问题的修复推荐。具体底层hook未定位。
