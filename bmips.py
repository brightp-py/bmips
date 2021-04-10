import sys
from src import simulator, parsemips

if len(sys.argv) < 2:
    print("FAILED: Expected a file name.")
    print("'python bmips.py [filename] (-d)'")
    sys.exit()

simulator.DEBUGPRINT = False
simulator.REPORTPRINT = None

wantreportfile = False
for arg in sys.argv[2:]:
    if wantreportfile:
        if arg[0] != "-":
            simulator.REPORTPRINT = arg
        else:
            simulator.REPORTPRINT = "print"
        wantreportfile = False
    if arg == "-d":
        simulator.DEBUGPRINT = True
    elif arg == "-r":
        wantreportfile = True

if "-d" in sys.argv[2:]:
    simulator.DEBUGPRINT = True

with open(sys.argv[1], 'r') as f:
    p = parsemips.parseCode(f.read())

sim = simulator.Simulator(p)
sim.run()