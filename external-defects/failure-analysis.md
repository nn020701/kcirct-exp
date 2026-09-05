# 已重现缺陷的证据分析

本文依据 `.runs/batch-first-01` 的 D13、D8，以及 `.runs/batch-memory-01` 的 D4，说明真实失败怎样从输入、控制条件、跨事件状态和存储写入形成。这三例均已完整通过正常/缺陷 × Verilator/Kimulator 验收。所有分析均为读取保存工件后的人工核对，本轮没有实现或运行新的 Error-trace 自动定位功能。

本文中的路径相对于本目录。完整历史归档现位于 `.runs/`，共享的关键原字节证据见 [evidence/index.json](evidence/index.json)。原 IR/location 和状态记录中的旧路径保留历史含义，通过源码哈希和 `designs/*/provenance/layout.json` 对应当前设计，不用于当前路径解析。正式精简结果采用后续最终批次；本文 SSA 和内部窗口仍绑定明确标出的分析批次。采样索引、事件索引均从 0 开始。`event=2×sample` 是低电平观测，后续奇数事件提交上升沿；最后一条观测后不再提交上升沿。低电平观测协议只在本次逐案例核对范围内成立。

## 1. 证据范围与判定

| 案例 | 独立采样 | 正常原生 / K 与 oracle | 缺陷 K 与缺陷原生 | 首次 oracle 差异 | 全部差异 |
|---|---:|---|---|---|---|
| D13 / d13 | 6 | 各 12 个规定输出单元格全部一致 | 12 个输出单元格全部一致 | sample 5，frame_len，1 → 3，i16 | 仅这一处 |
| D8 / d8 | 14 | 各 112 个规定输出单元格全部一致 | 112 个输出单元格全部一致 | sample 4，m_axis_tvalid，1 → 0，i1 | sample 4、5 的同一信号 |
| D4 / d4 | 185 | 各 1480 个规定输出单元格全部一致 | 1480 个输出单元格全部一致 | sample 67，s_axis_tready，0 → 1，i1 | 118 个 ready 差异、7 个 status_good_frame 差异 |

正式判定与批次选择见 [RUNS.md](RUNS.md)、[D13 结果](results/cases/d13.json)、[D8 结果](results/cases/d8.json)、[D4 结果](results/cases/d4.json)。缺陷版 `oracle_mismatch` 是预期缺陷被检测的证据；案例整体 `pass` 要求正常版通过独立 oracle，并且两版 K 均与对应原生输出全轨迹相符。正常与缺陷输出不同本身不构成验收。

运行版本、参数和来源哈希分别保存在批次 `versions.json`、各案例 `manifest.json` 和每后端命令记录中。所有已保存 K 事件均保留 `.kore.gz` 及 `events.json` 中的未压缩 SHA256。本文没有重新仿真或改写原始结果。

为了便于核查内部 SSA 值，使用现有 `KCIRCT.read_signals` 离线读取了指定状态，并逐个验证事件 SHA256。所得 [D13 正常窗口](evidence/analysis/d13-golden-state-window.json)、[D13 缺陷窗口](evidence/analysis/d13-buggy-state-window.json)、[D8 正常窗口](evidence/analysis/d8-golden-state-window.json)、[D8 缺陷窗口](evidence/analysis/d8-buggy-state-window.json) 包含全部读取信号。原复核脚本和完整事件序列保存在本地历史归档；共享目录保留了本文用到的原始状态与读取结果，离线读取不是自动因果查询。

## 2. D13：连续单拍帧沿用了前一帧长度

### 2.1 首次失败及前一事件

实际 DUT 参数是 `DATA_WIDTH=64, KEEP_WIDTH=8, KEEP_ENABLE=1, LEN_WIDTH=16`。原 TB 声明的 `DATA_WIDTH=8` 没有传给 UUT；不能据 TB 名字改用 8 位 DUT。

首次规定观测失败是 event 10 / sample 5：`rst=0, keep=0, valid=0, ready=1, last=0`，正常 `frame_len=1`，缺陷 `frame_len=3`，两版 `frame_len_valid=1`。当前输入没有传输，因此只查看失败时输入不能解释多出的 2；必须回到前一上升沿。

