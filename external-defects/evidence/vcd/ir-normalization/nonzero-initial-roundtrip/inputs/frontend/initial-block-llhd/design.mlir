module {
  hw.module @init_ff(in %clk : i1, in %d : i4, out q : i4) {
    %0 = llhd.constant_time <0ns, 1d, 0e>
    %true = hw.constant true
    %1 = llhd.constant_time <0ns, 0d, 1e>
    %c0_i4 = hw.constant 0 : i4
    %c5_i4 = hw.constant 5 : i4
    %false = hw.constant false
    %clk_0 = llhd.sig name "clk" %false : i1
    %2 = llhd.prb %clk_0 : i1
    %d_1 = llhd.sig name "d" %c0_i4 : i4
    %q = llhd.sig %c0_i4 : i4
    llhd.process {
      llhd.drv %q, %c5_i4 after %1 : i4
      llhd.halt
    }
    llhd.process {
      cf.br ^bb1
    ^bb1:  // 3 preds: ^bb0, ^bb2, ^bb3
      %4 = llhd.prb %clk_0 : i1
      llhd.wait (%2 : i1), ^bb2
    ^bb2:  // pred: ^bb1
      %5 = llhd.prb %clk_0 : i1
      %6 = comb.xor bin %4, %true : i1
      %7 = comb.and bin %6, %5 : i1
      cf.cond_br %7, ^bb3, ^bb1
    ^bb3:  // pred: ^bb2
      %8 = llhd.prb %d_1 : i4
      llhd.drv %q, %8 after %0 : i4
      cf.br ^bb1
    }
    llhd.drv %clk_0, %clk after %1 : i1
    llhd.drv %d_1, %d after %1 : i4
    %3 = llhd.prb %q : i4
    hw.output %3 : i4
  }
}
