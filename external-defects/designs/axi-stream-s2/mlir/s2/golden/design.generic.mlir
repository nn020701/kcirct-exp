#loc = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/s2/golden/kimulator/design.mlir":5:105)
#loc1 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/s2/golden/kimulator/design.mlir":5:129)
#loc2 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/s2/golden/kimulator/design.mlir":5:153)
#loc3 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/s2/golden/kimulator/design.mlir":5:176)
"builtin.module"() ({
  "hw.module"() <{module_type = !hw.modty<input M_AXIS_ACLK : i1, input M_AXIS_ARESETN : i1, output M_AXIS_TVALID : i1, output M_AXIS_TDATA : i32, output M_AXIS_TSTRB : i4, output M_AXIS_TLAST : i1, input M_AXIS_TREADY : i1>, parameters = [], result_locs = [#loc, #loc1, #loc2, #loc3], sym_name = "xlnxstream_2018_3"}> ({
  ^bb0(%arg0: i1, %arg1: i1, %arg2: i1):
    %0 = "hw.constant"() <{value = true}> : () -> i1
    %1 = "hw.constant"() <{value = -8 : i4}> : () -> i4
    %2 = "hw.constant"() <{value = 1 : i4}> : () -> i4
    %3 = "hw.constant"() <{value = 7 : i4}> : () -> i4
    %4 = "hw.constant"() <{value = 1 : i5}> : () -> i5
    %5 = "hw.constant"() <{value = -1 : i5}> : () -> i5
    %6 = "hw.constant"() <{value = -1 : i4}> : () -> i4
    %7 = "llhd.constant_time"() <{value = #llhd.time<0ns, 0d, 1e>}> : () -> !llhd.time
    %8 = "hw.constant"() <{value = 0 : i28}> : () -> i28
    %9 = "hw.constant"() <{value = 0 : i4}> : () -> i4
    %10 = "hw.constant"() <{value = 8 : i32}> : () -> i32
    %11 = "hw.constant"() <{value = -2 : i2}> : () -> i2
    %12 = "hw.constant"() <{value = 1 : i32}> : () -> i32
    %13 = "hw.constant"() <{value = 1 : i2}> : () -> i2
    %14 = "hw.constant"() <{value = 0 : i5}> : () -> i5
    %15 = "hw.constant"() <{value = 0 : i2}> : () -> i2
    %16 = "llhd.sig"(%15) <{name = "mst_exec_state"}> : (i2) -> !llhd.ref<i2>
    %17 = "llhd.sig"(%9) <{name = "read_pointer"}> : (i4) -> !llhd.ref<i4>
    %18 = "llhd.sig"(%14) <{name = "count"}> : (i5) -> !llhd.ref<i5>
    %19 = "llhd.prb"(%18) : (!llhd.ref<i5>) -> i5
    %20 = "comb.xor"(%arg1, %0) : (i1, i1) -> i1
    %21 = "comb.icmp"(%46, %15) <{predicate = 10 : i64}> : (i2, i2) -> i1
    %22 = "comb.icmp"(%46, %13) <{predicate = 10 : i64}> : (i2, i2) -> i1
    %23 = "comb.add"(%19, %4) : (i5, i5) -> i5
    %24 = "comb.xor"(%21, %0) : (i1, i1) -> i1
    %25 = "comb.and"(%24, %arg1) : (i1, i1) -> i1
    %26 = "comb.and"(%arg1, %21) : (i1, i1) -> i1
    %27 = "comb.mux"(%26, %13, %11) : (i1, i2, i2) -> i2
    %28 = "comb.mux"(%20, %15, %27) : (i1, i2, i2) -> i2
    %29 = "comb.mux"(%20, %14, %19) : (i1, i5, i5) -> i5
    %30 = "comb.icmp"(%19, %5) <{predicate = 1 : i64}> : (i5, i5) -> i1
    %31 = "comb.and"(%30, %22, %25) : (i1, i1, i1) -> i1
    %32 = "comb.mux"(%31, %13, %28) : (i1, i2, i2) -> i2
    %33 = "comb.mux"(%31, %23, %29) : (i1, i5, i5) -> i5
    %34 = "comb.or"(%31, %20) : (i1, i1) -> i1
    %35 = "comb.xor"(%22, %0) : (i1, i1) -> i1
    %36 = "comb.icmp"(%46, %11) <{predicate = 11 : i64}> : (i2, i2) -> i1
    %37 = "comb.and"(%35, %25, %36) : (i1, i1, i1) -> i1
    %38 = "comb.mux"(%37, %19, %33) : (i1, i5, i5) -> i5
    %39 = "comb.xor"(%37, %0) : (i1, i1) -> i1
    %40 = "comb.and"(%39, %34) : (i1, i1) -> i1
    %41 = "seq.to_clock"(%arg0) : (i1) -> !seq.clock
    %42 = "comb.mux"(%37, %43, %32) <{twoState}> : (i1, i2, i2) -> i2
    %43 = "seq.firreg"(%42, %41) <{name = "mst_exec_state"}> : (i2, !seq.clock) -> i2
    "llhd.drv"(%16, %43, %7) : (!llhd.ref<i2>, i2, !llhd.time) -> ()
    %44 = "comb.mux"(%40, %38, %45) <{twoState}> : (i1, i5, i5) -> i5
    %45 = "seq.firreg"(%44, %41) <{name = "count"}> : (i5, !seq.clock) -> i5
    "llhd.drv"(%18, %45, %7) : (!llhd.ref<i5>, i5, !llhd.time) -> ()
    %46 = "llhd.prb"(%16) : (!llhd.ref<i2>) -> i2
    %47 = "comb.icmp"(%46, %11) <{predicate = 0 : i64}> : (i2, i2) -> i1
    %48 = "llhd.prb"(%17) : (!llhd.ref<i4>) -> i4
    %49 = "comb.concat"(%8, %48) : (i28, i4) -> i32
    %50 = "comb.icmp"(%49, %10) <{predicate = 6 : i64}> : (i32, i32) -> i1
    %51 = "comb.and"(%47, %50) : (i1, i1) -> i1
    %52 = "comb.icmp"(%48, %3) <{predicate = 0 : i64}> : (i4, i4) -> i1
    %53 = "comb.xor"(%58, %0) : (i1, i1) -> i1
    %54 = "comb.or"(%53, %arg2) : (i1, i1) -> i1
    %55 = "comb.and"(%arg1, %51) : (i1, i1) -> i1
    %56 = "comb.and"(%arg1, %54, %52) : (i1, i1, i1) -> i1
    %57 = "comb.or"(%20, %54) : (i1, i1) -> i1
    %58 = "seq.firreg"(%55, %41) <{name = "axis_tvalid_delay"}> : (i1, !seq.clock) -> i1
    %59 = "comb.mux"(%57, %56, %60) <{twoState}> : (i1, i1, i1) -> i1
    %60 = "seq.firreg"(%59, %41) <{name = "axis_tlast_delay"}> : (i1, !seq.clock) -> i1
    %61 = "comb.icmp"(%48, %1) <{predicate = 0 : i64}> : (i4, i4) -> i1
    %62 = "comb.add"(%48, %2) : (i4, i4) -> i4
    %63 = "comb.mux"(%20, %9, %48) : (i1, i4, i4) -> i4
    %64 = "comb.and"(%50, %arg1) : (i1, i1) -> i1
    %65 = "comb.and"(%81, %64) : (i1, i1) -> i1
    %66 = "comb.mux"(%65, %62, %63) : (i1, i4, i4) -> i4
    %67 = "comb.or"(%65, %20) : (i1, i1) -> i1
    %68 = "comb.xor"(%65, %0) : (i1, i1) -> i1
    %69 = "comb.or"(%65, %20, %61) : (i1, i1, i1) -> i1
    %70 = "comb.xor"(%81, %0) : (i1, i1) -> i1
    %71 = "comb.and"(%64, %70) : (i1, i1) -> i1
    %72 = "comb.mux"(%71, %48, %66) : (i1, i4, i4) -> i4
    %73 = "comb.xor"(%71, %0) : (i1, i1) -> i1
    %74 = "comb.and"(%73, %67) : (i1, i1) -> i1
    %75 = "comb.and"(%73, %68, %arg1, %61) : (i1, i1, i1, i1) -> i1
    %76 = "comb.and"(%73, %69) : (i1, i1) -> i1
    %77 = "comb.mux"(%74, %72, %78) <{twoState}> : (i1, i4, i4) -> i4
    %78 = "seq.firreg"(%77, %41) <{name = "read_pointer"}> : (i4, !seq.clock) -> i4
    "llhd.drv"(%17, %78, %7) : (!llhd.ref<i4>, i4, !llhd.time) -> ()
    %79 = "comb.mux"(%76, %75, %80) <{twoState}> : (i1, i1, i1) -> i1
    %80 = "seq.firreg"(%79, %41) <{name = "tx_done"}> : (i1, !seq.clock) -> i1
    %81 = "comb.and"(%arg2, %51) : (i1, i1) -> i1
    %82 = "comb.add"(%49, %12) : (i32, i32) -> i32
    %83 = "comb.and"(%81, %arg1) : (i1, i1) -> i1
    %84 = "comb.mux"(%83, %82, %12) : (i1, i32, i32) -> i32
    %85 = "comb.and"(%arg1, %70) : (i1, i1) -> i1
    %86 = "comb.mux"(%85, %87, %84) <{twoState}> : (i1, i32, i32) -> i32
    %87 = "seq.firreg"(%86, %41) <{name = "stream_data_out"}> : (i32, !seq.clock) -> i32
    "llhd.drv"(%18, %14, %7) : (!llhd.ref<i5>, i5, !llhd.time) -> ()
    "llhd.drv"(%16, %15, %7) : (!llhd.ref<i2>, i2, !llhd.time) -> ()
    "llhd.drv"(%17, %9, %7) : (!llhd.ref<i4>, i4, !llhd.time) -> ()
    "hw.output"(%58, %87, %6, %60) : (i1, i32, i4, i1) -> ()
  }) : () -> ()
}) : () -> ()

