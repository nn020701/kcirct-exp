module {
  sv.macro.decl @SYNTHESIS
  sv.macro.decl @VERILATOR
  emit.fragment @RANDOM_INIT_FRAGMENT {
    sv.verbatim "// Standard header to adapt well known macros for register randomization."
    sv.verbatim "\0A// RANDOM may be set to an expression that produces a 32-bit random unsigned value."
    sv.ifdef @RANDOM {
    } else {
      sv.macro.def @RANDOM "$random"
    }
    sv.verbatim "\0A// Users can define INIT_RANDOM as general code that gets injected into the\0A// initializer block for modules with registers."
    sv.ifdef @INIT_RANDOM {
    } else {
      sv.macro.def @INIT_RANDOM ""
    }
    sv.verbatim "\0A// If using random initialization, you can also define RANDOMIZE_DELAY to\0A// customize the delay used, otherwise 0.002 is used."
    sv.ifdef @RANDOMIZE_DELAY {
    } else {
      sv.macro.def @RANDOMIZE_DELAY "0.002"
    }
    sv.verbatim "\0A// Define INIT_RANDOM_PROLOG_ for use in our modules below."
    sv.ifdef @INIT_RANDOM_PROLOG_ {
    } else {
      sv.ifdef @RANDOMIZE {
        sv.ifdef @VERILATOR {
          sv.macro.def @INIT_RANDOM_PROLOG_ "`INIT_RANDOM"
        } else {
          sv.macro.def @INIT_RANDOM_PROLOG_ "`INIT_RANDOM #`RANDOMIZE_DELAY begin end"
        }
      } else {
        sv.macro.def @INIT_RANDOM_PROLOG_ ""
      }
    }
  }
  emit.fragment @RANDOM_INIT_REG_FRAGMENT {
    sv.verbatim "\0A// Include register initializers in init blocks unless synthesis is set"
    sv.ifdef @RANDOMIZE {
    } else {
      sv.ifdef @RANDOMIZE_REG_INIT {
        sv.macro.def @RANDOMIZE ""
      }
    }
    sv.ifdef @SYNTHESIS {
    } else {
      sv.ifdef @ENABLE_INITIAL_REG_ {
      } else {
        sv.macro.def @ENABLE_INITIAL_REG_ ""
      }
    }
    sv.verbatim ""
  }
  sv.macro.decl @ENABLE_INITIAL_REG_
  sv.macro.decl @ENABLE_INITIAL_MEM_
  sv.macro.decl @FIRRTL_BEFORE_INITIAL
  sv.macro.decl @FIRRTL_AFTER_INITIAL
  sv.macro.decl @RANDOMIZE_REG_INIT
  sv.macro.decl @RANDOMIZE
  sv.macro.decl @RANDOMIZE_DELAY
  sv.macro.decl @RANDOM
  sv.macro.decl @INIT_RANDOM
  sv.macro.decl @INIT_RANDOM_PROLOG_
  hw.module @xlnxstream_2018_3(in %M_AXIS_ACLK : i1, in %M_AXIS_ARESETN : i1, out M_AXIS_TVALID : i1, out M_AXIS_TDATA : i32, out M_AXIS_TSTRB : i4, out M_AXIS_TLAST : i1, in %M_AXIS_TREADY : i1) attributes {emit.fragments = [@RANDOM_INIT_REG_FRAGMENT, @RANDOM_INIT_FRAGMENT]} {
    %c0_i4 = hw.constant 0 : i4
    %c0_i5 = hw.constant 0 : i5
    %true = hw.constant true
    %false = hw.constant false
    %c1_i2 = hw.constant 1 : i2
    %c-2_i2 = hw.constant -2 : i2
    %c0_i2 = hw.constant 0 : i2
    %c-8_i4 = hw.constant -8 : i4
    %c1_i4 = hw.constant 1 : i4
    %c7_i4 = hw.constant 7 : i4
    %c1_i5 = hw.constant 1 : i5
    %c-1_i5 = hw.constant -1 : i5
    %c-1_i4 = hw.constant -1 : i4
    %c0_i28 = hw.constant 0 : i28
    %c8_i32 = hw.constant 8 : i32
    %c1_i32 = hw.constant 1 : i32
    %0 = comb.xor %M_AXIS_ARESETN, %true : i1
    %1 = comb.icmp ceq %20, %c0_i2 : i2
    %2 = comb.icmp ceq %20, %c1_i2 : i2
    %3 = comb.add %23, %c1_i5 : i5
    %4 = comb.xor %1, %true : i1
    %5 = comb.and %4, %M_AXIS_ARESETN : i1
    %6 = comb.and %M_AXIS_ARESETN, %1 : i1
    %7 = comb.mux %6, %c1_i2, %c-2_i2 : i2
    %8 = comb.mux %0, %c0_i2, %7 : i2
    %9 = comb.mux %0, %c0_i5, %23 : i5
    %10 = comb.icmp ne %23, %c-1_i5 : i5
    %11 = comb.and %10, %2, %5 : i1
    %12 = comb.mux %11, %c1_i2, %8 : i2
    %13 = comb.mux %11, %3, %9 : i5
    %14 = comb.or %11, %0 : i1
    %15 = comb.xor %2, %true : i1
    %16 = comb.icmp cne %20, %c-2_i2 : i2
    %17 = comb.and %15, %5, %16 : i1
    %18 = comb.xor %17, %true : i1
    %19 = comb.and %18, %14 : i1
    %mst_exec_state = sv.reg : !hw.inout<i2> 
    %20 = sv.read_inout %mst_exec_state : !hw.inout<i2>
    %21 = comb.xor %19, %true : i1
    %22 = comb.or %21, %17 : i1
    %count = sv.reg : !hw.inout<i5> 
    %23 = sv.read_inout %count : !hw.inout<i5>
    %24 = comb.icmp eq %20, %c-2_i2 : i2
    %25 = comb.concat %c0_i28, %50 : i28, i4
    %26 = comb.icmp ult %25, %c8_i32 : i32
    %27 = comb.and %24, %26 : i1
    %28 = comb.icmp eq %50, %c7_i4 : i4
    %29 = comb.and %M_AXIS_ARESETN, %27 : i1
    %30 = comb.and %M_AXIS_ARESETN, %28 : i1
    %axis_tvalid_delay = sv.reg : !hw.inout<i1> 
    %31 = sv.read_inout %axis_tvalid_delay : !hw.inout<i1>
    %axis_tlast_delay = sv.reg : !hw.inout<i1> 
    %32 = sv.read_inout %axis_tlast_delay : !hw.inout<i1>
    %33 = comb.icmp eq %50, %c-8_i4 : i4
    %34 = comb.add %50, %c1_i4 : i4
    %35 = comb.mux %0, %c0_i4, %50 : i4
    %36 = comb.and %26, %M_AXIS_ARESETN : i1
    %37 = comb.and %51, %36 : i1
    %38 = comb.mux %37, %34, %35 : i4
    %39 = comb.or %37, %0 : i1
    %40 = comb.xor %37, %true : i1
    %41 = comb.or %37, %0, %33 : i1
    %42 = comb.xor %51, %true : i1
    %43 = comb.and %36, %42 : i1
    %44 = comb.xor %43, %true : i1
    %45 = comb.and %44, %39 : i1
    %46 = comb.and %44, %40, %M_AXIS_ARESETN, %33 : i1
    %47 = comb.and %44, %41 : i1
    %48 = comb.xor %45, %true : i1
    %49 = comb.or %48, %43 : i1
    %read_pointer = sv.reg : !hw.inout<i4> 
    %50 = sv.read_inout %read_pointer : !hw.inout<i4>
    %tx_done = sv.reg : !hw.inout<i1> 
    %51 = comb.and %M_AXIS_TREADY, %27 : i1
    %52 = comb.add %25, %c1_i32 : i32
    %53 = comb.and %51, %M_AXIS_ARESETN : i1
    %54 = comb.mux %53, %52, %c1_i32 : i32
    %55 = comb.and %M_AXIS_ARESETN, %42 : i1
    %stream_data_out = sv.reg : !hw.inout<i32> 
    %56 = sv.read_inout %stream_data_out : !hw.inout<i32>
    sv.always posedge %M_AXIS_ACLK {
      sv.if %17 {
      } else {
        sv.passign %mst_exec_state, %12 : i2
      }
      sv.if %22 {
      } else {
        sv.passign %count, %13 : i5
      }
      sv.passign %axis_tvalid_delay, %29 : i1
      sv.passign %axis_tlast_delay, %30 : i1
      sv.if %49 {
      } else {
        sv.passign %read_pointer, %38 : i4
      }
      sv.if %47 {
        sv.passign %tx_done, %46 : i1
      }
      sv.if %55 {
      } else {
        sv.passign %stream_data_out, %54 : i32
      }
    }
    sv.ifdef @ENABLE_INITIAL_REG_ {
      sv.ordered {
        sv.ifdef @FIRRTL_BEFORE_INITIAL {
          sv.verbatim "`FIRRTL_BEFORE_INITIAL"
        }
        sv.initial {
          sv.ifdef.procedural @INIT_RANDOM_PROLOG_ {
            sv.verbatim "`INIT_RANDOM_PROLOG_"
          }
          sv.ifdef.procedural @RANDOMIZE_REG_INIT {
            %_RANDOM = sv.logic : !hw.inout<uarray<2xi32>>
            sv.for %i = %c0_i2 to %c-2_i2 step %c1_i2 : i2 {
              %RANDOM = sv.macro.ref.expr.se @RANDOM() : () -> i32
              %70 = comb.extract %i from 0 : (i2) -> i1
              %71 = sv.array_index_inout %_RANDOM[%70] : !hw.inout<uarray<2xi32>>, i1
              sv.bpassign %71, %RANDOM : i32
            }
            %57 = sv.array_index_inout %_RANDOM[%false] : !hw.inout<uarray<2xi32>>, i1
            %58 = sv.array_index_inout %_RANDOM[%true] : !hw.inout<uarray<2xi32>>, i1
            %59 = sv.read_inout %57 : !hw.inout<i32>
            %60 = comb.extract %59 from 0 : (i32) -> i1
            sv.bpassign %axis_tvalid_delay, %60 : i1
            %61 = sv.read_inout %57 : !hw.inout<i32>
            %62 = comb.extract %61 from 1 : (i32) -> i1
            sv.bpassign %axis_tlast_delay, %62 : i1
            %63 = sv.read_inout %57 : !hw.inout<i32>
            %64 = comb.extract %63 from 2 : (i32) -> i1
            sv.bpassign %tx_done, %64 : i1
            %65 = sv.read_inout %57 : !hw.inout<i32>
            %66 = comb.extract %65 from 3 : (i32) -> i29
            %67 = sv.read_inout %58 : !hw.inout<i32>
            %68 = comb.extract %67 from 0 : (i32) -> i3
            %69 = comb.concat %66, %68 : i29, i3
            sv.bpassign %stream_data_out, %69 : i32
          }
          sv.bpassign %mst_exec_state, %c0_i2 : i2
          sv.bpassign %count, %c0_i5 : i5
          sv.bpassign %read_pointer, %c0_i4 : i4
        }
        sv.ifdef @FIRRTL_AFTER_INITIAL {
          sv.verbatim "`FIRRTL_AFTER_INITIAL"
        }
      }
    }
    hw.output %31, %56, %c-1_i4, %32 : i1, i32, i4, i1
  }
}

