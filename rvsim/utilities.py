# Copyright 2021-2023 Zhijie Shi. All rights reserved. See LICENSE.txt.
XLEN = 32

SIGN = (1 << (XLEN - 1))
MASK = (SIGN + SIGN) - 1

# We need 32-bit values even on 64-bit processors
MASK32 = 0xFFFF_FFFF
SIGN32 = (1 << 31)

def int_to_signed_32 (v):
    """
    Input: v is an integer
    Output: the value if the lower 32 bits are considered as 2's complement numbers 
    """
    v = v & MASK32
    if (v & SIGN32):
        v = v - MASK32 - 1
    return v

def int_to_unsigned_32 (v):
    """
    Input: v is an integer
    Output: Only lower 32 bits are kept
    """
    return (v & MASK32)  # only lower 32 bits

def int_to_signed (v):
    """
    Input: v is an integer
    Output: Only lower XLEN bits are kept
    """
    v = v & MASK
    if v & SIGN:
        v = v - MASK - 1
    return v

def int_to_unsigned (v):
    """
    Input: v is an integer
    Output: Only lower XLEN bits are kept
    """
    return (v & MASK)

def print_memory_instr (addr, i):
    ui = int_to_unsigned_32(i)
    print("0x{:08X}: 0x{:08X}".format(addr, ui))

def print_memory (addr, i):
    ui = int_to_unsigned(i)
    si = int_to_signed(i)
    print("0x{:08X}: 0x{:08X} {:12d}".format(addr, ui, si))

def print_register (num, i, end=None):
    ui = int_to_unsigned(i)
    si = int_to_signed(i)
    print("x{:<2d}=0x{:08X}({:11d})".format(num, ui, si), end=end)

def dump_register_file (reg):
    for i in range(32):
        end = None if (i & 0x3 == 0x3) else  ' '
        print_register(i, reg[i], end)

def dump_memory_instr(data):
    for addr in sorted(data.keys()):
        print_memory_instr(addr, data[addr])

def dump_memory(data):
    for addr in sorted(data.keys()):
        print_memory(addr, data[addr])

def dump_memory_str(data, start):
    c = data.get(start) 
    while c is not None: 
        print(chr(c), end='')
        start += 4
        c = data.get(start) 

def print_instruction (addr, i):
    print("0x{:08X}: 0x{:08X}".format(addr, i))

def print_cycle_number(cycle_num):
    print("==========Cycle {:5d}".format(cycle_num))

def print_signal(name, s, n = XLEN):
    """
    Input: Name, v, n
    Output: None
    """
    v = int(s) & ((1 << n) - 1)
    if (n == 1) : 
        print ("{}={}".format(name, v))
        return
    elif (n < 16) :
        s = "{:#0{}b}".format(v, n+2)
    else: 
        s = "{:#0{}X}".format(v, n // 4 + 2)
    print ("{}={} {}".format(name, s, (int_to_signed(v))))
    return 

def load_instructions(filename):
    """ load instructions from dump file
    """
    # load instructions from the file
    import re
    pattern = re.compile('^((0x)*([0-9A-Fa-f]+))\s+((0x)*([0-9A-Fa-f]+))')
    mem = {}
    with open(filename) as file:
        for line in file:
            m = re.search(pattern, line)
            if (m):
                address = int(m.group(1), 0)
                value = int(m.group(4), 0)
                mem[address] = value
                # print ("Mem[%s]=%s"% ( hex(address),hex(value)))
    return mem

def mem_set_string(data, start, s):
    for c in s:
        data[start] = ord(c)
        start += 4
    return data

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Test utility functions')
    parser.add_argument('--instruction', '-i', help='instruction dump file')
    parser.add_argument('--signal', '-s', action='store_true', help='print signals')
    parser.add_argument('--string', help='place and print a string in memory')
    parser.add_argument('-v', action='store_true', help='verbose')

    args = parser.parse_args()
    if args.v:
        print(args)

    if args.signal:
        print_signal("B1_0", 1, 1)
        print_signal("B1_1", 0xF, 1)
        print_signal("B5_0", 10, 5)
        print_signal("B5_1", 31, 5)
        print_signal("B7_0", 7, 7)
        print_signal("B7_1", 0xF7, 7)
        print_signal("B12_0", 0x123, 12)
        print_signal("B12_1", 0xCCC, 12)
        print_signal("B16_0", 0x1234, 16)
        print_signal("B16_1", 0xABCD, 16)
        print_signal("PC", 0x040000C4)
        print_signal("a0", -1)

    if args.instruction:
        mem = load_instructions(args.instruction)
        dump_memory(mem)
        dump_memory_instr(mem)

    if args.string:
        start = 1000
        mem = mem_set_string({}, start, args.string)
        dump_memory(mem)
        dump_memory_str(mem, start)

