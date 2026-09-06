#loc = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/s3/buggy/kimulator/design.mlir":10:197)
#loc1 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/s3/buggy/kimulator/design.mlir":10:301)
#loc2 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/s3/buggy/kimulator/design.mlir":10:329)
#loc3 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/s3/buggy/kimulator/design.mlir":10:357)
#loc4 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/s3/buggy/kimulator/design.mlir":10:426)
#loc5 = loc("/Users/bytedance/cym/cymProject/k-circt-top-repo/services/circt-semantics/benchmarks/external-defects/results/batch-final-01/s3/buggy/kimulator/design.mlir":10:454)
"builtin.module"() ({
  "hw.module"() <{module_type = !hw.modty<input clk : i1, input rst : i1, input input_axis_tdata : i64, input input_axis_tkeep : i8, input input_axis_tvalid : i1, output input_axis_tready : i1, input input_axis_tlast : i1, input input_axis_tuser : i1, output output_axis_tdata : i8, output output_axis_tkeep : i1, output output_axis_tvalid : i1, input output_axis_tready : i1, output output_axis_tlast : i1, output output_axis_tuser : i1>, parameters = [], result_locs = [#loc, #loc1, #loc2, #loc3, #loc4, #loc5], sym_name = "axis_adapter"}> ({
  ^bb0(%arg0: i1, %arg1: i1, %arg2: i64, %arg3: i8, %arg4: i1, %arg5: i1, %arg6: i1, %arg7: i1):
    %0 = "hw.constant"() <{value = 0 : i7}> : () -> i7
    %1 = "hw.constant"() <{value = -1 : i8}> : () -> i8
    %2 = "hw.constant"() <{value = 0 : i56}> : () -> i56
    %3 = "hw.constant"() <{value = -1 : i64}> : () -> i64
    %4 = "hw.constant"() <{value = 255 : i64}> : () -> i64
    %5 = "hw.constant"() <{value = 0 : i58}> : () -> i58
    %6 = "hw.constant"() <{value = true}> : () -> i1
    %7 = "hw.constant"() <{value = 0 : i53}> : () -> i53
    %8 = "hw.constant"() <{value = 7 : i8}> : () -> i8
    %9 = "hw.constant"() <{value = 0 : i5}> : () -> i5
    %10 = "hw.constant"() <{value = -1 : i3}> : () -> i3
    %11 = "hw.constant"() <{value = -1 : i6}> : () -> i6
    %12 = "hw.constant"() <{value = false}> : () -> i1
    %13 = "hw.constant"() <{value = 1 : i3}> : () -> i3
    %14 = "hw.constant"() <{value = 2 : i3}> : () -> i3
    %15 = "hw.constant"() <{value = 1 : i8}> : () -> i8
    %16 = "hw.constant"() <{value = 0 : i64}> : () -> i64
    %17 = "hw.constant"() <{value = 0 : i8}> : () -> i8
    %18 = "hw.constant"() <{value = 0 : i3}> : () -> i3
    %19 = "comb.icmp"(%137, %18) <{predicate = 10 : i64}> : (i3, i3) -> i1
    %20 = "comb.extract"(%arg2) <{lowBit = 0 : i32}> : (i64) -> i8
    %21 = "comb.extract"(%arg3) <{lowBit = 0 : i32}> : (i8) -> i1
    %22 = "comb.xor"(%21, %6) : (i1, i1) -> i1
    %23 = "comb.and"(%arg5, %22) : (i1, i1) -> i1
    %24 = "comb.and"(%arg6, %22) : (i1, i1) -> i1
    %25 = "comb.icmp"(%137, %13) <{predicate = 10 : i64}> : (i3, i3) -> i1
    %26 = "comb.extract"(%138) <{lowBit = 3 : i32}> : (i8) -> i5
    %27 = "comb.icmp"(%26, %9) <{predicate = 0 : i64}> : (i5, i5) -> i1
    %28 = "comb.extract"(%138) <{lowBit = 0 : i32}> : (i8) -> i3
    %29 = "comb.concat"(%28, %18) : (i3, i3) -> i6
    %30 = "comb.mux"(%27, %29, %11) : (i1, i6, i6) -> i6
    %31 = "comb.concat"(%5, %30) : (i58, i6) -> i64
    %32 = "comb.shl"(%4, %31) : (i64, i64) -> i64
    %33 = "comb.xor"(%32, %3) <{twoState}> : (i64, i64) -> i64
    %34 = "comb.and"(%139, %33) : (i64, i64) -> i64
    %35 = "comb.concat"(%2, %20) : (i56, i8) -> i64
    %36 = "comb.shl"(%35, %31) : (i64, i64) -> i64
    %37 = "comb.or"(%34, %36) : (i64, i64) -> i64
    %38 = "comb.mux"(%27, %28, %10) : (i1, i3, i3) -> i3
    %39 = "comb.concat"(%9, %38) : (i5, i3) -> i8
    %40 = "comb.shl"(%15, %39) : (i8, i8) -> i8
    %41 = "comb.xor"(%40, %1) <{twoState}> : (i8, i8) -> i8
    %42 = "comb.and"(%140, %41) : (i8, i8) -> i8
    %43 = "comb.concat"(%0, %21) : (i7, i1) -> i8
    %44 = "comb.shl"(%43, %39) : (i8, i8) -> i8
    %45 = "comb.or"(%42, %44) : (i8, i8) -> i8
    %46 = "comb.add"(%138, %15) : (i8, i8) -> i8
    %47 = "comb.icmp"(%138, %8) <{predicate = 0 : i64}> : (i8, i8) -> i1
    %48 = "comb.or"(%47, %arg5) : (i1, i1) -> i1
    %49 = "comb.icmp"(%137, %14) <{predicate = 10 : i64}> : (i3, i3) -> i1
    %50 = "comb.concat"(%7, %138, %18) : (i53, i8, i3) -> i64
    %51 = "comb.shru"(%139, %50) : (i64, i64) -> i64
    %52 = "comb.extract"(%51) <{lowBit = 0 : i32}> : (i64) -> i8
    %53 = "comb.shru"(%140, %138) : (i8, i8) -> i8
    %54 = "comb.extract"(%53) <{lowBit = 0 : i32}> : (i8) -> i1
    %55 = "comb.xor"(%54, %6) : (i1, i1) -> i1
    %56 = "comb.or"(%47, %55) : (i1, i1) -> i1
    %57 = "comb.xor"(%56, %6) : (i1, i1) -> i1
    %58 = "comb.concat"(%12, %57, %12) : (i1, i1, i1) -> i3
    %59 = "comb.xor"(%19, %6) : (i1, i1) -> i1
    %60 = "comb.xor"(%25, %6) : (i1, i1) -> i1
    %61 = "comb.and"(%60, %59) : (i1, i1) -> i1
    %62 = "comb.xor"(%210, %6) : (i1, i1) -> i1
    %63 = "comb.and"(%49, %61, %62) : (i1, i1, i1) -> i1
    %64 = "comb.mux"(%63, %14, %58) : (i1, i3, i3) -> i3
    %65 = "comb.xor"(%63, %6) : (i1, i1) -> i1
    %66 = "comb.and"(%65, %56) : (i1, i1) -> i1
    %67 = "comb.mux"(%48, %14, %13) : (i1, i3, i3) -> i3
    %68 = "comb.xor"(%48, %6) : (i1, i1) -> i1
    %69 = "comb.or"(%68, %149) : (i1, i1) -> i1
    %70 = "comb.and"(%25, %59) : (i1, i1) -> i1
    %71 = "comb.and"(%arg4, %70) : (i1, i1) -> i1
    %72 = "comb.mux"(%71, %67, %64) : (i1, i3, i3) -> i3
    %73 = "comb.or"(%71, %65) : (i1, i1) -> i1
    %74 = "comb.xor"(%71, %6) : (i1, i1) -> i1
    %75 = "comb.mux"(%71, %69, %66) : (i1, i1, i1) -> i1
    %76 = "comb.xor"(%arg4, %6) : (i1, i1) -> i1
    %77 = "comb.and"(%70, %76) : (i1, i1) -> i1
    %78 = "comb.mux"(%77, %13, %72) : (i1, i3, i3) -> i3
    %79 = "comb.xor"(%73, %6) : (i1, i1) -> i1
    %80 = "comb.or"(%77, %79) : (i1, i1) -> i1
    %81 = "comb.mux"(%80, %138, %46) : (i1, i8, i8) -> i8
    %82 = "comb.or"(%77, %74) : (i1, i1) -> i1
    %83 = "comb.mux"(%82, %139, %37) : (i1, i64, i64) -> i64
    %84 = "comb.mux"(%82, %140, %45) : (i1, i8, i8) -> i8
    %85 = "comb.or"(%77, %71) : (i1, i1) -> i1
    %86 = "comb.mux"(%85, %17, %52) : (i1, i8, i8) -> i8
    %87 = "comb.xor"(%77, %6) : (i1, i1) -> i1
    %88 = "comb.and"(%87, %74, %54) : (i1, i1, i1) -> i1
    %89 = "comb.and"(%87, %74) : (i1, i1) -> i1
    %90 = "comb.and"(%87, %74, %141, %56) : (i1, i1, i1, i1) -> i1
    %91 = "comb.and"(%87, %74, %142, %56) : (i1, i1, i1, i1) -> i1
    %92 = "comb.or"(%77, %75) : (i1, i1) -> i1
    %93 = "comb.concat"(%0, %210) : (i7, i1) -> i8
    %94 = "comb.and"(%arg4, %19) : (i1, i1) -> i1
    %95 = "comb.mux"(%94, %14, %78) : (i1, i3, i3) -> i3
    %96 = "comb.mux"(%94, %93, %81) : (i1, i8, i8) -> i8
    %97 = "comb.mux"(%94, %arg2, %83) : (i1, i64, i64) -> i64
    %98 = "comb.mux"(%94, %arg3, %84) : (i1, i8, i8) -> i8
    %99 = "comb.xor"(%82, %6) : (i1, i1) -> i1
    %100 = "comb.or"(%94, %99) : (i1, i1) -> i1
    %101 = "comb.mux"(%94, %20, %86) : (i1, i8, i8) -> i8
    %102 = "comb.mux"(%94, %21, %88) : (i1, i1, i1) -> i1
    %103 = "comb.or"(%94, %89) : (i1, i1) -> i1
    %104 = "comb.mux"(%94, %23, %90) : (i1, i1, i1) -> i1
    %105 = "comb.mux"(%94, %24, %91) : (i1, i1, i1) -> i1
    %106 = "comb.xor"(%94, %6) : (i1, i1) -> i1
    %107 = "comb.and"(%106, %92) : (i1, i1) -> i1
    %108 = "comb.and"(%19, %76) : (i1, i1) -> i1
    %109 = "comb.xor"(%100, %6) : (i1, i1) -> i1
    %110 = "comb.xor"(%108, %6) : (i1, i1) -> i1
    %111 = "comb.or"(%108, %107) : (i1, i1) -> i1
    %112 = "comb.xor"(%49, %6) : (i1, i1) -> i1
    %113 = "comb.and"(%61, %112) : (i1, i1) -> i1
    %114 = "comb.or"(%113, %108) : (i1, i1) -> i1
    %115 = "comb.mux"(%114, %138, %96) : (i1, i8, i8) -> i8
    %116 = "comb.mux"(%114, %139, %97) : (i1, i64, i64) -> i64
    %117 = "comb.mux"(%114, %140, %98) : (i1, i8, i8) -> i8
    %118 = "comb.or"(%113, %108, %109) : (i1, i1, i1) -> i1
    %119 = "comb.mux"(%118, %141, %arg5) : (i1, i1, i1) -> i1
    %120 = "comb.mux"(%118, %142, %arg6) : (i1, i1, i1) -> i1
    %121 = "comb.mux"(%114, %17, %101) : (i1, i8, i8) -> i8
    %122 = "comb.xor"(%113, %6) : (i1, i1) -> i1
    %123 = "comb.and"(%122, %110, %102) : (i1, i1, i1) -> i1
    %124 = "comb.and"(%122, %110, %103) : (i1, i1, i1) -> i1
    %125 = "comb.and"(%122, %110, %104) : (i1, i1, i1) -> i1
    %126 = "comb.and"(%122, %110, %105) : (i1, i1, i1) -> i1
    %127 = "comb.or"(%arg1, %114) : (i1, i1) -> i1
    %128 = "comb.mux"(%127, %18, %95) : (i1, i3, i3) -> i3
    %129 = "comb.mux"(%arg1, %17, %115) : (i1, i8, i8) -> i8
    %130 = "comb.mux"(%arg1, %16, %116) : (i1, i64, i64) -> i64
    %131 = "comb.mux"(%arg1, %17, %117) : (i1, i8, i8) -> i8
    %132 = "comb.xor"(%arg1, %6) : (i1, i1) -> i1
    %133 = "comb.and"(%132, %119) : (i1, i1) -> i1
    %134 = "comb.and"(%132, %120) : (i1, i1) -> i1
    %135 = "comb.and"(%132, %122, %111) : (i1, i1, i1) -> i1
    %136 = "seq.to_clock"(%arg0) : (i1) -> !seq.clock
    %137 = "seq.firreg"(%128, %136) <{name = "state_reg"}> : (i3, !seq.clock) -> i3
    %138 = "seq.firreg"(%129, %136) <{name = "cycle_count_reg"}> : (i8, !seq.clock) -> i8
    %139 = "seq.firreg"(%130, %136) <{name = "temp_tdata_reg"}> : (i64, !seq.clock) -> i64
    %140 = "seq.firreg"(%131, %136) <{name = "temp_tkeep_reg"}> : (i8, !seq.clock) -> i8
    %141 = "seq.firreg"(%133, %136) <{name = "temp_tlast_reg"}> : (i1, !seq.clock) -> i1
    %142 = "seq.firreg"(%134, %136) <{name = "temp_tuser_reg"}> : (i1, !seq.clock) -> i1
    %143 = "seq.firreg"(%135, %136) <{name = "input_axis_tready_reg"}> : (i1, !seq.clock) -> i1
    %144 = "comb.xor"(%216, %6) : (i1, i1) -> i1
    %145 = "comb.xor"(%205, %6) : (i1, i1) -> i1
    %146 = "comb.and"(%144, %145) : (i1, i1) -> i1
    %147 = "comb.xor"(%124, %6) : (i1, i1) -> i1
    %148 = "comb.and"(%144, %147) : (i1, i1) -> i1
    %149 = "comb.or"(%arg7, %146, %148) : (i1, i1, i1) -> i1
    %150 = "comb.or"(%arg7, %145) : (i1, i1) -> i1
    %151 = "comb.mux"(%arg7, %212, %17) : (i1, i8, i8) -> i8
    %152 = "comb.and"(%arg7, %214) : (i1, i1) -> i1
    %153 = "comb.mux"(%arg7, %216, %205) : (i1, i1, i1) -> i1
    %154 = "comb.and"(%arg7, %218) : (i1, i1) -> i1
    %155 = "comb.and"(%arg7, %220) : (i1, i1) -> i1
    %156 = "comb.mux"(%arg7, %17, %212) : (i1, i8, i8) -> i8
    %157 = "comb.xor"(%arg7, %6) : (i1, i1) -> i1
    %158 = "comb.and"(%157, %214) : (i1, i1) -> i1
    %159 = "comb.and"(%157, %216) : (i1, i1) -> i1
    %160 = "comb.and"(%157, %218) : (i1, i1) -> i1
    %161 = "comb.and"(%157, %220) : (i1, i1) -> i1
    %162 = "comb.xor"(%150, %6) : (i1, i1) -> i1
    %163 = "comb.or"(%162, %114) : (i1, i1) -> i1
    %164 = "comb.mux"(%163, %17, %101) : (i1, i8, i8) -> i8
    %165 = "comb.and"(%150, %123) : (i1, i1) -> i1
    %166 = "comb.mux"(%150, %124, %205) : (i1, i1, i1) -> i1
    %167 = "comb.and"(%150, %125) : (i1, i1) -> i1
    %168 = "comb.and"(%150, %126) : (i1, i1) -> i1
    %169 = "comb.mux"(%150, %212, %121) : (i1, i8, i8) -> i8
    %170 = "comb.mux"(%150, %214, %123) : (i1, i1, i1) -> i1
    %171 = "comb.mux"(%150, %216, %124) : (i1, i1, i1) -> i1
    %172 = "comb.mux"(%150, %218, %125) : (i1, i1, i1) -> i1
    %173 = "comb.mux"(%150, %220, %126) : (i1, i1, i1) -> i1
    %174 = "comb.and"(%210, %132) : (i1, i1) -> i1
    %175 = "comb.mux"(%174, %164, %151) : (i1, i8, i8) -> i8
    %176 = "comb.and"(%174, %145) : (i1, i1) -> i1
    %177 = "comb.mux"(%174, %165, %152) : (i1, i1, i1) -> i1
    %178 = "comb.mux"(%174, %166, %153) : (i1, i1, i1) -> i1
    %179 = "comb.mux"(%174, %167, %154) : (i1, i1, i1) -> i1
    %180 = "comb.mux"(%174, %168, %155) : (i1, i1, i1) -> i1
    %181 = "comb.mux"(%174, %169, %156) : (i1, i8, i8) -> i8
    %182 = "comb.mux"(%174, %162, %arg7) : (i1, i1, i1) -> i1
    %183 = "comb.mux"(%174, %170, %158) : (i1, i1, i1) -> i1
    %184 = "comb.mux"(%174, %171, %159) : (i1, i1, i1) -> i1
    %185 = "comb.mux"(%174, %172, %160) : (i1, i1, i1) -> i1
    %186 = "comb.mux"(%174, %173, %161) : (i1, i1, i1) -> i1
    %187 = "comb.mux"(%arg1, %17, %175) : (i1, i8, i8) -> i8
    %188 = "comb.or"(%arg1, %176, %arg7) : (i1, i1, i1) -> i1
    %189 = "comb.and"(%132, %177) : (i1, i1) -> i1
    %190 = "comb.and"(%132, %178) : (i1, i1) -> i1
    %191 = "comb.and"(%132, %179) : (i1, i1) -> i1
    %192 = "comb.and"(%132, %180) : (i1, i1) -> i1
    %193 = "comb.and"(%132, %149) : (i1, i1) -> i1
    %194 = "comb.mux"(%arg1, %17, %181) : (i1, i8, i8) -> i8
    %195 = "comb.or"(%arg1, %182) : (i1, i1) -> i1
    %196 = "comb.and"(%132, %183) : (i1, i1) -> i1
    %197 = "comb.and"(%132, %184) : (i1, i1) -> i1
    %198 = "comb.and"(%132, %185) : (i1, i1) -> i1
    %199 = "comb.and"(%132, %186) : (i1, i1) -> i1
    %200 = "comb.mux"(%188, %187, %201) <{twoState}> : (i1, i8, i8) -> i8
    %201 = "seq.firreg"(%200, %136) <{name = "output_axis_tdata_reg"}> : (i8, !seq.clock) -> i8
    %202 = "comb.mux"(%188, %189, %203) <{twoState}> : (i1, i1, i1) -> i1
    %203 = "seq.firreg"(%202, %136) <{name = "output_axis_tkeep_reg"}> : (i1, !seq.clock) -> i1
    %204 = "comb.mux"(%188, %190, %205) <{twoState}> : (i1, i1, i1) -> i1
    %205 = "seq.firreg"(%204, %136) <{name = "output_axis_tvalid_reg"}> : (i1, !seq.clock) -> i1
    %206 = "comb.mux"(%188, %191, %207) <{twoState}> : (i1, i1, i1) -> i1
    %207 = "seq.firreg"(%206, %136) <{name = "output_axis_tlast_reg"}> : (i1, !seq.clock) -> i1
    %208 = "comb.mux"(%188, %192, %209) <{twoState}> : (i1, i1, i1) -> i1
    %209 = "seq.firreg"(%208, %136) <{name = "output_axis_tuser_reg"}> : (i1, !seq.clock) -> i1
    %210 = "seq.firreg"(%193, %136) <{name = "output_axis_tready_int"}> : (i1, !seq.clock) -> i1
    %211 = "comb.mux"(%195, %194, %212) <{twoState}> : (i1, i8, i8) -> i8
    %212 = "seq.firreg"(%211, %136) <{name = "temp_axis_tdata_reg"}> : (i8, !seq.clock) -> i8
    %213 = "comb.mux"(%195, %196, %214) <{twoState}> : (i1, i1, i1) -> i1
    %214 = "seq.firreg"(%213, %136) <{name = "temp_axis_tkeep_reg"}> : (i1, !seq.clock) -> i1
    %215 = "comb.mux"(%195, %197, %216) <{twoState}> : (i1, i1, i1) -> i1
    %216 = "seq.firreg"(%215, %136) <{name = "temp_axis_tvalid_reg"}> : (i1, !seq.clock) -> i1
    %217 = "comb.mux"(%195, %198, %218) <{twoState}> : (i1, i1, i1) -> i1
    %218 = "seq.firreg"(%217, %136) <{name = "temp_axis_tlast_reg"}> : (i1, !seq.clock) -> i1
    %219 = "comb.mux"(%195, %199, %220) <{twoState}> : (i1, i1, i1) -> i1
    %220 = "seq.firreg"(%219, %136) <{name = "temp_axis_tuser_reg"}> : (i1, !seq.clock) -> i1
    "hw.output"(%143, %201, %203, %205, %207, %209) : (i1, i8, i1, i1, i1, i1) -> ()
  }) : () -> ()
}) : () -> ()

