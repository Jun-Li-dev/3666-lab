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
    
    # Instruction Memory
    u_imem = Rom(sig.instruction, sig.PC, imem_data)

    # Main Control
    u_control = MainControl(sig.opcode,
                        sig.ALUOp,
                        sig.ALUSrc,
                        sig.Branch,
                        sig.MemRead,
                        sig.MemWrite,
                        sig.MemtoReg,
                        sig.RegWrite)

    # Register File
    u_rf = RegisterFile(sig.ReadData1, sig.ReadData2,
                    sig.rs1, sig.rs2, sig.rd,
                    sig.WriteData, sig.RegWrite,
                    rf, clock)

    # Immediate Generator
    u_imm = ImmGen(sig.immediate, sig.instruction)

    # ALU Control
    u_alu_control = ALUControl(sig.ALUOp, sig.instr30, sig.funct3, sig.ALUOperation)

    # ALU input mux
    u_mux_alu = Mux2(sig.ALUInput2, sig.ReadData2, sig.immediate, sig.ALUSrc)

    # ALU
    u_alu = ALU(sig.ALUResult, sig.Zero,
            sig.ReadData1, sig.ALUInput2,
            sig.ALUOperation)

    # Data Memory
    u_dmem = Ram(sig.MemReadData, sig.ALUResult, sig.ReadData2,
             sig.MemRead, sig.MemWrite,
             dmem_data, clock)

    # Write-back mux
    u_mux_wb = Mux2(sig.WriteData, sig.ALUResult, sig.MemReadData, sig.MemtoReg)

    # PC + 4
    u_pc4 = Adder(sig.PC4, sig.PC, sig.Const4)

    # Branch target (IMPORTANT: shift left 1)
    u_branch = Adder(sig.BranchTarget, sig.PC, sig.immediate << 1)

    # Branch decision
    u_and = And2(sig.PCSrc, sig.Branch, sig.Zero)

    # PC mux
    u_mux_pc = Mux2(sig.NextPC, sig.PC4, sig.BranchTarget, sig.PCSrc)

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
