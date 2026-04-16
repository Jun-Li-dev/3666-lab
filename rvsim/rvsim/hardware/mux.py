# Copyright 2021-2023 Zhijie Shi. All rights reserved. See LICENSE.txt.
from myhdl import block, always_comb

@block
def Mux2(z, a, b, sel):
    """ 2-input multiplexer

    z = sel ? b : a

    The width of signals do not mattter. 
    """

    @always_comb
    def comb():
        if sel:
            z.next = b
        else:
            z.next = a

    return comb

@block
def Mux4(z, a, b, c, d, sel):
    """ 4-input multiplexer

    sel[1]  sel[0]  z
    0       0       a    
    0       1       b    
    1       0       c    
    1       1       d    

    The width of signals do not mattter. 
    """

    @always_comb
    def comb():
        if sel == 0:
            z.next = a
        elif sel == 1:
            z.next = b
        elif sel == 2:
            z.next = c
        else:
            z.next = d

    return comb
