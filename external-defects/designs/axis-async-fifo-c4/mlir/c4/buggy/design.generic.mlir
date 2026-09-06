#loc = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/c4/buggy/kimulator/design.mlir":27:181)
#loc1 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/c4/buggy/kimulator/design.mlir":27:317)
#loc2 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/c4/buggy/kimulator/design.mlir":27:345)
#loc3 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/c4/buggy/kimulator/design.mlir":27:414)
#loc4 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/c4/buggy/kimulator/design.mlir":27:442)
#loc5 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/c4/buggy/kimulator/design.mlir":125:173)
#loc6 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/c4/buggy/kimulator/design.mlir":125:279)
#loc7 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/c4/buggy/kimulator/design.mlir":125:307)
#loc8 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/c4/buggy/kimulator/design.mlir":125:377)
#loc9 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/c4/buggy/kimulator/design.mlir":125:405)
#loc10 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/c4/buggy/kimulator/design.mlir":132:198)
#loc11 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/c4/buggy/kimulator/design.mlir":132:360)
#loc12 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/c4/buggy/kimulator/design.mlir":132:383)
#loc13 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/c4/buggy/kimulator/design.mlir":132:406)
#loc14 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/c4/buggy/kimulator/design.mlir":132:466)
#loc15 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/c4/buggy/kimulator/design.mlir":132:489)
#loc16 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/c4/buggy/kimulator/design.mlir":132:510)
#loc17 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/c4/buggy/kimulator/design.mlir":132:533)
"builtin.module"() ({
  "hw.module"() <{module_type = !hw.modty<input async_rst : i1, input input_clk : i1, input input_axis_tdata : i8, input input_axis_tvalid : i1, output input_axis_tready : i1, input input_axis_tlast : i1, input input_axis_tuser : i1, input output_clk : i1, output output_axis_tdata : i8, output output_axis_tvalid : i1, input output_axis_tready : i1, output output_axis_tlast : i1, output output_axis_tuser : i1>, parameters = [], result_locs = [#loc, #loc1, #loc2, #loc3, #loc4], sym_name = "axis_async_fifo"}> ({
  ^bb0(%arg17: i1, %arg18: i1, %arg19: i8, %arg20: i1, %arg21: i1, %arg22: i1, %arg23: i1, %arg24: i1):
    %70 = "hw.constant"() <{value = true}> : () -> i1
    %71 = "hw.constant"() <{value = 1 : i6}> : () -> i6
    %72 = "hw.constant"() <{value = 0 : i10}> : () -> i10
    %73 = "hw.constant"() <{value = 0 : i6}> : () -> i6
    %74 = "hw.constant"() <{value = false}> : () -> i1
    %75 = "comb.concat"(%arg21, %arg22, %arg19) : (i1, i1, i8) -> i10
    %76 = "comb.extract"(%126) <{lowBit = 5 : i32}> : (i6) -> i1
    %77 = "comb.extract"(%134) <{lowBit = 5 : i32}> : (i6) -> i1
    %78 = "comb.icmp"(%76, %77) <{predicate = 1 : i64}> : (i1, i1) -> i1
    %79 = "comb.extract"(%126) <{lowBit = 4 : i32}> : (i6) -> i1
    %80 = "comb.extract"(%134) <{lowBit = 4 : i32}> : (i6) -> i1
    %81 = "comb.icmp"(%79, %80) <{predicate = 1 : i64}> : (i1, i1) -> i1
    %82 = "comb.extract"(%126) <{lowBit = 0 : i32}> : (i6) -> i4
    %83 = "comb.extract"(%134) <{lowBit = 0 : i32}> : (i6) -> i4
    %84 = "comb.icmp"(%82, %83) <{predicate = 0 : i64}> : (i4, i4) -> i1
    %85 = "comb.and"(%78, %81, %84) {sv.namehint = "full"} : (i1, i1, i1) -> i1
    %86 = "comb.xor"(%85, %70) : (i1, i1) -> i1
    %87 = "comb.and"(%arg20, %86) : (i1, i1) -> i1
    %88 = "comb.xor"(%164, %70) : (i1, i1) -> i1
    %89 = "comb.or"(%arg24, %88) : (i1, i1) -> i1
    %90 = "comb.icmp"(%155, %161) <{predicate = 1 : i64}> : (i6, i6) -> i1
    %91 = "comb.and"(%89, %90) : (i1, i1) -> i1
    %92 = "comb.extract"(%157) <{lowBit = 9 : i32}> : (i10) -> i1
    %93 = "comb.extract"(%157) <{lowBit = 8 : i32}> : (i10) -> i1
    %94 = "comb.extract"(%157) <{lowBit = 0 : i32}> : (i10) -> i8
    %95 = "comb.or"(%arg17, %98, %104) : (i1, i1, i1) -> i1
    %96 = "comb.or"(%arg17, %99) : (i1, i1) -> i1
    %97 = "seq.to_clock"(%arg18) : (i1) -> !seq.clock
    %98 = "seq.firreg"(%arg17, %97) <{name = "input_rst_sync1"}> : (i1, !seq.clock) -> i1
    %99 = "seq.firreg"(%95, %97) <{name = "input_rst_sync2"}> : (i1, !seq.clock) -> i1
    %100 = "seq.firreg"(%96, %97) <{name = "input_rst_sync3"}> : (i1, !seq.clock) -> i1
    %101 = "comb.or"(%arg17, %104) : (i1, i1) -> i1
    %102 = "comb.or"(%arg17, %105) : (i1, i1) -> i1
    %103 = "seq.to_clock"(%arg23) : (i1) -> !seq.clock
    %104 = "seq.firreg"(%arg17, %103) <{name = "output_rst_sync1"}> : (i1, !seq.clock) -> i1
    %105 = "seq.firreg"(%101, %103) <{name = "output_rst_sync2"}> : (i1, !seq.clock) -> i1
    %106 = "seq.firreg"(%102, %103) <{name = "output_rst_sync3"}> : (i1, !seq.clock) -> i1
    %107 = "comb.add"(%124, %71) : (i6, i6) -> i6
    %108 = "comb.extract"(%124) <{lowBit = 0 : i32}> : (i6) -> i5
    %109 = "hw.array_inject"(%130, %108, %75) : (!hw.array<32xi10>, i5, i10) -> !hw.array<32xi10>
    %110 = "comb.extract"(%107) <{lowBit = 1 : i32}> : (i6) -> i5
    %111 = "comb.concat"(%74, %110) : (i1, i5) -> i6
    %112 = "comb.xor"(%107, %111) : (i6, i6) -> i6
    %113 = "comb.xor"(%100, %70) : (i1, i1) -> i1
    %114 = "comb.and"(%87, %113) : (i1, i1) -> i1
    %115 = "comb.mux"(%114, %107, %73) : (i1, i6, i6) -> i6
    %116 = "comb.xor"(%87, %70) : (i1, i1) -> i1
    %117 = "comb.and"(%113, %116) : (i1, i1) -> i1
    %118 = "comb.xor"(%114, %70) : (i1, i1) -> i1
    %119 = "comb.or"(%117, %118) : (i1, i1) -> i1
    %120 = "comb.mux"(%119, %73, %112) : (i1, i6, i6) -> i6
    %121 = "comb.xor"(%117, %70) : (i1, i1) -> i1
    %122 = "comb.and"(%121, %114) : (i1, i1) -> i1
    %123 = "comb.mux"(%117, %124, %115) <{twoState}> : (i1, i6, i6) -> i6
    %124 = "seq.firreg"(%123, %97) <{name = "wr_ptr"}> : (i6, !seq.clock) -> i6
    %125 = "comb.mux"(%117, %126, %120) <{twoState}> : (i1, i6, i6) -> i6
    %126 = "seq.firreg"(%125, %97) <{name = "wr_ptr_gray"}> : (i6, !seq.clock) -> i6
    %127 = "comb.xor"(%122, %70) : (i1, i1) -> i1
    %128 = "comb.or"(%127, %119) : (i1, i1) -> i1
    %129 = "comb.mux"(%128, %130, %109) <{twoState}> : (i1, !hw.array<32xi10>, !hw.array<32xi10>) -> !hw.array<32xi10>
    %130 = "seq.firreg"(%129, %97) <{name = "mem"}> : (!hw.array<32xi10>, !seq.clock) -> !hw.array<32xi10>
    %131 = "comb.mux"(%100, %73, %155) : (i1, i6, i6) -> i6
    %132 = "comb.mux"(%100, %73, %133) : (i1, i6, i6) -> i6
    %133 = "seq.firreg"(%131, %97) <{name = "rd_ptr_gray_sync1"}> : (i6, !seq.clock) -> i6
    %134 = "seq.firreg"(%132, %97) <{name = "rd_ptr_gray_sync2"}> : (i6, !seq.clock) -> i6
    %135 = "comb.add"(%153, %71) : (i6, i6) -> i6
    %136 = "comb.extract"(%153) <{lowBit = 0 : i32}> : (i6) -> i5
    %137 = "hw.array_get"(%130, %136) : (!hw.array<32xi10>, i5) -> i10
    %138 = "comb.extract"(%135) <{lowBit = 1 : i32}> : (i6) -> i5
    %139 = "comb.concat"(%74, %138) : (i1, i5) -> i6
    %140 = "comb.xor"(%135, %139) : (i6, i6) -> i6
    %141 = "comb.xor"(%106, %70) : (i1, i1) -> i1
    %142 = "comb.and"(%91, %141) : (i1, i1) -> i1
    %143 = "comb.mux"(%142, %135, %73) : (i1, i6, i6) -> i6
    %144 = "comb.xor"(%91, %70) : (i1, i1) -> i1
    %145 = "comb.and"(%141, %144) : (i1, i1) -> i1
    %146 = "comb.xor"(%142, %70) : (i1, i1) -> i1
    %147 = "comb.or"(%145, %146) : (i1, i1) -> i1
    %148 = "comb.mux"(%147, %73, %140) : (i1, i6, i6) -> i6
    %149 = "comb.mux"(%147, %72, %137) : (i1, i10, i10) -> i10
    %150 = "comb.xor"(%145, %70) : (i1, i1) -> i1
    %151 = "comb.and"(%150, %142) : (i1, i1) -> i1
    %152 = "comb.mux"(%145, %153, %143) <{twoState}> : (i1, i6, i6) -> i6
    %153 = "seq.firreg"(%152, %103) <{name = "rd_ptr"}> : (i6, !seq.clock) -> i6
    %154 = "comb.mux"(%145, %155, %148) <{twoState}> : (i1, i6, i6) -> i6
    %155 = "seq.firreg"(%154, %103) <{name = "rd_ptr_gray"}> : (i6, !seq.clock) -> i6
    %156 = "comb.mux"(%151, %149, %157) <{twoState}> : (i1, i10, i10) -> i10
    %157 = "seq.firreg"(%156, %103) <{name = "data_out_reg"}> : (i10, !seq.clock) -> i10
    %158 = "comb.mux"(%106, %73, %126) : (i1, i6, i6) -> i6
    %159 = "comb.mux"(%106, %73, %160) : (i1, i6, i6) -> i6
    %160 = "seq.firreg"(%158, %103) <{name = "wr_ptr_gray_sync1"}> : (i6, !seq.clock) -> i6
    %161 = "seq.firreg"(%159, %103) <{name = "wr_ptr_gray_sync2"}> : (i6, !seq.clock) -> i6
    %162 = "comb.mux"(%89, %90, %164) : (i1, i1, i1) -> i1
    %163 = "comb.and"(%141, %162) : (i1, i1) -> i1
    %164 = "seq.firreg"(%163, %103) <{name = "output_axis_tvalid_reg"}> : (i1, !seq.clock) -> i1
    "hw.output"(%86, %94, %164, %92, %93) : (i1, i8, i1, i1, i1) -> ()
  }) {sym_visibility = "private"} : () -> ()
  "hw.module"() <{module_type = !hw.modty<input async_rst : i1, input clk : i1, input input_axis_tdata : i8, input input_axis_tvalid : i1, output input_axis_tready : i1, input input_axis_tlast : i1, input input_axis_tuser : i1, output output_axis_tdata : i8, output output_axis_tvalid : i1, input output_axis_tready : i1, output output_axis_tlast : i1, output output_axis_tuser : i1>, parameters = [], result_locs = [#loc5, #loc6, #loc7, #loc8, #loc9], sym_name = "axis_fifo_wrapper"}> ({
  ^bb0(%arg10: i1, %arg11: i1, %arg12: i8, %arg13: i1, %arg14: i1, %arg15: i1, %arg16: i1):
    %66 = "hw.constant"() <{value = 0 : i8}> : () -> i8
    %67 = "hw.constant"() <{value = false}> : () -> i1
    %68:8 = "hw.instance"(%arg11, %arg10, %arg12, %67, %arg13, %arg14, %66, %66, %arg15, %69#0) <{argNames = ["clk", "rst", "s_axis_tdata", "s_axis_tkeep", "s_axis_tvalid", "s_axis_tlast", "s_axis_tid", "s_axis_tdest", "s_axis_tuser", "m_axis_tready"], instanceName = "axis_reg_inst", moduleName = @axis_register, parameters = [], resultNames = ["s_axis_tready", "m_axis_tdata", "m_axis_tkeep", "m_axis_tvalid", "m_axis_tlast", "m_axis_tid", "m_axis_tdest", "m_axis_tuser"]}> {sv.namehint = "reg_axis_tuser"} : (i1, i1, i8, i1, i1, i1, i8, i8, i1, i1) -> (i1, i8, i1, i1, i1, i8, i8, i1)
    %69:5 = "hw.instance"(%arg10, %arg11, %68#1, %68#3, %68#4, %68#7, %arg11, %arg16) <{argNames = ["async_rst", "input_clk", "input_axis_tdata", "input_axis_tvalid", "input_axis_tlast", "input_axis_tuser", "output_clk", "output_axis_tready"], instanceName = "UUT", moduleName = @axis_async_fifo, parameters = [], resultNames = ["input_axis_tready", "output_axis_tdata", "output_axis_tvalid", "output_axis_tlast", "output_axis_tuser"]}> {sv.namehint = "reg_axis_tready"} : (i1, i1, i8, i1, i1, i1, i1, i1) -> (i1, i8, i1, i1, i1)
    "hw.output"(%68#0, %69#1, %69#2, %69#3, %69#4) : (i1, i8, i1, i1, i1) -> ()
  }) : () -> ()
  "hw.module"() <{module_type = !hw.modty<input clk : i1, input rst : i1, input s_axis_tdata : i8, input s_axis_tkeep : i1, input s_axis_tvalid : i1, output s_axis_tready : i1, input s_axis_tlast : i1, input s_axis_tid : i8, input s_axis_tdest : i8, input s_axis_tuser : i1, output m_axis_tdata : i8, output m_axis_tkeep : i1, output m_axis_tvalid : i1, input m_axis_tready : i1, output m_axis_tlast : i1, output m_axis_tid : i8, output m_axis_tdest : i8, output m_axis_tuser : i1>, parameters = [], result_locs = [#loc10, #loc11, #loc12, #loc13, #loc14, #loc15, #loc16, #loc17], sym_name = "axis_register"}> ({
  ^bb0(%arg0: i1, %arg1: i1, %arg2: i8, %arg3: i1, %arg4: i1, %arg5: i1, %arg6: i8, %arg7: i8, %arg8: i1, %arg9: i1):
    %0 = "hw.constant"() <{value = 0 : i8}> : () -> i8
    %1 = "hw.constant"() <{value = true}> : () -> i1
    %2 = "comb.xor"(%41, %1) : (i1, i1) -> i1
    %3 = "comb.xor"(%40, %1) : (i1, i1) -> i1
    %4 = "comb.xor"(%arg4, %1) : (i1, i1) -> i1
    %5 = "comb.or"(%3, %4) : (i1, i1) -> i1
    %6 = "comb.and"(%2, %5) : (i1, i1) -> i1
    %7 = "comb.or"(%arg9, %6) : (i1, i1) -> i1
    %8 = "comb.or"(%arg9, %3) : (i1, i1) -> i1
    %9 = "comb.mux"(%arg9, %41, %40) : (i1, i1, i1) -> i1
    %10 = "comb.xor"(%arg9, %1) : (i1, i1) -> i1
    %11 = "comb.and"(%10, %41) : (i1, i1) -> i1
    %12 = "comb.mux"(%8, %arg4, %40) : (i1, i1, i1) -> i1
    %13 = "comb.mux"(%8, %41, %arg4) : (i1, i1, i1) -> i1
    %14 = "comb.xor"(%8, %1) : (i1, i1) -> i1
    %15 = "comb.mux"(%39, %12, %9) : (i1, i1, i1) -> i1
    %16 = "comb.mux"(%39, %13, %11) : (i1, i1, i1) -> i1
    %17 = "comb.and"(%39, %8) : (i1, i1) -> i1
    %18 = "comb.and"(%39, %14) : (i1, i1) -> i1
    %19 = "comb.xor"(%39, %1) : (i1, i1) -> i1
    %20 = "comb.and"(%19, %arg9) : (i1, i1) -> i1
    %21 = "comb.xor"(%arg1, %1) : (i1, i1) -> i1
    %22 = "comb.and"(%21, %7) : (i1, i1) -> i1
    %23 = "comb.and"(%21, %15) : (i1, i1) -> i1
    %24 = "comb.and"(%21, %16) : (i1, i1) -> i1
    %25 = "comb.mux"(%20, %55, %0) : (i1, i8, i8) -> i8
    %26 = "comb.and"(%20, %57) : (i1, i1) -> i1
    %27 = "comb.and"(%20, %59) : (i1, i1) -> i1
    %28 = "comb.mux"(%20, %61, %0) : (i1, i8, i8) -> i8
    %29 = "comb.mux"(%20, %63, %0) : (i1, i8, i8) -> i8
    %30 = "comb.and"(%20, %65) : (i1, i1) -> i1
    %31 = "comb.mux"(%17, %arg2, %25) : (i1, i8, i8) -> i8
    %32 = "comb.or"(%17, %20) : (i1, i1) -> i1
    %33 = "comb.mux"(%17, %arg3, %26) : (i1, i1, i1) -> i1
    %34 = "comb.mux"(%17, %arg5, %27) : (i1, i1, i1) -> i1
    %35 = "comb.mux"(%17, %arg6, %28) : (i1, i8, i8) -> i8
    %36 = "comb.mux"(%17, %arg7, %29) : (i1, i8, i8) -> i8
    %37 = "comb.mux"(%17, %arg8, %30) : (i1, i1, i1) -> i1
    %38 = "seq.to_clock"(%arg0) : (i1) -> !seq.clock
    %39 = "seq.firreg"(%22, %38) <{name = "genblk1.s_axis_tready_reg"}> : (i1, !seq.clock) -> i1
    %40 = "seq.firreg"(%23, %38) <{name = "genblk1.m_axis_tvalid_reg"}> : (i1, !seq.clock) -> i1
    %41 = "seq.firreg"(%24, %38) <{name = "genblk1.temp_m_axis_tvalid_reg"}> : (i1, !seq.clock) -> i1
    %42 = "comb.mux"(%32, %31, %43) <{twoState}> : (i1, i8, i8) -> i8
    %43 = "seq.firreg"(%42, %38) <{name = "genblk1.m_axis_tdata_reg"}> : (i8, !seq.clock) -> i8
    %44 = "comb.mux"(%32, %33, %45) <{twoState}> : (i1, i1, i1) -> i1
    %45 = "seq.firreg"(%44, %38) <{name = "genblk1.m_axis_tkeep_reg"}> : (i1, !seq.clock) -> i1
    %46 = "comb.mux"(%32, %34, %47) <{twoState}> : (i1, i1, i1) -> i1
    %47 = "seq.firreg"(%46, %38) <{name = "genblk1.m_axis_tlast_reg"}> : (i1, !seq.clock) -> i1
    %48 = "comb.mux"(%32, %35, %49) <{twoState}> : (i1, i8, i8) -> i8
    %49 = "seq.firreg"(%48, %38) <{name = "genblk1.m_axis_tid_reg"}> : (i8, !seq.clock) -> i8
    %50 = "comb.mux"(%32, %36, %51) <{twoState}> : (i1, i8, i8) -> i8
    %51 = "seq.firreg"(%50, %38) <{name = "genblk1.m_axis_tdest_reg"}> : (i8, !seq.clock) -> i8
    %52 = "comb.mux"(%32, %37, %53) <{twoState}> : (i1, i1, i1) -> i1
    %53 = "seq.firreg"(%52, %38) <{name = "genblk1.m_axis_tuser_reg"}> : (i1, !seq.clock) -> i1
    %54 = "comb.mux"(%18, %arg2, %55) <{twoState}> : (i1, i8, i8) -> i8
    %55 = "seq.firreg"(%54, %38) <{name = "genblk1.temp_m_axis_tdata_reg"}> : (i8, !seq.clock) -> i8
    %56 = "comb.mux"(%18, %arg3, %57) <{twoState}> : (i1, i1, i1) -> i1
    %57 = "seq.firreg"(%56, %38) <{name = "genblk1.temp_m_axis_tkeep_reg"}> : (i1, !seq.clock) -> i1
    %58 = "comb.mux"(%18, %arg5, %59) <{twoState}> : (i1, i1, i1) -> i1
    %59 = "seq.firreg"(%58, %38) <{name = "genblk1.temp_m_axis_tlast_reg"}> : (i1, !seq.clock) -> i1
    %60 = "comb.mux"(%18, %arg6, %61) <{twoState}> : (i1, i8, i8) -> i8
    %61 = "seq.firreg"(%60, %38) <{name = "genblk1.temp_m_axis_tid_reg"}> : (i8, !seq.clock) -> i8
    %62 = "comb.mux"(%18, %arg7, %63) <{twoState}> : (i1, i8, i8) -> i8
    %63 = "seq.firreg"(%62, %38) <{name = "genblk1.temp_m_axis_tdest_reg"}> : (i8, !seq.clock) -> i8
    %64 = "comb.mux"(%18, %arg8, %65) <{twoState}> : (i1, i1, i1) -> i1
    %65 = "seq.firreg"(%64, %38) <{name = "genblk1.temp_m_axis_tuser_reg"}> : (i1, !seq.clock) -> i1
    "hw.output"(%39, %43, %1, %40, %47, %0, %0, %53) : (i1, i8, i1, i1, i1, i8, i8, i1) -> ()
  }) {sym_visibility = "private"} : () -> ()
}) : () -> ()

