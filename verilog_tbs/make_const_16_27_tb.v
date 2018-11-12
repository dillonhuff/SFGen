`define assert(signal, value) if ((signal) !== (value)) begin $display("ASSERTION FAILED in %m: signal != value"); $finish(1); end

module top();

   reg [15:0] n;
   
   wire [15:0] out;
   
   initial begin

      #1 n = 16'd4;
      #1 `assert(out, 16'd31);
      
      #1 $display("passed");
      
   end

   make_const_16_27 div(.a(n), .out(out));

endmodule