| 事件 | 输入和阶段 | 正常内部状态 | 缺陷内部状态 |
|---:|---|---|---|
| 8 / sample 4 | clk=0，rst=0，keep=1，valid=ready=last=1 | len_reg=2，len_valid_reg=1，frame_reg=0；清零后基值=0，增量=1，待写值=1 | 同样旧寄存器；保留基值=2，增量=1，待写值=3 |
| 9 | 相同输入，clk=1 | len_reg 从 2 提交为 1 | len_reg 从 2 提交为 3 |
| 10 / sample 5 | clk=0，keep=valid=last=0，ready=1 | len_reg=1，len_valid_reg=1 | len_reg=3，len_valid_reg=1；首次 oracle 失败 |

选定事件的输入、输出、状态哈希及静止检查见两版 [golden 窗口](evidence/analysis/d13-golden-state-window.json) / [buggy 窗口](evidence/analysis/d13-buggy-state-window.json)。原 TB 的独立 VCD 也给出相同机制：7 ns 稳定后形成不同 next 值，9 ns 提交为 1/3，11 ns pre-NBA 观测到差异；见 [原生失败窗口](evidence/d13/native-independent/buggy/native-failure-window.json)。这些原 TB 时间不能直接当成批量驱动的物理时间单位。

### 2.2 原 RTL 改动与实际分支

正常 [axis_frame_len.v](designs/axis-frame-len-d13/original/axis_frame_len.v) 与缺陷 [axis_frame_len_bug_d13.v](designs/axis-frame-len-d13/variants/d13/axis_frame_len_bug_d13.v) 的核心差异如下，方向为缺陷 → 正常：

```diff
 frame_len_next = frame_len_reg;
 frame_len_valid_next = 1'b0;
 frame_next = frame_reg;
+if (frame_len_valid_reg) begin
+    frame_len_next = 0;
+end
 ...
 if (monitor_axis_tlast) begin
     frame_len_valid_next = 1'b1;
     frame_next = 1'b0;
 end else if (!frame_reg) begin
-    frame_len_next = 0;
     frame_next = 1'b1;
 end
```

正常版 81–83 行根据上一拍 `frame_len_valid_reg=1` 清零；之后 103 行累加当前有效字节数 1。缺陷版只在 87–90 行的 `!last && !frame_reg` 分支清零。当前 `last=1`，所以该分支不被选择，100 行把保留的 2 加 1，形成 3。错误不是加法器算错，而是进入加法器的跨帧基值未清零。

### 2.3 真实 generic SSA 和位置

以下 SSA 标识只对本批次对应版本有效，不能跨版本直接以相同编号对齐：

| 角色 | 正常 SSA / event 8 值 | 缺陷 SSA / event 8 值 | 原 RTL / location |
|---|---|---|---|
| len 寄存器旧值 | `%46=2:i16` | `%47=2:i16` | `seq.firreg name="frame_len_reg"`，两版第 63 行，`#loc18` |
| 上一帧完成标志 | `%47=1:i1` | `%48=1:i1` | `frame_len_valid_reg`，第 65 行，`#loc19` |
| 帧状态 | `%48=0:i1` | `%49=0:i1` | `frame_reg`，第 67 行，`#loc20` |
| 基值选择 | `%18=mux(%47,0,%46)=0` | `%19=or(last,%49)=1`；`%20=mux(%19,%47,0)=2` | 正常 `#loc11` 精确指向 81–83 行；缺陷 `#loc12` 被前端归到第 70 行 |
| 字节增量 | `%36=1:i16` | `%37=1:i16` | 展开的 keep 比较/mux 链，`#loc9` |
| 加法及待写值 | `%37=1`，复位 mux 后 `%41=1` | `%38=3`，复位 mux 后 `%42=3` | 加法 `#loc15`：正常 103:30–54，缺陷 100:30–54；复位 `#loc17` |

证据见 [正常 debug generic IR](evidence/d13/analysis/golden/design.debug.generic.mlir)、[缺陷 debug generic IR](evidence/d13/analysis/buggy/design.debug.generic.mlir) 和对应 `source-map.json`。正常寄存器输入 `%41`、缺陷 `%42` 在 event 8 就不同，event 9 提交，event 10 观测到差异。

