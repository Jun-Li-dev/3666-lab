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

    # PC + 4

    u_pc_adder = Adder(
        in1=sig.PC,
        in2=4,
        out=sig.PC_plus4
    )

  
    # Hazard Detection 

    @always_comb
    def hazard_detection():
        sig.stall.next = 0

        # Check EX stage
        if (sig.ID_rs1 == sig.EX_rd and sig.EX_RegWrite) or \
           (sig.ID_rs2 == sig.EX_rd and sig.EX_RegWrite):
            sig.stall.next = 1

        # Check MEM stage
        elif (sig.ID_rs1 == sig.MEM_rd and sig.MEM_RegWrite) or \
             (sig.ID_rs2 == sig.MEM_rd and sig.MEM_RegWrite):
            sig.stall.next = 1


    # PC Control

    @always_comb
    def pc_logic():
        if sig.stall:
            sig.NextPC.next = sig.PC   # freeze PC
        else:
            sig.NextPC.next = sig.PC_plus4


    # Pipeline Stall Control
 
    @always_comb
    def stall_logic():
        if sig.stall:
            sig.IF_ID_Write.next = 0   # freeze IF/ID
            sig.ID_EX_Flush.next = 1   # insert bubble
        else:
            sig.IF_ID_Write.next = 1
            sig.ID_EX_Flush.next = 0


    # PC Register

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
