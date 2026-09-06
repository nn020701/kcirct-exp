#loc = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d11/buggy/kimulator/design.mlir":9:161)
#loc1 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d11/buggy/kimulator/design.mlir":9:265)
#loc2 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d11/buggy/kimulator/design.mlir":9:293)
#loc3 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d11/buggy/kimulator/design.mlir":9:362)
#loc4 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/d11/buggy/kimulator/design.mlir":9:390)
"builtin.module"() ({
  "hw.module"() <{module_type = !hw.modty<input clk : i1, input rst : i1, input input_axis_tdata : i8, input input_axis_tvalid : i1, output input_axis_tready : i1, input input_axis_tlast : i1, input input_axis_tuser : i1, output output_axis_tdata : i8, output output_axis_tvalid : i1, input output_axis_tready : i1, output output_axis_tlast : i1, output drop_frame : i1>, parameters = [], result_locs = [#loc, #loc1, #loc2, #loc3, #loc4], sym_name = "axis_frame_fifo"}> ({
  ^bb0(%arg0: i1, %arg1: i1, %arg2: i8, %arg3: i1, %arg4: i1, %arg5: i1, %arg6: i1):
    %0 = "hw.constant"() <{value = true}> : () -> i1
    %1 = "hw.constant"() <{value = 1 : i3}> : () -> i3
    %2 = "hw.constant"() <{value = 0 : i10}> : () -> i10
    %3 = "hw.constant"() <{value = 0 : i3}> : () -> i3
    %4 = "hw.constant"() <{value = false}> : () -> i1
    %5 = "comb.concat"(%4, %arg4, %arg2) : (i1, i1, i8) -> i10
    %6 = "comb.extract"(%66) <{lowBit = 2 : i32}> : (i3) -> i1
    %7 = "comb.extract"(%91) <{lowBit = 2 : i32}> : (i3) -> i1
    %8 = "comb.icmp"(%6, %7) <{predicate = 1 : i64}> : (i1, i1) -> i1
    %9 = "comb.extract"(%66) <{lowBit = 0 : i32}> : (i3) -> i2
    %10 = "comb.extract"(%91) <{lowBit = 0 : i32}> : (i3) -> i2
    %11 = "comb.icmp"(%9, %10) <{predicate = 0 : i64}> : (i2, i2) -> i1
    %12 = "comb.and"(%8, %11) : (i1, i1) -> i1
    %13 = "comb.extract"(%74) <{lowBit = 2 : i32}> : (i3) -> i1
    %14 = "comb.icmp"(%6, %13) <{predicate = 1 : i64}> : (i1, i1) -> i1
    %15 = "comb.extract"(%74) <{lowBit = 0 : i32}> : (i3) -> i2
    %16 = "comb.icmp"(%9, %15) <{predicate = 0 : i64}> : (i2, i2) -> i1
    %17 = "comb.and"(%14, %16) : (i1, i1) -> i1
    %18 = "comb.xor"(%96, %0) : (i1, i1) -> i1
    %19 = "comb.or"(%arg6, %18) : (i1, i1) -> i1
    %20 = "comb.icmp"(%66, %91) <{predicate = 1 : i64}> : (i3, i3) -> i1
    %21 = "comb.and"(%19, %20) : (i1, i1) -> i1
    %22 = "comb.extract"(%93) <{lowBit = 8 : i32}> : (i10) -> i1
    %23 = "comb.extract"(%93) <{lowBit = 0 : i32}> : (i10) -> i8
    %24 = "comb.or"(%12, %17, %70) : (i1, i1, i1) -> i1
    %25 = "hw.array_inject"(%78, %15, %5) : (!hw.array<4xi10>, i2, i10) -> !hw.array<4xi10>
    %26 = "comb.add"(%74, %1) : (i3, i3) -> i3
    %27 = "comb.mux"(%arg5, %66, %26) : (i1, i3, i3) -> i3
    %28 = "comb.xor"(%arg5, %0) : (i1, i1) -> i1
    %29 = "comb.xor"(%arg4, %0) : (i1, i1) -> i1
    %30 = "comb.mux"(%arg4, %66, %74) : (i1, i3, i3) -> i3
    %31 = "comb.xor"(%arg1, %0) : (i1, i1) -> i1
    %32 = "comb.and"(%arg3, %31) : (i1, i1) -> i1
    %33 = "comb.and"(%24, %32) : (i1, i1) -> i1
    %34 = "comb.or"(%33, %arg5) : (i1, i1) -> i1
    %35 = "comb.mux"(%34, %66, %26) : (i1, i3, i3) -> i3
    %36 = "comb.xor"(%33, %0) : (i1, i1) -> i1
    %37 = "comb.and"(%36, %28) : (i1, i1) -> i1
    %38 = "comb.mux"(%33, %30, %27) : (i1, i3, i3) -> i3
    %39 = "comb.or"(%36, %arg4) : (i1, i1) -> i1
    %40 = "comb.mux"(%arg1, %3, %35) : (i1, i3, i3) -> i3
    %41 = "comb.or"(%arg1, %37) : (i1, i1) -> i1
    %42 = "comb.mux"(%arg1, %74, %38) : (i1, i3, i3) -> i3
    %43 = "comb.and"(%31, %39) : (i1, i1) -> i1
    %44 = "comb.or"(%arg1, %33) : (i1, i1) -> i1
    %45 = "comb.and"(%31, %36) : (i1, i1) -> i1
    %46 = "comb.xor"(%24, %0) : (i1, i1) -> i1
    %47 = "comb.and"(%46, %32, %29) : (i1, i1, i1) -> i1
    %48 = "comb.xor"(%47, %0) : (i1, i1) -> i1
    %49 = "comb.mux"(%47, %26, %42) : (i1, i3, i3) -> i3
    %50 = "comb.or"(%47, %43) : (i1, i1) -> i1
    %51 = "comb.xor"(%44, %0) : (i1, i1) -> i1
    %52 = "comb.or"(%47, %51) : (i1, i1) -> i1
    %53 = "comb.or"(%47, %45) : (i1, i1) -> i1
    %54 = "comb.xor"(%arg3, %0) : (i1, i1) -> i1
    %55 = "comb.and"(%31, %54) : (i1, i1) -> i1
    %56 = "comb.xor"(%55, %0) : (i1, i1) -> i1
    %57 = "comb.and"(%56, %48, %41) : (i1, i1, i1) -> i1
    %58 = "comb.and"(%56, %48, %33) : (i1, i1, i1) -> i1
    %59 = "comb.and"(%56, %50) : (i1, i1) -> i1
    %60 = "comb.xor"(%52, %0) : (i1, i1) -> i1
    %61 = "comb.and"(%56, %53) : (i1, i1) -> i1
    %62 = "seq.to_clock"(%arg0) : (i1) -> !seq.clock
    %63 = "comb.xor"(%57, %0) : (i1, i1) -> i1
    %64 = "comb.or"(%63, %55, %47) : (i1, i1, i1) -> i1
    %65 = "comb.mux"(%64, %66, %40) <{twoState}> : (i1, i3, i3) -> i3
    %66 = "seq.firreg"(%65, %62) <{name = "wr_ptr"}> : (i3, !seq.clock) -> i3
    %67 = "comb.xor"(%58, %0) : (i1, i1) -> i1
    %68 = "comb.or"(%67, %55, %47, %arg1, %36) : (i1, i1, i1, i1, i1) -> i1
    %69 = "comb.mux"(%68, %70, %29) <{twoState}> : (i1, i1, i1) -> i1
    %70 = "seq.firreg"(%69, %62) <{name = "drop_frame"}> : (i1, !seq.clock) -> i1
    %71 = "comb.xor"(%59, %0) : (i1, i1) -> i1
    %72 = "comb.or"(%71, %55) : (i1, i1) -> i1
    %73 = "comb.mux"(%72, %74, %49) <{twoState}> : (i1, i3, i3) -> i3
    %74 = "seq.firreg"(%73, %62) <{name = "wr_ptr_cur"}> : (i3, !seq.clock) -> i3
    %75 = "comb.xor"(%61, %0) : (i1, i1) -> i1
    %76 = "comb.or"(%75, %55, %60) : (i1, i1, i1) -> i1
    %77 = "comb.mux"(%76, %78, %25) <{twoState}> : (i1, !hw.array<4xi10>, !hw.array<4xi10>) -> !hw.array<4xi10>
    %78 = "seq.firreg"(%77, %62) <{name = "mem"}> : (!hw.array<4xi10>, !seq.clock) -> !hw.array<4xi10>
    %79 = "hw.array_get"(%78, %10) : (!hw.array<4xi10>, i2) -> i10
    %80 = "comb.add"(%91, %1) : (i3, i3) -> i3
    %81 = "comb.and"(%21, %31) : (i1, i1) -> i1
    %82 = "comb.mux"(%81, %80, %3) : (i1, i3, i3) -> i3
    %83 = "comb.xor"(%21, %0) : (i1, i1) -> i1
    %84 = "comb.and"(%31, %83) : (i1, i1) -> i1
    %85 = "comb.xor"(%81, %0) : (i1, i1) -> i1
    %86 = "comb.or"(%84, %85) : (i1, i1) -> i1
    %87 = "comb.mux"(%86, %2, %79) : (i1, i10, i10) -> i10
    %88 = "comb.xor"(%84, %0) : (i1, i1) -> i1
    %89 = "comb.and"(%88, %81) : (i1, i1) -> i1
    %90 = "comb.mux"(%84, %91, %82) <{twoState}> : (i1, i3, i3) -> i3
    %91 = "seq.firreg"(%90, %62) <{name = "rd_ptr"}> : (i3, !seq.clock) -> i3
    %92 = "comb.mux"(%89, %87, %93) <{twoState}> : (i1, i10, i10) -> i10
    %93 = "seq.firreg"(%92, %62) <{name = "data_out_reg"}> : (i10, !seq.clock) -> i10
    %94 = "comb.mux"(%19, %20, %96) : (i1, i1, i1) -> i1
    %95 = "comb.and"(%31, %94) : (i1, i1) -> i1
    %96 = "seq.firreg"(%95, %62) <{name = "output_axis_tvalid_reg"}> : (i1, !seq.clock) -> i1
    "hw.output"(%0, %23, %96, %22, %70) : (i1, i8, i1, i1, i1) -> ()
  }) : () -> ()
}) : () -> ()

