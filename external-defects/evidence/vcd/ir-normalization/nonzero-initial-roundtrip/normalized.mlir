module {
  hw.module @init_ff(in %clk : i1, in %d : i4, out q : i4) {
    %0 = seq.to_clock %clk
    %q = seq.firreg %d clock %0 preset 5 : i4
    hw.output %q : i4
  }
}

