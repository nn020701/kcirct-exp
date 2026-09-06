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
  hw.module @init_ff(in %clk : i1, in %d : i4, out q : i4) attributes {emit.fragments = [@RANDOM_INIT_REG_FRAGMENT, @RANDOM_INIT_FRAGMENT]} {
    %c5_i4 = hw.constant 5 : i4
    %q = sv.reg : !hw.inout<i4> 
    %0 = sv.read_inout %q : !hw.inout<i4>
    sv.always posedge %clk {
      sv.passign %q, %d : i4
    }
    sv.ifdef @ENABLE_INITIAL_REG_ {
      sv.ordered {
        sv.ifdef @FIRRTL_BEFORE_INITIAL {
          sv.verbatim "`FIRRTL_BEFORE_INITIAL"
        }
        sv.initial {
          sv.bpassign %q, %c5_i4 : i4
        }
        sv.ifdef @FIRRTL_AFTER_INITIAL {
          sv.verbatim "`FIRRTL_AFTER_INITIAL"
        }
      }
    }
    hw.output %0 : i4
  }
}

