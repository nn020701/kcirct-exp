#loc = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d4/golden/kimulator/design.mlir":19:189)
#loc1 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d4/golden/kimulator/design.mlir":19:348)
#loc2 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d4/golden/kimulator/design.mlir":19:371)
#loc3 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d4/golden/kimulator/design.mlir":19:394)
#loc4 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d4/golden/kimulator/design.mlir":19:454)
#loc5 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d4/golden/kimulator/design.mlir":19:477)
#loc6 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d4/golden/kimulator/design.mlir":19:498)
#loc7 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d4/golden/kimulator/design.mlir":19:521)
#loc8 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d4/golden/kimulator/design.mlir":19:544)
#loc9 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d4/golden/kimulator/design.mlir":19:570)
#loc10 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d4/golden/kimulator/design.mlir":19:597)
#loc11 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d4/golden/kimulator/design.mlir":102:159)
#loc12 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d4/golden/kimulator/design.mlir":102:253)
#loc13 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d4/golden/kimulator/design.mlir":102:276)
#loc14 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d4/golden/kimulator/design.mlir":102:336)
#loc15 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d4/golden/kimulator/design.mlir":102:359)
#loc16 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d4/golden/kimulator/design.mlir":102:382)
#loc17 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d4/golden/kimulator/design.mlir":102:408)
#loc18 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d4/golden/kimulator/design.mlir":102:435)
"builtin.module"() ({
  "hw.module"() <{module_type = !hw.modty<input clk : i1, input rst : i1, input s_axis_tdata : i8, input s_axis_tkeep : i1, input s_axis_tvalid : i1, output s_axis_tready : i1, input s_axis_tlast : i1, input s_axis_tid : i8, input s_axis_tdest : i8, input s_axis_tuser : i1, output m_axis_tdata : i8, output m_axis_tkeep : i1, output m_axis_tvalid : i1, input m_axis_tready : i1, output m_axis_tlast : i1, output m_axis_tid : i8, output m_axis_tdest : i8, output m_axis_tuser : i1, output status_overflow : i1, output status_bad_frame : i1, output status_good_frame : i1>, parameters = [], result_locs = [#loc, #loc1, #loc2, #loc3, #loc4, #loc5, #loc6, #loc7, #loc8, #loc9, #loc10], sym_name = "axis_fifo"}> ({
  ^bb0(%arg7: i1, %arg8: i1, %arg9: i8, %arg10: i1, %arg11: i1, %arg12: i1, %arg13: i8, %arg14: i8, %arg15: i1, %arg16: i1):
    %3 = "hw.constant"() <{value = 1 : i6}> : () -> i6
    %4 = "hw.constant"() <{value = 0 : i8}> : () -> i8
    %5 = "hw.constant"() <{value = 0 : i10}> : () -> i10
    %6 = "hw.constant"() <{value = 0 : i6}> : () -> i6
    %7 = "hw.constant"() <{value = true}> : () -> i1
    %8 = "hw.constant"() <{value = false}> : () -> i1
    %9 = "comb.concat"(%arg15, %arg12, %arg9) : (i1, i1, i8) -> i10
    %10 = "comb.extract"(%48) <{lowBit = 5 : i32}> : (i6) -> i1
    %11 = "comb.extract"(%70) <{lowBit = 5 : i32}> : (i6) -> i1
    %12 = "comb.extract"(%48) <{lowBit = 0 : i32}> : (i6) -> i5
    %13 = "comb.extract"(%70) <{lowBit = 0 : i32}> : (i6) -> i5
    %14 = "comb.extract"(%49) <{lowBit = 5 : i32}> : (i6) -> i1
    %15 = "comb.icmp"(%14, %11) <{predicate = 1 : i64}> : (i1, i1) -> i1
    %16 = "comb.extract"(%49) <{lowBit = 0 : i32}> : (i6) -> i5
    %17 = "comb.icmp"(%16, %13) <{predicate = 0 : i64}> : (i5, i5) -> i1
    %18 = "comb.and"(%15, %17) : (i1, i1) -> i1
    %19 = "comb.icmp"(%10, %14) <{predicate = 1 : i64}> : (i1, i1) -> i1
    %20 = "comb.icmp"(%12, %16) <{predicate = 0 : i64}> : (i5, i5) -> i1
    %21 = "comb.and"(%19, %20) : (i1, i1) -> i1
    %22 = "comb.xor"(%18, %7) : (i1, i1) -> i1
    %23 = "comb.or"(%22, %21) : (i1, i1) -> i1
    %24 = "comb.extract"(%81) <{lowBit = 0 : i32}> : (i10) -> i8
    %25 = "comb.extract"(%81) <{lowBit = 8 : i32}> : (i10) -> i1
    %26 = "comb.extract"(%81) <{lowBit = 9 : i32}> : (i10) -> i1
    %27 = "comb.and"(%23, %arg11) : (i1, i1) -> i1
    %28 = "comb.or"(%18, %21, %50) : (i1, i1, i1) -> i1
    %29 = "comb.add"(%49, %3) : (i6, i6) -> i6
    %30 = "comb.xor"(%arg12, %7) : (i1, i1) -> i1
    %31 = "comb.mux"(%arg12, %48, %49) : (i1, i6, i6) -> i6
    %32 = "comb.and"(%28, %27) : (i1, i1) -> i1
    %33 = "comb.xor"(%32, %7) : (i1, i1) -> i1
    %34 = "comb.mux"(%32, %31, %29) : (i1, i6, i6) -> i6
    %35 = "comb.xor"(%27, %7) : (i1, i1) -> i1
    %36 = "comb.and"(%27, %33) : (i1, i1) -> i1
    %37 = "comb.or"(%35, %32, %30) : (i1, i1, i1) -> i1
    %38 = "comb.mux"(%37, %48, %29) : (i1, i6, i6) -> i6
    %39 = "comb.mux"(%35, %49, %34) : (i1, i6, i6) -> i6
    %40 = "comb.mux"(%arg8, %6, %38) : (i1, i6, i6) -> i6
    %41 = "comb.mux"(%arg8, %6, %39) : (i1, i6, i6) -> i6
    %42 = "comb.xor"(%arg8, %7) : (i1, i1) -> i1
    %43 = "comb.and"(%42, %32, %30) : (i1, i1, i1) -> i1
    %44 = "comb.and"(%42, %32, %arg12) : (i1, i1, i1) -> i1
    %45 = "comb.and"(%42, %27, %33, %arg12) : (i1, i1, i1, i1) -> i1
    %46 = "comb.extract"(%54) <{lowBit = 0 : i32}> : (i6) -> i5
    %47 = "seq.to_clock"(%arg7) : (i1) -> !seq.clock
    %48 = "seq.firreg"(%40, %47) <{name = "wr_ptr_reg"}> : (i6, !seq.clock) -> i6
    %49 = "seq.firreg"(%41, %47) <{name = "wr_ptr_cur_reg"}> : (i6, !seq.clock) -> i6
    %50 = "seq.firreg"(%43, %47) <{name = "drop_frame_reg"}> : (i1, !seq.clock) -> i1
    %51 = "seq.firreg"(%44, %47) <{name = "overflow_reg"}> : (i1, !seq.clock) -> i1
    %52 = "seq.firreg"(%8, %47) <{name = "bad_frame_reg"}> : (i1, !seq.clock) -> i1
    %53 = "seq.firreg"(%45, %47) <{name = "good_frame_reg"}> : (i1, !seq.clock) -> i1
    %54 = "seq.firreg"(%39, %47) <{name = "wr_addr_reg"}> : (i6, !seq.clock) -> i6
    %55 = "seq.firmem"() <{name = "mem", readLatency = 0 : i32, ruw = 0 : i32, writeLatency = 1 : i32, wuw = 0 : i32}> : () -> !seq.firmem<32 x 10, mask 1>
    %56 = "seq.firmem.read_port"(%55, %67, %47) : (!seq.firmem<32 x 10, mask 1>, i5, !seq.clock) -> i10
    "seq.firmem.write_port"(%55, %46, %47, %36, %9) <{operandSegmentSizes = array<i32: 1, 1, 1, 1, 1, 0>}> : (!seq.firmem<32 x 10, mask 1>, i5, !seq.clock, i1, i10) -> ()
    %57 = "comb.xor"(%71, %7) : (i1, i1) -> i1
    %58 = "comb.or"(%76, %57) : (i1, i1) -> i1
    %59 = "comb.icmp"(%48, %70) <{predicate = 1 : i64}> : (i6, i6) -> i1
    %60 = "comb.add"(%70, %3) : (i6, i6) -> i6
    %61 = "comb.and"(%59, %58) : (i1, i1) -> i1
    %62 = "comb.xor"(%58, %7) : (i1, i1) -> i1
    %63 = "comb.mux"(%61, %60, %70) : (i1, i6, i6) -> i6
    %64 = "comb.mux"(%62, %71, %61) : (i1, i1, i1) -> i1
    %65 = "comb.mux"(%arg8, %6, %63) : (i1, i6, i6) -> i6
    %66 = "comb.and"(%42, %64) : (i1, i1) -> i1
    %67 = "comb.extract"(%72) <{lowBit = 0 : i32}> : (i6) -> i5
    %68 = "comb.xor"(%61, %7) : (i1, i1) -> i1
    %69 = "comb.mux"(%68, %5, %56) : (i1, i10, i10) -> i10
    %70 = "seq.firreg"(%65, %47) <{name = "rd_ptr_reg"}> : (i6, !seq.clock) -> i6
    %71 = "seq.firreg"(%66, %47) <{name = "mem_read_data_valid_reg"}> : (i1, !seq.clock) -> i1
    %72 = "seq.firreg"(%63, %47) <{name = "rd_addr_reg"}> : (i6, !seq.clock) -> i6
    %73 = "comb.mux"(%61, %69, %74) <{twoState}> : (i1, i10, i10) -> i10
    %74 = "seq.firreg"(%73, %47) <{name = "mem_read_data_reg"}> : (i10, !seq.clock) -> i10
    %75 = "comb.xor"(%79, %7) : (i1, i1) -> i1
    %76 = "comb.or"(%arg16, %75) : (i1, i1) -> i1
    %77 = "comb.mux"(%76, %71, %79) : (i1, i1, i1) -> i1
    %78 = "comb.and"(%42, %77) : (i1, i1) -> i1
    %79 = "seq.firreg"(%78, %47) <{name = "m_axis_tvalid_reg"}> : (i1, !seq.clock) -> i1
    %80 = "comb.mux"(%76, %74, %81) <{twoState}> : (i1, i10, i10) -> i10
    %81 = "seq.firreg"(%80, %47) <{name = "m_axis_reg"}> : (i10, !seq.clock) -> i10
    "hw.output"(%23, %24, %7, %79, %25, %4, %4, %26, %51, %52, %53) : (i1, i8, i1, i1, i1, i8, i8, i1, i1, i1, i1) -> ()
  }) {sym_visibility = "private"} : () -> ()
  "hw.module"() <{module_type = !hw.modty<input clk : i1, input rst : i1, input s_axis_tdata : i8, input s_axis_tvalid : i1, output s_axis_tready : i1, input s_axis_tlast : i1, input s_axis_tuser : i1, output m_axis_tdata : i8, output m_axis_tvalid : i1, input m_axis_tready : i1, output m_axis_tlast : i1, output m_axis_tuser : i1, output status_overflow : i1, output status_bad_frame : i1, output status_good_frame : i1>, parameters = [], result_locs = [#loc11, #loc12, #loc13, #loc14, #loc15, #loc16, #loc17, #loc18], sym_name = "axis_fifo_wrapper"}> ({
  ^bb0(%arg0: i1, %arg1: i1, %arg2: i8, %arg3: i1, %arg4: i1, %arg5: i1, %arg6: i1):
    %0 = "hw.constant"() <{value = 0 : i8}> : () -> i8
    %1 = "hw.constant"() <{value = false}> : () -> i1
    %2:11 = "hw.instance"(%arg0, %arg1, %arg2, %1, %arg3, %arg4, %0, %0, %arg5, %arg6) <{argNames = ["clk", "rst", "s_axis_tdata", "s_axis_tkeep", "s_axis_tvalid", "s_axis_tlast", "s_axis_tid", "s_axis_tdest", "s_axis_tuser", "m_axis_tready"], instanceName = "axis_fifo_inst", moduleName = @axis_fifo, parameters = [], resultNames = ["s_axis_tready", "m_axis_tdata", "m_axis_tkeep", "m_axis_tvalid", "m_axis_tlast", "m_axis_tid", "m_axis_tdest", "m_axis_tuser", "status_overflow", "status_bad_frame", "status_good_frame"]}> : (i1, i1, i8, i1, i1, i1, i8, i8, i1, i1) -> (i1, i8, i1, i1, i1, i8, i8, i1, i1, i1, i1)
    "hw.output"(%2#0, %2#1, %2#3, %2#4, %2#7, %2#8, %2#9, %2#10) : (i1, i8, i1, i1, i1, i1, i1, i1) -> ()
  }) : () -> ()
}) : () -> ()

