from colorama import Fore
from io import StringIO
import sys

from src import container
from src.mips_const import REGISTERS
from src.reporter import Reporter

DEBUGPRINT = False
REPORTPRINT = None

CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'

BRANCH = set()
MEMORY = set()

def branch_instr(f):
    BRANCH.add(str(f).split(' ')[1][2:].lower())
    return f

def memory_instr(f):
    MEMORY.add(str(f).split(' ')[1][2:].lower())
    return f

"""
I wanted to use these, but they interfere with accessing
the storage properly.
"""
# def UNSIGNED(n):
#     return n & ((1 << 32) - 1)

# def SIGNED(n):
#     se = -1 if n < 0 else 1
#     return se * ((se * n) & ((1 << 31) - 1))

class Simulator:
    
    def __init__(self, program: container.Program):

        self.program = program
        self.pc = self.program.getAddr(self.program.start)
        self.lastpc = self.pc

        self.reg = {r: 0 for r in REGISTERS}
        self.reg["$ra"] = -1
        self.reg["$gp"] = 1 << 16

        self.data = container.Storage(self.program.lines)
        self.allocptr = self.reg["$gp"]

        self.instr = {}
        for g in globals():
            if g[:2] == "i_":
                self.instr[g[2:]] = globals()[g]
        
        self.output = ""

        self.rep = Reporter([self.prettyLine(l) for l in self.program.lines])
    
    def printd(self, *s):
        if DEBUGPRINT:
            line = self.program.getLine(self.lastpc*4)

            col = Fore.RESET
            if line[0] in BRANCH:
                col = Fore.GREEN
            elif line[0] in MEMORY:
                col = Fore.CYAN
            elif line[0] == "syscall":
                col = Fore.MAGENTA
            
            print(
                col + str(self.lastpc),
                ' '*(7-len(str(self.lastpc))),
                self.prettyLine(line),
                ' '.join(map(str, s))
            )
    
    def printo(self, *s):

        self.output += ''.join(map(str, s))

    def printOutput(self):

        print(Fore.RESET)
        print(self.output)
    
    def clearOutput(self):

        pass
        # sys.stdout.write("\x1b[s")
        # for _ in range(self.output.count('\n') + 3):
        #     sys.stdout.write(CURSOR_UP_ONE)
        # sys.stdout.write("\x1b[J")
        # sys.stdout.write("\x1b[u")
    
    def prettyArg(self, arg):
        if type(arg) == str:
            return arg
        if arg[0] == 0:
            return arg[1]
        if arg[1] == "$0":
            return str(arg[0])
        return f"{str(arg[0])}({arg[1]})"
    
    def prettyLine(self, line):

        if type(line) != list:
            return str(line)
    
        if len(line) == 1:
            return line[0]

        toret = line[0] + ' ' + ' '.join(map(self.prettyArg, line[1]))
        a = 28 - len(toret)
        if a > 0:
            toret += ' ' * a
        return toret

    def resolveArg(self, arg):

        if type(arg) == tuple:
            return int(arg[0]) + self.reg[arg[1]]
        
        else:
            return self.program.getAddr(arg)
    
    def writeToReg(self, dest, val):
        
        rd = dest if type(dest) == str else dest[1]
        self.reg[rd] = val
    
    def readFromReg(self, dest):
        
        rd = dest if type(dest) == str else dest[1]
        return self.reg[rd]
    
    def writeData(self, arg, val):
        
        offset, pointer = arg
        index = self.resolveArg(arg)
        self.data.write(index, val)
    
    def readData(self, arg):

        offset, pointer = arg
        index = self.resolveArg(arg)
        return self.data.read(index)
    
    def branchTo(self, lineno):

        self.pc = lineno - 1
    
    def runLine(self):

        line = self.program.getLine(self.pc*4)
        self.lastpc = self.pc

        if type(line) == list:

            instr = line[0].upper()

            if len(line) > 1:
                args = line[1]
            else:
                args = []
            
            try:
                self.instr[instr](self, args)
                self.rep.addInstr(
                    self.lastpc,
                    instr.lower() in MEMORY,
                    instr.lower() in BRANCH
                )
            except Exception as e:
                if type(e) == KeyError:
                    print(Fore.MAGENTA)
                    print(f"Could not find instruction {str(e)}")
                else:
                    print(Fore.RED)
                    print(e)
                print(Fore.RESET)
        
        self.pc += 1
    
    def run(self):
        while self.pc >= 0:
            self.runLine()
        
        if REPORTPRINT == "print":
            print(str(self.rep))
        elif REPORTPRINT:
            with open(REPORTPRINT, 'w', encoding = 'utf-8') as f:
                f.write(str(self.rep))
                f.write('\n----- Output  -----\n\n')
                f.write(self.output)
        
        self.printOutput()

