from myhdl import *

#tag: 2030f31e7cc658399d3e8348af4a8667fc0153c1

#Number of bits in multiplicand and multiplier.
NBITS = 8

@block 
def RegisterLoad(dout, din, en, load_data, load, clock, reset):
    """ register with enable 

        dout: data out
        din: data in
        en:  write enable
        load: if asserted, load_data will be saved in register
        load_data: data loaded into register when load is asserted

        load_data is aved in register if load = 1
        din is saved in register if load = 0 and en = 1
        Otherwise, dout is not changed
    """

    @always_seq(clock.posedge, reset=reset)
    def reg_en():
        if load:
            dout.next = load_data
        elif en: 
            dout.next = din

    return reg_en

@block 
def RegisterShiftLeft(dout, load_data, en, load, clock, reset):
    """ shift left register with load

        register is set to load_data if load is 1
        register is shifted left by 1 if en is 1 and load is 0
        Otherwise, register is not changed.

        The bit shifted in is always 0.

        Note: 
        If load_data is narrower (has fewer bits) than dout, 
        it is 0 extended. 
    """

    @always_seq(clock.posedge, reset=reset)
    def logic_seq():
        if load: 
            dout.next = load_data
        elif en:
            dout.next = (dout << 1)
    return logic_seq

@block 
def RegisterShiftRight(dout, load_data, en, load, clock, reset):
    """ shift right register with load

        register is set to load_data if load is 1
        register is shifted right by 1 if en is 1 and load is 0
        Otherwise, register is not changed.

        The bit shifted in is always 0.
    """

    @always_seq(clock.posedge, reset=reset)
    def logic_seq():
        if load: 
            dout.next = load_data
        elif en:
            dout.next = (dout >> 1)
    return logic_seq

@block
def Adder(s, a, b):
    """
        s = a + b
    """
    @always_comb
    def adder_logic():
        s.next = a + b

    return adder_logic

@block
def Control(done, p_en, s_en, test, load, clock, reset): 
    """ Control module

    Input:
        load:   Load signal to the multiplier. Reset the internal counter.
        test:   Informaton from y to determine the enable signals for registers.

        clock and reset.

    Output:
        done:   Multiplication is done. Determined by a counter.
        p_en:   Write enable for register p
        s_en:   Shift enable for both registers x and y.
    """

    # signals for internal counter
    counter_in = Signal(0)
    counter = Signal(0)

    # counter logic
    @always_seq(clock.posedge, reset=reset)
    def logic_seq():
        counter.next = counter_in

    @always_comb
    def logic_comb():
        if load:
            counter_in.next = 0
            done.next = 0
            p_en.next = 0
            s_en.next = 0
        elif counter == NBITS:
            counter_in.next = counter 
            done.next = 1
            p_en.next = 0
            s_en.next = 0
        else:
            counter_in.next = counter + 1
            done.next = 0
            p_en.next = test
            s_en.next = 1

    return logic_seq, logic_comb

############### Do not change the code above this line

