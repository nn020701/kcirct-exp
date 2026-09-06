#loc = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d11/golden/kimulator/design.mlir":9:161)
#loc1 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d11/golden/kimulator/design.mlir":9:265)
#loc2 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d11/golden/kimulator/design.mlir":9:293)
#loc3 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d11/golden/kimulator/design.mlir":9:362)
#loc4 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d11/golden/kimulator/design.mlir":9:390)
"builtin.module"() ({
  "hw.module"() <{module_type = !hw.modty<input clk : i1, input rst : i1, input input_axis_tdata : i8, input input_axis_tvalid : i1, output input_axis_tready : i1, input input_axis_tlast : i1, input input_axis_tuser : i1, output output_axis_tdata : i8, output output_axis_tvalid : i1, input output_axis_tready : i1, output output_axis_tlast : i1, output drop_frame : i1>, parameters = [], result_locs = [#loc, #loc1, #loc2, #loc3, #loc4], sym_name = "axis_frame_fifo"}> ({
  ^bb0(%arg0: i1, %arg1: i1, %arg2: i8, %arg3: i1, %arg4: i1, %arg5: i1, %arg6: i1):
    %0 = "hw.constant"() <{value = true}> : () -> i1
    %1 = "hw.constant"() <{value = 1 : i3}> : () -> i3
    %2 = "hw.constant"() <{value = 0 : i10}> : () -> i10
    %3 = "hw.constant"() <{value = 0 : i3}> : () -> i3
    %4 = "hw.constant"() <{value = false}> : () -> i1
    %5 = "comb.concat"(%4, %arg4, %arg2) : (i1, i1, i8) -> i10
    %6 = "comb.extract"(%67) <{lowBit = 2 : i32}> : (i3) -> i1
    %7 = "comb.extract"(%92) <{lowBit = 2 : i32}> : (i3) -> i1
    %8 = "comb.icmp"(%6, %7) <{predicate = 1 : i64}> : (i1, i1) -> i1
    %9 = "comb.extract"(%67) <{lowBit = 0 : i32}> : (i3) -> i2
    %10 = "comb.extract"(%92) <{lowBit = 0 : i32}> : (i3) -> i2
    %11 = "comb.icmp"(%9, %10) <{predicate = 0 : i64}> : (i2, i2) -> i1
    %12 = "comb.and"(%8, %11) : (i1, i1) -> i1
    %13 = "comb.extract"(%71) <{lowBit = 2 : i32}> : (i3) -> i1
    %14 = "comb.icmp"(%6, %13) <{predicate = 1 : i64}> : (i1, i1) -> i1
    %15 = "comb.extract"(%71) <{lowBit = 0 : i32}> : (i3) -> i2
    %16 = "comb.icmp"(%9, %15) <{predicate = 0 : i64}> : (i2, i2) -> i1
    %17 = "comb.and"(%14, %16) : (i1, i1) -> i1
    %18 = "comb.xor"(%97, %0) : (i1, i1) -> i1
    %19 = "comb.or"(%arg6, %18) : (i1, i1) -> i1
    %20 = "comb.icmp"(%67, %92) <{predicate = 1 : i64}> : (i3, i3) -> i1
    %21 = "comb.and"(%19, %20) : (i1, i1) -> i1
    %22 = "comb.extract"(%94) <{lowBit = 8 : i32}> : (i10) -> i1
    %23 = "comb.extract"(%94) <{lowBit = 0 : i32}> : (i10) -> i8
    %24 = "comb.or"(%12, %17, %75) : (i1, i1, i1) -> i1
    %25 = "hw.array_inject"(%79, %15, %5) : (!hw.array<4xi10>, i2, i10) -> !hw.array<4xi10>
    %26 = "comb.add"(%71, %1) : (i3, i3) -> i3
    %27 = "comb.mux"(%arg5, %67, %26) : (i1, i3, i3) -> i3
    %28 = "comb.xor"(%arg5, %0) : (i1, i1) -> i1
    %29 = "comb.mux"(%arg4, %67, %71) : (i1, i3, i3) -> i3
    %30 = "comb.xor"(%arg4, %0) : (i1, i1) -> i1
    %31 = "comb.xor"(%arg1, %0) : (i1, i1) -> i1
    %32 = "comb.and"(%arg3, %31) : (i1, i1) -> i1
    %33 = "comb.and"(%24, %32) : (i1, i1) -> i1
    %34 = "comb.or"(%33, %arg5) : (i1, i1) -> i1
    %35 = "comb.mux"(%34, %67, %26) : (i1, i3, i3) -> i3
    %36 = "comb.xor"(%33, %0) : (i1, i1) -> i1
    %37 = "comb.and"(%36, %28) : (i1, i1) -> i1
    %38 = "comb.mux"(%33, %29, %27) : (i1, i3, i3) -> i3
    %39 = "comb.mux"(%33, %30, %75) : (i1, i1, i1) -> i1
    %40 = "comb.mux"(%arg1, %3, %35) : (i1, i3, i3) -> i3
    %41 = "comb.or"(%arg1, %37) : (i1, i1) -> i1
    %42 = "comb.mux"(%arg1, %3, %38) : (i1, i3, i3) -> i3
    %43 = "comb.and"(%31, %39) : (i1, i1) -> i1
    %44 = "comb.or"(%arg1, %33) : (i1, i1) -> i1
    %45 = "comb.and"(%31, %36) : (i1, i1) -> i1
    %46 = "comb.xor"(%24, %0) : (i1, i1) -> i1
    %47 = "comb.and"(%46, %32, %30) : (i1, i1, i1) -> i1
    %48 = "comb.xor"(%47, %0) : (i1, i1) -> i1
    %49 = "comb.mux"(%47, %26, %42) : (i1, i3, i3) -> i3
    %50 = "comb.or"(%47, %arg1, %36, %arg4) : (i1, i1, i1, i1) -> i1
    %51 = "comb.xor"(%44, %0) : (i1, i1) -> i1
    %52 = "comb.or"(%47, %51) : (i1, i1) -> i1
    %53 = "comb.or"(%47, %45) : (i1, i1) -> i1
    %54 = "comb.xor"(%arg3, %0) : (i1, i1) -> i1
    %55 = "comb.and"(%31, %54) : (i1, i1) -> i1
    %56 = "comb.or"(%55, %47) : (i1, i1) -> i1
    %57 = "comb.xor"(%55, %0) : (i1, i1) -> i1
    %58 = "comb.and"(%57, %48, %41) : (i1, i1, i1) -> i1
    %59 = "comb.and"(%57, %50) : (i1, i1) -> i1
    %60 = "comb.and"(%57, %48, %44) : (i1, i1, i1) -> i1
    %61 = "comb.xor"(%52, %0) : (i1, i1) -> i1
    %62 = "comb.and"(%57, %53) : (i1, i1) -> i1
    %63 = "seq.to_clock"(%arg0) : (i1) -> !seq.clock
    %64 = "comb.xor"(%58, %0) : (i1, i1) -> i1
    %65 = "comb.or"(%64, %56) : (i1, i1) -> i1
    %66 = "comb.mux"(%65, %67, %40) <{twoState}> : (i1, i3, i3) -> i3
    %67 = "seq.firreg"(%66, %63) <{name = "wr_ptr"}> : (i3, !seq.clock) -> i3
    %68 = "comb.xor"(%59, %0) : (i1, i1) -> i1
    %69 = "comb.or"(%68, %55) : (i1, i1) -> i1
    %70 = "comb.mux"(%69, %71, %49) <{twoState}> : (i1, i3, i3) -> i3
    %71 = "seq.firreg"(%70, %63) <{name = "wr_ptr_cur"}> : (i3, !seq.clock) -> i3
    %72 = "comb.xor"(%60, %0) : (i1, i1) -> i1
    %73 = "comb.or"(%72, %56) : (i1, i1) -> i1
    %74 = "comb.mux"(%73, %75, %43) <{twoState}> : (i1, i1, i1) -> i1
    %75 = "seq.firreg"(%74, %63) <{name = "drop_frame"}> : (i1, !seq.clock) -> i1
    %76 = "comb.xor"(%62, %0) : (i1, i1) -> i1
    %77 = "comb.or"(%76, %55, %61) : (i1, i1, i1) -> i1
    %78 = "comb.mux"(%77, %79, %25) <{twoState}> : (i1, !hw.array<4xi10>, !hw.array<4xi10>) -> !hw.array<4xi10>
    %79 = "seq.firreg"(%78, %63) <{name = "mem"}> : (!hw.array<4xi10>, !seq.clock) -> !hw.array<4xi10>
    %80 = "hw.array_get"(%79, %10) : (!hw.array<4xi10>, i2) -> i10
    %81 = "comb.add"(%92, %1) : (i3, i3) -> i3
    %82 = "comb.and"(%21, %31) : (i1, i1) -> i1
    %83 = "comb.mux"(%82, %81, %3) : (i1, i3, i3) -> i3
    %84 = "comb.xor"(%21, %0) : (i1, i1) -> i1
    %85 = "comb.and"(%31, %84) : (i1, i1) -> i1
    %86 = "comb.xor"(%82, %0) : (i1, i1) -> i1
    %87 = "comb.or"(%85, %86) : (i1, i1) -> i1
    %88 = "comb.mux"(%87, %2, %80) : (i1, i10, i10) -> i10
    %89 = "comb.xor"(%85, %0) : (i1, i1) -> i1
    %90 = "comb.and"(%89, %82) : (i1, i1) -> i1
    %91 = "comb.mux"(%85, %92, %83) <{twoState}> : (i1, i3, i3) -> i3
    %92 = "seq.firreg"(%91, %63) <{name = "rd_ptr"}> : (i3, !seq.clock) -> i3
    %93 = "comb.mux"(%90, %88, %94) <{twoState}> : (i1, i10, i10) -> i10
    %94 = "seq.firreg"(%93, %63) <{name = "data_out_reg"}> : (i10, !seq.clock) -> i10
    %95 = "comb.mux"(%19, %20, %97) : (i1, i1, i1) -> i1
    %96 = "comb.and"(%31, %95) : (i1, i1) -> i1
    %97 = "seq.firreg"(%96, %63) <{name = "output_axis_tvalid_reg"}> : (i1, !seq.clock) -> i1
    "hw.output"(%0, %23, %97, %22, %75) : (i1, i8, i1, i1, i1) -> ()
  }) : () -> ()
}) : () -> ()

