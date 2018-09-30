#! /usr/local/bin/vvp
:ivl_version "11.0 (devel)" "(s20150603-476-gac87138)";
:ivl_delay_selection "TYPICAL";
:vpi_time_precision + 0;
:vpi_module "system";
:vpi_module "vhdl_sys";
:vpi_module "vhdl_textio";
:vpi_module "v2005_math";
:vpi_module "va_math";
S_0x7f817651dc80 .scope module, "non_inlined_32" "non_inlined_32" 2 94;
 .timescale 0 0;
    .port_info 0 /INPUT 1 "en"
    .port_info 1 /INPUT 1 "clk"
    .port_info 2 /INPUT 32 "x"
    .port_info 3 /OUTPUT 32 "out"
o0x10aba70c8 .functor BUFZ 1, C4<z>; HiZ drive
v0x7f817640f2d0_0 .net "clk", 0 0, o0x10aba70c8;  0 drivers
o0x10aba7c68 .functor BUFZ 1, C4<z>; HiZ drive
v0x7f817640f370_0 .net "en", 0 0, o0x10aba7c68;  0 drivers
v0x7f817640f430_0 .net "fresh_wire_0", 31 0, L_0x7f81764101f0;  1 drivers
v0x7f817640f520_0 .net "fresh_wire_10", 31 0, v0x7f817640ce50_0;  1 drivers
v0x7f817640f5b0_0 .net "fresh_wire_12", 31 0, L_0x7f8176410760;  1 drivers
v0x7f817640f700_0 .net "fresh_wire_17", 31 0, L_0x7f8176410970;  1 drivers
v0x7f817640f790_0 .net "fresh_wire_19", 31 0, v0x7f817640d500_0;  1 drivers
v0x7f817640f860_0 .net "fresh_wire_2", 31 0, L_0x7f81764102f0;  1 drivers
v0x7f817640f930_0 .net "fresh_wire_21", 31 0, L_0x7f8176410b80;  1 drivers
v0x7f817640fa40_0 .net "fresh_wire_4", 31 0, v0x7f817640db70_0;  1 drivers
v0x7f817640fad0_0 .net "fresh_wire_6", 31 0, L_0x7f8176410480;  1 drivers
v0x7f817640fba0_0 .net "fresh_wire_8", 31 0, L_0x7f81764104f0;  1 drivers
v0x7f817640fc70_0 .net "fs_0", 31 0, L_0x7f81764106f0;  1 drivers
v0x7f817640fd40_0 .net "fs_1", 31 0, L_0x7f8176410680;  1 drivers
v0x7f817640fe10_0 .net "global_stage_counter", 0 0, L_0x7f817640f9c0;  1 drivers
v0x7f817640ff20_0 .net "out", 31 0, L_0x7f8176410ad0;  1 drivers
L_0x10abd9008 .functor BUFT 1, C4<xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx>, C4<0>, C4<0>, C4<0>;
v0x7f817640ffb0_0 .net "undefined_value_16", 31 0, L_0x10abd9008;  1 drivers
o0x10aba70f8 .functor BUFZ 32, C4<zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz>; HiZ drive
v0x7f8176410140_0 .net "x", 31 0, o0x10aba70f8;  0 drivers
S_0x7f817651e5e0 .scope module, "assign_32_1" "builtin_assign_32" 2 128, 2 59 0, S_0x7f817651dc80;
 .timescale 0 0;
    .port_info 0 /INPUT 32 "in"
    .port_info 1 /OUTPUT 32 "out"
L_0x7f8176410b80 .functor BUFZ 32, v0x7f817640d500_0, C4<00000000000000000000000000000000>, C4<00000000000000000000000000000000>, C4<00000000000000000000000000000000>;
v0x7f817651cf70_0 .net "in", 31 0, v0x7f817640d500_0;  alias, 1 drivers
v0x7f817640a4a0_0 .net "out", 31 0, L_0x7f8176410b80;  alias, 1 drivers
S_0x7f817640a590 .scope module, "fifo_1" "builtin_fifo_0_32" 2 115, 2 20 0, S_0x7f817651dc80;
 .timescale 0 0;
    .port_info 0 /INPUT 1 "clk"
    .port_info 1 /INPUT 32 "in"
    .port_info 2 /OUTPUT 32 "out"
