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
        # Instruction Memory (ROM)
    u_imem = Rom(sig.instr, sig.PC, imem_data)

    # Main Control
    u_control = MainControl(sig.opcode, sig.Branch, sig.MemRead, sig.MemtoReg,
                            sig.ALUOp, sig.MemWrite, sig.ALUSrc, sig.RegWrite)

    # Register File
    u_rf = RegisterFile(sig.rs1_data, sig.rs2_data,
                        sig.rs1, sig.rs2, sig.rd,
                        sig.write_data, sig.RegWrite,
                        rf, clock)

    # Immediate Generator
    u_imm = ImmGen(sig.imm, sig.instr)

    u_alu_control = ALUControl(sig.ALUOp, sig.funct3, sig.funct7, sig.alu_ctrl)

    u_mux_alu = Mux2(sig.alu_in2, sig.rs2_data, sig.imm, sig.ALUSrc)

    u_alu = ALU(sig.alu_result, sig.zero, sig.rs1_data, sig.alu_in2, sig.alu_ctrl)

    u_dmem = Ram(sig.mem_data, sig.alu_result, sig.rs2_data,
                 sig.MemRead, sig.MemWrite, dmem_data, clock)

    u_mux_wb = Mux2(sig.write_data, sig.alu_result, sig.mem_data, sig.MemtoReg)

    u_pc4 = Adder(sig.pc4, sig.PC, sig.const4)

    u_branch = Adder(sig.branch_addr, sig.PC, sig.imm)

    u_and = And2(sig.pc_src, sig.Branch, sig.zero)

    u_mux_pc = Mux2(sig.NextPC, sig.pc4, sig.branch_addr, sig.pc_src)

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
