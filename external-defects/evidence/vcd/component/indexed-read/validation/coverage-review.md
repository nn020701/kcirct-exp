# indexed READ 覆盖与证据只读复核

本记录没有重新仿真、修改语义或测试输入。检查的是已经存在的 generic MLIR、13 组标准测试选择和三份完整事件重放产物；标准 operation 当时仍在运行，本记录不提前宣称其通过。

## 覆盖判断

本次没有发现必须新增执行样例的缺口：13 组 operation 加上已经执行的 S3 原始 prestate，以及正在进行的 complete03 全池，覆盖了本次改动涉及的公开输入形状。这里区分“样例存在/路径会触发”和“测试已完成通过”。

| 边界 | 当前样例 | 判断 |
| --- | --- | --- |
| 零参数 operation | `hw/constant/constant.generic.mlir:5–7`；`seq/firmem_rx/firmem_rx.generic.mlir:5–8` 的无参 firmem | 覆盖无参 operation 继续求值；AutoConnect 的非空条件使它们不进入新的 READ 遍历。 |
| 重复 SSA 参数 | 13 组 operation 本身没有同一 op 内重复 SSA；正式 S3 golden `design.generic.mlir:89,129` 的 concat 分别是 `(%13,%78,%13)`、`(%13,%34,%13)`，buggy:68 是 `(%12,%57,%12)` | S3 完整 prestate 重放已执行此图；complete03 两版本继续检验波形。因此无需为了补覆盖而改运行中的 concat 输入。 |
| Map memory 读取 | `seq/firmem_rx` 含四级 memory，RL1/RL0 混合、依赖读值写入后级；`seq/firmem_mask` 含 read_write_port、mode、enable、mask | 新收集器整体保存 READ:List，仍调用原 Map READ_DIRECT。现有样例能发现被误限制成 Bits 的问题，并覆盖相关延迟/写路径。 |
| 层级 alias 链 | `hw/instance`：Foo → AddTwo → AddOne，再连接另一 AddOne | 多层实例输入/输出别名和依赖返回均在样例中；不是仅单个同名端口。 |
| preset 与反馈 | `seq/firreg_preset`：preset 5/-91/-1/true、q4+1 回馈、enable 保持、同步复位，以及普通零初始化 | 保持沿用 preset priority30 和 history 规则；再由 firreg2、firreg_array 覆盖寄存器链和打包数组反馈。 |

`HARDWARE#READ ~> .List` 的内部空分支没有发现现成公共输入会触发：新入口仅来自非空 AutoConnect 参数和单元素 alias 读取。源码从 I=0 到 size=0 的终止分支不访问 L[0]；可以将一个直接 helper 空列表探针列为可选诊断，但不能将无参 hw.constant 的通过误称为执行了这个空分支。它不是本轮必须增添的设计样例。

## 三份重放独立复核

用独立的严格 Map 拆解复核全 connection，拒绝重复 key，仅忽略递归 Map 项顺序；所有 sort、构造器、叶值与 List 顺序保持。输入/输出 SHA 同时核对 replays.json 和 ast-audit.json；没有采用 proof-hint 对照时忽略 inj 目标 sort 的宽松策略。

| 案例 | connection 项数 | 原输入→候选终态 | 旧坏状态 positive control |
| --- | ---: | --- | --- |
| S3 | 250 | 全部不变；current 数量 0，prog/setup/cmd 均 .K | 精确识别 `axis_adapter/%131` 改变 |
| D12 | 78 | 全部不变；current 数量 0，prog/setup/cmd 均 .K | 精确识别 `axis_fifo/%69` 改变 |
| S2 | 83 | 全部不变；current 数量 0，prog/setup/cmd 均 .K | 精确识别 `xlnxstream_2018_3/%53` 改变 |

原 ast-audit.json 的三例结论得到独立确认；原 validation.json 只记录了 S3/D12 positive control，本次另外对 S2 已保存的真实坏状态作了同样的离线对照。三个坏状态均只检出预期 mux key，证明比较器没有因忽略 Map 项顺序而忽略 List 参数变化。

原 replay.py 的 map_items 使用 dict.update，理论上会覆盖重复 key；这次独立复核明确拒绝重复 key，三个输入、候选输出和旧坏状态中均未发现重复 key，故不影响这三例结论。

## 标准 operation 后续审计边界

已准备 [operation/audit_final.py](operation/audit_final.py)，但尚未执行其 operation 审计入口；等待根任务确认全部 13 组完成。它将检查每组 setup.kore 与最后保留的 simulated.0.kore/simulated.1.kore，核对整个 connection、终态和原测试输入/参考资产哈希。