@block
def Mul_ww(p, x_init, y_init, load, done, clock, reset):
    """ Multiplier

    Input:
        x_init, y_init, load, clock, reset

    Output:
        p, done

    p:  the product

        p = x_init * y_init when done is asserted

    x_init: initial value of x, the multiplicand
    y_init: initial value of y, the multiplier

    load:
        1:  load x_init and y_init into x and y registers. Also clear p.
        0:  work mode

    done:
        0: not done
        1: done. result is available in p

    """
    
    W = NBITS
    W2 = W + W

    # create signals
    # W2 bits 0's, to be loaded into register p
    w2_0 = Signal(intbv(0)[W2:])      
    adder_out = Signal(modbv(0)[W2:]) # output of adder

    # x and y are the output of registers x and y
    x    = Signal(modbv(0)[W2:]) 
    y    = Signal(intbv(0)[W:])
    # p is one of arguments (ports) of the multiplier
    
    # enable signal for p, x, and y registers
    p_en = Signal(bool(0))  
    shift_en = Signal(bool(0)) # x and y sare the same shift enable signal

    # test signal from register y to the control
    test = Signal(bool(0))

    # Example of instantiating an existing module
    # instantiate register P
    # pay attention to the signals  
    reg_p = RegisterLoad(p, adder_out, p_en, w2_0, load, clock, reset)

    # TODO:
    reg_x = RegisterShiftLeft(x, x_init, shift_en, load, clock, reset)

    reg_y = RegisterShiftRight(y, y_init, shift_en, load, clock, reset)

    adder = Adder(adder_out, p, x)

    control = Control(done, p_en, shift_en, test, load, clock, reset)

    # instantiate x and y registers, and adder
    # to make things easier, we connect x_init to reg_x directly, instead
    # of 0 extended to 16 bits.
    # reg_x = 
    # reg_y = 
    # adder = 
    # contorl = 
    # x_init and y_init are the load_data signal to reg_x and reg_y, respectively

    # set the test signal (a single bit) going into the control module
    @always_comb
    def testgen():
        #TODO:
        test.next = y[0]
        # test.next = 

    ##################################################
    # There is no need to change any lines below. 
    ##################################################
    # Monitor for testing
    # it is not really part of the circuit
    # we place it here because it is easier to monitor internal signals
    @instance
    def monitor():
        cycle_number = 0
        wl = [3, 4, W2, W2, max(W, 8), 4, 4, 4] 
        fmt_str = ' '.join(["{:"+str(_)+"}" for _ in wl])
        print(fmt_str.format("cnt", "load", "p", "x", 
            "y", "p_en", "s_en", "done"))
        while 1:
            yield clock.posedge
            # wait all signals are updated after positive edge
            yield delay(2) 
            print(fmt_str.format(
                cycle_number, int(load), bin(p, W2), bin(x, W2), bin(y, W), 
                int(p_en), int(shift_en), int(done)))
            cycle_number += 1

    return instances()

if __name__ == "__main__":
    ACTIVE_LOW, INACTIVE_HIGH = 0, 1

    @block
    def testbench(num_lists):
        n = NBITS 
        n2 = n + n

        multiplicand = Signal(intbv(0)[n:])
        multiplier = Signal(intbv(0)[n:])
        product = Signal(intbv(0)[n2:])
        load = Signal(bool(1))
        done = Signal(bool(0))

        clock   = Signal(bool(0))
        reset = ResetSignal(ACTIVE_LOW, active=0, isasync=True)

        tut = Mul_ww(product, multiplicand, multiplier, load, done, clock, reset)

        HALF_PERIOD = delay(10)

        @always(HALF_PERIOD)
        def clockGen():
            clock.next = not clock

        @instance
        def stimulus():

            # all input changes happen after the negative edge
            # yield clock.negedge

            # release reset
            reset.next = INACTIVE_HIGH

            # delay for signals to become stable after clock edge
            delayp = delay(3)

            for (x, y) in [ (num_lists[i], num_lists[i+1]) for i in range(0, len(num_lists) - 1) ]: 
                # specify the initial values
                # the output is formatted for 8-bit numbers
                multiplicand.next = x
                multiplier.next = y
                load.next = 1
                # wait for the rising edge of the clock  
                yield clock.posedge
                # wait a little to release load
                yield delayp
                load.next = 0

                # just wait until it's done
                while not done:
                    yield clock.posedge
                    yield delayp        # it takes a while for done to set

                # additional clock for checking
                yield clock.posedge     
                yield delayp

                # check if the result is correct
                if x * y != product:
                    print("Error:p!={}".format(bin(x * y, n2)))
                print("{} * {} = {}".format(x, y, int(product)))

            raise StopSimulation()

        return tut, clockGen, stimulus

    import argparse
    parser = argparse.ArgumentParser(description='Multiplier')
    parser.add_argument('numbers', nargs='*', type=int, default=[255, 255], help='List of numbers')
    parser.add_argument('--trace', action='store_true', help='generate trace file')

    args = parser.parse_args()
    if len(args.numbers) <= 1:
        print("Error: specify at least two numbers.")
        exit(1)

    tb = testbench(args.numbers)
    tb.config_sim(trace=args.trace)
    tb.run_sim()