L_0x7f81764101f0 .functor BUFZ 32, o0x10aba70f8, C4<00000000000000000000000000000000>, C4<00000000000000000000000000000000>, C4<00000000000000000000000000000000>;
v0x7f817640a7d0_0 .net "clk", 0 0, o0x10aba70c8;  alias, 0 drivers
v0x7f817640a890_0 .net "in", 31 0, o0x10aba70f8;  alias, 0 drivers
v0x7f817640a940_0 .net "out", 31 0, L_0x7f81764101f0;  alias, 1 drivers
S_0x7f817640aa50 .scope module, "fifo_18" "builtin_fifo_0_32" 2 125, 2 20 0, S_0x7f817651dc80;
 .timescale 0 0;
    .port_info 0 /INPUT 1 "clk"
    .port_info 1 /INPUT 32 "in"
    .port_info 2 /OUTPUT 32 "out"
L_0x7f8176410970 .functor BUFZ 32, L_0x7f81764106f0, C4<00000000000000000000000000000000>, C4<00000000000000000000000000000000>, C4<00000000000000000000000000000000>;
v0x7f817640ac80_0 .net "clk", 0 0, o0x10aba70c8;  alias, 0 drivers
v0x7f817640ad40_0 .net "in", 31 0, L_0x7f81764106f0;  alias, 1 drivers
v0x7f817640ade0_0 .net "out", 31 0, L_0x7f8176410970;  alias, 1 drivers
S_0x7f817640aef0 .scope module, "fifo_3" "builtin_fifo_1_32" 2 116, 2 29 0, S_0x7f817651dc80;
 .timescale 0 0;
    .port_info 0 /INPUT 1 "clk"
    .port_info 1 /INPUT 32 "in"
    .port_info 2 /OUTPUT 32 "out"
L_0x7f81764102f0 .functor BUFZ 32, v0x7f817640b240_0, C4<00000000000000000000000000000000>, C4<00000000000000000000000000000000>, C4<00000000000000000000000000000000>;
v0x7f817640b150_0 .net "clk", 0 0, o0x10aba70c8;  alias, 0 drivers
v0x7f817640b240_0 .var "delay_reg_0", 31 0;
v0x7f817640b2e0_0 .net "in", 31 0, L_0x7f8176410680;  alias, 1 drivers
v0x7f817640b390_0 .net "out", 31 0, L_0x7f81764102f0;  alias, 1 drivers
E_0x7f817640b100 .event posedge, v0x7f817640a7d0_0;
S_0x7f817640b490 .scope module, "fifo_7" "builtin_fifo_0_32" 2 118, 2 20 0, S_0x7f817651dc80;
 .timescale 0 0;
    .port_info 0 /INPUT 1 "clk"
    .port_info 1 /INPUT 32 "in"
    .port_info 2 /OUTPUT 32 "out"
L_0x7f8176410480 .functor BUFZ 32, o0x10aba70f8, C4<00000000000000000000000000000000>, C4<00000000000000000000000000000000>, C4<00000000000000000000000000000000>;
v0x7f817640b6e0_0 .net "clk", 0 0, o0x10aba70c8;  alias, 0 drivers
v0x7f817640b770_0 .net "in", 31 0, o0x10aba70f8;  alias, 0 drivers
v0x7f817640b830_0 .net "out", 31 0, L_0x7f8176410480;  alias, 1 drivers
S_0x7f817640b930 .scope module, "fifo_9" "builtin_fifo_1_32" 2 119, 2 29 0, S_0x7f817651dc80;
 .timescale 0 0;
    .port_info 0 /INPUT 1 "clk"
    .port_info 1 /INPUT 32 "in"
    .port_info 2 /OUTPUT 32 "out"
L_0x7f81764104f0 .functor BUFZ 32, v0x7f817640bc70_0, C4<00000000000000000000000000000000>, C4<00000000000000000000000000000000>, C4<00000000000000000000000000000000>;
v0x7f817640bb40_0 .net "clk", 0 0, o0x10aba70c8;  alias, 0 drivers
v0x7f817640bc70_0 .var "delay_reg_0", 31 0;
v0x7f817640bd10_0 .net "in", 31 0, o0x10aba70f8;  alias, 0 drivers
v0x7f817640bde0_0 .net "out", 31 0, L_0x7f81764104f0;  alias, 1 drivers
S_0x7f817640beb0 .scope module, "fresh_assign_13" "builtin_assign_32" 2 121, 2 59 0, S_0x7f817651dc80;
 .timescale 0 0;
    .port_info 0 /INPUT 32 "in"
    .port_info 1 /OUTPUT 32 "out"
