# Copyright 2021-2023 Zhijie Shi. All rights reserved. See LICENSE.txt.
from myhdl import Signal, intbv, modbv

from utilities import print_signal, print_instruction, print_cycle_number

XLEN = 32

class RISCVSignals: 
    """ Define all the signals in the single-cycle processor. """
    def __init__(self, initPC):
        """ initialize the object. Create all signals.

        Args:
            initPC: the address of the first instruction.
        """

        # always 0 and always 1 signals
        self.signal1 = Signal(bool(1))
        self.signal0 = Signal(bool(0))

        self.PC = Signal(intbv(initPC)[XLEN:])
        self.Const4 = Signal(intbv(4)[XLEN:])       # constant 4
        self.PC4 = Signal(modbv(0)[XLEN:])          # PC + 4
        
        # IMem
        self.instruction = Signal(intbv(0x13)[32:]) # initialized to NOP

        # signals that are extracted from instruction  
        # these are shadow signals
        # when instruction changes, these signals will change too
        self.opcode = self.instruction(7, 0)
        self.rd = self.instruction(12, 7)
        self.funct3 = self.instruction(15, 12)
        self.rs1 = self.instruction(20, 15)
        self.rs2 = self.instruction(25, 20)
        self.funct7 = self.instruction(32,25)
        self.instr30 = self.instruction(30)

        # immediate
        self.immediate = Signal(modbv(0)[XLEN:])

        # output of the main control, generated from opcode 
        self.Branch, self.ALUSrc, self.MemRead, self.MemWrite, self.MemtoReg, self.RegWrite = \
                [ Signal(bool(0)) for i in range(6) ]

        self.ALUOp = Signal(intbv(0)[2:])

        self.ALUOperation = Signal(intbv(0)[4:])

        self.BranchTarget = Signal(modbv(0)[XLEN:])

        # Register File
        self.ReadData1 = Signal(intbv(0)[XLEN:])
        self.ReadData2 = Signal(intbv(0)[XLEN:])

        # second input to ALU
        # ReadData2 or immediate
        self.ALUInput2 = Signal(intbv(0)[XLEN:])

        # ALU
        self.ALUResult = Signal(modbv(0)[XLEN:])
        self.Zero = Signal(bool(0))

        # DMem
        self.MemReadData = Signal(modbv(0)[XLEN:])

        # data to be written into RF
        # ALUResult or MemReadData
        self.WriteData = Signal(intbv(0)[XLEN:])

        # PCSrc 
        # PC4 or BranchTarget for NextPC
        self.PCSrc = Signal(bool(0))

        # nextPC, the address of the instruction to be executed 
        # in the next cycle
        self.NextPC = Signal(0)

    def print(self, cyclenum = 0, options=""):
        """ Print all signals.

        Args:
            cyclenum:   Cycle number
            options:    Not used for now.
        """
        print_cycle_number(cyclenum)
        print_instruction(int(self.PC), int(self.instruction))
        print_signal("opcode", self.opcode, 7);
        print_signal("funct7", self.funct7, 7);
        print_signal("funct3", self.funct3, 3);
        print_signal("rs1", self.rs1, 5);
        print_signal("rs2", self.rs2, 5);
        print_signal("rd", self.rd, 5);
        print_signal("immediate", self.immediate);
        print_signal("Branch", self.Branch, 1);
        print_signal("MemRead", self.MemRead, 1);
        print_signal("MemtoReg", self.MemtoReg, 1);
        print_signal("ALUOp", self.ALUOp, 2);
        print_signal("MemWrite", self.MemWrite, 1);
        print_signal("ALUSrc", self.ALUSrc, 1);
        print_signal("RegWrite", self.RegWrite, 1);
        print_signal("ALUOperation", self.ALUOperation, 4);
        print_signal("BranchTarget", self.BranchTarget);
        print_signal("ReadData1", self.ReadData1);
        print_signal("ReadData2", self.ReadData2);
        print_signal("ALUInput2", self.ALUInput2);
        print_signal("ALUResult", self.ALUResult);
        print_signal("Zero", self.Zero, 1);
        print_signal("MemReadData", self.MemReadData);
        print_signal("WriteData", self.WriteData);
        print_signal("PCSrc", self.PCSrc, 1);
        print_signal("NextPC", self.NextPC);

if __name__ == '__main__':
    sig = RVSignals(0x4000)
    sig.print()
