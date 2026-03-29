from myhdl import block, always_comb, instances, intbv, Signal
from alu1 import ALU1bit

# tag: a09569a7ea11a8a592cb75b6eeedf910

# For large design, we can put blocks (hardware modules) in different Python
# modules 

#ALU1bit(a, b, carryin, binvert, operation, result, carryout):

@block
def ALU4bits(a, b, alu_operation, result, zero):

    """ 4-bit ALU

        See the diagram for details. 

    """
    # create internal signals in the 4-bit ALU

    # bnegate and operation are shadow signals, not regular signals
    # They follow the bits in alu_operation 
    # If alu_operation changes, they change 
    # So we do not need to set value for bnegate and operation manually
    # If we use bit slicing, like alu_operation[2], we only get current value 
    # of bit 2 in alu_operation. It is not a signal.
    # We could create regular Signal objects. Then we have to copy 
    # values from alu_operation with a combinational function
    bnegate = alu_operation(2)      # bit 2 in alu_operation
    # like any range in Python, upper bound is open and lower is closed. 
    operation = alu_operation(2,0)  # bits 1 and 0

    # Create signals for carryout of 1-bit ALUs.
    # We could use Python list to keep track of similar signalsl. 
    # In this lab, we use individual variables.
    # TODO: create c2, c3, and c4
    c1 = Signal(intbv(0)[1:]) 
    c2 = Signal(intbv(0)[1:])
    c3 = Signal(intbv(0)[1:])
    c4 = Signal(intbv(0)[1:])
    # Create signals for result of 1-bit ALUs
    # We cannot use shadow signals from result because shadow
    # signals are read only. We will have to copy them to result manually
    # TODO: create result1, result2, and result3
    result0 = Signal(intbv(0)[1:]) 
    result1 = Signal(intbv(0)[1:])
    result2 = Signal(intbv(0)[1:])
    result3 = Signal(intbv(0)[1:])

    # TODO
    # instantiat four 1-bit ALUs
    # 
    # Use shadow signals to connnect individual bits in 
    # signals `a` and `b` to 1-bit ALUs. 
    # a(0) is a shadow signal that follows bit 0 in a
    # a[0] is bit 0's current value and it is not a Signal

    alu1_0 = ALU1bit(a(0), b(0), bnegate, bnegate, operation, result0, c1);
    alu1_1 = ALU1bit(a(1), b(1), c1, bnegate, operation, result1, c2)
    alu1_2 = ALU1bit(a(2), b(2), c2, bnegate, operation, result2, c3)
    alu1_3 = ALU1bit(a(3), b(3), c3, bnegate, operation, result3, c4)


    @always_comb
    def comb_output():
        result.next[0] = result0
        result.next[1] = result1
        result.next[2] = result2
        result.next[3] = result3

    # zero = 1 if result == 0000
        if result0 == 0 and result1 == 0 and result2 == 0 and result3 == 0:
            zero.next = 1
        else:
            zero.next = 0
        # TODO
        # Generate output signals `result` and `zero`
        # from the output of 1-bit ALUs
        #
        # To set an individual bit in `result`, like bit 0, we do
        #   result.next[0] = ... 
        # Do not forget signal zero.


    # return all logic  
    return instances()

if __name__ == "__main__":
    from myhdl import delay, instance, StopSimulation, bin
    import argparse

    # testbench itself is a block
    @block
    def test_comb(args):

        # create signals
        # use intbv for multiple bits
        a = Signal(intbv(0)[4:])
        b = Signal(intbv(0)[4:])
        result = Signal(intbv(0)[4:0])
        alu_operation = Signal(intbv(0)[4:])
        zero = Signal(bool(0))

        # instantiating a block
        alu = ALU4bits(a, b, alu_operation, result, zero)

        @instance
        def stimulus():
            print("ALU_operation a     b    | result zero")
            for op in args.operation_list:
                alu_operation.next = op
                for i in range(16):
                    bi = intbv(i)
                    a.next = args.a
                    b.next = bi[4:]
                    yield delay(10)
                    print("{:12}  {}  {} | {}   {}".format(
                        bin(op, 4), bin(a, 4), bin(b, 4),
                        bin(result, 4), int(zero)))

            # stop simulation
            raise StopSimulation()

        return alu, stimulus

    operation_list = [-1, 0, 1, 2, 6]
    parser = argparse.ArgumentParser(description='4-bit ALU')
    parser.add_argument('op', nargs='?', type=int, default=-1, choices=operation_list, 
            help='alu operation in decimal. -1 for all operations')

    parser.add_argument('-a', type=int, default=0b1010, help='input a in decimal')
    parser.add_argument('--trace', action='store_true', help='generate trace file')

    args = parser.parse_args()
    # print(args)

    if args.op < 0:
        args.operation_list = operation_list[1:]
    else:
        args.operation_list = [args.op]

    tb = test_comb(args)
    tb.config_sim(trace=args.trace)
    tb.run_sim()

