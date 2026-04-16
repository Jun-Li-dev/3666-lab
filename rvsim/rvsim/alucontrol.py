# Copyright 2021-2023 Zhijie Shi. All rights reserved. See LICENSE.txt.
from myhdl import block, always_comb

@block
def ALUControl(ALUOp, instr30, funct3, operation):
    """ Generate 4-bit ALU operation

    Args:
        ALUOp:    2 bits from the main control
        instr30:  instruction[30]. A bit in funct7
        funct3:   funct3

        operation:  4-bit ALU operation
    """

    @always_comb
    def comb_logic():
        v = 0               # default operation AND
        if ALUOp == 0:      # load or store
            v = 0b0010
        elif ALUOp == 0b01:   # branch
            v = 0b0110
        else:   # R-type or I-type ALU 
            if funct3 == 0b111:   # AND
                v = 0b0000
            elif funct3 == 0b110:   # OR
                v = 0b0001
            elif funct3 == 0b001:   # shift left
                v = 0b1000
            elif funct3 == 0b101:   # shift right 
                if instr30: 
                    v = 0b1101 # arith
                else:
                    v = 0b1001 # logical
            elif funct3 == 0:  # add or sub
                if ALUOp == 2 and instr30:  # only R-type
                    v = 0b0110 # sub
                else:
                    v = 0b0010 # add

        operation.next = v

    return comb_logic
