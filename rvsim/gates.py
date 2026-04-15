# Copyright 2021-2023 Zhijie Shi. All rights reserved. See LICENSE.txt.
from myhdl import block, always_seq

@block 
def RegisterE(dout, din, en, clock, reset):
    """ register with enable, positive edge triggered

    Args:
        dout: output of the register
        din:  input of the register
        en:   write enable signal. dout is updated only when en is 1

    The implementation does not care about
    the width of dout and din, but they should match.
    """

    @always_seq(clock.posedge, reset=reset)
    def seq():
        if en: 
            dout.next = din
        else:
            dout.next = dout

    return seq
