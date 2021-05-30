"""
    Projekt do IPP
    interpret.py

    Ales Jaksik
        xjaksi01

"""

# -------------------- KNIHOVNY A POPIS/NAPOVEDA ------------------------------

from xml.etree.ElementTree import *
import getopt
from sys import *
from enum import Enum
from io import StringIO

# popis programu
def callHelp():
    print("------------------- HELP ------------------")
    print(" Program nacte XML reprezentaci programu a")
    print(" tento program s vyuzitim vstupu dle para-")
    print(" metru prikazove radky interpretuje a gen-")
    print(" eruje vystup")
    print(" Parametry pro script:")
    print("    --help .......... napoveda")
    print("    --source=file ... svtupni soubor s XML")
    print("    --input=file .... svtup pro read")
    print("-------------------------------------------")



# -------------------- POMOCNE VELICINY A MISTO -------------------------------

# seznam datovych typu
class dataType(Enum):
    INT = 1
    BOOL = 2
    STRING = 3
    NIL = 4

# seznamy promennych
class Frames:
    globalFrame = list()
    globalValues = list()

    localFrame = list()
    localValues = list()
    
    tempFrame = list()
    tempValues = list()

    labelList = list()
    stack = list()

# globalni promenne
class GlobalVariable:
    labelOrder = 0
    indx = 0


# -------------------------- ZPRACOVANI ARGUMENTU -----------------------------


# moznosti
options = ["help", "source=", "input="]

# ziskani hodnot
try:
    arg, val = getopt.getopt(argv[1:],"", options)
except getopt.error:
    exit(10)

source = ""
input = ""
inputIs = False

# projiti a zjisteni
for argNow, argVal in arg:
    if argNow in ("--help"):
        callHelp()
        exit(0)
    elif argNow in ("--source"):
        source = argVal
    elif argNow in ("--input"):
        input = argVal
        inputIs = True
    else:
        print("spatne argumenty")
        exit(10)

if source == "":
    temp = list()
    iterator = True
    while iterator == True:
        try:
            line = input()
            if line:
                temp.append(line)
            else:
                break
        except EOFError as e:
            iterator = False
    inFile = '\n'.join(temp)
    source = StringIO(inFile)

if inputIs:
    with open(input, 'r') as file:
        input = file.read()



