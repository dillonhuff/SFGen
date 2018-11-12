`define assert(signal, value) if ((signal) !== (value)) begin $display("ASSERTION FAILED in %m: signal != value"); $finish(1); end

module top();

   reg [63:0] a;
   reg [63:0] b;
   

   wire [63:0] out;
   
   initial begin
      #1 a = {32'd10, 32'd14};
      #1 b = {32'd8, 32'd9};      
      
      #1 `assert(out, {32'd18, 32'd23});
      
      #1 $display("passed");
      
   end

   add_complex m(.a(a), .b(b), .fs_0(fs_0));
   

endmodule