operation 脚本只保留最后两份轮换状态；通过这项检查只能说明这 26 个末尾状态，不能声明每次评估都不变。complete03 的全部逐次快照由独立正式实验审计承担。VCD 比对与内部 connection 审计需要同时保留，尤其 S2 旧异常原本不导致 VCD 失败。

## 本次离线核对的机器记录

```json
{
  "ast_audit": {
    "path": "/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/.kcirct/indexed-read/ast-audit.json",
    "sha256": "af0300bfdb5cb061f8a03a7f151ac6adbe8f0ad2126b338f41b84908435dad40",
    "bytes": 1109
  },
  "replays": {
    "path": "/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/.kcirct/indexed-read/replays.json",
    "sha256": "f2ba48722fb7007e367434c04d86fe6e648e4fff512291b4618bab8db55a7a2a",
    "bytes": 11039
  },
  "comparison_helper": {
    "path": "/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/.kcirct/indexed-read/operation/audit_final.py",
    "sha256": "b10ee5793aeeb22ce5c2ad460536e6ea384fcaad93d7dc266909e057a087e221",
    "bytes": 5973
  },
  "states": [
    {
      "case": "s3",
      "entries": 250,
      "input_sha256": "a5388d3758a00d24192fa1c545de618d787327e8d1ddda90d46202f0eda89b2b",
      "output_sha256": "2971f11de33fbbc476a18f9441bbe924d7ae8f7490854f066d150b78e49e6ec3",
      "hashes_match_existing_reports": true,
      "connection_unchanged": true,
      "terminal": true,
      "positive_control": {
        "path": "/Users/bytedance/cym/cymProject/k-circt-top-repo/services/kcirct-exp/external-defects/evidence/vcd/execution-failures/vcd-complete-01/diagnosis/s3/eval1/depth-1957.kore",
        "sha256": "2b795340503a03a51512b15d08669a607082be4893347dd497a20b3e3ef0485c",
        "bytes": 854934
      },
      "positive_control_changed_keys": [
        "inj{SortString{}, SortKItem{}}(\\dv{SortString{}}(\"axis_adapter/%131\"))"
      ]
    },
    {
      "case": "d12",
      "entries": 78,
      "input_sha256": "a497e04d235733fd92536b6e7707de3438be6c436c30227e326b4cf116b7158c",
      "output_sha256": "fd7305c42266d1a89b21bd6612e2af47ef9585cc240ff3ab082195ac5a900cc6",
      "hashes_match_existing_reports": true,
      "connection_unchanged": true,
      "terminal": true,
      "positive_control": {
        "path": "/Users/bytedance/cym/cymProject/k-circt-top-repo/services/kcirct-exp/external-defects/evidence/vcd/execution-failures/vcd-complete-01/diagnosis/d12/previous-depth-943.kore",
        "sha256": "153eda44b06528b1925acdabc73e35c049219305ce52d8c22543d3a80902305f",
        "bytes": 348706
      },
      "positive_control_changed_keys": [
        "inj{SortString{}, SortKItem{}}(\\dv{SortString{}}(\"axis_fifo/%69\"))"
      ]
    },
    {
      "case": "s2",
      "entries": 83,
      "input_sha256": "2a291c7f2c7d20330c2128a95eeae0ad3ccf7d3fc8d371fe8bd46f54d585bdc1",
      "output_sha256": "da35e4f75e5cb83f6a804da2afdb82fd13b4aa7999692eb6e51debbad1fe8277",
      "hashes_match_existing_reports": true,
      "connection_unchanged": true,
      "terminal": true,
      "positive_control": {
        "path": "/Users/bytedance/cym/cymProject/k-circt-top-repo/services/kcirct-exp/external-defects/evidence/vcd/metadata-integrity/vcd-complete-02/diagnosis/depth-1024.kore",
        "sha256": "27f8ddf095bf454ea09cf498b8ff12478bdedd6fef170347c304c959f4c50400",
        "bytes": 320199
      },
      "positive_control_changed_keys": [
        "inj{SortString{}, SortKItem{}}(\\dv{SortString{}}(\"xlnxstream_2018_3/%53\"))"
      ]
    }
  ]
}
```

## 标准 operation 完成后补记

13 组 evaluation 与 VCDdiff 均已完成，返回码均为 0。收到完成通知后执行了只读末态审计：26 份 simulated.0/.1 的完整 connection 均与各自 setup 一致，current 数量均为 0，prog/setup/cmd 均为 .K。67 份原输入、generic MLIR、C++参考与 Verilator VCD 等资产在 inputs-before/after 中逐项相等，当前文件 SHA 也全部匹配。

见 [audit-validation.json](operation/audit-validation.json)、[final-state-audit.json](operation/final-state-audit.json)。该结论仍只覆盖最后两个轮换状态。
