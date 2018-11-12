`define assert(signal, value) if (signal !== value) begin $display("ASSERTION FAILED in %m: signal != value"); $finish(1); end

module top();

   reg [15:0] a;
   wire [15:0] out;
   
   initial begin
      #1 a = 1;
      #1 `assert(out, -16'b1);

      #1 $display("passed");
      
   end

   tc_neg_16 neg(.a(a), .fs_5(out));
   
endmodule
