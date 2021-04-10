class Reporter:

    def __init__(self, lines):

        self.length = len(lines)
        self.lines = lines
        self.counts = [0] * self.length
        self.totals = {
            "ALL": 0,
            "MEM": 0,
            "BCH": 0,
            "ETC": 0
        }
    
    def addInstr(self, lineno, ismem, isbch):
        
        if isbch:
            cycles = 2
            self.totals["BCH"] += cycles
        
        elif ismem:
            cycles = 10
            self.totals["MEM"] += cycles
        
        else:
            cycles = 1
            self.totals["ETC"] += cycles
        
        self.totals["ALL"] += cycles
        self.counts[lineno] += cycles
        # self.counts[lineno][','.join(map(str, args))] += cycles

    def __str__(self):
        
        toret = "\n"

        bpercent = round(100 * self.totals["BCH"] / self.totals["ALL"], 2)
        mpercent = round(100 * self.totals["MEM"] / self.totals["ALL"], 2)
        opercent = round(100 * self.totals["ETC"] / self.totals["ALL"], 2)

        toret += "----- Summary -----\n"
        toret += f"Total: {str(self.totals['ALL'])} cycles\n"
        toret += f"Branch: {str(self.totals['BCH'])} ({str(bpercent)} %)\n"
        toret += f"Memory: {str(self.totals['MEM'])} ({str(mpercent)} %)\n"
        toret += f"Others: {str(self.totals['ETC'])} ({str(opercent)} %)\n"
        toret += "-------------------\n\n"
        needsEllipsis = True

        for i, c in enumerate(self.counts):
            line = self.lines[i]
            if c == 0:
                if needsEllipsis:
                    toret += "⋮\n"
                needsEllipsis = False
                continue
            toret += f"{str(i)}\t{str(c)}\t{line}\n"
            needsEllipsis = True
        
        return toret