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

    # Instruction Memory

    u_imem = Rom(
        addr=sig.PC,
        dout=sig.instruction,
        mem=imem_data
    )

    # Register File

    u_rf = RegisterFile(
        rs1=sig.rs1,
        rs2=sig.rs2,
        rd=sig.rd,
        rd_data=sig.WriteData,
        regWrite=sig.RegWrite,
        rs1_data=sig.ReadData1,
        rs2_data=sig.ReadData2,
        clock=clock,
        regs=rf
    )

    # Immediate Generator

    u_imm = ImmGen(
        instr=sig.instruction,
        imm=sig.immediate
    )

 
    # Control Unit

    u_ctrl = MainControl(
        opcode=sig.opcode,
        RegWrite=sig.RegWrite,
        MemRead=sig.MemRead,
        MemtoReg=sig.MemtoReg,
        MemWrite=sig.MemWrite,
        ALUSrc=sig.ALUSrc,
        Branch=sig.Branch,
        ALUOp=sig.ALUOp
    )


    # ALU Control

    u_alu_ctrl = ALUControl(
        ALUOp=sig.ALUOp,
        funct3=sig.funct3,
        funct7=sig.funct7,
        ALUCtrl=sig.ALUOperation
    )

    # ALU Input MUX

    u_alu_mux = Mux2(
        sel=sig.ALUSrc,
        in0=sig.ReadData2,
        in1=sig.immediate,
        out=sig.ALUInput2
    )


    # ALU

    u_alu = ALU(
        op=sig.ALUOperation,
        in1=sig.ReadData1,
        in2=sig.ALUInput2,
        result=sig.ALUResult,
        zero=sig.Zero
    )


    # Data Memory

    u_dmem = Ram(
        addr=sig.ALUResult,
        din=sig.ReadData2,
        dout=sig.MemReadData,
        we=sig.MemWrite,
        clock=clock,
        mem=dmem_data
    )


    # Writeback MUX

    u_wb_mux = Mux2(
        sel=sig.MemtoReg,
        in0=sig.ALUResult,
        in1=sig.MemReadData,
        out=sig.WriteData
    )


    # PC + 4

    u_pc_add = Adder(
        in1=sig.PC,
        in2=sig.Const4,
        out=sig.PC4
    )


    # Branch Target

    u_branch_add = Adder(
        in1=sig.PC,
        in2=sig.immediate,
        out=sig.BranchTarget
    )


    # PCSrc logic

    u_and = And2(
        in1=sig.Branch,
        in2=sig.Zero,
        out=sig.PCSrc
    )


    # Next PC MUX

    u_pc_mux = Mux2(
        sel=sig.PCSrc,
        in0=sig.PC4,
        in1=sig.BranchTarget,
        out=sig.NextPC
    )

    # PC Register

    u_PC = RegisterE(
        sig.PC,
        sig.NextPC,
        sig.signal1,
        clock,
        reset
    )
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
