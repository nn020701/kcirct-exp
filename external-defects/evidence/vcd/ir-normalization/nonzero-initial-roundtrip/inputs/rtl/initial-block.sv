module init_ff(input logic clk, input logic [3:0] d, output logic [3:0] q);
 initial q = 4'h5;
 always @(posedge clk) q <= d;
endmodule