def i_ADD(self, args):
    rd, rs, rt = args
    t0, t1 = self.resolveArg(rs), self.resolveArg(rt)
    t2 = t0 + t1
    self.writeToReg(rd, t2)
    self.printd(rd[1], ":=", t2, "(", t0, "+", t1, ")")

def i_ADDI(self, args):
    rd, rs, imm = args
    t0, t1 = self.resolveArg(rs), self.resolveArg(imm)
    t2 = t0 + t1
    self.writeToReg(rd, t2)
    self.printd(rd[1], ":=", t2, "(", t0, "+", t1, ")")

def i_ADDIU(self, args):
    rd, rs, imm = args
    t0, t1 = self.resolveArg(rs), self.resolveArg(imm)
    t2 = t0 + t1
    self.writeToReg(rd, t2)
    self.printd(rd[1], ":=", t2, "(", t0, "+", t1, ")")

def i_AND(self, args):
    rd, rs, rt = args
    t0, t1 = self.resolveArg(rs), self.resolveArg(rt)
    t2 = t0 & t1
    self.writeToReg(rd, t2)
    self.printd(rd[1], ":=", t0, "&", t1)

@branch_instr
def i_B(self, args):
    off = args[0]
    if type(off) == str:
        t1 = self.resolveArg(off)
        t0 = t1 -  self.pc
    else:
        t0 = self.resolveArg(off)
        t1 = self.pc + t0
    self.branchTo(t1)
    self.printd("goto pc +", t0, "=", t1)

@branch_instr
def i_BEQ(self, args):
    rs, rt, ra = args
    t0, t1 = self.resolveArg(rs), self.resolveArg(rt)
    if t0 == t1:
        t2 = self.resolveArg(ra)
        self.branchTo(t2)
        self.printd("goto", t2, "(", t0, "=", t1, ")")
    else:
        self.printd("(", t0, "!=", t1, ")")

@branch_instr
def i_BEQZ(self, args):
    rs, ra = args
    t0 = self.resolveArg(rs)
    if t0 == 0:
        t1 = self.resolveArg(ra)
        self.branchTo(t1)
        self.printd("goto", t1, "(", t0, "= 0 )")
    else:
        self.printd("(", t0, "!= 0 )")

@branch_instr
def i_BNE(self, args):
    rs, rt, ra = args
    t0, t1 = self.resolveArg(rs), self.resolveArg(rt)
    if t0 != t1:
        t2 = self.resolveArg(ra)
        self.branchTo(t2)
        self.printd("goto", t2, "(", t0, "!=", t1, ")")
    else:
        self.printd("(", t0, "=", t1, ")")

@branch_instr
def i_BNEZ(self, args):
    rs, ra = args
    t0 = self.resolveArg(rs)
    if t0 != 0:
        t1 = self.resolveArg(ra)
        self.branchTo(t1)
        self.printd("goto", t1, "(", t0, "!= 0 )")
    else:
        self.printd("(", t0, "= 0 )")

def i_DIV(self, args):
    rd, rs, rt = args
    t0, t1 = self.resolveArg(rs), self.resolveArg(rt)
    t2 = int(t0 / t1)
    self.writeToReg(rd, t2)
    self.printd(rd[1], ":=", t2, "(", t0, "/", t1, ")")

