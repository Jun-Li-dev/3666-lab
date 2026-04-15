# Copyright 2021-2023 Zhijie Shi. All rights reserved. See LICENSE.txt.
# tag: adeccb49a0ec73532b768cda5f609bcb6297f5ca1233

from turtle import reset

from turtle import reset

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
    
    u_PC = RegisterE(sig.PC, sig.NextPC, sig.signal1, clock, reset)
    
    u_instr_mem = Rom(sig.instruction, sig.PC, imem_data)

    u_adder_1 = Adder(sig.PC4, sig.PC, sig.Const4)

    u_adder_2 = Adder(sig.BranchTarget, sig.PC, sig.immediate)

    u_mux = Mux2(sig.ALUInput2, sig.ReadData2, sig.immediate, sig.ALUSrc)

    u_mux2 = Mux2(sig.WriteData, sig.ALUResult, sig.MemReadData, sig.MemtoReg)

    u_mux3 = Mux2(sig.NextPC, sig.PC4, sig.BranchTarget, sig.PCSrc)

    u_pcsrc = And2(sig.PCSrc, sig.Branch, sig.Zero)

    u_main_control = MainControl(sig.opcode, sig.ALUOp, sig.ALUSrc, sig.Branch,
    sig.MemRead, sig.MemWrite, sig.MemtoReg, sig.RegWrite)

    u_alu_control = ALUControl(sig.ALUOp, sig.instr30, sig.funct3, sig.ALUOperation)

    u_alu = ALU(sig.ALUResult, sig.Zero, sig.ReadData1, sig.ALUInput2, sig.ALUOperation)

    u_immgen = ImmGen(sig.immediate, sig.instruction)

    u_dmem = Ram(sig.MemReadData, sig.ReadData2, sig.ALUResult, sig.MemRead,
    sig.MemWrite, dmem_data, clock)

    u_rf = RegisterFile(sig.ReadData1, sig.ReadData2, sig.rs1, sig.rs2, sig.rd,
    sig.WriteData, sig.RegWrite, rf, clock)

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
