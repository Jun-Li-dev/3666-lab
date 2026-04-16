# Copyright 2021-2023 Zhijie Shi. All rights reserved. See LICENSE.txt.
from myhdl import block, always_comb, intbv, concat

@block
def ImmGen(immediate, instruction):
    """Generate immediate from instruction.

    Supported instruction types:

        000 0011: I, LW ...
        001 0011: I, ANDI, ORI, ...
        010 0011: S
        110 0011: SB 

        011 0011: R   treated as I

    Not supported (to be implemented in assignments): 
        001 0111: U, AUIPC
        011 0111: U, LUI
        110 0111: I, JALR
        110 1111: UJ, JAL

    See the paragraph at the end of Section 4.3 in textbook for comments about
    generating immediate for R, Load, Store, and branches.

    """

    # 12-bit immd
    # Note that the upper bound is not inclusive in MyHDL
    # [12:] specifies 12 bits: bits 11 to 0
    imm12 = intbv(0)[12:]

    # 20-bit immd, for U and UJ type
    imm20 = intbv(0)[20:]

    # change 20 to 52 for 64 bits
    sign1 = intbv(-1)[20:]  

    @always_comb
    def comb_logic():
        opcode = instruction[7:]
        if opcode == 0x63: # SB
            imm12 = concat(instruction[7], instruction[31:25], instruction[12:8], bool(0))
        elif opcode == 0x23: # S
            imm12 = concat(instruction[32:25], instruction[12:7])
        else:  # I and R
            imm12 = instruction[32:20]

        if instruction[31]:  # duplicate 1's
            immediate.next = concat(sign1, imm12)
        else:
            immediate.next = imm12

    return comb_logic