L_0x7f8176410680 .functor BUFZ 32, L_0x7f8176410760, C4<00000000000000000000000000000000>, C4<00000000000000000000000000000000>, C4<00000000000000000000000000000000>;
v0x7f817640c0b0_0 .net "in", 31 0, L_0x7f8176410760;  alias, 1 drivers
v0x7f817640c170_0 .net "out", 31 0, L_0x7f8176410680;  alias, 1 drivers
S_0x7f817640c230 .scope module, "fresh_assign_14" "builtin_assign_32" 2 122, 2 59 0, S_0x7f817651dc80;
 .timescale 0 0;
    .port_info 0 /INPUT 32 "in"
    .port_info 1 /OUTPUT 32 "out"
L_0x7f81764106f0 .functor BUFZ 32, L_0x7f8176410760, C4<00000000000000000000000000000000>, C4<00000000000000000000000000000000>, C4<00000000000000000000000000000000>;
v0x7f817640c420_0 .net "in", 31 0, L_0x7f8176410760;  alias, 1 drivers
v0x7f817640c4f0_0 .net "out", 31 0, L_0x7f81764106f0;  alias, 1 drivers
S_0x7f817640c5c0 .scope module, "fresh_assign_22" "builtin_assign_32" 2 127, 2 59 0, S_0x7f817651dc80;
 .timescale 0 0;
    .port_info 0 /INPUT 32 "in"
    .port_info 1 /OUTPUT 32 "out"
L_0x7f8176410ad0 .functor BUFZ 32, L_0x7f8176410b80, C4<00000000000000000000000000000000>, C4<00000000000000000000000000000000>, C4<00000000000000000000000000000000>;
v0x7f817640c830_0 .net "in", 31 0, L_0x7f8176410b80;  alias, 1 drivers
v0x7f817640c900_0 .net "out", 31 0, L_0x7f8176410ad0;  alias, 1 drivers
S_0x7f817640c990 .scope module, "in_mux_11" "builtin_mux_2_32" 2 120, 2 42 0, S_0x7f817651dc80;
 .timescale 0 0;
    .port_info 0 /INPUT 32 "in0"
    .port_info 1 /INPUT 32 "in1"
    .port_info 2 /INPUT 1 "sel"
    .port_info 3 /OUTPUT 32 "out"
v0x7f817640cc20_0 .net "in0", 31 0, L_0x7f8176410480;  alias, 1 drivers
v0x7f817640ccf0_0 .net "in1", 31 0, L_0x7f81764104f0;  alias, 1 drivers
v0x7f817640cda0_0 .net "out", 31 0, v0x7f817640ce50_0;  alias, 1 drivers
v0x7f817640ce50_0 .var "out_reg", 31 0;
v0x7f817640cf00_0 .net "sel", 0 0, L_0x7f817640f9c0;  alias, 1 drivers
E_0x7f817640cbd0 .event edge, v0x7f817640cf00_0, v0x7f817640b830_0, v0x7f817640bde0_0;
S_0x7f817640d030 .scope module, "in_mux_20" "builtin_mux_2_32" 2 126, 2 42 0, S_0x7f817651dc80;
 .timescale 0 0;
    .port_info 0 /INPUT 32 "in0"
    .port_info 1 /INPUT 32 "in1"
    .port_info 2 /INPUT 1 "sel"
    .port_info 3 /OUTPUT 32 "out"
v0x7f817640d2b0_0 .net "in0", 31 0, L_0x10abd9008;  alias, 1 drivers
v0x7f817640d370_0 .net "in1", 31 0, L_0x7f8176410970;  alias, 1 drivers
v0x7f817640d430_0 .net "out", 31 0, v0x7f817640d500_0;  alias, 1 drivers
v0x7f817640d500_0 .var "out_reg", 31 0;
v0x7f817640d590_0 .net "sel", 0 0, L_0x7f817640f9c0;  alias, 1 drivers
E_0x7f817640d250 .event edge, v0x7f817640cf00_0, v0x7f817640d2b0_0, v0x7f817640ade0_0;
S_0x7f817640d6c0 .scope module, "in_mux_5" "builtin_mux_2_32" 2 117, 2 42 0, S_0x7f817651dc80;
 .timescale 0 0;
    .port_info 0 /INPUT 32 "in0"
    .port_info 1 /INPUT 32 "in1"
    .port_info 2 /INPUT 1 "sel"
    .port_info 3 /OUTPUT 32 "out"