@branch_instr
def i_J(self, args):
    ra = args[0]
    t0 = self.resolveArg(ra)
    self.branchTo(t0)
    self.printd("goto", t0)

@branch_instr
def i_JAL(self, args):
    ra = args[0]
    t0 = self.resolveArg(ra)
    t1 = self.pc + 1
    self.writeToReg("$ra", t1)
    self.branchTo(t0)
    self.printd("goto", t0, "( ra :=", t1, ")")

@branch_instr
def i_JALR(self, args):
    if len(args) == 1:
        rd, rs = "$ra", args[0]
    else:
        rd, rs = args
    t0 = self.resolveArg(rs)
    t1 = self.pc + 1
    self.writeToReg(rd, t1)
    self.branchTo(t0)
    self.printd("goto", t0, "( ra :=", t1, ")")
    
@branch_instr
def i_JR(self, args):
    ra = args[0]
    t0 = self.resolveArg(ra)
    self.pc = t0 - 1
    self.printd("goto", t0)

# @memory_instr
def i_LB(self, args):
    """
    See SB
    """
    # rd, pos = args
    # t0 = self.readData(pos)
    # se = -1 if t0 < 0 else 1    # sign extension
    # t1 = (se * t0) & ((1 << 8) - 1)
    # t1 *= se
    # self.writeToReg(rd, t1)
    # self.printd(rd[1], ":=", t1, "from", pos)
    rd, pos = args
    self.writeToReg(rd, 0)
    self.printd(rd[1], ":= 0 ( don't judge me )")

@memory_instr
def i_LBU(self, args):
    rd, pos = args
    t0 = self.readData(pos)
    t0 = t0 & ((1 << 8) - 1)
    self.writeToReg(rd, t0)
    self.printd(rd[1], ":=", t0, "from", pos)

def i_LA(self, args):
    rd, ra = args
    t0 = self.resolveArg(ra) * 4
    self.writeToReg(rd, t0)
    self.printd(rd[1], ":=", t0)

def i_LI(self, args):
    rd, imm = args
    t0 = self.resolveArg(imm)
    self.writeToReg(rd, t0)
    self.printd(rd[1], ":=", t0)

@memory_instr
def i_LW(self, args):
    rd, pos = args
    t0 = self.readData(pos)
    self.writeToReg(rd, t0)
    self.printd(rd[1], ":=", t0, "from", pos)

def i_MOVE(self, args):
    rd, rs = args
    t0 = self.readFromReg(rs)
    self.writeToReg(rd, t0)
    self.printd(rd[1], ":=", t0)

def i_MUL(self, args):
    rd, rs, rt = args
    t0, t1 = self.resolveArg(rs), self.resolveArg(rt)
    t2 = t0 * t1
    self.writeToReg(rd, t2)
    self.printd(rd[1], ":=", t2, "(", t0, "*", t1, ")")

def i_OR(self, args):
    rd, rs, rt = args
    t0, t1 = self.resolveArg(rs), self.resolveArg(rt)
    t2 = t0 | t1
    self.writeToReg(rd, t2)
    self.printd(rd[1], ":=", t0, "|", t1)

def i_REM(self, args):
    rd, rs, rt = args
    t0, t1 = self.resolveArg(rs), self.resolveArg(rt)
    t2 = t0 % t1
    self.writeToReg(rd, t2)
    self.printd(rd[1], ":=", t0, "%", t1)

def i_SB(self, args):
    """
    Ok, hear me out.

    I can only find this used in '_ReadLine', where it
    adds the newline character to the end of a string.
    We're using Python strings, so there is no need
    for this specific instance of this instruction.
    
    UNLESS cases come up later where this is needed,
    I'm going to leave this blank.  Adding functionality
    will require reworking of storage or syscall 8.
    """
    """
    EDIT: The instruction that causes the loop in
    _ReadLine is, by default, commented out (???).  So
    I'm just going to assume simulators ignore this
    whole section, and I'll leave SB and LB commented
    out.
    """
    pass

