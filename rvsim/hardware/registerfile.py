# Copyright 2021-2023 Zhijie Shi. All rights reserved. See LICENSE.txt.
from myhdl import block, always_comb, always, Signal

@block
def RegisterFile(dout1, dout2, rs1, rs2, rd, wrtdata, regw, data, clock, posedge = True):
    ''' Register file with two read ports.

    Args:
        dout1:  RF read data 1

        dout2:  RF read data 2

        rs1:    read register number 1

        rs2:    read register number 2

        rd:     write register number

        wrtdata: Write data

        regw:   reg write. register is updated if regw is 1 and rd is not 0

        data:   a list of 32 Python integers. Since data are not signals, we
                need to trigger read operation manually.

        clock:  the clock

        posedge:  
            If true, write happens at the positive clock edge. 
            Otherwise, it happens at the negative edge.
    '''
    # Reg[0] is always 0
    data[0] = 0

    # signal for triggering read
    read_trigger = Signal(bool(0))

    @always(clock.posedge)
    def write_logic_pos():
        if regw and rd != 0:
            data[rd] = int(wrtdata)
            # we could check if rd is rs1 or rs2
            read_trigger.next = not read_trigger

    @always(clock.negedge)
    def write_logic_neg():
        if regw and rd != 0:
            data[rd] = int(wrtdata)
            # we could check if rd is rs1 or rs2
            read_trigger.next = not read_trigger

    @always(rs1, rs2, read_trigger)
    def read_logic():
        dout1.next = data[rs1] 
        dout2.next = data[rs2] 

    # The following implementation uses clock to trigger
    # @always(clock.negedge)
    # def read_logic():
    #    dout1.next = data[rs1] 
    #    dout2.next = data[rs2] 

    if posedge:
        return read_logic, write_logic_pos
    else:
        return read_logic, write_logic_neg
