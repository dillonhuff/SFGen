`define assert(signal, value) if ((signal) !== (value)) begin $display("ASSERTION FAILED in %m: signal != value"); $finish(1); end

module top();

   reg [7:0] n;
   reg [7:0] d;
   
   wire [7:0] out;
   
   initial begin
      #1 n = 8'd18;
      #1 d = 8'd3;

      #1 `assert(out, 8'd6);

      #1 n = 8'd21;
      #1 d = -8'd3;

//      #1 $display("out = %d", out);
      
      #1 `assert(out, -8'd7);
      
      #1 $display("passed");
      
   end

   newton_raphson_divide_8_8 div(.ne(n), .de(d), .out(out));

endmodule