#-------------------------------- PARSER --------------------------------------
# parsovani
# trizeni instrukci a volani kontrol
class Parser:
    
    # hlavni funkce parsovani
    def XParse(source):
        # parsovaci funkce z importoane knihovny
        # pokud chyba exit
        try:
            res = parse(source)
            prog = res.getroot()
        except ParseError:
            exit(31)

        # kontrola udaju v hlavicce
        if prog.tag != 'program' or prog.attrib.get('language') != 'IPPcode21':
            exit(32)   # chybna struktura
        if len(prog.attrib) > 3:
            exit(32)

        # pocitadlo order
        ord = 0

        instructions = list()

        # for projde instrukce, zkontroluje poradi a nahraje do seznamu
        for x in prog:
            if x.tag != 'instruction':
                exit(32)
            if int(x.attrib.get('order')) <= 0:
                exit(32)

            instructions.append(x)
            if x.attrib.get('opcode') == "LABEL":
                GlobalVariable.labelOrder = ord
                CheckDo.Label(x)
            elif x.attrib.get('opcode') == "CALL":
                GlobalVariable.labelOrder = ord
                CheckDo.CallSet(x)
            ord += 1
        
        while GlobalVariable.indx < ord:
            if GlobalVariable.indx == ord:
                exit(0)

            if instructions[GlobalVariable.indx].attrib.get('opcode') != "LABEL":
                GlobalVariable.indx = Parser.__Ins(instructions[GlobalVariable.indx])
            else:
                GlobalVariable.indx += 1

    # trizeni a volani spravne funkce
    def __Ins(ins):
        inst = ins.attrib.get('opcode')

        if inst == 'MOVE':
            return CheckDo.Move(ins)
        elif inst == 'CREATEFRAME':
            return CheckDo.CreateFrame(ins)
        elif inst == 'PUSHFRAME':
            return CheckDo.PushFrame(ins)
        elif inst == 'POPFRAME':
            return CheckDo.PopFrame(ins)
        elif inst == 'DEFVAR':
            return CheckDo.DefVar(ins)
        elif inst == 'CALL':
            return CheckDo.Call(ins)
        elif inst == 'RETURN':
            return CheckDo.Return(ins)
        elif inst == 'PUSHS':
            return CheckDo.Pushs(ins)
        elif inst == 'POPS':
            return CheckDo.Pops(ins)
        elif inst == 'ADD':
            return CheckDo.Add(ins)
        elif inst == 'SUB':
            return CheckDo.Sub(ins)
        elif inst == 'MUL':
            return CheckDo.Mul(ins)
        elif inst == 'IDIV':
            return CheckDo.Idiv(ins)
        elif inst == 'LT':
            return CheckDo.Lt(ins)
        elif inst == 'GT':
            return CheckDo.Gt(ins)
        elif inst == 'EQ':
            return CheckDo.Eq(ins)
        elif inst == 'AND':
            return CheckDo.And(ins)
        elif inst == 'OR':
            return CheckDo.Or(ins)
        elif inst == 'NOT':
            return CheckDo.Not(ins)
        elif inst == 'INT2CHAR':
            return CheckDo.Int2Char(ins)
        elif inst == 'STRI2INT':
            return CheckDo.Stri2Int(ins)
        elif inst == 'READ':
            return CheckDo.Read(ins)
        elif inst == 'WRITE':
            return CheckDo.Write(ins)
        elif inst == 'CONCAT':
            return CheckDo.Concat(ins)
        elif inst == 'STRLEN':
            return CheckDo.StrLen(ins)
        elif inst == 'GETCHAR':
            return CheckDo.GetChar(ins)
        elif inst == 'SETCHAR':
            return CheckDo.SetChar(ins)
        elif inst == 'TYPE':
            return CheckDo.Type(ins)
        elif inst == 'LABEL':
            return CheckDo.Label(ins)
        elif inst == 'JUMP':
            return CheckDo.Jump(ins)
        elif inst == 'JUMPIFEQ':
            return CheckDo.JumpIfEq(ins)
        elif inst == 'JUMPIFNEQ':
            return CheckDo.JumpIfNEq(ins)
        elif inst == 'EXIT':
            return CheckDo.Exit(ins)
        elif inst == 'DPRINT':
            return CheckDo.DPrint(ins)
        elif inst == 'BREAK':
            return CheckDo.Break(ins)
        else:
            exit(32)


