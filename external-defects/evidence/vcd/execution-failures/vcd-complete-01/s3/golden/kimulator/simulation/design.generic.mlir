#loc = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/s3/golden/kimulator/design.mlir":10:197)
#loc1 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/s3/golden/kimulator/design.mlir":10:301)
#loc2 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/s3/golden/kimulator/design.mlir":10:329)
#loc3 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/s3/golden/kimulator/design.mlir":10:357)
#loc4 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/s3/golden/kimulator/design.mlir":10:426)
#loc5 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/s3/golden/kimulator/design.mlir":10:454)
"builtin.module"() ({
  "hw.module"() <{module_type = !hw.modty<input clk : i1, input rst : i1, input input_axis_tdata : i64, input input_axis_tkeep : i8, input input_axis_tvalid : i1, output input_axis_tready : i1, input input_axis_tlast : i1, input input_axis_tuser : i1, output output_axis_tdata : i8, output output_axis_tkeep : i1, output output_axis_tvalid : i1, input output_axis_tready : i1, output output_axis_tlast : i1, output output_axis_tuser : i1>, parameters = [], result_locs = [#loc, #loc1, #loc2, #loc3, #loc4, #loc5], sym_name = "axis_adapter"}> ({
  ^bb0(%arg0: i1, %arg1: i1, %arg2: i64, %arg3: i8, %arg4: i1, %arg5: i1, %arg6: i1, %arg7: i1):
    %0 = "hw.constant"() <{value = 0 : i7}> : () -> i7
    %1 = "hw.constant"() <{value = 0 : i56}> : () -> i56
    %2 = "hw.constant"() <{value = -1 : i64}> : () -> i64
    %3 = "hw.constant"() <{value = 255 : i64}> : () -> i64
    %4 = "hw.constant"() <{value = 0 : i58}> : () -> i58
    %5 = "hw.constant"() <{value = true}> : () -> i1
    %6 = "hw.constant"() <{value = 0 : i53}> : () -> i53
    %7 = "hw.constant"() <{value = 7 : i8}> : () -> i8
    %8 = "hw.constant"() <{value = 0 : i5}> : () -> i5
    %9 = "hw.constant"() <{value = -1 : i8}> : () -> i8
    %10 = "hw.constant"() <{value = -1 : i3}> : () -> i3
    %11 = "hw.constant"() <{value = -1 : i6}> : () -> i6
    %12 = "hw.constant"() <{value = 0 : i24}> : () -> i24
    %13 = "hw.constant"() <{value = false}> : () -> i1
    %14 = "hw.constant"() <{value = 1 : i3}> : () -> i3
    %15 = "hw.constant"() <{value = 2 : i3}> : () -> i3
    %16 = "hw.constant"() <{value = 1 : i8}> : () -> i8
    %17 = "hw.constant"() <{value = 1 : i32}> : () -> i32
    %18 = "hw.constant"() <{value = 0 : i64}> : () -> i64
    %19 = "hw.constant"() <{value = 0 : i8}> : () -> i8
    %20 = "hw.constant"() <{value = 0 : i3}> : () -> i3
    %21 = "comb.icmp"(%166, %20) <{predicate = 10 : i64}> : (i3, i3) -> i1
    %22 = "comb.and"(%172, %arg4) : (i1, i1) -> i1
    %23 = "comb.extract"(%arg3) <{lowBit = 0 : i32}> : (i8) -> i1
    %24 = "comb.xor"(%23, %5) : (i1, i1) -> i1
    %25 = "comb.extract"(%arg3) <{lowBit = 1 : i32}> : (i8) -> i1
    %26 = "comb.xor"(%25, %5) : (i1, i1) -> i1
    %27 = "comb.or"(%24, %26) : (i1, i1) -> i1
    %28 = "comb.extract"(%arg2) <{lowBit = 0 : i32}> : (i64) -> i8
    %29 = "comb.and"(%arg5, %27) : (i1, i1) -> i1
    %30 = "comb.and"(%arg6, %27) : (i1, i1) -> i1
    %31 = "comb.concat"(%0, %239) : (i7, i1) -> i8
    %32 = "comb.xor"(%27, %5) : (i1, i1) -> i1
    %33 = "comb.xor"(%239, %5) : (i1, i1) -> i1
    %34 = "comb.or"(%32, %33) : (i1, i1) -> i1
    %35 = "comb.icmp"(%166, %14) <{predicate = 10 : i64}> : (i3, i3) -> i1
    %36 = "comb.extract"(%167) <{lowBit = 3 : i32}> : (i8) -> i5
    %37 = "comb.icmp"(%36, %8) <{predicate = 0 : i64}> : (i5, i5) -> i1
    %38 = "comb.extract"(%167) <{lowBit = 0 : i32}> : (i8) -> i3
    %39 = "comb.concat"(%38, %20) : (i3, i3) -> i6
    %40 = "comb.mux"(%37, %39, %11) : (i1, i6, i6) -> i6
    %41 = "comb.concat"(%4, %40) : (i58, i6) -> i64
    %42 = "comb.shl"(%3, %41) : (i64, i64) -> i64
    %43 = "comb.xor"(%42, %2) <{twoState}> : (i64, i64) -> i64
    %44 = "comb.and"(%168, %43) : (i64, i64) -> i64
    %45 = "comb.concat"(%1, %28) : (i56, i8) -> i64
    %46 = "comb.shl"(%45, %41) : (i64, i64) -> i64
    %47 = "comb.or"(%44, %46) : (i64, i64) -> i64
    %48 = "comb.mux"(%37, %38, %10) : (i1, i3, i3) -> i3
    %49 = "comb.concat"(%8, %48) : (i5, i3) -> i8
    %50 = "comb.shl"(%16, %49) : (i8, i8) -> i8
    %51 = "comb.xor"(%50, %9) <{twoState}> : (i8, i8) -> i8
    %52 = "comb.and"(%169, %51) : (i8, i8) -> i8
    %53 = "comb.concat"(%0, %23) : (i7, i1) -> i8
    %54 = "comb.shl"(%53, %49) : (i8, i8) -> i8
    %55 = "comb.or"(%52, %54) : (i8, i8) -> i8
    %56 = "comb.add"(%167, %16) : (i8, i8) -> i8
    %57 = "comb.icmp"(%167, %7) <{predicate = 0 : i64}> : (i8, i8) -> i1
    %58 = "comb.or"(%57, %arg5) : (i1, i1) -> i1
    %59 = "comb.icmp"(%166, %15) <{predicate = 10 : i64}> : (i3, i3) -> i1
    %60 = "comb.shru"(%169, %167) : (i8, i8) -> i8
    %61 = "comb.extract"(%60) <{lowBit = 0 : i32}> : (i8) -> i1
    %62 = "comb.xor"(%61, %5) : (i1, i1) -> i1
    %63 = "comb.concat"(%12, %167) : (i24, i8) -> i32
    %64 = "comb.add"(%63, %17) : (i32, i32) -> i32
    %65 = "comb.extract"(%64) <{lowBit = 8 : i32}> : (i32) -> i24
    %66 = "comb.icmp"(%65, %12) <{predicate = 0 : i64}> : (i24, i24) -> i1
    %67 = "comb.extract"(%64) <{lowBit = 0 : i32}> : (i32) -> i8
    %68 = "comb.mux"(%66, %67, %9) : (i1, i8, i8) -> i8
    %69 = "comb.shru"(%169, %68) : (i8, i8) -> i8
    %70 = "comb.extract"(%69) <{lowBit = 0 : i32}> : (i8) -> i1
    %71 = "comb.xor"(%70, %5) : (i1, i1) -> i1
    %72 = "comb.xor"(%57, %5) : (i1, i1) -> i1
    %73 = "comb.and"(%72, %62) : (i1, i1) -> i1
    %74 = "comb.or"(%57, %73, %71) : (i1, i1, i1) -> i1
    %75 = "comb.concat"(%6, %167, %20) : (i53, i8, i3) -> i64
    %76 = "comb.shru"(%168, %75) : (i64, i64) -> i64
    %77 = "comb.extract"(%76) <{lowBit = 0 : i32}> : (i64) -> i8
    %78 = "comb.xor"(%74, %5) : (i1, i1) -> i1
    %79 = "comb.concat"(%13, %78, %13) : (i1, i1, i1) -> i3
    %80 = "comb.xor"(%21, %5) : (i1, i1) -> i1
    %81 = "comb.xor"(%35, %5) : (i1, i1) -> i1
    %82 = "comb.and"(%81, %80) : (i1, i1) -> i1
    %83 = "comb.and"(%59, %82) : (i1, i1) -> i1
    %84 = "comb.and"(%72, %83) : (i1, i1) -> i1
    %85 = "comb.and"(%61, %84) : (i1, i1) -> i1
    %86 = "comb.and"(%62, %84) : (i1, i1) -> i1
    %87 = "comb.and"(%57, %83) : (i1, i1) -> i1
    %88 = "comb.or"(%85, %86, %87) : (i1, i1, i1) -> i1
    %89 = "comb.and"(%88, %33) : (i1, i1) -> i1
    %90 = "comb.mux"(%89, %15, %79) : (i1, i3, i3) -> i3
    %91 = "comb.xor"(%89, %5) : (i1, i1) -> i1
    %92 = "comb.and"(%91, %74) : (i1, i1) -> i1
    %93 = "comb.mux"(%58, %15, %14) : (i1, i3, i3) -> i3
    %94 = "comb.xor"(%58, %5) : (i1, i1) -> i1
    %95 = "comb.or"(%94, %178) : (i1, i1) -> i1
    %96 = "comb.and"(%35, %80) : (i1, i1) -> i1
    %97 = "comb.and"(%22, %96) : (i1, i1) -> i1
    %98 = "comb.mux"(%97, %93, %90) : (i1, i3, i3) -> i3
    %99 = "comb.or"(%97, %91) : (i1, i1) -> i1
    %100 = "comb.xor"(%97, %5) : (i1, i1) -> i1
    %101 = "comb.mux"(%97, %95, %92) : (i1, i1, i1) -> i1
    %102 = "comb.xor"(%22, %5) : (i1, i1) -> i1
    %103 = "comb.and"(%96, %102) : (i1, i1) -> i1
    %104 = "comb.mux"(%103, %14, %98) : (i1, i3, i3) -> i3
    %105 = "comb.xor"(%99, %5) : (i1, i1) -> i1
    %106 = "comb.or"(%103, %105) : (i1, i1) -> i1
    %107 = "comb.mux"(%106, %167, %56) : (i1, i8, i8) -> i8
    %108 = "comb.or"(%103, %100) : (i1, i1) -> i1
    %109 = "comb.mux"(%108, %168, %47) : (i1, i64, i64) -> i64
    %110 = "comb.mux"(%108, %169, %55) : (i1, i8, i8) -> i8
    %111 = "comb.or"(%103, %97) : (i1, i1) -> i1
    %112 = "comb.mux"(%111, %19, %77) : (i1, i8, i8) -> i8
    %113 = "comb.xor"(%103, %5) : (i1, i1) -> i1
    %114 = "comb.and"(%113, %100, %61) : (i1, i1, i1) -> i1
    %115 = "comb.and"(%113, %100) : (i1, i1) -> i1
    %116 = "comb.and"(%113, %100, %170, %74) : (i1, i1, i1, i1) -> i1
    %117 = "comb.and"(%113, %100, %171, %74) : (i1, i1, i1, i1) -> i1
    %118 = "comb.or"(%103, %101) : (i1, i1) -> i1
    %119 = "comb.concat"(%13, %34, %13) : (i1, i1, i1) -> i3
    %120 = "comb.xor"(%34, %5) : (i1, i1) -> i1
    %121 = "comb.and"(%22, %21) : (i1, i1) -> i1
    %122 = "comb.and"(%23, %121) : (i1, i1) -> i1
    %123 = "comb.and"(%24, %121) : (i1, i1) -> i1
    %124 = "comb.or"(%122, %123) : (i1, i1) -> i1
    %125 = "comb.mux"(%124, %119, %104) : (i1, i3, i3) -> i3
    %126 = "comb.mux"(%124, %31, %107) : (i1, i8, i8) -> i8
    %127 = "comb.mux"(%124, %arg2, %109) : (i1, i64, i64) -> i64
    %128 = "comb.mux"(%124, %arg3, %110) : (i1, i8, i8) -> i8
    %129 = "comb.xor"(%108, %5) : (i1, i1) -> i1
    %130 = "comb.or"(%124, %129) : (i1, i1) -> i1
    %131 = "comb.mux"(%124, %28, %112) : (i1, i8, i8) -> i8
    %132 = "comb.mux"(%124, %23, %114) : (i1, i1, i1) -> i1
    %133 = "comb.or"(%124, %115) : (i1, i1) -> i1
    %134 = "comb.mux"(%124, %29, %116) : (i1, i1, i1) -> i1
    %135 = "comb.mux"(%124, %30, %117) : (i1, i1, i1) -> i1
    %136 = "comb.mux"(%124, %120, %118) : (i1, i1, i1) -> i1
    %137 = "comb.and"(%21, %102) : (i1, i1) -> i1
    %138 = "comb.xor"(%130, %5) : (i1, i1) -> i1
    %139 = "comb.xor"(%137, %5) : (i1, i1) -> i1
    %140 = "comb.or"(%137, %136) : (i1, i1) -> i1
    %141 = "comb.xor"(%59, %5) : (i1, i1) -> i1
    %142 = "comb.and"(%82, %141) : (i1, i1) -> i1
    %143 = "comb.or"(%142, %137) : (i1, i1) -> i1
    %144 = "comb.mux"(%143, %167, %126) : (i1, i8, i8) -> i8
    %145 = "comb.mux"(%143, %168, %127) : (i1, i64, i64) -> i64
    %146 = "comb.mux"(%143, %169, %128) : (i1, i8, i8) -> i8
    %147 = "comb.or"(%142, %137, %138) : (i1, i1, i1) -> i1
    %148 = "comb.mux"(%147, %170, %arg5) : (i1, i1, i1) -> i1
    %149 = "comb.mux"(%147, %171, %arg6) : (i1, i1, i1) -> i1
    %150 = "comb.mux"(%143, %19, %131) : (i1, i8, i8) -> i8
    %151 = "comb.xor"(%142, %5) : (i1, i1) -> i1
    %152 = "comb.and"(%151, %139, %132) : (i1, i1, i1) -> i1
    %153 = "comb.and"(%151, %139, %133) : (i1, i1, i1) -> i1
    %154 = "comb.and"(%151, %139, %134) : (i1, i1, i1) -> i1
    %155 = "comb.and"(%151, %139, %135) : (i1, i1, i1) -> i1
    %156 = "comb.or"(%arg1, %143) : (i1, i1) -> i1
    %157 = "comb.mux"(%156, %20, %125) : (i1, i3, i3) -> i3
    %158 = "comb.mux"(%arg1, %19, %144) : (i1, i8, i8) -> i8
    %159 = "comb.mux"(%arg1, %18, %145) : (i1, i64, i64) -> i64
    %160 = "comb.mux"(%arg1, %19, %146) : (i1, i8, i8) -> i8
    %161 = "comb.xor"(%arg1, %5) : (i1, i1) -> i1
    %162 = "comb.and"(%161, %148) : (i1, i1) -> i1
    %163 = "comb.and"(%161, %149) : (i1, i1) -> i1
    %164 = "comb.and"(%161, %151, %140) : (i1, i1, i1) -> i1
    %165 = "seq.to_clock"(%arg0) : (i1) -> !seq.clock
    %166 = "seq.firreg"(%157, %165) <{name = "state_reg"}> : (i3, !seq.clock) -> i3
    %167 = "seq.firreg"(%158, %165) <{name = "cycle_count_reg"}> : (i8, !seq.clock) -> i8
    %168 = "seq.firreg"(%159, %165) <{name = "temp_tdata_reg"}> : (i64, !seq.clock) -> i64
    %169 = "seq.firreg"(%160, %165) <{name = "temp_tkeep_reg"}> : (i8, !seq.clock) -> i8
    %170 = "seq.firreg"(%162, %165) <{name = "temp_tlast_reg"}> : (i1, !seq.clock) -> i1
    %171 = "seq.firreg"(%163, %165) <{name = "temp_tuser_reg"}> : (i1, !seq.clock) -> i1
    %172 = "seq.firreg"(%164, %165) <{name = "input_axis_tready_reg"}> : (i1, !seq.clock) -> i1
    %173 = "comb.xor"(%245, %5) : (i1, i1) -> i1
    %174 = "comb.xor"(%234, %5) : (i1, i1) -> i1
    %175 = "comb.and"(%173, %174) : (i1, i1) -> i1
    %176 = "comb.xor"(%153, %5) : (i1, i1) -> i1
    %177 = "comb.and"(%173, %176) : (i1, i1) -> i1
    %178 = "comb.or"(%arg7, %175, %177) : (i1, i1, i1) -> i1
    %179 = "comb.or"(%arg7, %174) : (i1, i1) -> i1
    %180 = "comb.mux"(%arg7, %241, %19) : (i1, i8, i8) -> i8
    %181 = "comb.and"(%arg7, %243) : (i1, i1) -> i1
    %182 = "comb.mux"(%arg7, %245, %234) : (i1, i1, i1) -> i1
    %183 = "comb.and"(%arg7, %247) : (i1, i1) -> i1
    %184 = "comb.and"(%arg7, %249) : (i1, i1) -> i1
    %185 = "comb.mux"(%arg7, %19, %241) : (i1, i8, i8) -> i8
    %186 = "comb.xor"(%arg7, %5) : (i1, i1) -> i1
    %187 = "comb.and"(%186, %243) : (i1, i1) -> i1
    %188 = "comb.and"(%186, %245) : (i1, i1) -> i1
    %189 = "comb.and"(%186, %247) : (i1, i1) -> i1
    %190 = "comb.and"(%186, %249) : (i1, i1) -> i1
    %191 = "comb.xor"(%179, %5) : (i1, i1) -> i1
    %192 = "comb.or"(%191, %143) : (i1, i1) -> i1
    %193 = "comb.mux"(%192, %19, %131) : (i1, i8, i8) -> i8
    %194 = "comb.and"(%179, %152) : (i1, i1) -> i1
    %195 = "comb.mux"(%179, %153, %234) : (i1, i1, i1) -> i1
    %196 = "comb.and"(%179, %154) : (i1, i1) -> i1
    %197 = "comb.and"(%179, %155) : (i1, i1) -> i1
    %198 = "comb.mux"(%179, %241, %150) : (i1, i8, i8) -> i8
    %199 = "comb.mux"(%179, %243, %152) : (i1, i1, i1) -> i1
    %200 = "comb.mux"(%179, %245, %153) : (i1, i1, i1) -> i1
    %201 = "comb.mux"(%179, %247, %154) : (i1, i1, i1) -> i1
    %202 = "comb.mux"(%179, %249, %155) : (i1, i1, i1) -> i1
    %203 = "comb.and"(%239, %161) : (i1, i1) -> i1
    %204 = "comb.mux"(%203, %193, %180) : (i1, i8, i8) -> i8
    %205 = "comb.and"(%203, %174) : (i1, i1) -> i1
    %206 = "comb.mux"(%203, %194, %181) : (i1, i1, i1) -> i1
    %207 = "comb.mux"(%203, %195, %182) : (i1, i1, i1) -> i1
    %208 = "comb.mux"(%203, %196, %183) : (i1, i1, i1) -> i1
    %209 = "comb.mux"(%203, %197, %184) : (i1, i1, i1) -> i1
    %210 = "comb.mux"(%203, %198, %185) : (i1, i8, i8) -> i8
    %211 = "comb.mux"(%203, %191, %arg7) : (i1, i1, i1) -> i1
    %212 = "comb.mux"(%203, %199, %187) : (i1, i1, i1) -> i1
    %213 = "comb.mux"(%203, %200, %188) : (i1, i1, i1) -> i1
    %214 = "comb.mux"(%203, %201, %189) : (i1, i1, i1) -> i1
    %215 = "comb.mux"(%203, %202, %190) : (i1, i1, i1) -> i1
    %216 = "comb.mux"(%arg1, %19, %204) : (i1, i8, i8) -> i8
    %217 = "comb.or"(%arg1, %205, %arg7) : (i1, i1, i1) -> i1
    %218 = "comb.and"(%161, %206) : (i1, i1) -> i1
    %219 = "comb.and"(%161, %207) : (i1, i1) -> i1
    %220 = "comb.and"(%161, %208) : (i1, i1) -> i1
    %221 = "comb.and"(%161, %209) : (i1, i1) -> i1
    %222 = "comb.and"(%161, %178) : (i1, i1) -> i1
    %223 = "comb.mux"(%arg1, %19, %210) : (i1, i8, i8) -> i8
    %224 = "comb.or"(%arg1, %211) : (i1, i1) -> i1
    %225 = "comb.and"(%161, %212) : (i1, i1) -> i1
    %226 = "comb.and"(%161, %213) : (i1, i1) -> i1
    %227 = "comb.and"(%161, %214) : (i1, i1) -> i1
    %228 = "comb.and"(%161, %215) : (i1, i1) -> i1
    %229 = "comb.mux"(%217, %216, %230) <{twoState}> : (i1, i8, i8) -> i8
    %230 = "seq.firreg"(%229, %165) <{name = "output_axis_tdata_reg"}> : (i8, !seq.clock) -> i8
    %231 = "comb.mux"(%217, %218, %232) <{twoState}> : (i1, i1, i1) -> i1
    %232 = "seq.firreg"(%231, %165) <{name = "output_axis_tkeep_reg"}> : (i1, !seq.clock) -> i1
    %233 = "comb.mux"(%217, %219, %234) <{twoState}> : (i1, i1, i1) -> i1
    %234 = "seq.firreg"(%233, %165) <{name = "output_axis_tvalid_reg"}> : (i1, !seq.clock) -> i1
    %235 = "comb.mux"(%217, %220, %236) <{twoState}> : (i1, i1, i1) -> i1
    %236 = "seq.firreg"(%235, %165) <{name = "output_axis_tlast_reg"}> : (i1, !seq.clock) -> i1
    %237 = "comb.mux"(%217, %221, %238) <{twoState}> : (i1, i1, i1) -> i1
    %238 = "seq.firreg"(%237, %165) <{name = "output_axis_tuser_reg"}> : (i1, !seq.clock) -> i1
    %239 = "seq.firreg"(%222, %165) <{name = "output_axis_tready_int"}> : (i1, !seq.clock) -> i1
    %240 = "comb.mux"(%224, %223, %241) <{twoState}> : (i1, i8, i8) -> i8
    %241 = "seq.firreg"(%240, %165) <{name = "temp_axis_tdata_reg"}> : (i8, !seq.clock) -> i8
    %242 = "comb.mux"(%224, %225, %243) <{twoState}> : (i1, i1, i1) -> i1
    %243 = "seq.firreg"(%242, %165) <{name = "temp_axis_tkeep_reg"}> : (i1, !seq.clock) -> i1
    %244 = "comb.mux"(%224, %226, %245) <{twoState}> : (i1, i1, i1) -> i1
    %245 = "seq.firreg"(%244, %165) <{name = "temp_axis_tvalid_reg"}> : (i1, !seq.clock) -> i1
    %246 = "comb.mux"(%224, %227, %247) <{twoState}> : (i1, i1, i1) -> i1
    %247 = "seq.firreg"(%246, %165) <{name = "temp_axis_tlast_reg"}> : (i1, !seq.clock) -> i1
    %248 = "comb.mux"(%224, %228, %249) <{twoState}> : (i1, i1, i1) -> i1
    %249 = "seq.firreg"(%248, %165) <{name = "temp_axis_tuser_reg"}> : (i1, !seq.clock) -> i1
    "hw.output"(%172, %230, %232, %234, %236, %238) : (i1, i8, i1, i1, i1, i1) -> ()
  }) : () -> ()
}) : () -> ()

