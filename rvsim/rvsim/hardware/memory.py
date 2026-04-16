# Copyright 2021-2023 Zhijie Shi. All rights reserved. See LICENSE.txt.
from myhdl import block, always_comb, always

RAM_DEFAULT = 0
ROM_DEFAULT = 0x13

# Single-port ram
# since we only use it for simulation, we do not care the addr width
@block
def Ram(dout, din, addr, memr, memw, data, clk): 
    """ One port RAM

    Args:
        dout:   Read data from memory

        din:    Write data to memory

        addr:   address

        memr:   Mem Read

        memw:   Mem Write

        data:   a dictionary to simulate memory

        clk:    clock 

    Write only when memw is asserted and memr is not asserted.
    Write is triggered by postive edge. 

    Read only when memr is asserted and memw is not asserted. 
    Read is a comb operation. Triggered by addr, memr, and memw.

    *Important*:
    When writing, dout is not updated in the same cycle.

    Memory content is saved in data, which is a dictionary. 
    Address is the key. 
    """

    @always(clk.posedge)
    def write_logic():
        if memw and not memr: 
            data[int(addr)] = int(din)

    @always_comb
    def read_logic():
        if memr and not memw:
            a = int(addr)
            if a in data:
                dout.next = data[a]
            else:
                dout.next = RAM_DEFAULT

    return write_logic, read_logic

@block
def Rom(dout, addr, data): 
    """ ROM. For instruction memory.  

    Args:
        dout:   data read from the memory

        addr:   address

        data:   a dictionary that simulates the memory. Address is the key.

    Memory content is passed in with data.

    The module works as a combinational circuit. 

    Read is triggered by addr. 
    """

    @always_comb
    def rom_logic():
        a = int(addr)
        if a in data:
            dout.next = data[a]
        else:
            dout.next = ROM_DEFAULT 

    return rom_logic
