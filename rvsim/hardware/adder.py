# Copyright 2021-2023 Zhijie Shi. All rights reserved. See LICENSE.txt.
from myhdl import block, always_comb

@block
def Adder(result, in1, in2):
    """
    result = in1 + in2

    The width of each number is controlled outside. 

    To avoid exceptions, result should be based on modbv.
    """

    @always_comb
    def comb_logic():
        result.next = in1 + in2

    return comb_logic

