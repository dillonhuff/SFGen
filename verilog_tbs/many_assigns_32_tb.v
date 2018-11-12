`define assert(signal, value) if ((signal) !== (value)) begin $display("ASSERTION FAILED in %m: signal != value"); $finish(1); end

module top();

   reg [31:0] y;
   wire [31:0] out;
   
   initial begin
      #1 y = 10;

//      $display("out = %d", out);
      
      #1 `assert(out, (y + 1)*(y + 1));


      #1 y = 3;
      
      #1 `assert(out, (y + 1)*(y + 1));
      
      #1 $display("passed");
      
   end

   many_assigns_32 m(.y(y), .out(out));
   

endmodule
