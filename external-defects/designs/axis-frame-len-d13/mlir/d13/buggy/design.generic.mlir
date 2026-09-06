#loc = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d13/buggy/kimulator/design.mlir":8:245)
#loc1 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/d13/buggy/kimulator/design.mlir":8:266)
"builtin.module"() ({
  "hw.module"() <{module_type = !hw.modty<input clk : i1, input rst : i1, input monitor_axis_tkeep : i8, input monitor_axis_tvalid : i1, input monitor_axis_tready : i1, input monitor_axis_tlast : i1, output frame_len : i16, output frame_len_valid : i1>, parameters = [], result_locs = [#loc, #loc1], sym_name = "axis_frame_len"}> ({
  ^bb0(%arg0: i1, %arg1: i1, %arg2: i8, %arg3: i1, %arg4: i1, %arg5: i1):
    %0 = "hw.constant"() <{value = 8 : i16}> : () -> i16
    %1 = "hw.constant"() <{value = 7 : i16}> : () -> i16
    %2 = "hw.constant"() <{value = 6 : i16}> : () -> i16
    %3 = "hw.constant"() <{value = 5 : i16}> : () -> i16
    %4 = "hw.constant"() <{value = 4 : i16}> : () -> i16
    %5 = "hw.constant"() <{value = 3 : i16}> : () -> i16
    %6 = "hw.constant"() <{value = 0 : i15}> : () -> i15
    %7 = "hw.constant"() <{value = 2 : i16}> : () -> i16
    %8 = "hw.constant"() <{value = 127 : i8}> : () -> i8
    %9 = "hw.constant"() <{value = 63 : i8}> : () -> i8
    %10 = "hw.constant"() <{value = 31 : i8}> : () -> i8
    %11 = "hw.constant"() <{value = 15 : i8}> : () -> i8
    %12 = "hw.constant"() <{value = 7 : i8}> : () -> i8
    %13 = "hw.constant"() <{value = 3 : i8}> : () -> i8
    %14 = "hw.constant"() <{value = 1 : i8}> : () -> i8
    %15 = "hw.constant"() <{value = true}> : () -> i1
    %16 = "hw.constant"() <{value = -1 : i8}> : () -> i8
    %17 = "hw.constant"() <{value = 0 : i16}> : () -> i16
    %18 = "comb.and"(%arg4, %arg3) : (i1, i1) -> i1
    %19 = "comb.or"(%arg5, %49) : (i1, i1) -> i1
    %20 = "comb.mux"(%19, %47, %17) : (i1, i16, i16) -> i16
    %21 = "comb.xor"(%arg5, %15) : (i1, i1) -> i1
    %22 = "comb.icmp"(%arg2, %14) <{predicate = 0 : i64}> : (i8, i8) -> i1
    %23 = "comb.icmp"(%arg2, %13) <{predicate = 0 : i64}> : (i8, i8) -> i1
    %24 = "comb.concat"(%6, %22) : (i15, i1) -> i16
    %25 = "comb.mux"(%23, %7, %24) : (i1, i16, i16) -> i16
    %26 = "comb.icmp"(%arg2, %12) <{predicate = 0 : i64}> : (i8, i8) -> i1
    %27 = "comb.mux"(%26, %5, %25) : (i1, i16, i16) -> i16
    %28 = "comb.icmp"(%arg2, %11) <{predicate = 0 : i64}> : (i8, i8) -> i1
    %29 = "comb.mux"(%28, %4, %27) : (i1, i16, i16) -> i16
    %30 = "comb.icmp"(%arg2, %10) <{predicate = 0 : i64}> : (i8, i8) -> i1
    %31 = "comb.mux"(%30, %3, %29) : (i1, i16, i16) -> i16
    %32 = "comb.icmp"(%arg2, %9) <{predicate = 0 : i64}> : (i8, i8) -> i1
    %33 = "comb.mux"(%32, %2, %31) : (i1, i16, i16) -> i16
    %34 = "comb.icmp"(%arg2, %8) <{predicate = 0 : i64}> : (i8, i8) -> i1
    %35 = "comb.mux"(%34, %1, %33) : (i1, i16, i16) -> i16
    %36 = "comb.icmp"(%arg2, %16) <{predicate = 0 : i64}> : (i8, i8) -> i1
    %37 = "comb.mux"(%36, %0, %35) : (i1, i16, i16) -> i16
    %38 = "comb.add"(%20, %37) : (i16, i16) -> i16
    %39 = "comb.xor"(%18, %15) : (i1, i1) -> i1
    %40 = "comb.mux"(%39, %47, %38) : (i1, i16, i16) -> i16
    %41 = "comb.mux"(%39, %49, %21) : (i1, i1, i1) -> i1
    %42 = "comb.mux"(%arg1, %17, %40) : (i1, i16, i16) -> i16
    %43 = "comb.xor"(%arg1, %15) : (i1, i1) -> i1
    %44 = "comb.and"(%43, %18, %arg5) : (i1, i1, i1) -> i1
    %45 = "comb.and"(%43, %41) : (i1, i1) -> i1
    %46 = "seq.to_clock"(%arg0) : (i1) -> !seq.clock
    %47 = "seq.firreg"(%42, %46) <{name = "frame_len_reg"}> : (i16, !seq.clock) -> i16
    %48 = "seq.firreg"(%44, %46) <{name = "frame_len_valid_reg"}> : (i1, !seq.clock) -> i1
    %49 = "seq.firreg"(%45, %46) <{name = "frame_reg"}> : (i1, !seq.clock) -> i1
    "hw.output"(%47, %48) : (i16, i1) -> ()
  }) : () -> ()
}) : () -> ()

