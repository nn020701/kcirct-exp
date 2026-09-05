#loc = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-first-01/d13/golden/kimulator/design.mlir":8:245)
#loc1 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-first-01/d13/golden/kimulator/design.mlir":8:266)
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
    %18 = "comb.mux"(%47, %17, %46) : (i1, i16, i16) -> i16
    %19 = "comb.and"(%arg4, %arg3) : (i1, i1) -> i1
    %20 = "comb.xor"(%arg5, %15) : (i1, i1) -> i1
    %21 = "comb.icmp"(%arg2, %14) <{predicate = 0 : i64}> : (i8, i8) -> i1
    %22 = "comb.icmp"(%arg2, %13) <{predicate = 0 : i64}> : (i8, i8) -> i1
    %23 = "comb.concat"(%6, %21) : (i15, i1) -> i16
    %24 = "comb.mux"(%22, %7, %23) : (i1, i16, i16) -> i16
    %25 = "comb.icmp"(%arg2, %12) <{predicate = 0 : i64}> : (i8, i8) -> i1
    %26 = "comb.mux"(%25, %5, %24) : (i1, i16, i16) -> i16
    %27 = "comb.icmp"(%arg2, %11) <{predicate = 0 : i64}> : (i8, i8) -> i1
    %28 = "comb.mux"(%27, %4, %26) : (i1, i16, i16) -> i16
    %29 = "comb.icmp"(%arg2, %10) <{predicate = 0 : i64}> : (i8, i8) -> i1
    %30 = "comb.mux"(%29, %3, %28) : (i1, i16, i16) -> i16
    %31 = "comb.icmp"(%arg2, %9) <{predicate = 0 : i64}> : (i8, i8) -> i1
    %32 = "comb.mux"(%31, %2, %30) : (i1, i16, i16) -> i16
    %33 = "comb.icmp"(%arg2, %8) <{predicate = 0 : i64}> : (i8, i8) -> i1
    %34 = "comb.mux"(%33, %1, %32) : (i1, i16, i16) -> i16
    %35 = "comb.icmp"(%arg2, %16) <{predicate = 0 : i64}> : (i8, i8) -> i1
    %36 = "comb.mux"(%35, %0, %34) : (i1, i16, i16) -> i16
    %37 = "comb.add"(%18, %36) : (i16, i16) -> i16
    %38 = "comb.xor"(%19, %15) : (i1, i1) -> i1
    %39 = "comb.mux"(%38, %18, %37) : (i1, i16, i16) -> i16
    %40 = "comb.mux"(%38, %48, %20) : (i1, i1, i1) -> i1
    %41 = "comb.mux"(%arg1, %17, %39) : (i1, i16, i16) -> i16
    %42 = "comb.xor"(%arg1, %15) : (i1, i1) -> i1
    %43 = "comb.and"(%42, %19, %arg5) : (i1, i1, i1) -> i1
    %44 = "comb.and"(%42, %40) : (i1, i1) -> i1
    %45 = "seq.to_clock"(%arg0) : (i1) -> !seq.clock
    %46 = "seq.firreg"(%41, %45) <{name = "frame_len_reg"}> : (i16, !seq.clock) -> i16
    %47 = "seq.firreg"(%43, %45) <{name = "frame_len_valid_reg"}> : (i1, !seq.clock) -> i1
    %48 = "seq.firreg"(%44, %45) <{name = "frame_reg"}> : (i1, !seq.clock) -> i1
    "hw.output"(%46, %47) : (i16, i1) -> ()
  }) : () -> ()
}) : () -> ()