位置映射存在实际限制：缺陷版基值 mux 的 location 指向第 70 行声明附近，并非原分支的精确执行行；若只报告最末加法操作，第 100 行也会掩盖“应清零但未清零”的原因。缺陷 IR 不包含正常版新增的条件语句，不能要求自动查询返回一个并不存在的故障节点。正常/缺陷源码差异可作为人工辅助证据，但当前没有自动对齐功能。

### 2.4 原 TB 谓词和范围

原 TB 在最后一条检查 `frame_len > 1` 并打印错误；CSV 逐行精确比较是另一项更强检查。两版原生退出码均为 0。D13 两个输出是寄存器直连；独立 VCD 已验证全部六条低相位与原 TB pre-NBA 观测一致。此例没有存储器，也没有验证四态未知值或任意 SV 调度。

## 3. D8：有效位选择用了错误的二维展开步长

### 3.1 首次失败与控制窗口

实际参数为 `S_COUNT=4, M_COUNT=1, DATA_WIDTH=8, S_REG_TYPE=0, M_REG_TYPE=2`；TB 参数覆盖块被注释，使用 DUT 默认值。首次失败在 event 8 / sample 4，`m_axis_tvalid` 期望 1、实际 0；下一条 sample 5 同样失败，其余规定输出全部匹配。

event 6 / sample 3 的共同输入是 `rst=0, s_axis_tdata=0xabcd1234, keep=0xf, valid=0x7, last=0x4, tid=0x01020304, dest=0xd, user=0, m_axis_tready=1`。这时仲裁已经选择输入 1，内部待选 valid 总线是 `0b0010`。

| 事件 | 共同控制值 | 正常 | 缺陷 |
|---:|---|---|---|
| 6 / sample 3 | int_axis_tvalid=2:i4，grant_encoded=1:i2，grant_valid=1；输出侧 ready_reg=1，m_axis_tready=1，旧输出 valid_reg=0 | valid 选择索引=1，选中位=1，valid_mux=1；寄存器待写值=1 | 索引=4，4 位总线右移 4 后为 0，valid_mux=0；寄存器待写值=0 |
| 7 / 上升沿 | 同一组输入，rst=0 | 输出侧 valid_reg 从 0 提交为 1 | valid_reg 仍为 0 |
| 8 / sample 4 | 下一行 valid=0x3、last=0x2，其余输入如上 | 顶层 m_axis_tvalid=1 | 顶层 m_axis_tvalid=0；首次 oracle 差异 |

记录来自 [正常状态窗口](evidence/analysis/d8-golden-state-window.json) 与 [缺陷状态窗口](evidence/analysis/d8-buggy-state-window.json)，不是从源码推测的寄存器值。

本例还显示了采样边界必须随证据一起保留：保存的 event 7 内部输出侧寄存器已经是 1/0，但该事件导出的顶层 `outputs.m_axis_tvalid` 仍是 0/0；到下一 low eval / event 8 才在顶层输出观测到 1/0。本文以已核对的偶数事件作为外部采样，不把奇数事件的内部寄存器值冒充同事件顶层端口值，也不宣称所有中间事件与原生调度相等。

### 3.2 原 RTL 差异与本次触发范围

正常 [axis_switch.v](designs/axis-switch-d8/original/axis_switch.v) 和缺陷 [axis_switch_bug_d8.v](designs/axis-switch-d8/variants/d8/axis_switch_bug_d8.v) 两处差异如下，方向为缺陷 → 正常：

```diff
-assign int_s_axis_tready[m] = int_axis_tready[select_reg*M_COUNT+m] || drop_reg;
+assign int_s_axis_tready[m] = int_axis_tready[select_reg*S_COUNT+m] || drop_reg;
 ...
-wire s_axis_tvalid_mux = int_axis_tvalid[grant_encoded*S_COUNT+n] && grant_valid;
+wire s_axis_tvalid_mux = int_axis_tvalid[grant_encoded*M_COUNT+n] && grant_valid;
```

