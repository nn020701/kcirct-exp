#loc = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/s2/buggy/kimulator/design.mlir":5:105)
#loc1 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/s2/buggy/kimulator/design.mlir":5:129)
#loc2 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/s2/buggy/kimulator/design.mlir":5:153)
#loc3 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-memory-01/s2/buggy/kimulator/design.mlir":5:176)
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
    %53 = "comb.and"(%arg1, %51) : (i1, i1) -> i1
    %54 = "comb.and"(%arg1, %52) : (i1, i1) -> i1
    %55 = "seq.firreg"(%53, %41) <{name = "axis_tvalid_delay"}> : (i1, !seq.clock) -> i1
    %56 = "seq.firreg"(%54, %41) <{name = "axis_tlast_delay"}> : (i1, !seq.clock) -> i1
    %57 = "comb.icmp"(%48, %1) <{predicate = 0 : i64}> : (i4, i4) -> i1
    %58 = "comb.add"(%48, %2) : (i4, i4) -> i4
    %59 = "comb.mux"(%20, %9, %48) : (i1, i4, i4) -> i4
    %60 = "comb.and"(%50, %arg1) : (i1, i1) -> i1
    %61 = "comb.and"(%77, %60) : (i1, i1) -> i1
    %62 = "comb.mux"(%61, %58, %59) : (i1, i4, i4) -> i4
    %63 = "comb.or"(%61, %20) : (i1, i1) -> i1
    %64 = "comb.xor"(%61, %0) : (i1, i1) -> i1
    %65 = "comb.or"(%61, %20, %57) : (i1, i1, i1) -> i1
    %66 = "comb.xor"(%77, %0) : (i1, i1) -> i1
    %67 = "comb.and"(%60, %66) : (i1, i1) -> i1
    %68 = "comb.mux"(%67, %48, %62) : (i1, i4, i4) -> i4
    %69 = "comb.xor"(%67, %0) : (i1, i1) -> i1
    %70 = "comb.and"(%69, %63) : (i1, i1) -> i1
    %71 = "comb.and"(%69, %64, %arg1, %57) : (i1, i1, i1, i1) -> i1
    %72 = "comb.and"(%69, %65) : (i1, i1) -> i1
    %73 = "comb.mux"(%70, %68, %74) <{twoState}> : (i1, i4, i4) -> i4
    %74 = "seq.firreg"(%73, %41) <{name = "read_pointer"}> : (i4, !seq.clock) -> i4
    "llhd.drv"(%17, %74, %7) : (!llhd.ref<i4>, i4, !llhd.time) -> ()
    %75 = "comb.mux"(%72, %71, %76) <{twoState}> : (i1, i1, i1) -> i1
    %76 = "seq.firreg"(%75, %41) <{name = "tx_done"}> : (i1, !seq.clock) -> i1
    %77 = "comb.and"(%arg2, %51) : (i1, i1) -> i1
    %78 = "comb.add"(%49, %12) : (i32, i32) -> i32
    %79 = "comb.and"(%77, %arg1) : (i1, i1) -> i1
    %80 = "comb.mux"(%79, %78, %12) : (i1, i32, i32) -> i32
    %81 = "comb.and"(%arg1, %66) : (i1, i1) -> i1
    %82 = "comb.mux"(%81, %83, %80) <{twoState}> : (i1, i32, i32) -> i32
    %83 = "seq.firreg"(%82, %41) <{name = "stream_data_out"}> : (i32, !seq.clock) -> i32
    "llhd.drv"(%18, %14, %7) : (!llhd.ref<i5>, i5, !llhd.time) -> ()
    "llhd.drv"(%16, %15, %7) : (!llhd.ref<i2>, i2, !llhd.time) -> ()
    "llhd.drv"(%17, %9, %7) : (!llhd.ref<i4>, i4, !llhd.time) -> ()
    "hw.output"(%55, %83, %6, %56) : (i1, i32, i4, i1) -> ()
  }) : () -> ()
}) : () -> ()