v0x7f817640d940_0 .net "in0", 31 0, L_0x7f81764101f0;  alias, 1 drivers
v0x7f817640da10_0 .net "in1", 31 0, L_0x7f81764102f0;  alias, 1 drivers
v0x7f817640dac0_0 .net "out", 31 0, v0x7f817640db70_0;  alias, 1 drivers
v0x7f817640db70_0 .var "out_reg", 31 0;
v0x7f817640dc20_0 .net "sel", 0 0, L_0x7f817640f9c0;  alias, 1 drivers
E_0x7f817640d8e0 .event edge, v0x7f817640cf00_0, v0x7f817640a940_0, v0x7f817640b390_0;
S_0x7f817640dd60 .scope module, "plus_nums_32_32_0" "plus_nums_32_32" 2 123, 2 67 0, S_0x7f817651dc80;
 .timescale 0 0;
    .port_info 0 /INPUT 32 "b"
    .port_info 1 /INPUT 32 "a"
    .port_info 2 /OUTPUT 32 "fs_0"
v0x7f817640e7e0_0 .net "a", 31 0, v0x7f817640db70_0;  alias, 1 drivers
v0x7f817640e8b0_0 .net "b", 31 0, v0x7f817640ce50_0;  alias, 1 drivers
v0x7f817640e980_0 .net "fresh_wire_0", 31 0, L_0x7f81764107f0;  1 drivers
v0x7f817640ea50_0 .net "fs_0", 31 0, L_0x7f8176410760;  alias, 1 drivers
S_0x7f817640df70 .scope module, "add_32_0" "builtin_add_32_32" 2 74, 2 78 0, S_0x7f817640dd60;
 .timescale 0 0;
    .port_info 0 /INPUT 32 "in0"
    .port_info 1 /INPUT 32 "in1"
    .port_info 2 /OUTPUT 32 "out"
v0x7f817640e1b0_0 .net "in0", 31 0, v0x7f817640db70_0;  alias, 1 drivers
v0x7f817640e280_0 .net "in1", 31 0, v0x7f817640ce50_0;  alias, 1 drivers
v0x7f817640e330_0 .net "out", 31 0, L_0x7f81764107f0;  alias, 1 drivers
L_0x7f81764107f0 .arith/sum 32, v0x7f817640db70_0, v0x7f817640ce50_0;
S_0x7f817640e430 .scope module, "fresh_assign_1" "builtin_assign_32" 2 73, 2 59 0, S_0x7f817640dd60;
 .timescale 0 0;
    .port_info 0 /INPUT 32 "in"
    .port_info 1 /OUTPUT 32 "out"
L_0x7f8176410760 .functor BUFZ 32, L_0x7f81764107f0, C4<00000000000000000000000000000000>, C4<00000000000000000000000000000000>, C4<00000000000000000000000000000000>;
v0x7f817640e630_0 .net "in", 31 0, L_0x7f81764107f0;  alias, 1 drivers
v0x7f817640e6e0_0 .net "out", 31 0, L_0x7f8176410760;  alias, 1 drivers
S_0x7f817640eb00 .scope module, "stage_counter" "builtin_counter_1" 2 114, 2 1 0, S_0x7f817651dc80;
 .timescale 0 0;
    .port_info 0 /INPUT 1 "rst"
    .port_info 1 /INPUT 1 "clk"
    .port_info 2 /OUTPUT 1 "out"
L_0x7f817640f9c0 .functor BUFZ 1, v0x7f817640ef20_0, C4<0>, C4<0>, C4<0>;
v0x7f817640ed10_0 .net "clk", 0 0, o0x10aba70c8;  alias, 0 drivers
v0x7f817640edc0_0 .net "out", 0 0, L_0x7f817640f9c0;  alias, 1 drivers
v0x7f817640ee60_0 .net "rst", 0 0, o0x10aba7c68;  alias, 0 drivers
v0x7f817640ef20_0 .var "stage_num", 0 0;
S_0x7f817640f020 .scope module, "x_const_15" "builtin_constant_32_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" 2 124, 2 87 0, S_0x7f817651dc80;
 .timescale 0 0;
    .port_info 0 /OUTPUT 32 "out"
v0x7f817640f1f0_0 .net "out", 31 0, L_0x10abd9008;  alias, 1 drivers
    .scope S_0x7f817640eb00;
