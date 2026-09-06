#loc = loc(".work/ir-preparation/initial-register-v1/s2/golden/design.mlir":5:105)
#loc1 = loc(".work/ir-preparation/initial-register-v1/s2/golden/design.mlir":5:129)
#loc2 = loc(".work/ir-preparation/initial-register-v1/s2/golden/design.mlir":5:153)
#loc3 = loc(".work/ir-preparation/initial-register-v1/s2/golden/design.mlir":5:176)
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
    %7 = "hw.constant"() <{value = 0 : i28}> : () -> i28
    %8 = "hw.constant"() <{value = 0 : i4}> : () -> i4
    %9 = "hw.constant"() <{value = 8 : i32}> : () -> i32
    %10 = "hw.constant"() <{value = -2 : i2}> : () -> i2
    %11 = "hw.constant"() <{value = 1 : i32}> : () -> i32
    %12 = "hw.constant"() <{value = 1 : i2}> : () -> i2
    %13 = "hw.constant"() <{value = 0 : i5}> : () -> i5
    %14 = "hw.constant"() <{value = 0 : i2}> : () -> i2
    %15 = "comb.xor"(%arg1, %0) : (i1, i1) -> i1
    %16 = "comb.icmp"(%37, %14) <{predicate = 10 : i64}> : (i2, i2) -> i1
    %17 = "comb.icmp"(%37, %12) <{predicate = 10 : i64}> : (i2, i2) -> i1
    %18 = "comb.add"(%41, %4) : (i5, i5) -> i5
    %19 = "comb.xor"(%16, %0) : (i1, i1) -> i1
    %20 = "comb.and"(%19, %arg1) : (i1, i1) -> i1
    %21 = "comb.and"(%arg1, %16) : (i1, i1) -> i1
    %22 = "comb.mux"(%21, %12, %10) : (i1, i2, i2) -> i2
    %23 = "comb.mux"(%15, %14, %22) : (i1, i2, i2) -> i2
    %24 = "comb.mux"(%15, %13, %41) : (i1, i5, i5) -> i5
    %25 = "comb.icmp"(%41, %5) <{predicate = 1 : i64}> : (i5, i5) -> i1
    %26 = "comb.and"(%25, %17, %20) : (i1, i1, i1) -> i1
    %27 = "comb.mux"(%26, %12, %23) : (i1, i2, i2) -> i2
    %28 = "comb.mux"(%26, %18, %24) : (i1, i5, i5) -> i5
    %29 = "comb.or"(%26, %15) : (i1, i1) -> i1
    %30 = "comb.xor"(%17, %0) : (i1, i1) -> i1
    %31 = "comb.icmp"(%37, %10) <{predicate = 11 : i64}> : (i2, i2) -> i1
    %32 = "comb.and"(%30, %20, %31) : (i1, i1, i1) -> i1
    %33 = "comb.xor"(%32, %0) : (i1, i1) -> i1
    %34 = "comb.and"(%33, %29) : (i1, i1) -> i1
    %35 = "seq.to_clock"(%arg0) : (i1) -> !seq.clock
    %36 = "comb.mux"(%32, %37, %27) <{twoState}> : (i1, i2, i2) -> i2
    %37 = "seq.firreg"(%36, %35) <{name = "mst_exec_state", preset = 0 : i2}> : (i2, !seq.clock) -> i2
    %38 = "comb.xor"(%34, %0) : (i1, i1) -> i1
    %39 = "comb.or"(%38, %32) : (i1, i1) -> i1
    %40 = "comb.mux"(%39, %41, %28) <{twoState}> : (i1, i5, i5) -> i5
    %41 = "seq.firreg"(%40, %35) <{name = "count", preset = 0 : i5}> : (i5, !seq.clock) -> i5
    %42 = "comb.icmp"(%37, %10) <{predicate = 0 : i64}> : (i2, i2) -> i1
    %43 = "comb.concat"(%7, %73) : (i28, i4) -> i32
    %44 = "comb.icmp"(%43, %9) <{predicate = 6 : i64}> : (i32, i32) -> i1
    %45 = "comb.and"(%42, %44) : (i1, i1) -> i1
    %46 = "comb.icmp"(%73, %3) <{predicate = 0 : i64}> : (i4, i4) -> i1
    %47 = "comb.xor"(%52, %0) : (i1, i1) -> i1
    %48 = "comb.or"(%47, %arg2) : (i1, i1) -> i1
    %49 = "comb.and"(%arg1, %45) : (i1, i1) -> i1
    %50 = "comb.and"(%arg1, %48, %46) : (i1, i1, i1) -> i1
    %51 = "comb.or"(%15, %48) : (i1, i1) -> i1
    %52 = "seq.firreg"(%49, %35) <{name = "axis_tvalid_delay"}> : (i1, !seq.clock) -> i1
    %53 = "comb.mux"(%51, %50, %54) <{twoState}> : (i1, i1, i1) -> i1
    %54 = "seq.firreg"(%53, %35) <{name = "axis_tlast_delay"}> : (i1, !seq.clock) -> i1
    %55 = "comb.icmp"(%73, %1) <{predicate = 0 : i64}> : (i4, i4) -> i1
    %56 = "comb.add"(%73, %2) : (i4, i4) -> i4
    %57 = "comb.mux"(%15, %8, %73) : (i1, i4, i4) -> i4
    %58 = "comb.and"(%44, %arg1) : (i1, i1) -> i1
    %59 = "comb.and"(%76, %58) : (i1, i1) -> i1
    %60 = "comb.mux"(%59, %56, %57) : (i1, i4, i4) -> i4
    %61 = "comb.or"(%59, %15) : (i1, i1) -> i1
    %62 = "comb.xor"(%59, %0) : (i1, i1) -> i1
    %63 = "comb.or"(%59, %15, %55) : (i1, i1, i1) -> i1
    %64 = "comb.xor"(%76, %0) : (i1, i1) -> i1
    %65 = "comb.and"(%58, %64) : (i1, i1) -> i1
    %66 = "comb.xor"(%65, %0) : (i1, i1) -> i1
    %67 = "comb.and"(%66, %61) : (i1, i1) -> i1
    %68 = "comb.and"(%66, %62, %arg1, %55) : (i1, i1, i1, i1) -> i1
    %69 = "comb.and"(%66, %63) : (i1, i1) -> i1
    %70 = "comb.xor"(%67, %0) : (i1, i1) -> i1
    %71 = "comb.or"(%70, %65) : (i1, i1) -> i1
    %72 = "comb.mux"(%71, %73, %60) <{twoState}> : (i1, i4, i4) -> i4
    %73 = "seq.firreg"(%72, %35) <{name = "read_pointer", preset = 0 : i4}> : (i4, !seq.clock) -> i4
    %74 = "comb.mux"(%69, %68, %75) <{twoState}> : (i1, i1, i1) -> i1
    %75 = "seq.firreg"(%74, %35) <{name = "tx_done"}> : (i1, !seq.clock) -> i1
    %76 = "comb.and"(%arg2, %45) : (i1, i1) -> i1
    %77 = "comb.add"(%43, %11) : (i32, i32) -> i32
    %78 = "comb.and"(%76, %arg1) : (i1, i1) -> i1
    %79 = "comb.mux"(%78, %77, %11) : (i1, i32, i32) -> i32
    %80 = "comb.and"(%arg1, %64) : (i1, i1) -> i1
    %81 = "comb.mux"(%80, %82, %79) <{twoState}> : (i1, i32, i32) -> i32
    %82 = "seq.firreg"(%81, %35) <{name = "stream_data_out"}> : (i32, !seq.clock) -> i32
    "hw.output"(%52, %82, %6, %54) : (i1, i32, i4, i1) -> ()
  }) : () -> ()
}) : () -> ()

