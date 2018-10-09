`define assert(signal, value) if ((signal) !== (value)) begin $display("ASSERTION FAILED in %m: signal != value"); $finish(1); end

module top();

   reg [3:0] a;

   wire [3:0] res;
   
   
   initial begin
      #1 a = 3;
      
      #1 `assert(res, 4'd2);
      
      #1 $display("passed");
      
   end

   foo_4 m(.a(a), .res(res));
   

endmodule