T_0 ;
    %wait E_0x7f817640b100;
    %load/vec4 v0x7f817640ee60_0;
    %flag_set/vec4 8;
    %jmp/0xz  T_0.0, 8;
    %pushi/vec4 0, 0, 1;
    %assign/vec4 v0x7f817640ef20_0, 0;
    %jmp T_0.1;
T_0.0 ;
    %load/vec4 v0x7f817640ef20_0;
    %pad/u 32;
    %cmpi/e 1, 0, 32;
    %jmp/0xz  T_0.2, 4;
    %pushi/vec4 0, 0, 1;
    %assign/vec4 v0x7f817640ef20_0, 0;
    %jmp T_0.3;
T_0.2 ;
    %load/vec4 v0x7f817640ef20_0;
    %pad/u 2;
    %addi 1, 0, 2;
    %pad/u 1;
    %assign/vec4 v0x7f817640ef20_0, 0;
T_0.3 ;
T_0.1 ;
    %jmp T_0;
    .thread T_0;
    .scope S_0x7f817640aef0;
T_1 ;
    %wait E_0x7f817640b100;
    %load/vec4 v0x7f817640b2e0_0;
    %assign/vec4 v0x7f817640b240_0, 0;
    %jmp T_1;
    .thread T_1;
    .scope S_0x7f817640d6c0;
T_2 ;
    %wait E_0x7f817640d8e0;
    %load/vec4 v0x7f817640dc20_0;
    %dup/vec4;
    %pushi/vec4 0, 0, 1;
    %cmp/u;
    %jmp/1 T_2.0, 6;
    %dup/vec4;
    %pushi/vec4 1, 0, 1;
    %cmp/u;
    %jmp/1 T_2.1, 6;
    %jmp T_2.2;
T_2.0 ;
    %load/vec4 v0x7f817640d940_0;
    %store/vec4 v0x7f817640db70_0, 0, 32;
    %jmp T_2.2;
T_2.1 ;
    %load/vec4 v0x7f817640da10_0;
    %store/vec4 v0x7f817640db70_0, 0, 32;
    %jmp T_2.2;
T_2.2 ;
    %pop/vec4 1;
    %jmp T_2;
    .thread T_2, $push;
    .scope S_0x7f817640b930;
T_3 ;
    %wait E_0x7f817640b100;
    %load/vec4 v0x7f817640bd10_0;
    %assign/vec4 v0x7f817640bc70_0, 0;
    %jmp T_3;
    .thread T_3;
    .scope S_0x7f817640c990;
T_4 ;
    %wait E_0x7f817640cbd0;
    %load/vec4 v0x7f817640cf00_0;
    %dup/vec4;
    %pushi/vec4 0, 0, 1;
    %cmp/u;
    %jmp/1 T_4.0, 6;
    %dup/vec4;
    %pushi/vec4 1, 0, 1;
    %cmp/u;
    %jmp/1 T_4.1, 6;
    %jmp T_4.2;
T_4.0 ;
    %load/vec4 v0x7f817640cc20_0;
    %store/vec4 v0x7f817640ce50_0, 0, 32;
    %jmp T_4.2;
T_4.1 ;
    %load/vec4 v0x7f817640ccf0_0;
    %store/vec4 v0x7f817640ce50_0, 0, 32;
    %jmp T_4.2;
T_4.2 ;
    %pop/vec4 1;
    %jmp T_4;
    .thread T_4, $push;
    .scope S_0x7f817640d030;
T_5 ;
    %wait E_0x7f817640d250;
    %load/vec4 v0x7f817640d590_0;
    %dup/vec4;
    %pushi/vec4 0, 0, 1;
    %cmp/u;
    %jmp/1 T_5.0, 6;
    %dup/vec4;
    %pushi/vec4 1, 0, 1;
    %cmp/u;
    %jmp/1 T_5.1, 6;
    %jmp T_5.2;
T_5.0 ;
    %load/vec4 v0x7f817640d2b0_0;
    %store/vec4 v0x7f817640d500_0, 0, 32;
    %jmp T_5.2;
T_5.1 ;
    %load/vec4 v0x7f817640d370_0;
    %store/vec4 v0x7f817640d500_0, 0, 32;
    %jmp T_5.2;
T_5.2 ;
    %pop/vec4 1;
    %jmp T_5;
    .thread T_5, $push;
# The file index is used to find the file name in the following table.
:file_names 3;
    "N/A";
    "<interactive>";
    "non_inlined_32.v";