两处对应第 233、301 行。本配置只有一个输出，`select_reg=0`，因此第 233 行乘法结果相同，本次轨迹不能证明 ready 索引修复在多输出配置中的行为。已重现的首次失败来自第 301 行：正常选择 `1×1+0=1`，缺陷选择 `1×4+0=4`。IR 的 `i4` 右移把这个越过总线宽度的选择具体化为 0；这是本次二态编译/执行结果，不是对四态越界索引行为的证明。

输出寄存器逻辑本身保留原始设计：`axis_register.v` 138–143 行在 `s_axis_tready_reg=1` 且 `m_axis_tready || !m_axis_tvalid_reg=1` 时采用输入 valid；164 行提交。它接收到上游错误的 0，因此应继续追到 mux 索引和仲裁选择，不能只停在输出 valid 寄存器。

### 3.3 层次、generic SSA 与 source location

| 角色 / 层次 | 正常 SSA | 缺陷 SSA | event 6 值与来源 |
|---|---|---|---|
| 顶层 valid 向量 | `axis_switch/%36` | 相同路径 `%36` | 2:i4 |
| 仲裁器实例输出 | 顶层 `%141#1 / %141#2` | 同编号 | grant_valid=1；grant_encoded=1；实例 `m_ifaces_0.arb_inst` |
| 选择位移 | `%145=concat(0:i2,%141#2)` | `%148=concat(%141#2,0:i2)` | 1:i4 对 4:i4 |
| valid 位与使能 | `%148=shru(%36,%145)` → `%149=extract` → `%150=and(...,%141#1)` | `%149=shru(%36,%148)` → `%150=extract` → `%151=and(...,%141#1)` | 正常 1，缺陷 0；`#loc113/#loc114` |
| 输出寄存器实例 | `%178:8`，`m_ifaces_0.reg_inst` | `%179:8`，同实例名 | 输入参数 `s_axis_tvalid` 为上述 mux 结果 |
| 输出侧 ready 寄存器 | `m_ifaces_0.reg_inst/%218` | `.../%219` | 两版均 1 |
| 输出侧 valid 待写值 | `m_ifaces_0.reg_inst/%202` | `.../%203` | 1 对 0；复位已解除 |
| 输出侧 valid 寄存器 | `m_ifaces_0.reg_inst/%219` | `.../%220` | event 6 为 0/0，event 7 为 1/0 |

`#loc113` 分别指向正常/缺陷 `axis_switch*.v:301:52–92`，`#loc114` 扩展至列 107，覆盖 valid 索引及 grant_valid 条件。寄存器实例为 `axis_register_0`，其中 `seq.firreg name="genblk1.m_axis_tvalid_reg"` 的 `#loc48` 指向 `axis_register.v:89:19`；控制 mux `#loc58` 被归到第 127 行表达式，复位/提交 `#loc59` 覆盖 158–166 行。这些映射可以缩小源码区域，但不能把前端合并位置当作精确执行行。

查看 [正常 debug generic IR](evidence/d8/analysis/golden/design.debug.generic.mlir)、[缺陷 debug generic IR](evidence/d8/analysis/buggy/design.debug.generic.mlir) 和各自 `source-map.json`。同一局部 `%219` 在两版扮演不同角色；查询标识必须至少绑定 IR 哈希、实例路径、SSA 和事件。

### 3.4 原 TB 与完整轨迹的界限

原 D8 TB 无 `$fwrite`，需要外部时钟，在 `cycle==12`（第 13 个 posedge）调用 `$finish`；其无条件 `@@@Bug` 文本不能当失败谓词。保留原 TB 不变，仅以 wrapper 暴露内部信号后，两版前 13 条低相位的全部输入/输出均与 CSV driver 一致。完整 14 行正常 oracle 和缺陷 K/native 一致性来自独立 CSV 回放，第 14 行不能宣称有原 TB 对照。证据见 [原生适配器验证](evidence/README.md)。

`project.toml` 明确限定原 TB 使用二态仿真。此例验证了 4→1 层次实例和该轨迹触发的 valid 索引错误，没有验证多输出 ready 索引分支、全部仲裁策略或任意 AXI 行为。

