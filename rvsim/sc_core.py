# Copyright 2021-2023 Zhijie Shi. All rights reserved. See LICENSE.txt.
# tag: adeccb49a0ec73532b768cda5f609bcb6297f5ca1233

from myhdl import * 

from hardware.register import RegisterE
from hardware.memory import Ram, Rom
from hardware.mux import Mux2
from hardware.gates import And2
from hardware.alu import ALU
from hardware.adder import Adder
from hardware.registerfile import RegisterFile

from sc_signals import RISCVSignals
from immgen import ImmGen 
from maincontrol import MainControl
from alucontrol import ALUControl

@block
def     RISCVCore(imem_data, dmem_data, rf, clock, reset, env):
    """
    All signals are input

    imem_data:   instruction memory. A Python dictionary
    dmem_data:   data memory. A Python dictionary
    rf:     register file. A list of 32 integers
    clock:  clock 
    reset:  reset
    env:    additonal info, mainly for controlling print

    env.done:   asserted when simulation is done
    """

    # find max and min of instruction addresses
    # always start from the first instruction in the instruction memory
    max_pc = max(imem_data.keys()) 
    init_pc = min(imem_data.keys()) 

    # signals
    sig = RISCVSignals(init_pc)

    ##### Do NOT change the lines above
    # TODO
    # instantiate hardware modules 
    # check the diagram, make sure nothing is missing
    # and signals are connected correctly
    # 
    # The memory modules are in hardware/memory.py
    # Use Rom for instruction memory and Ram for data memory
    # imem_data and dmem_data will be passed to memory as data

    # for example, PC register is instantiated with the following line
    # sig.signal1 is always 1, which means that PC is always updated in this
    # implementation

    # Instruction Memory (ROM)

    u_imem = Rom(
        addr=sig.PC,
        dout=sig.instr,
        mem=imem_data
    )


    # Data Memory (RAM)

    u_dmem = Ram(
        addr=sig.ALU_result,
        din=sig.rs2_val,
        dout=sig.mem_data,
        we=sig.MemWrite,
        clock=clock,
        mem=dmem_data
    )


    # Register File

    u_rf = RegisterFile(
        rs1=sig.rs1,
        rs2=sig.rs2,
        rd=sig.rd,
        rd_data=sig.write_data,
        regWrite=sig.RegWrite,
        rs1_data=sig.rs1_val,
        rs2_data=sig.rs2_val,
        clock=clock,
        regs=rf
    )


    # Immediate Generator

    u_imm = ImmGen(
        instr=sig.instr,
        imm=sig.imm
    )


    # Control Unit

    u_ctrl = MainControl(
        opcode=sig.instr[6:0],
        RegWrite=sig.RegWrite,
        MemRead=sig.MemRead,
        MemWrite=sig.MemWrite,
        MemtoReg=sig.MemtoReg,
        ALUSrc=sig.ALUSrc,
        Branch=sig.Branch,
        ALUOp=sig.ALUOp
    )


    # ALU Control

    u_alu_ctrl = ALUControl(
        ALUOp=sig.ALUOp,
        funct3=sig.instr[14:12],
        funct7=sig.instr[31:25],
        ALUCtrl=sig.ALUCtrl
    )


    # ALU Input MUX

    u_alu_mux = Mux2(
        sel=sig.ALUSrc,
        in0=sig.rs2_val,
        in1=sig.imm,
        out=sig.alu_in2
    )

    
    # ALU

    u_alu = ALU(
        op=sig.ALUCtrl,
        in1=sig.rs1_val,
        in2=sig.alu_in2,
        result=sig.ALU_result,
        zero=sig.zero
    )

    # Writeback MUX

    u_wb_mux = Mux2(
        sel=sig.MemtoReg,
        in0=sig.ALU_result,
        in1=sig.mem_data,
        out=sig.write_data
    )


    # PC + 4 Adder

    u_pc_adder = Adder(
        in1=sig.PC,
        in2=4,
        out=sig.PC_plus4
    )


    # Hazard Detection 

    @always_comb
    def hazard_detection():
        sig.stall.next = 0

        # Check EX stage hazard
        if sig.ID_rs1 == sig.EX_rd and sig.EX_RegWrite:
            sig.stall.next = 1
        elif sig.ID_rs2 == sig.EX_rd and sig.EX_RegWrite:
            sig.stall.next = 1

        # Check MEM stage hazard
        elif sig.ID_rs1 == sig.MEM_rd and sig.MEM_RegWrite:
            sig.stall.next = 1
        elif sig.ID_rs2 == sig.MEM_rd and sig.MEM_RegWrite:
            sig.stall.next = 1

    # PC Control 

    @always_comb
    def pc_logic():
        if sig.stall:
            sig.NextPC.next = sig.PC   # freeze PC
        else:
            sig.NextPC.next = sig.PC_plus4

    # Bubble Injection

    @always_comb
    def bubble_logic():
        if sig.stall:
            # convert ID/EX into NOP
            sig.ID_EX_RegWrite.next = 0
            sig.ID_EX_MemRead.next = 0
            sig.ID_EX_MemWrite.next = 0
            sig.ID_EX_Branch.next = 0
            sig.ID_EX_ALUSrc.next = 0
            sig.ID_EX_MemtoReg.next = 0
    u_PC = RegisterE(sig.PC, sig.NextPC, sig.signal1, clock, reset)


    ##### Do NOT change the lines below
    @always_comb
    def set_done():
        env.done.next = sig.PC > max_pc  

    # print at the negative edge. for simulation only 
    @always(clock.negedge)
    def print_logic():
        if env.print_enable:
            sig.print(env.cycle_number, env.print_option)

    return instances()

if __name__ == "__main__" :
    print("Error: Please start the simulation with rvsim.py")
    exit(1)
