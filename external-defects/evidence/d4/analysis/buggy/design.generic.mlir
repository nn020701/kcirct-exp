#loc = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d4/buggy/kimulator/design.mlir":19:189)
#loc1 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d4/buggy/kimulator/design.mlir":19:348)
#loc2 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d4/buggy/kimulator/design.mlir":19:371)
#loc3 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d4/buggy/kimulator/design.mlir":19:394)
#loc4 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d4/buggy/kimulator/design.mlir":19:454)
#loc5 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d4/buggy/kimulator/design.mlir":19:477)
#loc6 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d4/buggy/kimulator/design.mlir":19:498)
#loc7 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d4/buggy/kimulator/design.mlir":19:521)
#loc8 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d4/buggy/kimulator/design.mlir":19:544)
#loc9 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d4/buggy/kimulator/design.mlir":19:570)
#loc10 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d4/buggy/kimulator/design.mlir":19:597)
#loc11 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d4/buggy/kimulator/design.mlir":103:159)
#loc12 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d4/buggy/kimulator/design.mlir":103:253)
#loc13 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d4/buggy/kimulator/design.mlir":103:276)
#loc14 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d4/buggy/kimulator/design.mlir":103:336)
#loc15 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d4/buggy/kimulator/design.mlir":103:359)
#loc16 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d4/buggy/kimulator/design.mlir":103:382)
#loc17 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d4/buggy/kimulator/design.mlir":103:408)
#loc18 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d4/buggy/kimulator/design.mlir":103:435)
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
    %10 = "comb.extract"(%49) <{lowBit = 5 : i32}> : (i6) -> i1
    %11 = "comb.extract"(%71) <{lowBit = 5 : i32}> : (i6) -> i1
    %12 = "comb.icmp"(%10, %11) <{predicate = 1 : i64}> : (i1, i1) -> i1
    %13 = "comb.extract"(%49) <{lowBit = 0 : i32}> : (i6) -> i5
    %14 = "comb.extract"(%71) <{lowBit = 0 : i32}> : (i6) -> i5
    %15 = "comb.icmp"(%13, %14) <{predicate = 0 : i64}> : (i5, i5) -> i1
    %16 = "comb.and"(%12, %15) : (i1, i1) -> i1
    %17 = "comb.extract"(%50) <{lowBit = 5 : i32}> : (i6) -> i1
    %18 = "comb.icmp"(%10, %17) <{predicate = 1 : i64}> : (i1, i1) -> i1
    %19 = "comb.extract"(%50) <{lowBit = 0 : i32}> : (i6) -> i5
    %20 = "comb.icmp"(%13, %19) <{predicate = 0 : i64}> : (i5, i5) -> i1
    %21 = "comb.and"(%18, %20) : (i1, i1) -> i1
    %22 = "comb.xor"(%16, %7) : (i1, i1) -> i1
    %23 = "comb.extract"(%82) <{lowBit = 0 : i32}> : (i10) -> i8
    %24 = "comb.extract"(%82) <{lowBit = 8 : i32}> : (i10) -> i1
    %25 = "comb.extract"(%82) <{lowBit = 9 : i32}> : (i10) -> i1
    %26 = "comb.or"(%16, %21, %51) : (i1, i1, i1) -> i1
    %27 = "comb.add"(%50, %3) : (i6, i6) -> i6
    %28 = "comb.xor"(%arg12, %7) : (i1, i1) -> i1
    %29 = "comb.mux"(%arg12, %49, %50) : (i1, i6, i6) -> i6
    %30 = "comb.and"(%26, %22, %arg11) : (i1, i1, i1) -> i1
    %31 = "comb.xor"(%30, %7) : (i1, i1) -> i1
    %32 = "comb.mux"(%30, %29, %27) : (i1, i6, i6) -> i6
    %33 = "comb.and"(%arg11, %16) : (i1, i1) -> i1
    %34 = "comb.xor"(%33, %7) : (i1, i1) -> i1
    %35 = "comb.xor"(%arg11, %7) : (i1, i1) -> i1
    %36 = "comb.and"(%arg11, %34, %31) : (i1, i1, i1) -> i1
    %37 = "comb.or"(%35, %33, %30, %28) : (i1, i1, i1, i1) -> i1
    %38 = "comb.mux"(%37, %49, %27) : (i1, i6, i6) -> i6
    %39 = "comb.or"(%35, %33) : (i1, i1) -> i1
    %40 = "comb.mux"(%39, %50, %32) : (i1, i6, i6) -> i6
    %41 = "comb.mux"(%arg8, %6, %38) : (i1, i6, i6) -> i6
    %42 = "comb.mux"(%arg8, %6, %40) : (i1, i6, i6) -> i6
    %43 = "comb.xor"(%arg8, %7) : (i1, i1) -> i1
    %44 = "comb.and"(%43, %34, %30, %28) : (i1, i1, i1, i1) -> i1
    %45 = "comb.and"(%43, %34, %30, %arg12) : (i1, i1, i1, i1) -> i1
    %46 = "comb.and"(%43, %arg11, %34, %31, %arg12) : (i1, i1, i1, i1, i1) -> i1
    %47 = "comb.extract"(%55) <{lowBit = 0 : i32}> : (i6) -> i5
    %48 = "seq.to_clock"(%arg7) : (i1) -> !seq.clock
    %49 = "seq.firreg"(%41, %48) <{name = "wr_ptr_reg"}> : (i6, !seq.clock) -> i6
    %50 = "seq.firreg"(%42, %48) <{name = "wr_ptr_cur_reg"}> : (i6, !seq.clock) -> i6
    %51 = "seq.firreg"(%44, %48) <{name = "drop_frame_reg"}> : (i1, !seq.clock) -> i1
    %52 = "seq.firreg"(%45, %48) <{name = "overflow_reg"}> : (i1, !seq.clock) -> i1
    %53 = "seq.firreg"(%8, %48) <{name = "bad_frame_reg"}> : (i1, !seq.clock) -> i1
    %54 = "seq.firreg"(%46, %48) <{name = "good_frame_reg"}> : (i1, !seq.clock) -> i1
    %55 = "seq.firreg"(%40, %48) <{name = "wr_addr_reg"}> : (i6, !seq.clock) -> i6
    %56 = "seq.firmem"() <{name = "mem", readLatency = 0 : i32, ruw = 0 : i32, writeLatency = 1 : i32, wuw = 0 : i32}> : () -> !seq.firmem<32 x 10, mask 1>
    %57 = "seq.firmem.read_port"(%56, %68, %48) : (!seq.firmem<32 x 10, mask 1>, i5, !seq.clock) -> i10
    "seq.firmem.write_port"(%56, %47, %48, %36, %9) <{operandSegmentSizes = array<i32: 1, 1, 1, 1, 1, 0>}> : (!seq.firmem<32 x 10, mask 1>, i5, !seq.clock, i1, i10) -> ()
    %58 = "comb.xor"(%72, %7) : (i1, i1) -> i1
    %59 = "comb.or"(%77, %58) : (i1, i1) -> i1
    %60 = "comb.icmp"(%49, %71) <{predicate = 1 : i64}> : (i6, i6) -> i1
    %61 = "comb.add"(%71, %3) : (i6, i6) -> i6
    %62 = "comb.and"(%60, %59) : (i1, i1) -> i1
    %63 = "comb.xor"(%59, %7) : (i1, i1) -> i1
    %64 = "comb.mux"(%62, %61, %71) : (i1, i6, i6) -> i6
    %65 = "comb.mux"(%63, %72, %62) : (i1, i1, i1) -> i1
    %66 = "comb.mux"(%arg8, %6, %64) : (i1, i6, i6) -> i6
    %67 = "comb.and"(%43, %65) : (i1, i1) -> i1
    %68 = "comb.extract"(%73) <{lowBit = 0 : i32}> : (i6) -> i5
    %69 = "comb.xor"(%62, %7) : (i1, i1) -> i1
    %70 = "comb.mux"(%69, %5, %57) : (i1, i10, i10) -> i10
    %71 = "seq.firreg"(%66, %48) <{name = "rd_ptr_reg"}> : (i6, !seq.clock) -> i6
    %72 = "seq.firreg"(%67, %48) <{name = "mem_read_data_valid_reg"}> : (i1, !seq.clock) -> i1
    %73 = "seq.firreg"(%64, %48) <{name = "rd_addr_reg"}> : (i6, !seq.clock) -> i6
    %74 = "comb.mux"(%62, %70, %75) <{twoState}> : (i1, i10, i10) -> i10
    %75 = "seq.firreg"(%74, %48) <{name = "mem_read_data_reg"}> : (i10, !seq.clock) -> i10
    %76 = "comb.xor"(%80, %7) : (i1, i1) -> i1
    %77 = "comb.or"(%arg16, %76) : (i1, i1) -> i1
    %78 = "comb.mux"(%77, %72, %80) : (i1, i1, i1) -> i1
    %79 = "comb.and"(%43, %78) : (i1, i1) -> i1
    %80 = "seq.firreg"(%79, %48) <{name = "m_axis_tvalid_reg"}> : (i1, !seq.clock) -> i1
    %81 = "comb.mux"(%77, %75, %82) <{twoState}> : (i1, i10, i10) -> i10
    %82 = "seq.firreg"(%81, %48) <{name = "m_axis_reg"}> : (i10, !seq.clock) -> i10
    "hw.output"(%22, %23, %7, %80, %24, %4, %4, %25, %52, %53, %54) : (i1, i8, i1, i1, i1, i8, i8, i1, i1, i1, i1) -> ()
  }) {sym_visibility = "private"} : () -> ()
  "hw.module"() <{module_type = !hw.modty<input clk : i1, input rst : i1, input s_axis_tdata : i8, input s_axis_tvalid : i1, output s_axis_tready : i1, input s_axis_tlast : i1, input s_axis_tuser : i1, output m_axis_tdata : i8, output m_axis_tvalid : i1, input m_axis_tready : i1, output m_axis_tlast : i1, output m_axis_tuser : i1, output status_overflow : i1, output status_bad_frame : i1, output status_good_frame : i1>, parameters = [], result_locs = [#loc11, #loc12, #loc13, #loc14, #loc15, #loc16, #loc17, #loc18], sym_name = "axis_fifo_wrapper"}> ({
  ^bb0(%arg0: i1, %arg1: i1, %arg2: i8, %arg3: i1, %arg4: i1, %arg5: i1, %arg6: i1):
    %0 = "hw.constant"() <{value = 0 : i8}> : () -> i8
    %1 = "hw.constant"() <{value = false}> : () -> i1
    %2:11 = "hw.instance"(%arg0, %arg1, %arg2, %1, %arg3, %arg4, %0, %0, %arg5, %arg6) <{argNames = ["clk", "rst", "s_axis_tdata", "s_axis_tkeep", "s_axis_tvalid", "s_axis_tlast", "s_axis_tid", "s_axis_tdest", "s_axis_tuser", "m_axis_tready"], instanceName = "axis_fifo_inst", moduleName = @axis_fifo, parameters = [], resultNames = ["s_axis_tready", "m_axis_tdata", "m_axis_tkeep", "m_axis_tvalid", "m_axis_tlast", "m_axis_tid", "m_axis_tdest", "m_axis_tuser", "status_overflow", "status_bad_frame", "status_good_frame"]}> : (i1, i1, i8, i1, i1, i1, i8, i8, i1, i1) -> (i1, i8, i1, i1, i1, i8, i8, i1, i1, i1, i1)
    "hw.output"(%2#0, %2#1, %2#3, %2#4, %2#7, %2#8, %2#9, %2#10) : (i1, i8, i1, i1, i1, i1, i1, i1) -> ()
  }) : () -> ()
}) : () -> ()

