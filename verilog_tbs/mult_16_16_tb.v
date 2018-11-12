`define assert(signal, value) if ((signal) !== (value)) begin $display("ASSERTION FAILED in %m: signal != value"); $finish(1); end

module top();

   reg [15:0] a;
   reg [15:0] b;
   reg       en;
   reg       clk;
   
   
   wire [15:0] out;
   
   initial begin
      #1 clk = 0;

      #1 en = 1;
      #1 a = 8'd2;
      #1 b = 8'd3;
      
      #1 clk = 1;
      #1 clk = 0;

      #1 en = 0;
      // #1 a = 8'd0;
      // #1 b = 8'd0;

      #1 clk = 1;
      #1 clk = 0;

      #1 clk = 1;
      #1 clk = 0;

      #1 $display("out = %d", out);

      #1 clk = 1;
      #1 clk = 0;

      #1 $display("out = %d", out);

      #1 clk = 1;
      #1 clk = 0;

      #1 $display("out = %d", out);
      #1 clk = 1;
      #1 clk = 0;

      #1 $display("out = %d", out);
      #1 clk = 1;
      #1 clk = 0;

      #1 $display("out = %d", out);
      #1 clk = 1;
      #1 clk = 0;

      #1 $display("out = %d", out);
      #1 clk = 1;
      #1 clk = 0;

      #1 $display("out = %d", out);
      #1 clk = 1;
      #1 clk = 0;

      #1 $display("out = %d", out);
      
      #1 `assert(out, 2 * 3 * 3 * 3);

      #1 $display("passed");
      
   end

   mult_16_16 mult(.a(a), .b(b), .out(out), .en(en), .clk(clk));
   

endmodule
