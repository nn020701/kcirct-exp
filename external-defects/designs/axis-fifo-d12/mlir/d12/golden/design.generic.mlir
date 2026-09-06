#loc = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d12/golden/kimulator/design.mlir":12:181)
#loc1 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d12/golden/kimulator/design.mlir":12:340)
#loc2 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d12/golden/kimulator/design.mlir":12:363)
#loc3 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d12/golden/kimulator/design.mlir":12:386)
#loc4 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d12/golden/kimulator/design.mlir":12:446)
#loc5 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d12/golden/kimulator/design.mlir":12:469)
#loc6 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d12/golden/kimulator/design.mlir":12:490)
#loc7 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d12/golden/kimulator/design.mlir":12:513)
#loc8 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d12/golden/kimulator/design.mlir":12:536)
#loc9 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d12/golden/kimulator/design.mlir":12:562)
#loc10 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d12/golden/kimulator/design.mlir":12:589)
"builtin.module"() ({
  "hw.module"() <{module_type = !hw.modty<input clk : i1, input rst : i1, input s_axis_tdata : i8, input s_axis_tkeep : i1, input s_axis_tvalid : i1, output s_axis_tready : i1, input s_axis_tlast : i1, input s_axis_tid : i8, input s_axis_tdest : i8, input s_axis_tuser : i1, output m_axis_tdata : i8, output m_axis_tkeep : i1, output m_axis_tvalid : i1, input m_axis_tready : i1, output m_axis_tlast : i1, output m_axis_tid : i8, output m_axis_tdest : i8, output m_axis_tuser : i1, output status_overflow : i1, output status_bad_frame : i1, output status_good_frame : i1>, parameters = [], result_locs = [#loc, #loc1, #loc2, #loc3, #loc4, #loc5, #loc6, #loc7, #loc8, #loc9, #loc10], sym_name = "axis_fifo"}> ({
  ^bb0(%arg0: i1, %arg1: i1, %arg2: i8, %arg3: i1, %arg4: i1, %arg5: i1, %arg6: i8, %arg7: i8, %arg8: i1, %arg9: i1):
    %0 = "hw.constant"() <{value = 1 : i3}> : () -> i3
    %1 = "hw.constant"() <{value = 0 : i26}> : () -> i26
    %2 = "hw.constant"() <{value = 0 : i3}> : () -> i3
    %3 = "hw.constant"() <{value = true}> : () -> i1
    %4 = "hw.constant"() <{value = false}> : () -> i1
    %5 = "comb.concat"(%arg8, %arg7, %arg6, %arg5, %arg2) : (i1, i8, i8, i1, i8) -> i26
    %6 = "comb.extract"(%44) <{lowBit = 2 : i32}> : (i3) -> i1
    %7 = "comb.extract"(%66) <{lowBit = 2 : i32}> : (i3) -> i1
    %8 = "comb.extract"(%44) <{lowBit = 0 : i32}> : (i3) -> i2
    %9 = "comb.extract"(%66) <{lowBit = 0 : i32}> : (i3) -> i2
    %10 = "comb.extract"(%45) <{lowBit = 2 : i32}> : (i3) -> i1
    %11 = "comb.icmp"(%10, %7) <{predicate = 1 : i64}> : (i1, i1) -> i1
    %12 = "comb.extract"(%45) <{lowBit = 0 : i32}> : (i3) -> i2
    %13 = "comb.icmp"(%12, %9) <{predicate = 0 : i64}> : (i2, i2) -> i1
    %14 = "comb.and"(%11, %13) : (i1, i1) -> i1
    %15 = "comb.icmp"(%6, %10) <{predicate = 1 : i64}> : (i1, i1) -> i1
    %16 = "comb.icmp"(%8, %12) <{predicate = 0 : i64}> : (i2, i2) -> i1
    %17 = "comb.and"(%15, %16) : (i1, i1) -> i1
    %18 = "comb.extract"(%77) <{lowBit = 0 : i32}> : (i26) -> i8
    %19 = "comb.extract"(%77) <{lowBit = 8 : i32}> : (i26) -> i1
    %20 = "comb.extract"(%77) <{lowBit = 9 : i32}> : (i26) -> i8
    %21 = "comb.extract"(%77) <{lowBit = 17 : i32}> : (i26) -> i8
    %22 = "comb.extract"(%77) <{lowBit = 25 : i32}> : (i26) -> i1
    %23 = "comb.or"(%14, %17, %46) : (i1, i1, i1) -> i1
    %24 = "comb.add"(%45, %0) : (i3, i3) -> i3
    %25 = "comb.xor"(%arg5, %3) : (i1, i1) -> i1
    %26 = "comb.mux"(%arg5, %44, %45) : (i1, i3, i3) -> i3
    %27 = "comb.and"(%23, %arg4) : (i1, i1) -> i1
    %28 = "comb.xor"(%27, %3) : (i1, i1) -> i1
    %29 = "comb.mux"(%27, %26, %24) : (i1, i3, i3) -> i3
    %30 = "comb.xor"(%arg4, %3) : (i1, i1) -> i1
    %31 = "comb.and"(%arg4, %28) : (i1, i1) -> i1
    %32 = "comb.mux"(%27, %25, %46) : (i1, i1, i1) -> i1
    %33 = "comb.or"(%30, %27, %25) : (i1, i1, i1) -> i1
    %34 = "comb.mux"(%33, %44, %24) : (i1, i3, i3) -> i3
    %35 = "comb.mux"(%30, %45, %29) : (i1, i3, i3) -> i3
    %36 = "comb.mux"(%arg1, %2, %34) : (i1, i3, i3) -> i3
    %37 = "comb.mux"(%arg1, %2, %35) : (i1, i3, i3) -> i3
    %38 = "comb.xor"(%arg1, %3) : (i1, i1) -> i1
    %39 = "comb.and"(%38, %32) : (i1, i1) -> i1
    %40 = "comb.and"(%38, %27, %arg5) : (i1, i1, i1) -> i1
    %41 = "comb.and"(%38, %arg4, %28, %arg5) : (i1, i1, i1, i1) -> i1
    %42 = "comb.extract"(%50) <{lowBit = 0 : i32}> : (i3) -> i2
    %43 = "seq.to_clock"(%arg0) : (i1) -> !seq.clock
    %44 = "seq.firreg"(%36, %43) <{name = "wr_ptr_reg"}> : (i3, !seq.clock) -> i3
    %45 = "seq.firreg"(%37, %43) <{name = "wr_ptr_cur_reg"}> : (i3, !seq.clock) -> i3
    %46 = "seq.firreg"(%39, %43) <{name = "drop_frame_reg"}> : (i1, !seq.clock) -> i1
    %47 = "seq.firreg"(%40, %43) <{name = "overflow_reg"}> : (i1, !seq.clock) -> i1
    %48 = "seq.firreg"(%4, %43) <{name = "bad_frame_reg"}> : (i1, !seq.clock) -> i1
    %49 = "seq.firreg"(%41, %43) <{name = "good_frame_reg"}> : (i1, !seq.clock) -> i1
    %50 = "seq.firreg"(%35, %43) <{name = "wr_addr_reg"}> : (i3, !seq.clock) -> i3
    %51 = "seq.firmem"() <{name = "mem", readLatency = 0 : i32, ruw = 0 : i32, writeLatency = 1 : i32, wuw = 0 : i32}> : () -> !seq.firmem<4 x 26, mask 1>
    %52 = "seq.firmem.read_port"(%51, %63, %43) : (!seq.firmem<4 x 26, mask 1>, i2, !seq.clock) -> i26
    "seq.firmem.write_port"(%51, %42, %43, %31, %5) <{operandSegmentSizes = array<i32: 1, 1, 1, 1, 1, 0>}> : (!seq.firmem<4 x 26, mask 1>, i2, !seq.clock, i1, i26) -> ()
    %53 = "comb.xor"(%67, %3) : (i1, i1) -> i1
    %54 = "comb.or"(%72, %53) : (i1, i1) -> i1
    %55 = "comb.icmp"(%44, %66) <{predicate = 1 : i64}> : (i3, i3) -> i1
    %56 = "comb.add"(%66, %0) : (i3, i3) -> i3
    %57 = "comb.and"(%55, %54) : (i1, i1) -> i1
    %58 = "comb.xor"(%54, %3) : (i1, i1) -> i1
    %59 = "comb.mux"(%57, %56, %66) : (i1, i3, i3) -> i3
    %60 = "comb.mux"(%58, %67, %57) : (i1, i1, i1) -> i1
    %61 = "comb.mux"(%arg1, %2, %59) : (i1, i3, i3) -> i3
    %62 = "comb.and"(%38, %60) : (i1, i1) -> i1
    %63 = "comb.extract"(%68) <{lowBit = 0 : i32}> : (i3) -> i2
    %64 = "comb.xor"(%57, %3) : (i1, i1) -> i1
    %65 = "comb.mux"(%64, %1, %52) : (i1, i26, i26) -> i26
    %66 = "seq.firreg"(%61, %43) <{name = "rd_ptr_reg"}> : (i3, !seq.clock) -> i3
    %67 = "seq.firreg"(%62, %43) <{name = "mem_read_data_valid_reg"}> : (i1, !seq.clock) -> i1
    %68 = "seq.firreg"(%59, %43) <{name = "rd_addr_reg"}> : (i3, !seq.clock) -> i3
    %69 = "comb.mux"(%57, %65, %70) <{twoState}> : (i1, i26, i26) -> i26
    %70 = "seq.firreg"(%69, %43) <{name = "mem_read_data_reg"}> : (i26, !seq.clock) -> i26
    %71 = "comb.xor"(%75, %3) : (i1, i1) -> i1
    %72 = "comb.or"(%arg9, %71) : (i1, i1) -> i1
    %73 = "comb.mux"(%72, %67, %75) : (i1, i1, i1) -> i1
    %74 = "comb.and"(%38, %73) : (i1, i1) -> i1
    %75 = "seq.firreg"(%74, %43) <{name = "m_axis_tvalid_reg"}> : (i1, !seq.clock) -> i1
    %76 = "comb.mux"(%72, %70, %77) <{twoState}> : (i1, i26, i26) -> i26
    %77 = "seq.firreg"(%76, %43) <{name = "m_axis_reg"}> : (i26, !seq.clock) -> i26
    "hw.output"(%3, %18, %3, %75, %19, %20, %21, %22, %47, %48, %49) : (i1, i8, i1, i1, i1, i8, i8, i1, i1, i1, i1) -> ()
  }) : () -> ()
}) : () -> ()

