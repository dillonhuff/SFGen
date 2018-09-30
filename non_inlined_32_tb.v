`define assert(signal, value) if ((signal) !== (value)) begin $display("ASSERTION FAILED in %m: signal != value"); $finish(1); end

module top();

   reg [31:0] a;
   reg       en;
   reg       clk;
   
   
   wire [31:0] out;
   
   initial begin
      #1 clk = 0;

      #1 en = 1;
      #1 a = 32'd2;
      
      #1 clk = 1;
      #1 clk = 0;

      #1 en = 0;

      #1 clk = 1;
      #1 clk = 0;

//      #1 $display("out = %b", out);
      #1 `assert(out, 2 + 2 + 2);

      #1 $display("passed");
      
   end

   non_inlined_32 div(.x(a), .out(out), .en(en), .clk(clk));
   

endmodule