# -------------------- TRIDA KONTROL A VYKONANI -------------------------------
class CheckDo:

    # projde argumenty instrukce a vlozi je do seznamu
    def __listOfArg(ins):
        try:
            argsType = list()
            argsText = list()
            for x in ins:
                argsType.append(x.attrib.get('type'))
                argsText.append(x.text)
        except:
            exit(32)

        return argsType, argsText

    # kontrola symb, pokud var: [0]=True, jinak [1]=dataType
    def __symbCheck(symb):
        if symb == 'int':
            return False, dataType.INT
        elif symb == 'bool':
            return False, dataType.BOOL
        elif symb == 'string':
            return False, dataType.STRING
        elif symb == "":
            return False, dataType.NIL
        elif symb == 'var':
            return True, 0
        else:
            exit(32)

    # najde var a vrati jeho hodnotu
    def __VarValue(item):
        try:
            symbolText = item.split("@")
        except:
            exit(32)


        if symbolText[0] == "GF":
            if symbolText[1] in Frames.globalFrame:
                indx = Frames.globalFrame.index(symbolText[1])
                value = Frames.globalValues[indx]
            else:
                exit(52)
        elif symbolText[0] == "LF":
            if symbolText[1] in Frames.localFrame:
                indx = Frames.localFrame.index(symbolText[1])
                value = Frames.localValues[indx]
            else:
                exit(55)
        elif symbolText[0] == "TF":
            if symbolText[1] in Frames.tempFrame:
                indx = Frames.tempFrame.index(symbolText[1])
                value = Frames.tempValues[indx]
            else:
                exit(55)
        else:
            exit(32)

        return value

    # ulozi hodnotu do var
    def __VarSave(var, value):
        try:
            varText = var.split("@")
        except:
            exit(32)
        # v prvnim argumentu je var, zjistuji ramec, jestli existuje, index a ulozim
        if varText[0] == "GF":
            if varText[1] in Frames.globalFrame:
                indx = Frames.globalFrame.index(varText[1])
                Frames.globalValues[indx] = value
            else:
                exit(52)
        elif varText[0] == "LF":
            if varText[1] in Frames.localFrame:
                indx = Frames.localFrame.index(varText[1])
                Frames.localValues[indx] = value
            else:
                exit(52)
        elif varText[0] == "TF":
            if varText[1] in Frames.tempFrame:
                indx = Frames.tempFrame.index(varText[1])
                Frames.tempValues[indx] = value
            else:
                exit(52)
        else:
            exit(32)

    # zjisti datovy typ symb
    def __SymbType(typ, value):
        isVar1, type1 = CheckDo.__symbCheck(typ)

        if isVar1:
            item = CheckDo.__VarValue(value)
            if isinstance(item, bool):
                return dataType.BOOL, item
            elif isinstance(item, str):
                return dataType.STRING, item
            elif isinstance(item, int):
                return dataType.INT, item
            else:
                exit(32)
        else:
            if type1 == dataType.INT:
                try:
                    item = int(value)
                except:
                    exit(32)
                return dataType.INT, item
            elif type1 == dataType.STRING:
                return dataType.STRING, value
            elif type1 == dataType.BOOL :
                if value == 'true':
                    item = True
                elif value == 'false':
                    item = False
                else:
                    exit(32)
                return dataType.BOOL, item
            else:
                exit(32)

    # MOVE chce dva argumenty, kam se vklada a co se vklada
    def Move(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 2:
            exit(32)

        if argsType[0] != 'var':
            exit(32)

        isVar, type = CheckDo.__symbCheck(argsType[1])
        
        # pokud je symbol var, musim zjistit ramec a nazev
        if isVar:
            value = CheckDo.__VarValue(argsText[1])
        # pokud je symb neVar nahraji hodnotu
        else:
            if type == dataType.INT:
                try:    
                    value = int(argsText[1])
                except:
                    exit(32)
            elif type == dataType.BOOL:
                if argsText[1] == "true":
                    value = True
                elif argsText[1] == "false":
                    value = False
                else:
                    exit(32)
            elif type == dataType.STRING:
                value = argsText[1]
            else:
                exit(99)

        # vlozeni hodnoty
        CheckDo.__VarSave(argsText[0], value)
        return GlobalVariable.indx + 1
        

    # CREATEFRAME vytvori novy docasny ramec a smaze predchozi
    def CreateFrame(instruction):
        Frames.tempFrame.clear()
        Frames.tempValues.clear()
        Frames.tempFrame.insert(0, "1")
        Frames.tempValues.insert(0, '')
        return GlobalVariable.indx + 1

    # PUSHFRAME presune obsah temp do local
    def PushFrame(instruction):
        try:    
            if Frames.tempFrame[0] != "1":
                exit(55)
            Frames.localFrame = Frames.tempFrame.copy()
            Frames.localValues = Frames.tempValues.copy()
            Frames.tempFrame.clear()
            Frames.tempValues.clear()
        except:
            exit(55)

        return GlobalVariable.indx + 1

    # POPFRAME presune obsah local do temp
    def PopFrame(instruction):
        try:
            if Frames.localFrame[0] != "1":
                exit(55)
            Frames.tempFrame = Frames.localFrame.copy()
            Frames.tempValues = Frames.localValues.copy()
            Frames.localFrame.clear()
            Frames.tempValues.clear()
        except:
            exit(32)

        return GlobalVariable.indx + 1

    # DEFVAR definuje promennou v ramci, pokud existuje chyba
    def DefVar(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 1:
            exit(32)
        if argsType[0] != 'var':
            exit(32)


        varText = argsText[0].split("@")
        if varText[0] == "GF":
            if varText[1] in Frames.globalFrame:
                exit(52)
            else:
                Frames.globalFrame.append(varText[1])
                Frames.globalValues.append('')
        elif varText[0] == "LF":
            if Frames.localFrame[0] == "1":
                if varText[1] in Frames.localFrame:
                    exit(52)
                else:
                    Frames.localFrame.append(varText[1])
                    Frames.localValues.append('')
            else:
                exit(55)
        elif varText[0] == "TF":
            if Frames.tempFrame[0] == "1":
                if varText[1] in Frames.tempFrame:
                    exit(52)
                else:
                    Frames.tempFrame.append(varText[1])
                    Frames.tempValues.append('')
            else:
                exit(55)
        else:
            exit(32)

        return GlobalVariable.indx + 1

    # WRITE printuje ven, cokoliv dostane
    def Write(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)

        if len(argsType) != 1:
            exit(32)

        isVar, type = CheckDo.__symbCheck(argsType[0])

        if isVar:
            value = CheckDo.__VarValue(argsText[0])
            if isinstance(value, bool):
                if value:
                    value = "true"
                else:
                    value = "false"
        else:
            value = argsText[0]

        print(value, end='')

        return GlobalVariable.indx + 1

    # ADD secte a ulozi
    def Add(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 3:
            exit(32)
        if argsType[0] != 'var':
            exit(32)

        isVar1, type1 = CheckDo.__symbCheck(argsType[1])
        isVar2, type2 = CheckDo.__symbCheck(argsType[2])

        # kontrola symb
        if isVar1:
            value1 = CheckDo.__VarValue(argsText[1])
            if not isinstance(value1, int):
                exit(53)
        elif type1 == dataType.INT:
            value1 = int(argsText[1])
        else:    
            exit(53)

        if isVar2:
            value2 = CheckDo.__VarValue(argsText[2])
            if not isinstance(value2, int):
                exit(53)
        elif type2 == dataType.INT:
            value2 = int(argsText[2])
        else:
            exit(53)

        value = value1 + value2

        CheckDo.__VarSave(argsText[0], value)
        return GlobalVariable.indx + 1

    # SUB odecte a ulozi
    def Sub(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 3:
            exit(32)
        if argsType[0] != 'var':
            exit(32)

        isVar1, type1 = CheckDo.__symbCheck(argsType[1])
        isVar2, type2 = CheckDo.__symbCheck(argsType[2])

        # kontrola symb
        if isVar1:
            value1 = CheckDo.__VarValue(argsText[1])
            if not isinstance(value1, int):
                exit(53)
        elif type1 == dataType.INT:
            value1 = int(argsText[1])
        else:    
            exit(53)

        if isVar2:
            value2 = CheckDo.__VarValue(argsText[2])
            if not isinstance(value2, int):
                exit(53)
        elif type2 == dataType.INT:
            value2 = int(argsText[2])
        else:
            exit(53)

        value = value1 - value2

        CheckDo.__VarSave(argsText[0], value)
        return GlobalVariable.indx + 1

    # MUL vynasobi a ulozi
    def Mul(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 3:
            exit(32)
        if argsType[0] != 'var':
            exit(32)

        isVar1, type1 = CheckDo.__symbCheck(argsType[1])
        isVar2, type2 = CheckDo.__symbCheck(argsType[2])

        # kontrola symb
        if isVar1:
            value1 = CheckDo.__VarValue(argsText[1])
            if not isinstance(value1, int):
                exit(53)
        elif type1 == dataType.INT:
            value1 = int(argsText[1])
        else:    
            exit(53)

        if isVar2:
            value2 = CheckDo.__VarValue(argsText[2])
            if not isinstance(value2, int):
                exit(53)
        elif type2 == dataType.INT:
            value2 = int(argsText[2])
        else:
            exit(53)

        value = value1 * value2

        CheckDo.__VarSave(argsText[0], value)
        return GlobalVariable.indx + 1

    # IDIV vydeli a ulozi
    def Idiv(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 3:
            exit(32)
        if argsType[0] != 'var':
            exit(32)

        isVar1, type1 = CheckDo.__symbCheck(argsType[1])
        isVar2, type2 = CheckDo.__symbCheck(argsType[2])

        # kontrola symb
        if isVar1:
            value1 = CheckDo.__VarValue(argsText[1])
            if not isinstance(value1, int):
                exit(53)
        elif type1 == dataType.INT:
            value1 = int(argsText[1])
        else:    
            exit(53)

        if isVar2:
            value2 = CheckDo.__VarValue(argsText[2])
            if not isinstance(value2, int):
                exit(53)
        elif type2 == dataType.INT:
            value2 = int(argsText[2])
        else:
            exit(53)

        if value2 == 0:
            exit(57)

        value = value1 // value2

        CheckDo.__VarSave(argsText[0], value)
        return GlobalVariable.indx + 1

    # LABEL ulozeni znacky do seznamu
    def Label(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 1:
            exit(32)
        if argsType[0] != 'label':
            exit(32)

        order = GlobalVariable.labelOrder
        name = argsText[0]

        for x in Frames.labelList:
            test = x.split("%")
            if test[0] == name:
                exit(52)

        item = name + '%' + str(order)

        Frames.labelList.append(item)

    # CALL set - ulozi pozici instrukce
    def CallSet(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 1:
            exit(32)
        if argsType[0] != 'label':
            exit(32)

        order = GlobalVariable.labelOrder
        name = 'CALL'

        for x in Frames.labelList:
            test = x.split("%")
            if test[0] == name:
                exit(52)

        item = name + '%' + str(order)

        Frames.labelList.append(item)

    # CALL
    def Call(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 1:
            exit(32)
        if argsType[0] != 'label':
            exit(32)

        name = argsText[0]

        for x in Frames.labelList:
            find = x.split("%")
            if find[0] == name:
                order = int(find[1])
                return order

        exit(52)

    # RETURN vrati se na call
    def Return(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 0:
            exit(32)

        name = 'CALL'

        for x in Frames.labelList:
            find = x.split("%")
            if find[0] == name:
                order = int(find[1])
                return order + 1

        exit(52)


    # JUMP skoci na label
    def Jump(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 1:
            exit(32)
        if argsType[0] != 'label':
            exit(32)

        name = argsText[0]

        for x in Frames.labelList:
            find = x.split("%")
            if find[0] == name:
                order = int(find[1])
                return order

        exit(52)


    # JUMPIFEQ
    def JumpIfEq(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 3:
            exit(32)
        if argsType[0] != 'label':
            exit(32)

        for x in Frames.labelList:
            find = x.split("%")
            if find[0] == argsText[0]:
                order = int(find[1])
                label = order

        if not isinstance(label, int):
            exit(52)

        typ1, value1 = CheckDo.__SymbType(argsType[1], argsText[1])
        typ2, value2 = CheckDo.__SymbType(argsType[2], argsText[2])

        if typ1 == typ2:
            if value1 == value2:
                return label
            else:
                return GlobalVariable.indx + 1
        else:
            exit(32)

    # JUMPINFEQ
    def JumpIfNEq(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 3:
            exit(32)
        if argsType[0] != 'label':
            exit(32)

        for x in Frames.labelList:
            find = x.split("%")
            if find[0] == argsText[0]:
                order = int(find[1])
                label = order

        if not isinstance(label, int):
            exit(52)

        typ1, value1 = CheckDo.__SymbType(argsType[1], argsText[1])
        typ2, value2 = CheckDo.__SymbType(argsType[2], argsText[2])

        if typ1 == typ2:
            if value1 != value2:
                return label
            else:
                return GlobalVariable.indx + 1
        else:
            exit(32)

    # LT symb je mensi nez symbb
    def Lt(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 3:
            exit(32)
        if argsType[0] != 'var':
            exit(32)

        type1, value1 = CheckDo.__SymbType(argsType[1], argsText[1])
        type2, value2 = CheckDo.__SymbType(argsType[2], argsText[2])

        if type1 == type2:
            if value1 < value2:
                CheckDo.__VarSave(argsText[0], True)
            else:
                CheckDo.__VarSave(argsText[0], False)
        else:
            exit(53)

        return GlobalVariable.indx + 1

    # GT prvni je vetsi nez druhy
    def Gt(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 3:
            exit(32)
        if argsType[0] != 'var':
            exit(32)

        type1, value1 = CheckDo.__SymbType(argsType[1], argsText[1])
        type2, value2 = CheckDo.__SymbType(argsType[2], argsText[2])

        if type1 == type2:
            if value1 > value2:
                CheckDo.__VarSave(argsText[0], True)
            else:
                CheckDo.__VarSave(argsText[0], False)
        else:
            exit(53)

        return GlobalVariable.indx + 1

    # EQ zda jsou stejne
    def Eq(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 3:
            exit(32)
        if argsType[0] != 'var':
            exit(32)

        type1, value1 = CheckDo.__SymbType(argsType[1], argsText[1])
        type2, value2 = CheckDo.__SymbType(argsType[2], argsText[2])

        if type1 == type2:
            if value1 == value2:
                CheckDo.__VarSave(argsText[0], True)
            else:
                CheckDo.__VarSave(argsText[0], False)
        else:
            exit(53)

        return GlobalVariable.indx + 1

    # AND logika
    def And(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 3:
            exit(32)
        if argsType[0] != 'var':
            exit(32)

        type1, value1 = CheckDo.__SymbType(argsType[1], argsText[1])
        type2, value2 = CheckDo.__SymbType(argsType[2], argsText[2])

        if type1 == type2 == dataType.BOOL:
            if value1 == True and value2 == True:
                CheckDo.__VarSave(argsText[0], True)
            else:
                CheckDo.__VarSave(argsText[0], False)
        else:
            exit(53)

        return GlobalVariable.indx + 1

    # OR logika
    def Or(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 3:
            exit(32)
        if argsType[0] != 'var':
            exit(32)

        type1, value1 = CheckDo.__SymbType(argsType[1], argsText[1])
        type2, value2 = CheckDo.__SymbType(argsType[2], argsText[2])

        if type1 == type2 == dataType.BOOL:
            if value1 == True or value2 == True:
                CheckDo.__VarSave(argsText[0], True)
            else:
                CheckDo.__VarSave(argsText[0], False)
        else:
            exit(53)

        return GlobalVariable.indx + 1

    # NOT logika
    def Not(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 2:
            exit(32)
        if argsType[0] != 'var':
            exit(32)

        type1, value1 = CheckDo.__SymbType(argsType[1], argsText[1])

        if type1 == dataType.BOOL:
            if value1:
                CheckDo.__VarSave(argsText[0], False)
            else:
                CheckDo.__VarSave(argsText[0], True)
        else:
            exit(53)

        return GlobalVariable.indx + 1

    # PUSHS da na stack
    def Pushs(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 1:
            exit(32)

        type1, value1 = CheckDo.__SymbType(argsType[0], argsText[0])

        Frames.stack.append(value1)

        return GlobalVariable.indx + 1

    # POPS ze zasobniku
    def Pops(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 1:
            exit(32)
        if argsType[0] != 'var':
            exit(32)

        if len(Frames.stack) > 0:
            CheckDo.__VarSave(argsText[0], Frames.stack.pop())
        else:
            exit(56)

        return GlobalVariable.indx + 1

    # TYPE vypise typ
    def Type(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 2:
            exit(32)
        if argsType[0] != 'var':
            exit(32)

        type, value = CheckDo.__SymbType(argsType[1], argsText[1])

        if type == dataType.INT:
            CheckDo.__VarSave(argsText[1], "int")
        elif type == dataType.BOOL:
            CheckDo.__VarSave(argsText[1], "bool")
        elif type == dataType.STRING:
            CheckDo.__VarSave(argsText[1], "str")
        else:
            exit(99)

        return GlobalVariable.indx + 1

    # DPRINT vypisuje ja stderr
    def DPrint(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 1:
            exit(32)

        type, value = CheckDo.__SymbType(argsType[0], argsText[0])

        print(value, file=stderr)

        return GlobalVariable.indx + 1

    # BREAK
    def Break(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 0:
            exit(32)

        print("order: " + instruction.attrib.get('order'), file=stderr)

        return GlobalVariable.indx + 1

    # CONCAT
    def Concat(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 3:
            exit(32)
        if argsType[0] != 'var':
            exit(32)

        type1, value1 = CheckDo.__SymbType(argsType[1], argsText[1])
        type2, value2 = CheckDo.__SymbType(argsType[2], argsText[2])

        if type1 == type2 == dataType.STRING:
            value = value1 + value2
            CheckDo.__VarSave(argsText[0], value)
        else:
            exit(53)

        return GlobalVariable.indx + 1

    # STRLEN
    def StrLen(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 2:
            exit(32)
        if argsType[0] != 'var':
            exit(32)

        type1, value1 = CheckDo.__SymbType(argsType[1], argsText[1])

        if type1 == dataType.STRING:
            value = len(value1)
            CheckDo.__VarSave(argsText[0], value)
        else:
            exit(53)

        return GlobalVariable.indx + 1

    # GETCHAR
    def GetChar(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 3:
            exit(32)
        if argsType[0] != 'var':
            exit(32)

        type1, value1 = CheckDo.__SymbType(argsType[1], argsText[1])
        type2, value2 = CheckDo.__SymbType(argsType[2], argsText[2])

        if type1 == dataType.STRING:
            if type2 == dataType.INT:
                try:
                    value = value1[value2]
                except:
                    exit(58)
                CheckDo.__VarSave(argsText[0], value)
            else:
                exit(53)
        else:
            exit(53)

        return GlobalVariable.indx + 1

    # SETCHAR
    def SetChar(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 3:
            exit(32)
        if argsType[0] != 'var':
            exit(32)

        type, value = CheckDo.__SymbType(argsType[0], argsText[0])
        type1, value1 = CheckDo.__SymbType(argsType[1], argsText[1])
        type2, value2 = CheckDo.__SymbType(argsType[2], argsText[2])

        if type == dataType.STRING:
            if type1 == dataType.INT:
                if type2 == dataType.STRING:
                    try:
                        value[value1] = value2
                    except:
                        exit(58)
                    CheckDo.__VarSave(argsText[0], value)
            else:
                exit(53)
        else:
            exit(53)

        return GlobalVariable.indx + 1



    # EXIT ukonceni s navratovym kodem 
    def Exit(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 1:
            exit(32)
        if argsType[0] != 'int':
            exit(32)

        ret = int(argsText[0])

        if ret >= 0 and ret <= 49:
            exit(ret)
        else:
            exit(57)

    # READ
    def Read(instruction):
        argsType, argsText = CheckDo.__listOfArg(instruction)
        if len(argsType) != 2:
            exit(32)

        if argsType[0] != 'var':
            exit(32)

        if argsType[1] != 'type':
            exit(32)

        
        if  argsText[1] == "int":
            value = input
            value = int(value)
        elif  argsText[1] == "bool":
            value = input
            if value == "true":
                value = True
            elif value == "false":
                value = False
            else:
                exit(32)
        elif  argsText[1] == "string":
            value = input
        else:
            exit(32)

        # vlozeni hodnoty
        CheckDo.__VarSave(argsText[0], value)
        return GlobalVariable.indx + 1








Parser.XParse(source)




        