## 4. D4：帧内占用已满仍接受输入并覆盖已有存储

### 4.1 已验证轨迹和首次差异

[D4 结果](results/cases/d4.json) 中，正常原生与 K 各自全部 185 行、8 个输出符合独立 CSV；缺陷 K 与缺陷原生全部 1480 个规定输出单元格一致。首次 oracle 差异是 sample 67 / event 134 的 `s_axis_tready`，期望 0、实际 1。此后 sample 67–184 共118条 ready 不一致；`status_good_frame` 在 sample 77、94、111、128、145、162、179 额外出现7处差异。

真实配置由原样 `axis_fifo_wrapper.v` 固定：`ADDR_WIDTH=5`（32个地址），`DATA_WIDTH=8, USER_WIDTH=1, FRAME_FIFO=1, DROP_BAD_FRAME=0, DROP_WHEN_FULL=0`。`seq.firmem<32 x 10, mask 1>` 中每个10位单元由 `user:last:data` 拼接，读延迟0、写延迟1；本例没有动态部分写掩码输入。

### 4.2 首次差异前后的指针、写使能和地址

以下值来自逐个校验SHA256后的 [正常状态窗口](evidence/analysis/d4-golden-state-window.json) 与 [缺陷状态窗口](evidence/analysis/d4-buggy-state-window.json)。层次统一是 `axis_fifo_wrapper/axis_fifo_inst`。

| 事件 | 输入 / 共同状态 | 正常 | 缺陷 |
|---:|---|---|---|
| 132 / sample 66 | clk=0，rst=0，data=0，valid=1，last=user=0，m_ready=0；wr_ptr=33、wr_cur=33、rd_ptr=2，均为i6 | ready=1，write_enable=1，写地址1:i5，数据0:i10 | 相同 |
| 133 / 上升沿 | 提交前述写入 | mem[1] 从1改为0；wr_cur变为34，wr_ptr仍33，rd_ptr仍2 | 相同 |
| 134 / sample 67 | clk=0，data=1，valid=1，last=user=0，m_ready=0；wr_ptr=33、wr_cur=34、rd_ptr=2 | 当前帧占用full_cur=1，full_wr=0，ready=0，write_enable=0；地址2虽已算出但未使能 | 只由已提交wr_ptr判断的full=0，ready=1，write_enable=1，地址2，数据1；首次oracle差异 |
| 135 / 上升沿 | 对该行输入提交 | wr_cur保持34；mem[2]保持2 | wr_cur变35；mem[2]从2改为1 |

这把端口握手错误与后续真实内存写联系起来：首次失败是 ready 提前表示可以接受数据；覆盖发生在随后 event 135，不能把覆盖时间误标为 event 134。这里核查的是 K 保存的内存状态；跨后端全轨迹验收针对规定端口，没有额外声称原生与 K 的全部内部存储地址已经逐事件比对。

### 4.3 地址2的先前写入确实存在

针对失败后被写入的地址2，对缺陷版 event 0–134 的全部低相位写口逐个检查了地址和使能，并保留每个被读取状态的哈希：[d4-address-2-write-evidence.json](evidence/analysis/d4-address-2-write-evidence.json)。这不是根据CSV行号推测的写历史。

- event 34 / sample 17：地址2:i5、使能1、数据2:i10；event 35 后 `mem[2]=2`。
- 从这次写入到 event 132，没有另一条对地址2使能的写。
- event 134 / sample 67：缺陷版地址2、使能1、数据1；event 135 后 `mem[2]=1`。正常版同一事件使能0、存储仍为2。

因此存储追溯至少需要“地址 + 使能 + 数据 + 提交事件 + 上次同地址写入”。只根据任何操作当时出现的地址值添加内存写依赖，会错误地把正常版 event134 的禁用写当成真实写入。

### 4.4 原 RTL 差异、generic SSA 和位置

完整差异来自正常 [axis_fifo.v](designs/axis-fifo-d4/original/axis_fifo.v) 与缺陷 [axis_fifo_bug_d4.v](designs/axis-fifo-d4/variants/d4/axis_fifo_bug_d4.v)。关键变化有三项：

