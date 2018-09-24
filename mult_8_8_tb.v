`define assert(signal, value) if ((signal) !== (value)) begin $display("ASSERTION FAILED in %m: signal != value"); $finish(1); end

module top();

   reg [7:0] a;
   reg [7:0] b;
   
   wire [7:0] out;
   
   initial begin
      #1 a = 8'd2;
      #1 b = 8'd3;

      #1 `assert(out, 2 * 3 * 3 * 3);

      #1 $display("passed");
      
   end

   mult_8_8 div(.a(a), .b(b), .out(out));
   

endmodule
