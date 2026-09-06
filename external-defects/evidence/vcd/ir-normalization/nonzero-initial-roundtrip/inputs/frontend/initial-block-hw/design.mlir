module {
  hw.module @init_ff(in %clk : i1, in %d : i4, out q : i4) {
    %c5_i4 = hw.constant 5 : i4
    %0 = llhd.constant_time <0ns, 0d, 1e>
    %c0_i4 = hw.constant 0 : i4
    %q = llhd.sig %c0_i4 : i4
    llhd.drv %q, %c5_i4 after %0 : i4
    %1 = seq.to_clock %clk
    %q_0 = seq.firreg %d clock %1 {name = "q"} : i4
    llhd.drv %q, %q_0 after %0 : i4
    %2 = llhd.prb %q : i4
    hw.output %2 : i4
  }
}
