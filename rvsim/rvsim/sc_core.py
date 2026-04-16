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

    # Instruction memory
    u_imem = Rom(sig.PC, sig.instruction, imem_data)

    # Register file
    u_rf = RegisterFile(
        sig.rs1, sig.rs2, sig.rd,
        sig.WriteData, sig.RegWrite,
        sig.ReadData1, sig.ReadData2,
        clock, rf
    )

    # Immediate generator
    u_imm = ImmGen(sig.instruction, sig.immediate)

    # Control
    u_ctrl = MainControl(
        sig.opcode,
        sig.Branch, sig.ALUSrc, sig.MemRead,
        sig.MemWrite, sig.MemtoReg, sig.RegWrite,
        sig.ALUOp
    )

    # ALU control
    u_alu_ctrl = ALUControl(
        sig.ALUOp,
        sig.funct3,
        sig.funct7,
        sig.ALUOperation
    )

    # ALU input mux
    u_mux = Mux2(
        sig.ALUSrc,
        sig.ReadData2,
        sig.immediate,
        sig.ALUInput2
    )

    # ALU
    u_alu = ALU(
        sig.ALUOperation,
        sig.ReadData1,
        sig.ALUInput2,
        sig.ALUResult,
        sig.Zero
    )

    # Data memory
    u_dmem = Ram(
        sig.ALUResult,
        sig.ReadData2,
        sig.MemReadData,
        sig.MemWrite,
        clock,
        dmem_data
    )

    # Writeback mux
    u_wb = Mux2(
        sig.MemtoReg,
        sig.ALUResult,
        sig.MemReadData,
        sig.WriteData
    )

    # PC + 4
    u_pc_add = Adder(sig.PC, sig.Const4, sig.PC4)

    # Branch target
    u_branch = Adder(sig.PC, sig.immediate, sig.BranchTarget)

    # PC select
    u_and = And2(sig.Branch, sig.Zero, sig.PCSrc)

    u_pc_mux = Mux2(
        sig.PCSrc,
        sig.PC4,
        sig.BranchTarget,
        sig.NextPC
    )

    # PC register
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
