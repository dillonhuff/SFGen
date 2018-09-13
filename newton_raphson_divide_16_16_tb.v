`define assert(signal, value) if ((signal) !== (value)) begin $display("ASSERTION FAILED in %m: signal != value"); $finish(1); end

module top();

   reg [15:0] n;
   reg [15:0] d;
   
   wire [15:0] out;
   
   initial begin
      #1 n = 16'd18;
      #1 d = 16'd3;

      #1 `assert(out, 16'd6);

      #1 n = 16'd21;
      #1 d = -16'd3;

//      #1 $display("out = %d", out);
      
      #1 `assert(out, -16'd7);
      
      #1 $display("passed");
      
   end

   newton_raphson_divide_16_16 div(.ne(n), .de(d), .out(out));

endmodule
