#!/usr/bin/python3
# Copyright 2021-2023 Zhijie Shi. All rights reserved. See LICENSE.txt.

import importlib
import argparse
import utilities as U 
from myhdl import block, Signal, instance, ResetSignal, delay, always 
from myhdl import StopSimulation, now

def     sys_error(s):
    print("Error:", s)
    exit(1)

class   RunEnvironment():
    def __init__(self):
        pass

@block
def testbench(imem, dmem, register_file, args):

    # resest signal is active low
    # 0: reset is active
    # 1: not in reset
    ACTIVE_LOW, INACTIVE_HIGH = 0, 1

    # clock
    HALF_PERIOD = delay(5)
    PREPARE_DELAY = delay(4)

    clock  = Signal(bool(1))
    reset = ResetSignal(0, active=0, isasync=True)

    clock = clock
    reset = reset
    debug = Signal(0)

    env = RunEnvironment() 
    env.cycle_number = 0
    env.print_option = args.popt    # Not used in single-cycle processor
    env.print_enable = args.pstart == 0 and args.pend > 0
    env.done = Signal(bool(0))

    if args.core == "":
        core_module = importlib.import_module("sc_core") 
    else:
        core_module = importlib.import_module(f"{args.core}.core") 

    core = core_module.RISCVCore(imem, dmem, register_file, clock, reset, env)

    @always(HALF_PERIOD)
    def clockGen():
        clock.next = not clock

    @instance
    def stimulus():

        # release reset
        # reset.next = ACTIVE_LOW
        yield delay(1)
        reset.next = INACTIVE_HIGH

        # We are in cycle 0. PC is initialized.
        # The processor start to fetch the first instruction 

        while True:
            yield clock.negedge
            yield PREPARE_DELAY
            # by now the processor should have done its job for this cycle
            # all signals should be stable
            if env.done:
                print("INFO: done is set in cycle {}".format(env.cycle_number))
                break
            # prepare for the next cycle
            env.cycle_number += 1
            if env.cycle_number >= args.n:
                break
            env.print_enable = args.pstart <= env.cycle_number < args.pend

        raise StopSimulation()

    return core, clockGen, stimulus

# main

parser = argparse.ArgumentParser(description='RISC-V Simulator in Python')
parser.add_argument('inputfile', help='instruction dump file')
# parser.add_argument('--reginit', '-r', nargs='+', default=[], help='initialize registers')
parser.add_argument('--argv', '-a', nargs='+', default=[], help='place words in argument registers')
parser.add_argument('--data', '-d', nargs='+', default=[], help='place words in global data section')
parser.add_argument('--display', action='store_true', help='use tp as display buffer')
parser.add_argument('-n', type=int, default=10000, help='number of cycles to simulate')
parser.add_argument('--pstart', '-s', default=0, type=int, help='cycle number where printing signals starts')
parser.add_argument('--pend', '-e', default=100000, type=int, help='cycle number where printing signals stops')
parser.add_argument('--popt', default="", help='option for printing signals')
parser.add_argument('--qrf', action='store_true', help='do not print RF at the end')
parser.add_argument('--qdmem', action='store_true', help='do not print data memory at the end')
parser.add_argument('--core', default='', help='specify the core')
parser.add_argument('-v', action='store_true', help='verbose')

args = parser.parse_args()
if args.n < 0: 
    sys_error("Number of cycles must be nonnegative ({}).".format(args.n))

if args.v:
    print(args)

try:
    imem = U.load_instructions(args.inputfile)
except FileNotFoundError as e:
    sys_error(e)

# raise argparse.ArgumentTypeError("Loading data dump file is not supported.");
dmem = {}

sp = 0x7fffeff0 
gp = 0x10010000
tp = 0x7f010000
offset = 0
for v in args.data:
    try: 
        addr = gp + offset
        dmem[addr] = U.int_to_unsigned_32(int(v, 0))
        offset += 4
        if args.v:
            U.print_memory_w(addr, dmem[addr]) 
    except ValueError:
        sys_error("'{}' is not a valid number.".format(v))

register_file = [_ for _ in range(32)] 
register_file[2] = sp   
register_file[3] = gp  
register_file[4] = tp  

# place words arguments in a0, a1, ...
assert len(args.argv) <= 8
regno = 10
for v in args.argv:
    try: 
        register_file[regno] = U.int_to_unsigned_32(int(v, 0))
        if args.v:
            U.print_register(regno, register_file[regno])
        regno += 1
    except ValueError:
        sys_error("'{}' is not a valid number.".format(v))

# register initialization from the command line
# for s in args.reginit:
#     try: 
#         name,value = s.split("=") 
#         if not name.startswith("x"):
#             raise ValueError()
#         regno = int(name[1:])
#         assert 0 < regno and regno < 32
#         register_file[regno] = U.int_to_unsigned_32(int(value, 0))
#         if args.v:
#             U.print_register(regno, register_file[regno])
#     except ValueError:
#         sys_error("'{}' is not a valid register initialization string.".format(s))
#         # print("Example: 'x1=100' sets x1 to 100.")
#     except AssertionError:
#         sys_error("the register number {} is not valid.".format(regno))

tb = testbench(imem, dmem, register_file, args)
tb.config_sim(trace=False)
tb.run_sim()

print("==========Report")
# dump register file and memory 
if not args.qrf:
    U.dump_register_file (register_file)
if not args.qdmem:
    U.dump_memory(dmem)
if args.display:
    U.dump_memory_str(dmem, tp) 
    print()
print("Simulation time:", now())
