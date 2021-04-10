from colorama import Fore

class Program:

    def __init__(self, start = 'main'):
        
        self.start = start
        self.lineno = 0
        self.labels = {}
        self.lines = []
        self.toresolve = []
    
    def addLine(self, line):

        self.lines.append(line)
        self.lineno += 1
    
    def addLabel(self, label):

        self.labels[label] = self.lineno
    
    def addPregen(self, pregen):

        self.lines.append(pregen)
        self.toresolve.append(self.lineno)
        self.lineno += 1
    
    def resolvePregen(self):
        
        for line in self.toresolve:

            pregen = self.lines[line]

            if pregen[0] == '.asciiz':
                self.lines[line] = pregen[1]
            
            elif pregen[0] == '.globl':
                self.start = pregen[1]
                self.lines[line] = pregen[0]
            
            elif pregen[0] == '.word':
                self.lines[line] = self.getAddr(pregen[1])
            
            else:
                self.lines[line] = pregen[0]
    
    def getAddr(self, label):
        
        if label not in self.labels:
            raise(RuntimeError(f"Could not find label {label}"))
        return self.labels[label]
    
    def getLine(self, index):
        
        if index % 4:
            raise(RuntimeError(f"Data index {str(index)} not multiple of 4"))
        i = int(index / 4)

        if 0 > i or i >= len(self.lines):
            # print('\n\t'.join(map(str, ((index*4, l) for index, l in enumerate(self.lines)))))
            raise(RuntimeError(f"Text index {str(i)} out of bounds (size {str(len(self.lines))})"))
        
        return self.lines[i]
    
    def __len__(self):

        return len(self.lines)

class Storage:

    def __init__(self, data = []):

        self.data = data
        self.center = 0
    
    def write(self, index, val):

        if index % 4:
            raise(RuntimeError(f"Data index {str(index)} not multiple of 4"))
        i = int(index / 4) + self.center

        if i < 0:
            self.center -= i
            self.data = [0] * -i + self.data
            i = 0
        
        elif i >= len(self.data):
            self.data += [0] * (1 + i - len(self.data))
        
        self.data[i] = val
        # print(f"{Fore.BLUE}{str(val)} written to {str(i)}")
    
    def read(self, index):

        if index % 4:
            raise(RuntimeError(f"Data index {str(index)} not multiple of 4"))
        i = int(index / 4) + self.center
        # print(f"{Fore.BLUE}{str(self.data[i])} read from {str(i)}")
        return self.data[i]