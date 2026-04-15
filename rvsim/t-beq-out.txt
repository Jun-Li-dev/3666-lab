# Copyright 2021-2023 Zhijie Shi. All rights reserved. See LICENSE.txt.
from myhdl import block, always_comb

@block
def ALU(result, zero, in1, in2, operation):
    """ Implement ALU.

    Supported operations:
        0000    AND
        0001    OR
        0010    add
        0110    sub
        0111    slt
    
    # should not be in ALU, but in ALU in this course

        1000    SLL   
        1001    SRL   
        1101    SRA
    """

    # hardcode the masks. We could check the length of in1
    SHIFT_AMT_MASK = 0x1F    # 0x3F for 64 bits
    BITS_MASK = 0xFFFF_FFFF # 0xFFFF_FFFF_FFFF_FFFF for 64 bits

    @always_comb
    def comb_logic():
        if operation == 0:          # AND
            r = in1 & in2
        elif operation == 0b0001:   # OR
            r = in1 | in2
        elif operation == 0b0010:   # ADD
            r = in1 + in2
        elif operation == 0b0110:   # SUB
            r = in1 - in2
        elif operation == 0b0111:   # SLT
            r = n1.signed() < n2.signed()
        # shift operations are not performed in real ALU
        elif operation == 0b1000:   # SLL
            r = in1 << (in2 & SHIFT_AMT_MASK)
        elif operation == 0b1001:   # SRL
            r = in1 >> (in2 & SHIFT_AMT_MASK)
        elif operation == 0b1101:   # SRA
            r = in1.signed() >> (in2 & SHIFT_AMT_MASK)
        else:
            raise ValueError("Invalid ALU operation: {:04b}".format(int(operation)))
        # print(f"ALU Result = {r}")
        r &= BITS_MASK
        result.next = r
        zero.next = r == 0

    return comb_logic

