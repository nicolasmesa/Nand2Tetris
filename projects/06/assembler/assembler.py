import argparse
import re

ap = argparse.ArgumentParser()
ap.add_argument('-i', '--input', help='Input file', required=True)
ap.add_argument('-o', '--output', help='Output file', required=False, default="out.hack")
ap.add_argument('-v', '--verbose', action='store_true')

args = vars(ap.parse_args())

verbose = args['verbose']
inputFileName = args['input']
outputFileName = args['output']

jmpDict = {
    'JGT': '001',
    'JEQ': '010',
    'JGE': '011',
    'JLT': '100',
    'JNE': '101',
    'JLE': '110',
    'JMP': '111'
}

compDict = {
    '0':    '101010',
    '1':    '111111',
    '-1':   '111010',
    'D':    '001100',
    'X':    '110000',
    '!D':   '001101',
    '!X':   '110001',
    '-D':   '001111',
    '-X':   '110011',
    'D+1':  '011111',
    '1+D':  '011111',
    'X+1':  '110111',
    '1+X':  '110111',
    'D-1':  '001110',
    'X-1':  '110010',
    'D+X':  '000010',
    'X+D':  '000010',
    'D-X':  '010011',
    'X-D':  '000111',
    'D&X':  '000000',
    'X&D':  '000000',
    'D|X':  '010101',
    'X|D':  '010101'
}

def log(msg):
    if verbose:
        print msg


log('Openning input file ' + inputFileName)
inputFile = open(inputFileName, 'r')
log(inputFileName + ' has been opened')

log('Opening output file')
outputFile = open(outputFileName, 'w')
log(outputFileName + ' has been opened')

def getInstructionText(line):
    line = line.split("//")[0]
    line = line.strip()

    if (line == "" or line == "\n"):
        return None

    return line

def isLabel(instructionText):
    if instructionText.startswith('(') and instructionText.endswith(')'):
        return True
    return False

def getLabel(instructionText):
    return instructionText.replace('(', '').replace(')', '')

def isAInstruction(instructionText):
    return instructionText.startswith('@')

def getAInstruction(aInstruction, st):
    translated = getAInstructionTranslation(aInstruction, st)
    return '@' + str(translated)

def getAInstructionTranslation(aInstruction, st):
    instruction = aInstruction.replace('@', '')

    if re.match(r'^[0-9]+$', instruction):
        return instruction

    return st.addAndGetVariable(instruction)

def getBinaryString(number):
    if number == 0:
        return '0'

    binary = ''
    while number != 0:
        binary = str(number % 2) + binary
        number /= 2
    return binary

def getPaddedBinaryString(number):
    binary = getBinaryString(number)
    while len(binary) < 16:
        binary = '0' + binary
    return binary

def getAInstructionBinary(aInstruction):
    instruction = aInstruction.replace('@', '')
    number = int(instruction)
    return getPaddedBinaryString(number)

def getCInstructionParts(instructionText):
    destRest = instructionText.split('=')
    dest = None
    comp = None
    jmp = None

    if len(destRest) == 2:
        dest, instructionText = destRest

    instJmp = instructionText.split(';')
    comp = instructionText

    if len(instJmp) == 2:
        comp, jmp = instJmp

    return dest, comp, jmp

def getCInstructionBinary(instructionText):
    binary = '111'
    dest, comp, jmp = getCInstructionParts(instructionText)

    binary += getCompInstructionBinary(comp)
    binary += getDestBinary(dest)
    binary += getJmpBinary(jmp)

    return binary


def getCompInstructionBinary(comp):
    global compDict
    a = '0'

    if comp.find('M') > -1:
        a = '1'

    comp = comp.replace('A', 'X')
    comp = comp.replace('M', 'X')

    return a + compDict[comp]



def getDestBinary(dest):
    if dest == None:
        return '000'

    mText = '0'
    dText = '0'
    aText = '0'

    if dest.find('M') > -1:
        mText = '1'

    if dest.find('D') > -1:
        dText = '1'

    if dest.find('A') > -1:
        aText = '1'

    return aText + dText + mText

def getJmpBinary(jmp):
    global jmpDict
    if jmp == None:
        return '000'
    return jmpDict[jmp]


class SymbolTable:
    def __init__(self):
        self.init()

    def init(self):
        self.currVarAddress = 0
        self.table = {}
        self.__addVars()

    def addLabel(self, label, address):
        self.__addSymbol(label, address)

    def addVariable(self, varName):
        self.__addSymbol(varName, self.currVarAddress)

        print(varName + "\t" + str(self.currVarAddress))

        self.currVarAddress += 1

    def addAndGetVariable(self, varName):
        if not self.table.has_key(varName):
            self.addVariable(varName)
        return self.table[varName]

    def getSymbol(self, symbol):
        return self.table[symbol]

    def __addVars(self):
        self.__addRs()
        self.__addPredefinedSymbols()

    def __addRs(self):
        for i in range(16):
            self.addVariable("R" + str(i))

    def __addPredefinedSymbols(self):
        self.__addSymbol("SCREEN", 16384)
        self.__addSymbol("KBD", 24567)
        self.__addSymbol("SP", 0)
        self.__addSymbol("LCL", 1)
        self.__addSymbol("ARG", 2)
        self.__addSymbol("THIS", 3)
        self.__addSymbol("THAT", 4)

    def __addSymbol(self, symbol, address):
        self.table[symbol] = address

log('Initializing symbol table')
st = SymbolTable()
instructionCounter = 0

log('Starting first pass')
for line in inputFile:
    line = line.rstrip('\n')

    instructionText = getInstructionText(line)

    if not instructionText:
        continue

    if isLabel(instructionText):
        label = getLabel(instructionText)
        st.addLabel(label, instructionCounter)
        continue

    instructionCounter += 1

log('Done with first pass')

inputFile.seek(0)

log('Starting second pass')

instructionCounter = 0
for line in inputFile:
    line = line.rstrip('\n')

    instructionText = getInstructionText(line)

    if not instructionText:
        continue

    if isLabel(instructionText):
        continue

    binaryText = ''

    if isAInstruction(instructionText):
        instructionText = getAInstruction(instructionText, st)
        binaryText = getAInstructionBinary(instructionText)
    else:
        binaryText = getCInstructionBinary(instructionText)

    outputFile.write(binaryText + "\n")

    log(str(instructionCounter) + "\t" + instructionText + "\t" + binaryText)
    instructionCounter += 1

log('Done with second pass')

log('Closing input file')
inputFile.close()
log('Input file closed')

log('Closing output file')
outputFile.close()
log('Output file closed')
