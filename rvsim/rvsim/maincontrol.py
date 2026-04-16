# Copyright 2021-2023 Zhijie Shi. All rights reserved. See LICENSE.txt.
from myhdl import block, always_comb

@block
def MainControl(opcode, 
        ALUOp, 
        ALUSrc, 
        Branch,
        MemRead,
        MemWrite,
        MemtoReg,
        RegWrite
        ):
    """Generate control signals.

    Supported instructions:

        R-type   and opcode is 0b0110011 
        I-type   and opcode is 0b0010011
        load
        store
        branch
    """

    @always_comb
    def comb_logic():

        if   opcode == 0b0110011:   #R
            ALUOp.next = 0b10
            ALUSrc.next = 0 
            Branch.next = 0
            MemRead.next = 0
            MemWrite.next = 0
            MemtoReg.next = 0
            RegWrite.next = 1
        elif opcode == 0b0000011:   # Load
            ALUOp.next = 0b00
            ALUSrc.next = 1 
            Branch.next = 0
            MemRead.next = 1
            MemWrite.next = 0
            MemtoReg.next = 1
            RegWrite.next = 1
        elif opcode == 0b0100011:   # Store
            ALUOp.next = 0b00
            ALUSrc.next = 1 
            Branch.next = 0
            MemRead.next = 0
            MemWrite.next = 1
            MemtoReg.next = 0
            RegWrite.next = 0
        elif opcode == 0b1100011:   # Branch
            ALUOp.next = 0b01
            ALUSrc.next = 0 
            Branch.next = 1
            MemRead.next = 0
            MemWrite.next = 0
            MemtoReg.next = 0
            RegWrite.next = 0
        elif opcode == 0b0010011:   # ALU with immd
            ALUOp.next = 0b11       # I-type  
            ALUSrc.next = 1 
            Branch.next = 0
            MemRead.next = 0
            MemWrite.next = 0
            MemtoReg.next = 0
            RegWrite.next = 1
        else: # raise exception
            raise ValueError("Unkown opcode {:06b}".format(int(opcode)))

    return comb_logic