```diff
+full_cur = 与 rd_ptr 比较当前帧写指针 wr_ptr_cur；
 原先命名 full_cur 的“wr_ptr 与 wr_ptr_cur 相差整圈”条件改名为 full_wr；
-s_axis_tready = !full || DROP_WHEN_FULL;
+s_axis_tready = FRAME_FIFO ? (!full_cur || full_wr || DROP_WHEN_FULL) : !full;
-if (s_axis_tvalid) ... if (!full || DROP_WHEN_FULL) ...
+if (s_axis_tready && s_axis_tvalid) ...
```

这是说明性摘要，不替代完整源文件diff。event134中 `wr_cur=34=0b100010`、`rd_ptr=2=0b000010`，低5位相等而绕回位不同，当前帧占用已经满；`wr_ptr=33=0b100001` 的低5位却是1，用它判断的旧 `full` 仍为0。正常版在145–146行计算当前帧与读指针关系，167行据此停止ready，213行以真实握手门控写入；缺陷版165行缺少这一背压依据。

| 角色 | 正常SSA | 缺陷SSA | event134实际值 / 映射 |
|---|---|---|---|
| 已提交写指针 | `%48` | `%49` | 两版33:i6 |
| 当前帧写指针 | `%49` | `%50` | 两版34:i6 |
| 读指针 | `%70` | `%71` | 两版2:i6 |
| 相关满条件 | `%18=full_cur=1`，`%21=full_wr=0` | `%16=full=0` | 正常`#loc26`指145–146行；缺陷对应旧full比较143–144行 |
| ready / 真实写使能 | `%23=0` / `%36=0` | `%22=1` / `%36=1` | 正常ready `#loc30/#loc31`指167行；缺陷`#loc30`指165行 |
| 写地址 / 写数据 | `%46=2:i5` / `%9=1:i10` | `%47=2:i5` / `%9=1:i10` | 来自写地址寄存器低5位和user:last:data拼接 |
| 存储对象 | `%55` | `%56` | `seq.firmem name="mem"`，`#loc15`指各自RTL第131行 |

`seq.firmem.write_port` 明确消费上述地址、时钟、使能和10位数据；读口独立存在。证据见 [正常debug generic IR](evidence/d4/analysis/golden/design.debug.generic.mlir)、[缺陷debug generic IR](evidence/d4/analysis/buggy/design.debug.generic.mlir) 及其 `source-map.json`。地址/使能和原始存储状态足以核对本次写入差异；本例不验证多写口冲突、动态掩码、数组寄存器或异步跨时钟存储。

## 5. 当前材料能支持的后续需求

D13 需要跨上升沿恢复旧值、待写值和实际更新条件；D8 需要穿过实例边界解释控制信号，并给出索引值、总线位宽和所选位；D4提供了背压失效、写使能和同地址已有值被覆盖的真实存储材料。三者都要求把外部首次差异与内部产生差异的事件区分开，并把 SSA/location 绑定实际版本。

具体需求与优先级另列于 [error-trace-requirements.md](error-trace-requirements.md)。D4已支持基础firmem地址/使能追溯的P1需求，其他存储表示和复位场景仍需新案例证据。

S3/S1 在 `batch-first-01` 的 K `execution_error` 是保留的首次接入失败。普通仿真前置问题修复后的 [batch-final-01](RUNS.md) 中，S3、S1b、S1r 已全部通过正常/缺陷 × 原生/K 严格比较；D13、D8、D12也已在该批通过。本文详细机制仍引用前面已校验的D13/D8/D4状态版本，不拿新批次的SSA编号替换旧证据。D4的185行验收已由`batch-memory-01`独立成立。

尚未通过的 [D11](results/cases/d11.json) 和 [C4](results/cases/c4.json) 在两版K首事件均出现120秒超时；[S2](evidence/blockers.json) 在包含残留LLHD类型的generic IR进入K parser时出现语法错误。这些属于普通仿真前置支持缺口，不能记为K端已经重现DUT预期缺陷，也不能由增加Error-trace展示功能代替修复。本轮没有开发Error-trace。