def i_SEQ(self, args):
    rd, rs, rt = args
    t0, t1 = self.resolveArg(rs), self.resolveArg(rt)
    t2 = 1 if t0 == t1 else 0
    self.writeToReg(rd, t2)
    self.printd(rd[1], ":=", t2, "(", t0, "=" if t2 else "!=", t1, ")")

def i_SLT(self, args):
    rd, rs, rt = args
    t0, t1 = self.resolveArg(rs), self.resolveArg(rt)
    t2 = 1 if t0 < t1 else 0
    self.writeToReg(rd, t2)
    self.printd(rd[1], ":=", t2, "(", t0, "<" if t2 else ">=", t1, ")")

"""
Custom Instruction
Checks whether two Python strings are equal
"""
def i_STRE(self, args):
    rd, rs, rt = args
    p0, p1 = self.resolveArg(rs), self.resolveArg(rt)
    t0, t1 = self.readData((p0, "$0")), self.readData((p1, "$0"))
    t2 = 0
    if type(t0) == str and type(t1) == str:
        t2 = 1 if t0 == t1 else 0
    self.writeToReg(rd, t2)
    self.printd(rd[1], ":=", t2, "(", t0, "=" if t2 else "!=", t1, ")")

def i_SUB(self, args):
    rd, rs, rt = args
    t0, t1 = self.resolveArg(rs), self.resolveArg(rt)
    t2 = t0 - t1
    self.writeToReg(rd, t2)
    self.printd(rd[1], ":=", t2, "(", t0, "-", t1, ")")

def i_SUBU(self, args):
    rd, rs, rt = args
    t0, t1 = self.resolveArg(rs), self.resolveArg(rt)
    t2 = t0 - t1
    self.writeToReg(rd, t2)
    self.printd(rd[1], ":=", t2, "(", t0, "-", t1, ")")

@memory_instr
def i_SW(self, args):
    rt, pos = args
    t0 = self.resolveArg(rt)
    self.writeData(pos, t0)
    self.printd(pos, "<-", t0)

def i_SYSCALL(self, args):
    v0 = self.readFromReg("$v0")

    # PrintInt
    if v0 == 1:
        a0 = self.readFromReg("$a0")
        self.printo(a0)
        self.printd("cout <<", a0)
    
    # PrintString
    elif v0 == 4:
        a0 = self.readFromReg("$a0")
        a1 = self.readData((a0, "$0"))
        self.printo(a1)
        self.printd("cout <<", a1)

    #ReadInt
    elif v0 == 5:
        self.printOutput()
        txt = input()
        t0 = int(txt)
        self.writeToReg("$v0", t0)
        self.printd("$v0 :=", t0)
        self.clearOutput()
        self.printo(Fore.YELLOW + txt + Fore.RESET + "\n")
    
    # ReadLine
    # Look, this shouldn't be input(), but I don't feel like doing io just yet
    elif v0 == 8:
        self.printOutput()
        txt = input()
        self.writeData((0, "$a0"), txt)
        self.printd("(0, '$a0') <-", txt)
        self.clearOutput()
        self.printo(Fore.YELLOW + txt + Fore.RESET + "\n")

    # Alloc Heap Memory
    elif v0 == 9:
        a0 = self.readFromReg("$a0")
        self.allocptr -= a0 * 4
        self.writeToReg("$v0", self.allocptr)
        self.printd("$v0 :=", self.allocptr, "alloc on heap")
    
    # Halt
    elif v0 == 10:
        self.pc = -2
        self.printd("halt")
    
    # Syscall $v0 not found
    else:
        raise(RuntimeError(f"Failed syscall {str(v0)}"))

if __name__ == "__main__":
    import parsemips
    with open("sort.s", 'r') as f:
        p = parsemips.parseCode(f.read())
    sim = Simulator(p)
    sim.run()