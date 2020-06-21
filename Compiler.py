'''
Fullname    Fydanakis Iordanis-Rafail    
A.M.        2568    
Username    cse32568
'''

import sys;


#===============================================================================
# <SymbolTable Objects>
#===============================================================================
class Entity:
    pass;
    
class Variable(Entity):
    
    def __init__(self, offset, name):
        self.offset = offset;
        self.name = name;
        
    def __str__(self):
        return "Variable : " + str(self.name) + ", offset : " + str(self.offset); 

class Function(Entity):
    
    def __init__(self, funcType, name):
        self.type = funcType;
        self.startQuad = nextQuad();
        self.arguments = list();
        self.framelength = -1;
        self.name = name;
        
    def __str__(self):
        return "FunctionType : " + str(self.type) + ", name : " + str(self.name) + ", startQuad : " + str(self.startQuad) + ", frameLength : " + str(self.framelength) + ", " + str([str(x) for x in self.arguments]);

class Parameter(Entity):
    
    def __init__(self, parmode, offset, name):
        self.parmode = parmode;
        self.offset = offset;
        self.name = name;
        
    def __str__(self):
        return "ParameterMode : " + str(self.parmode) + ", name : " + str(self.name) + ", offset : " + str(self.offset); 

class TempVariable(Entity):
    
    def __init__(self, offset, name):
        self.offset = offset;
        self.name = name;
        
    def __str__(self):
        return "TempVariable : " + str(self.name) + ", offset : " + str(self.offset); 

class Argument():
    
    def __init__(self, parmode):
        self.parmode = parmode;
        
    def __str__(self):
        return "Argument : " + str(self.parmode); 

class Scope():
    
    def __init__(self, nestingLevel):
        self.nestingLevel = nestingLevel;
        self.enclosingScope = list();
        
    def __str__(self):
        return "Scope's nesting level : " + str(self.nestingLevel); 
#===============================================================================
# </SymbolTable Objects>
#===============================================================================        


#===============================================================================
# <Lex Constants>
#===============================================================================
IDENTIFIER_ID = 1;
CONSTANT = 2;
PLUS_OPERATOR = 3;
MINUS_OPERATOR = 4;
MULTIPLY_OPERATOR = 5;
DIVISION_OPERATOR = 6;
LESS_THAN_OPERATOR = 7;
GREATER_THAN_OPERATOR = 8;
EQUAL_TO_OPERATOR = 9;
GREATER_EQUAL_OPERATOR = 10;
LESS_EQUAL_OPERATOR = 11;
NOT_EQUAL_OPERATOR = 12;
ASSIGNMENT_SYMBOL = 13;
OPENING_PARENTHESES = 14;
CLOSING_PARENTHESES = 15;
OPENING_BRACKETS = 16;
CLOSING_BRACKETS = 17;
OPENING_SQUARED_BRACKETS = 18;
CLOSING_SQUARED_BRACKETS = 19;
COMMA = 20;
SEMICOLON = 21;
AND_RW = 22;
DECLARE_RW = 23;
DO_WHILE_RW = 24;
ELSE_RW = 25;
ENDDECLARE_RW = 26;
EXIT_RW = 27;
PROCEDURE_RW = 28;
FUNCTION_RW = 29;
PRINT_RW = 30;
CALL_RW = 31;
IF_RW = 32;
IN_RW = 33;
INOUT_RW = 34;
NOT_RW = 35;
SELECT_RW = 36;
PROGRAM_RW = 37;
OR_RW = 38;
RETURN_RW = 39;
WHILE_RW = 40;
DEFAULT_RW = 41;
COLON = 42;
#===============================================================================
# </Lex Constants>
#===============================================================================


#===========================================================================
# <Lex VARIABLES>
#===========================================================================
token = -1;
lastPos = 0;
savedLine = 1;
line = 1;
savedColumn = 0;
column = 0;
#===========================================================================
# </Lex VARIABLES>
#===========================================================================


#===============================================================================
# <Lex Special Characters>
#===============================================================================
arithmeticOperatorList = ['+', '-', '*', '/'];
comparisonOperatorList = ['<', '>', '=', '<=', '>=', '<>'];
assignmentSymbolList = [':=', ':'];
separatorList = [';', ','];
groupingSymbolList = ['{', '}', '(', ')', '[', ']'];
commentSymbolList = ['\*', '*\\', '\\'];
#===============================================================================
# </Lex Special Characters>
#===============================================================================


#===============================================================================
# <Intermediate VARIABLES>
#===============================================================================
quadList = [];
quadListSize = 1;
tempVarNum = 0;
programName = "";
returnStack = list();
exitStack = list();
exitList = list();
variableList = list();
#===============================================================================
# </Intermediate VARIABLES>
#===============================================================================


#===============================================================================
# <SymbolTable Variables>
#===============================================================================
scopeList = list();
programFrameLength = -1;
#===============================================================================
# </SymbolTable Variables>
#===============================================================================


#===============================================================================
# <ObjectCode Variables>
#===============================================================================
objectCodeList = [];
lastQuadNotCompiled = 0;
#===============================================================================
# </ObjectCode Variables>
#===============================================================================


#===============================================================================
# <ObjectCode Functions>
#===============================================================================
def gnlvCode(varName):
    global objectCodeList;
    global scopeList;
    
    scopeLevel,enclosingScopeLevel = searchForVariable(varName);
    varOffset = scopeList[scopeLevel].enclosingScope[enclosingScopeLevel].offset;
    
    for i in range(len(scopeList)-1-scopeLevel):
        objectCodeList.append("lw $t0, -4($sp)");
        
    objectCodeList.append("add $t0, $t0, -"+str(varOffset));
    
def loadvr(varName,registerNum):
    global objectCodeList;
    global scopeList;
    
    if (varName.isdigit()):
        objectCodeList.append("li $t"+str(registerNum) +", "+str(varName));
        return;
    
    scopeLevel,enclosingScopeLevel = searchForVariable(varName);
    varObject = scopeList[scopeLevel].enclosingScope[enclosingScopeLevel];
    
    if ((isinstance(varObject, Variable) or (isinstance(varObject, TempVariable))) and (scopeLevel == 0)):
        objectCodeList.append("lw $t"+str(registerNum) +", -"+str(varObject.offset)+"($s0)");
    elif ((isinstance(varObject, Parameter) and (varObject.parmode == "in") and (scopeLevel == len(scopeList)-1))  or (scopeLevel == len(scopeList)-1)):
        objectCodeList.append("lw $t"+str(registerNum) +", -"+str(varObject.offset)+"($sp)");
    elif ((isinstance(varObject, Parameter) and (varObject.parmode == "inout") and (scopeLevel == len(scopeList)-1))  or (scopeLevel == len(scopeList)-1)):
        objectCodeList.append("lw $t0, -"+str(varObject.offset)+"($sp)");
        objectCodeList.append("lw $t"+str(registerNum) +", -"+str(varObject.offset)+"($t0)");
    elif ((isinstance(varObject, Parameter) and (varObject.parmode == "in") and (scopeLevel < len(scopeList)-1))  or (scopeLevel < len(scopeList)-1)):
        gnlvCode(varName);
        objectCodeList.append("lw $t"+str(registerNum) +", ($t0)");
    elif ((isinstance(varObject, Parameter) and (varObject.parmode == "inout") and (scopeLevel < len(scopeList)-1))  or (scopeLevel < len(scopeList)-1)):
        gnlvCode(varName);
        objectCodeList.append("lw $t0, ($t0)");
        objectCodeList.append("lw $t"+str(registerNum) +", ($t0)");
    else:
        perror("Something went wrong with the loadvr("+str(varName)+","+str(registerNum)+")!");
        
def storerv(registerNum,varName):
    global objectCodeList;
    global scopeList;
    
    scopeLevel,enclosingScopeLevel = searchForVariable(varName);
    varObject = scopeList[scopeLevel].enclosingScope[enclosingScopeLevel];
    
    
    if ((isinstance(varObject, Variable) or (isinstance(varObject, TempVariable))) and (scopeLevel == 0)):
        objectCodeList.append("sw $t"+str(registerNum)+", -"+str(varObject.offset)+"($s0)");
    elif ((isinstance(varObject, Parameter) and (varObject.parmode == "in") and (scopeLevel == len(scopeList)-1))  or (scopeLevel == len(scopeList)-1)):
        objectCodeList.append("sw $t"+str(registerNum)+", -"+str(varObject.offset)+"($sp)");
    elif ((isinstance(varObject, Parameter) and (varObject.parmode == "inout") and (scopeLevel == len(scopeList)-1))  or (scopeLevel == len(scopeList)-1)):
        objectCodeList.append("sw $t0, -"+str(varObject.offset)+"($sp)");
        objectCodeList.append("sw $t"+str(registerNum)+", ($t0)");
    elif ((isinstance(varObject, Parameter) and (varObject.parmode == "in") and (scopeLevel < len(scopeList)-1))  or (scopeLevel < len(scopeList)-1)):
        gnlvCode(varName);
        objectCodeList.append("sw $t"+str(registerNum)+", ($t0)");
    elif ((isinstance(varObject, Parameter) and (varObject.parmode == "inout") and (scopeLevel < len(scopeList)-1))  or (scopeLevel < len(scopeList)-1)):
        gnlvCode(varName);
        objectCodeList.append("lw $t0, ($t0)");
        objectCodeList.append("sw $t"+str(registerNum)+", ($t0)");
    else:
        perror("Something went wrong with the storerv("+str(registerNum)+","+str(varName)+")!");

def produceObjectCodeForTheNextFunction(funcName):
    global programFrameLength;
    global objectCodeList;
    global scopeList;
    global programName;
    global lastQuadNotCompiled;
    global quadList;
    
    parameterCounter = 0;
    
    objectCodeList.append(str(funcName)+":");
    
    if (funcName == programName):
        objectCodeList.append("add $sp, $sp, "+str(programFrameLength));
        objectCodeList.append("move $s0, $sp");
    
    while(1):
        
        nextquad = quadList[lastQuadNotCompiled];
        nextquad = str(nextquad[0])+','+str(nextquad[1])+','+str(nextquad[2])+','+str(nextquad[3]);
        
        objectCodeList.append("L"+str(lastQuadNotCompiled+1)+":");
        lastQuadNotCompiled += 1;
    
        splittedQuad = nextquad.split(",");
        
        if (splittedQuad[0] == "begin_block"):
            if (splittedQuad[1] != str(funcName)):
                perror("The begin_block func name is not the same as the one i'm trying to compile! @produceObjectCodeForTheNextFunction");
            
            objectCodeList.append("sw $ra, ($sp)");
            continue;
                
        elif (splittedQuad[0] == "end_block"):
            objectCodeList.append("lw $ra, ($sp)");
            objectCodeList.append("jr $ra");
            return;
        
        elif (splittedQuad[0] == "halt"):
            objectCodeList.append("li $v0, 10");
            objectCodeList.append("syscall");
            continue;
        
        if (splittedQuad[3] == "retv"):
            loadvr(splittedQuad[1],1);
            objectCodeList.append("lw $t0, -8($sp)");
            objectCodeList.append("sw $t1, ($t0)");
        
        elif (splittedQuad[0] == "jump"):
            objectCodeList.append("j L"+str(splittedQuad[3]));
            
        elif (splittedQuad[0] in comparisonOperatorList):
            loadvr(splittedQuad[1], 1);
            loadvr(splittedQuad[2], 2);
            
            if (splittedQuad[0] == "="): compOper = "beq";
            elif (splittedQuad[0] == "<"): compOper = "blt";
            elif (splittedQuad[0] == ">"): compOper = "bgt";
            elif (splittedQuad[0] == "<="): compOper = "ble";
            elif (splittedQuad[0] == ">="): compOper = "bge";
            elif (splittedQuad[0] == "<>"): compOper = "bne";
            else: perror("Problem with the operator in produceObjectCodeFromQuad");
                
            objectCodeList.append(str(compOper)+" ,$t1 ,$t2 ,"+str("L"+splittedQuad[3]));
            
        elif (splittedQuad[0] in arithmeticOperatorList):
            loadvr(splittedQuad[1],1);
            loadvr(splittedQuad[2],2);
            
            if (splittedQuad[0] == "+"): arithOper = "add";
            elif (splittedQuad[0] == "-"): arithOper = "sub";
            elif (splittedQuad[0] == "*"): arithOper = "mul";
            elif (splittedQuad[0] == "/"): arithOper = "div";
            else: perror("Problem with the operator in produceObjectCodeFromQuad");
            
            objectCodeList.append(str(arithOper)+" $t1, $t1, $t2");
            storerv(1, splittedQuad[3]);
        
        elif (splittedQuad[0] == "print"):
            objectCodeList.append("li $v0, 1");
            objectCodeList.append("li $a0, "+str(splittedQuad[3]));
            objectCodeList.append("syscall");
        
        elif (splittedQuad[0] == ":="):
            loadvr(splittedQuad[1],1);
            storerv(1, splittedQuad[3]);
            
        elif (splittedQuad[0] == "par" and splittedQuad[2] == "CV"):
            parameterCounter += 1;
            loadvr(splittedQuad[1], 0);
            objectCodeList.append("sw $t0, -"+str(12+4*parameterCounter)+"($fp)");
            
        elif (splittedQuad[0] == "par" and splittedQuad[2] == "REF"):
            scopeLevel,enclosingScopeLevel = searchForVariable(splittedQuad[1]);
            varObject = scopeList[scopeLevel].enclosingScope[enclosingScopeLevel];
            parameterCounter += 1;
            
            if ((isinstance(varObject, Parameter) and (varObject.parmode == "in") and (scopeLevel == len(scopeList)-1))  or (scopeLevel == len(scopeList)-1)):
                objectCodeList.append("add $t0, $sp, -"+str(varObject.offset));
                objectCodeList.append("sw $t0, -"+str(12+4*parameterCounter)+"($fp)");
                
            elif ((isinstance(varObject, Parameter) and (varObject.parmode == "inout") and (scopeLevel == len(scopeList)-1))  or (scopeLevel == len(scopeList)-1)):
                objectCodeList.append("lw $t0, -"+str(varObject.offset)+"($sp)");
                objectCodeList.append("sw $t0, -"+str(12+4*parameterCounter)+"($fp)");
            
            elif ((isinstance(varObject, Parameter) and (varObject.parmode == "in") and (scopeLevel < len(scopeList)-1))  or (scopeLevel < len(scopeList)-1)):
                gnlvCode(splittedQuad[1]);
                objectCodeList.append("sw $t0, -"+str(12+4*parameterCounter)+"($fp)");
            
            elif ((isinstance(varObject, Parameter) and (varObject.parmode == "inout") and (scopeLevel < len(scopeList)-1))  or (scopeLevel < len(scopeList)-1)):
                gnlvCode(splittedQuad[1]);
                objectCodeList.append("lw $t0, ($t0)");
                objectCodeList.append("sw $t0, -"+str(12+4*parameterCounter)+"($fp)");
            
            else:
                perror("Someting went wrong in produceObjectCodeFromQuad @parameter in/inout!");
                
        elif (splittedQuad[0] == "par" and splittedQuad[2] == "RET"):
                scopeLevel,enclosingScopeLevel = searchForVariable(splittedQuad[1]);
                varOffset = scopeList[scopeLevel].enclosingScope[enclosingScopeLevel].offset;
                objectCodeList.append("add $t0, $sp, -"+str(varOffset));
                objectCodeList.append("sw $t0, -8($fp)");
                
        elif (splittedQuad[0] == "call"):
            scopeLevel, enclosingScopeLevel = getTheObjectOfFuncOrProc(splittedQuad[1]);
            funcObj = scopeList[scopeLevel].enclosingScope[enclosingScopeLevel];
            
            if (funcName == programName):
                objectCodeList.append("sw $sp, -4($fp)");
            else :
                scopeLevel2, enclosingScopeLevel2 = getTheObjectOfFuncOrProc(funcName);
                
                if (scopeLevel == scopeLevel2):
                    objectCodeList.append("lw $t0, -4($sp)");
                    objectCodeList.append("sw $t0, -4($fp)");
                elif (scopeLevel != scopeLevel2):
                    objectCodeList.append("sw $sp, -4($fp)");
                
            objectCodeList.append("add $sp, $sp, "+str(funcObj.framelength));
            objectCodeList.append("jal "+str(splittedQuad[1]));
            objectCodeList.append("add $sp, $sp, -"+str(funcObj.framelength));
        else:
            perror("Forgot to catch a quad in produceObjectCodeForTheNextFunction! " + str(splittedQuad));
            
            
#===============================================================================
# </ObjectCode Functions>
#===============================================================================


#===============================================================================
# <SymbolTable Functions>
#===============================================================================
def createFunctionEntity(funcType, name):
    global scopeList;
    
    scopeObj = Scope(len(scopeList));
    entityObj = Function(funcType, name);
    scopeList[-1].enclosingScope.append(entityObj);
    scopeList.append(scopeObj);
    
def createScope(nestingLevel):
    global scopeList;
    
    scopeObj = Scope(nestingLevel);
    scopeList.append(scopeObj);
        
def createArgument(parmode, offset, name):
    global scopeList;
    
    parameterObj = Parameter(parmode, offset, name);
    argumentObj = Argument(parmode);
    scopeList[-1].enclosingScope.append(parameterObj);
    scopeList[-2].enclosingScope[-1].arguments.append(argumentObj);
    
def createVariable(name):
    global scopeList;
    
    offset = -1;
    
    if (len(scopeList[-1].enclosingScope) == 0):
        offset = 12;
    else:
        for i in range(len(scopeList[-1].enclosingScope)-1,-1,-1):
            if (not isinstance(scopeList[-1].enclosingScope[i], Function)):
                offset = scopeList[-1].enclosingScope[i].offset+4;
                break;
            
    variableObj = Variable(offset, name);
    scopeList[-1].enclosingScope.append(variableObj);
    
def createVariableDeclarations(name, offset):
    global scopeList;
    
    variableObj = Variable(offset, name);
    scopeList[-1].enclosingScope.append(variableObj);
    
def updateFrameLength():
    global scopeList;
    
    frameLength = 12;
    
    for i in range(len(scopeList[-1].enclosingScope)-1,-1,-1):
        if (not isinstance(scopeList[-1].enclosingScope[i], Function)):
            frameLength = scopeList[-1].enclosingScope[i].offset;
            break;
        
    scopeList[-2].enclosingScope[-1].framelength = frameLength+4;
    
def searchForVariable(name):
    global scopeList;
    
    for i in range(len(scopeList)-1,-1,-1):
        for j in range(len(scopeList[i].enclosingScope)-1,-1,-1):
            if (isinstance(scopeList[i].enclosingScope[j], Parameter)):
                if (scopeList[i].enclosingScope[j].name == name):
                    return i,j;
            elif (isinstance(scopeList[i].enclosingScope[j], Variable)):
                if (scopeList[i].enclosingScope[j].name == name):
                    return i,j;
            elif (isinstance(scopeList[i].enclosingScope[j], TempVariable)):
                if (scopeList[i].enclosingScope[j].name == name):
                    return i,j;
                
    perror("The variable with the id "+str(name)+" is not defined.");
    
def searchDeclarationOfFuncOrProc(name):
    global scopeList;
    
    for i in range(len(scopeList)-1,-1,-1):
        for j in range(len(scopeList[i].enclosingScope)-1,-1,-1):
            if (isinstance(scopeList[i].enclosingScope[j], Function)):
                if (scopeList[i].enclosingScope[j].name == name):
                    perror("The Function or Procedure with the id "+str(name)+" is already defined!");
                
    return;

def getTheObjectOfFuncOrProc(name):
    global scopeList;
    
    for i in range(len(scopeList)-1,-1,-1):
        for j in range(len(scopeList[i].enclosingScope)-1,-1,-1):
            if (isinstance(scopeList[i].enclosingScope[j], Function)):
                    if (scopeList[i].enclosingScope[j].name == name):
                        return i,j;
                    
    perror("The function with the id "+str(name)+" is not defined.");
#===============================================================================
# </SymbolTable Functions>
#===============================================================================    


#===============================================================================
# <Intermediate Functions>
#===============================================================================
def genQuad(op,x,y,z):
    global quadList;
    global quadListSize;
    
    quadList.append([op,x,y,z]);
    quadListSize += 1;

def nextQuad():
    global quadListSize;
    
    return quadListSize;

def newTemp():
    global tempVarNum;
    
    tempVarNum += 1;
    tempVarName = "T_" + str(tempVarNum);
    createVariable(tempVarName);
    return tempVarName;

def emptyList():
    emptyList = list();
    return emptyList;

def makeList(x):
    newList = emptyList();
    newList.append(x);
    return newList;

def merge(list1,list2):
    if(list1 is None):
        list1 = emptyList();
    
    if (list2 is None):
        list2 = emptyList();

    return list1+list2;

def backpatch(newList,z):
    global quadList;
    
    for obj in newList:
        quadList[obj-1][3] = str(z);
#===============================================================================
# </Intermediate Functions>
#===============================================================================        


#===============================================================================
# <Lex Functions>
#===============================================================================
def perror(errMess):
    global line;
    global column;
    
    errMess += "' in line " + str(line) + " column " + str(column) + ".";
    print(errMess);
    sys.exit();

def readNextChar():
    global savedLine;
    global line;
    global savedColumn;
    global column;
    
    savedColumn = column;
    savedLine = line;
    
    token = f.read(1);
    if (token.isspace()):
        if (token == " "):
            column += 1;
        elif (token == "\t"):
            column += 4;
        elif (token == "\n"):
            column = 0;
            line += 1;
        else:
            perror("Problem with whitespaces!");
    elif (token in arithmeticOperatorList):
        column += 1;
    elif (token in comparisonOperatorList):
        column += 1;
    elif (token in assignmentSymbolList):
        column += 1;
    elif (token in separatorList):
        column += 1;
    elif (token in groupingSymbolList):
        column += 1;
    elif (token in commentSymbolList):
        column += 1;
    elif (token.isalpha()):
        column += 1;
    elif (token.isdigit()):
        column += 1;
    elif (token == ""):
        return token;
    
    return token;

def unreadLastChar():
    global savedLine;
    global line;
    global savedColumn;
    global column;
    global lastPos;
    
    column = savedColumn;
    line = savedLine;
    f.seek(lastPos);

def lex():
    global lastPos;
    global variableList;
    
    token = readNextChar();
    
    while(token.isspace()):
        token = readNextChar();
    
    tmpStr = token;
    lastPos = f.tell();
    
    if (token.isalpha()):
        
        counter = 1;
        while (1):
            token = readNextChar();
            if (token.isalpha() or token.isdigit()):
                counter +=1;
                if (counter <= 30):
                    tmpStr += token;
                lastPos = f.tell();
            else:
                unreadLastChar();
                if (tmpStr == "and"): return AND_RW, tmpStr;
                elif (tmpStr == "declare"): return DECLARE_RW, tmpStr;
                elif (tmpStr == "do"): return DO_WHILE_RW, tmpStr;
                elif (tmpStr == "else"): return ELSE_RW, tmpStr;
                elif (tmpStr == "enddeclare"): return ENDDECLARE_RW, tmpStr;
                elif (tmpStr == "exit"): return EXIT_RW, tmpStr;
                elif (tmpStr == "procedure"): return PROCEDURE_RW, tmpStr;
                elif (tmpStr == "function"): return FUNCTION_RW, tmpStr;
                elif (tmpStr == "print"): return PRINT_RW, tmpStr;
                elif (tmpStr == "call"): return CALL_RW, tmpStr;
                elif (tmpStr == "if"): return IF_RW, tmpStr;
                elif (tmpStr == "in"): return IN_RW, tmpStr;
                elif (tmpStr == "inout"): return INOUT_RW, tmpStr;
                elif (tmpStr == "not"): return NOT_RW, tmpStr;
                elif (tmpStr == "select"): return SELECT_RW, tmpStr;
                elif (tmpStr == "program"): return PROGRAM_RW, tmpStr;
                elif (tmpStr == "or"): return OR_RW, tmpStr;
                elif (tmpStr == "return"): return RETURN_RW, tmpStr;
                elif (tmpStr == "while"): return WHILE_RW, tmpStr;
                elif (tmpStr == "default"): return DEFAULT_RW, tmpStr;
                else:
                    if not tmpStr in variableList: variableList.append(tmpStr);
                    return IDENTIFIER_ID, tmpStr;
            
    elif (token.isdigit()):
        
        while(1):
            token = readNextChar();
            if (token.isdigit()):
                tmpStr += token;
                lastPos = f.tell();
            else:
                unreadLastChar();
                if (int(tmpStr) > 32767):
                    perror("Constants should be <= 32767 or >= -32767");
                return CONSTANT, tmpStr;
                
    elif (token == "+"):
        return PLUS_OPERATOR, tmpStr;
    elif (token == "-"):
        return MINUS_OPERATOR, tmpStr;
    elif (token == "*"):
        return MULTIPLY_OPERATOR, tmpStr;
    elif (token == "/"):
        return DIVISION_OPERATOR, tmpStr;
    elif (token == "="):
        return EQUAL_TO_OPERATOR, tmpStr;
    
    elif (token == "<"):
        token = readNextChar();
        if (token == "="):
            tmpStr += token;
            return LESS_EQUAL_OPERATOR, tmpStr;
        
        elif (token == ">"):
            tmpStr += token;
            return NOT_EQUAL_OPERATOR, tmpStr;
        
        else:
            unreadLastChar();
            return LESS_THAN_OPERATOR, tmpStr;
    
    elif (token == ">"):
        token = readNextChar();
        if (token == "="):
            tmpStr += token;
            return GREATER_EQUAL_OPERATOR, tmpStr;
        
        else:
            unreadLastChar();
            return GREATER_THAN_OPERATOR, tmpStr;
        
    elif (token == ":"):
        token = readNextChar();
        if (token == "="):
            tmpStr += token;
            return ASSIGNMENT_SYMBOL, tmpStr;
        else:
            unreadLastChar();
            return COLON, tmpStr;
            
    elif (token == "\\"):
        token = readNextChar();
        if (token == "*"):
            token = readNextChar();
            while (token != "*"):
                token = readNextChar();
            token = readNextChar();
            if (token == "\\"):
                return lex();
            else:
                perror("Expected '\' after '*' found '" + token);
        else:
            perror("Expected '*' after '\' found '" + token);
    
    elif (token == ","):
        return COMMA, tmpStr;
    elif (token == ";"):
        return SEMICOLON, tmpStr;
    elif (token == ")"):
        return CLOSING_PARENTHESES, tmpStr;
    elif (token == "("):
        return OPENING_PARENTHESES, tmpStr;
    elif (token == "{"):
        return OPENING_BRACKETS, tmpStr;
    elif (token == "}"):
        return CLOSING_BRACKETS, tmpStr;
    elif (token == "["):
        return OPENING_SQUARED_BRACKETS, tmpStr;
    elif (token == "]"):
        return CLOSING_SQUARED_BRACKETS, tmpStr;
    elif (token == ""):
        print("Found EOF in line " + str(line) + " column " + str(column) + ".");
        return 0,0;
    else:
        perror("Uknown symbol: " + token);
#===============================================================================
# </Lex Functions>
#===============================================================================
   

#===============================================================================
# <Syntax Analyzer Functions>
#===============================================================================     
        
def program():
    global programFrameLength;
    global scopeList;
    global token;
    global exitStack;
    global returnStack;
    global programName;
    global objectCodeList;
    
    token = lex();
    if (token[1] == "program"):
        token = lex();
        if (token[0] == IDENTIFIER_ID):
            programName = token[1];
            
            objectCodeList.append("j "+str(programName));
            
            createScope(0);
            
            exitStack.append(["program","_"]);
            returnStack.append(["program",programName,False]);
            
            block(programName); 
            
            returnStack.pop();
            exitStack.pop();
            
            
            for i in range(len(scopeList[0].enclosingScope)-1,0,-1):
                if (not isinstance(scopeList[0].enclosingScope[i], Function)):
                    programFrameLength = scopeList[0].enclosingScope[i].offset+4;
                    break;
            
            printSymbolTable();
            produceObjectCodeForTheNextFunction(programName);
            scopeList.pop();
            
        else:
            perror("Program ID was expected after 'program' found '" + str(token[1]));
    else:
        perror("The keyword 'program' was expected found '" + str(token[1]));

def block(name):
    global token;
    global programName;
    
    token = lex();
    if (token[0] == OPENING_BRACKETS):
        
        declarations();
        subprograms();
        
        genQuad("begin_block", name, "_", "_");
        sequence();
        if (name == programName):
            genQuad("halt", "_", "_", "_");
        genQuad("end_block", name, "_", "_");
        
        if (not(token[0] == CLOSING_BRACKETS)):
            perror("Expected '}' found '" + str(token[1]));
            
    else:
        perror("Expected '{' after ID found '" + str(token[1]));

def declarations():
    global token;
    
    token = lex();
    if (token[0] == DECLARE_RW):
        
        varlist();
        if (not(token[0] == ENDDECLARE_RW)):
            perror("The keyword 'enddeclare' was expected found '" + str(token[1]));
        
        token = lex();

def varlist():
    global token;
    
    offset = 12;
    
    token = lex();
    if (token[0] == IDENTIFIER_ID):
        for i in range(len(scopeList[-1].enclosingScope)-1,-1,-1):
            offset = scopeList[-1].enclosingScope[i].offset+4;
            break;
        createVariableDeclarations(token[1], offset);
        
        while (1):
            token = lex();
            if (token[0] == COMMA):
                offset += 4;
                token = lex();
                if (not(token[0] == IDENTIFIER_ID)):
                    perror("Expected an ID after ',' found '" + str(token[1]));
                createVariableDeclarations(token[1], offset);
            else:
                return;

def subprograms():
    global token;
    
    while (1):
        if ((token[0] == PROCEDURE_RW) or (token[0] == FUNCTION_RW)):
            func();
            token = lex();
        else:
            return;

def func():
    global scopeList;
    global token;
    global returnStack;
    global exitStack;
    
    if (token[0] == PROCEDURE_RW):
        token = lex();
        if (token[0] == IDENTIFIER_ID):
            name = token[1];
            
            searchDeclarationOfFuncOrProc(name);
            createFunctionEntity(0, name);
            
            exitStack.append(["procedure","_"]);
            returnStack.append(["procedure",name,False]);
            
            funcbody(name);

            returnStack.pop();
            exitStack.pop();

            updateFrameLength();
            printSymbolTable();
            produceObjectCodeForTheNextFunction(name);
            scopeList.pop();
                
        else:
            perror("Expected an ID after 'procedure' found '" + str(token[1]));
    else:
        token = lex();
        if (token[0] == IDENTIFIER_ID):
            name = token[1];
            
            searchDeclarationOfFuncOrProc(name);
            createFunctionEntity(1, name);
            
            exitStack.append(["function","_"]);
            returnStack.append(["function",name,False]);
            
            funcbody(name);

            exitStack.pop();
            tmpList = returnStack.pop();
            blockType,blockID,flag = tmpList;
            if (flag == False):
                perror("Expected 'return' inside the function block with the id " + name);
                
            updateFrameLength();
            printSymbolTable();
            produceObjectCodeForTheNextFunction(name);
            scopeList.pop();
            
        else:
            perror("Expected an ID after 'function' found '" + str(token[1]));
    
def funcbody(name):
    formalpars();
    block(name);
    
def formalpars():
    global token;
    
    token = lex();
    if (token[0] == OPENING_PARENTHESES):
        formalparlist();
        if (not(token[0] == CLOSING_PARENTHESES)):
            perror("Expected ')' found '" + str(token[1]));
    else:
        perror("Expected '(' after procedure or function found '" + str(token[1]));
        
def formalparlist():
    global token;
    
    offset = 12;
    
    token = lex();
    if ((token[0] == IN_RW) or (token[0] == INOUT_RW)):
        parmode = token[1];
        name = formalparitem();
        createArgument(parmode, offset, name)
    else:
        return;
    
    while (1):
        offset += 4;
            
        token = lex();
        if (token[0] == COMMA):
            token = lex();
            if ((token[0] == IN_RW) or (token[0] == INOUT_RW)):
                parmode = token[1];
                name = formalparitem();
                createArgument(parmode, offset, name);
            else:
                perror("Expected 'in' or 'inout' after ',' found '" + str(token[1]));
        else:
            return;
            
def formalparitem():
    global token;
    
    token = lex();
    if (not(token[0] == IDENTIFIER_ID)):
        perror("Expected an ID after in or inout found '" + str(str(token[1])));
    
    return token[1];
    
def sequence():
    global token;
    
    statement();

    while (1):
        if (token[0] == SEMICOLON):
            token = lex();
            
            statement();
        else:
            return;
    
def bracketsseq():
    global token;
    
    token = lex();
    sequence();
    
    if (not(token[0] == CLOSING_BRACKETS)):
        perror("Expected '}' after '{' found'" + str(token[1]));
        
def brackorstat():
    global token;
    global line;
    global column;
    
    token = lex();
    if (token[0] == OPENING_BRACKETS):
        bracketsseq();
    else:
        statement();
        if (not(token[0] == SEMICOLON)):
            perror("Expected ';' found '" + str(token[1]));
            
def statement():
    global token;
    global line;
    global column;
    
    if (token[0] == IDENTIFIER_ID):
        identifier = token[1];
        exprRet = assignmentstat();
        genQuad(':=', exprRet, '_', identifier);
        
    elif (token[0] == IF_RW):
        ifstat();
        
    elif (token[0] == DO_WHILE_RW):
        dowhilestat();
        token = lex();
        
    elif (token[0] == WHILE_RW):
        whilestat();
        
    elif (token[0] == SELECT_RW):
        selectstat();
        
    elif (token[0] == EXIT_RW):
        exitstat();
        token = lex();
        
    elif (token[0] == RETURN_RW):
        returnstat();
        token = lex();
        
    elif (token[0] == PRINT_RW):
        printstat();
        token = lex();
        
    elif (token[0] == CALL_RW):
        callstat();
        token = lex();
        
def exitstat():
    global token;
    global exitList;
    global exitStack;
    
    tmpList = exitStack.pop();
    blockType,blockID = tmpList;
    if (blockType != "dowhile"):
        if ((blockType == "function") or (blockType == "procedure") or (blockType == "program")):
            perror("Found 'exit' inside the " + str(blockType) + " block with the id " + str(blockID) + ". That's not allowed");
        else:
            perror("Found 'exit' inside the " + str(blockType) + " block. That's not allowed");
        
    exitStack.append([blockType,blockID]);
    
    exitList.append(nextQuad());
    genQuad('jump', '_', '_', '_');
    
def assignmentstat():
    global token;
    
    searchForVariable(token[1]);
    
    token = lex();
    if (token[0] == ASSIGNMENT_SYMBOL):
        token = lex();
        exprRet = expression();
        return exprRet;
    else:
        perror("Expected ':=' after an ID found '" + str(token[1]));
        
def ifstat():
    global token;
    
    token = lex();
    if (token[0] == OPENING_PARENTHESES):
        condTrue,condFalse = condition();
        if (token[0] == CLOSING_PARENTHESES):
            
            backpatch(condTrue, nextQuad());
            brackorstat();

            iflist = makeList(nextQuad());
            genQuad('jump', '_', '_', '_');
            
            backpatch(condFalse, nextQuad());
            token = lex();
            
            if (token[0] == ELSE_RW):
                elsepart();
            
            backpatch(iflist, nextQuad());
             
        else:
            perror("Expected ')' found '" + str(token[1]));
    else:
        perror("Expected '(' after 'if' found '" + str(token[1]));
        
def elsepart():
    global token;
    
    brackorstat();
    token = lex();
    
def whilestat():
    global token;
    global exitStack;
    
    token = lex();
    if (token[0] == OPENING_PARENTHESES):
        
        condQuad = nextQuad();
        condTrue,condFalse = condition();
        
        if (token[0] == CLOSING_PARENTHESES):
            
            backpatch(condTrue, nextQuad());
            
            exitStack.append(["while","_"]);

            brackorstat();

            exitStack.pop();
            
            genQuad('jump', '_', '_', condQuad);
            backpatch(condFalse, nextQuad());
            
            token = lex();
            
        else:
            perror("Expected ')' after '(' found '" + str(token[1]));
    else:
        perror("Expected '(' after 'while' found '" + str(token[1]));
        
def selectstat():
    global token;
    global exitStack;
    
    exitStack.append(["selectstat","_"]);
    
    token = lex();
    if (token[0] == OPENING_PARENTHESES):
        token = lex();
        if (token[0] == IDENTIFIER_ID):
            identifier = token[1];

            token = lex();
            if (token[0] == CLOSING_PARENTHESES):
                condBreak = emptyList();
                
                token = lex();
                i = 1;
                while(1):
                    if (token[0] == CONSTANT):
                        if (not(int(token[1]) == i)):
                            perror("Expected the case '" + str(i) + "' found '" + str(token[1]));
                            
                        condTrue = makeList(nextQuad());
                        genQuad('<>', i, identifier, '_');
                        
                        i += 1;
                        token = lex();
                        if (token[0] == COLON):
                            
                            brackorstat();
                            
                            condBreak = merge(condBreak, makeList(nextQuad()));
                            genQuad('jump', '_', '_', '_');
                            
                            backpatch(condTrue, nextQuad());
                            
                            token = lex();
                        else:
                            perror("Expected ';' after a constant found '" + str(token[1]));
                            
                    elif (token[0] == DEFAULT_RW):
                        
                        token = lex();
                        if (token[0] == COLON):
                            
                            brackorstat();
                            
                            backpatch(condBreak, nextQuad());

                            exitStack.pop();                            
                            token = lex();
                            
                            return;
                        else:
                            perror("Expected ';' after 'default' found '" + str(token[1]));
                    
                    else:
                        perror("Expected a constant or 'default' found '" + str(token[1]));
            else:
                perror("Expected ')' after an ID found '" + str(token[1]));
        else:
            perror("Expected and ID after '(' found '" + str(token[1]));
    else:
        perror("Expected '(' after 'select' found '" + str(token[1])); 
        
def dowhilestat():
    global token;
    global exitList;
    global exitStack;
    
    exitStack.append(["dowhile","_"]);
    
    seqQuad = nextQuad();
    brackorstat();
    
    exitStack.pop();
    
    token = lex();
    if (token[0] == WHILE_RW):
        token = lex();
        if (token[0] == OPENING_PARENTHESES):
            
            condTrue,condFalse = condition();
            
            backpatch(condTrue, seqQuad);
            
            backpatch(condFalse, nextQuad());
            
            if (not(token[0] == CLOSING_PARENTHESES)):
                perror("Expected ')' after '(' found '" + str(token[1]));
                
            backpatch(exitList, nextQuad());
            exitList = emptyList();   
                
        else:
            perror("Expected '(' after 'while' found '" + str(token[1]));
    else:
        perror("Expected 'while' found '" + str(token[1]));
        
def returnstat():
    global token;
    global returnStack;
    
    tmpList = returnStack.pop();
    blockType,blockID,flag = tmpList;
    if (blockType != "function"):
        perror("Found 'return' inside the " + str(blockType) + " block with the id " + str(blockID) + ". That's not allowed");
    
    flag = True;
        
    returnStack.append([blockType,blockID,flag]);
    
    token = lex();
    if (token[0] == OPENING_PARENTHESES):
        token = lex();
        
        exprRet = expression();
        
        genQuad(':=', exprRet, '_', 'retv');
        
        if (not(token[0] == CLOSING_PARENTHESES)):
            perror("Expected ')' after '(' found '" + str(token[1]));
            
    else:
        perror("Expected '(' after 'return' found '" + str(token[1]));
    
def printstat():
    global token;
    
    token = lex();
    if (token[0] == OPENING_PARENTHESES):
        token = lex();
        
        exprRet = expression();
        genQuad('print', exprRet, '_', '_');
        
        if (not(token[0] == CLOSING_PARENTHESES)):
            perror("Expected ')' after '(' found '" + str(token[1]));
    else:
        perror("Expected '(' after 'print' found '" + str(token[1]));
            
def callstat():
    global token;
    
    token = lex();
    if (token[0] == IDENTIFIER_ID):
        identifier = token[1];
        
        token = lex();
        if (token[0] == OPENING_PARENTHESES):
            actualpars(identifier);
            genQuad('call', identifier, '_', '_');
        else:
            perror("Expected '(' found '" + str(token[1]));
    else:    
        perror("Expected an ID after 'call' found '" + str(token[1]));
            
def actualpars(identifier):
    global token;
    
    actualparlist(identifier);
    if (not(token[0] == CLOSING_PARENTHESES)):
        perror("Expected ')' found '" + str(token[1]));
        
        
def actualparlist(identifier):
    global token;
    
    scope,enclosingScope = getTheObjectOfFuncOrProc(identifier);
        
    numOfArgs = 0;
    token = lex();
    
    if (token[0] == IN_RW or token[0] == INOUT_RW):
        
        if (numOfArgs >= len(scopeList[scope].enclosingScope[enclosingScope].arguments)):
            perror("The Function/Procedure "+str(identifier)+" was called incorrectly. Expected less arguments.");
        if (token[1] != scopeList[scope].enclosingScope[enclosingScope].arguments[numOfArgs].parmode):
            perror("The Function/Procedure "+str(identifier)+" was called incorrectly. Expected "+str(scopeList[scope].enclosingScope[enclosingScope].arguments[numOfArgs].parmode)+" found '" + str(token[1]));
        
        actualparitem();
        numOfArgs += 1;
    else:
        return;
    
    while (1):
            if (token[0] == COMMA):
                token = lex();
                if (token[0] == IN_RW or token[0] == INOUT_RW):
                    
                    if (numOfArgs >= len(scopeList[scope].enclosingScope[enclosingScope].arguments)):
                        perror("The Function/Procedure "+str(identifier)+" was called incorrectly. Expected less arguments.");
                    if (token[1] != scopeList[scope].enclosingScope[enclosingScope].arguments[numOfArgs].parmode):
                        perror("The Function/Procedure "+str(identifier)+" was called incorrectly. Expected "+str(scopeList[scope].enclosingScope[enclosingScope].arguments[numOfArgs].parmode)+" found '" + str(token[1]));
                    
                    actualparitem();
                    numOfArgs += 1;
                else:
                    perror("Expected 'in' or 'inout' after ',' found '" + str(token[1]));
            else:
                if (numOfArgs != len(scopeList[scope].enclosingScope[enclosingScope].arguments)):
                    perror("The Function/Procedure "+str(identifier)+" was called incorrectly. Expected more arguments.");
                
                return;
            
def actualparitem():
    global token;
    
    if (token[0] == IN_RW):
        token = lex();
        exprRet = expression();
        genQuad('par', exprRet, 'CV', '_');
    
    elif (token[0] == INOUT_RW):
        token = lex();
        genQuad('par', str(token[1]), 'REF', '_');
        if (not(token[0] == IDENTIFIER_ID)):
            perror("Expected an ID after inout found '" + str(token[1]));
        searchForVariable(token[1]);
        token = lex();
    
def condition():
    global token;
    
    condTrue,condFalse = boolterm();
    
    while(1):
        if(token[0] == OR_RW): 
            
            backpatch(condFalse, nextQuad());
            newTrue,newFalse = boolterm();
            
            condTrue = merge(condTrue, newTrue);
            condFalse = newFalse;
        else:
            return condTrue,condFalse;

def boolterm():
    global token;
    
    boolTermTrue,boolTermFalse = boolfactor();
    
    while(1):
        if (token[0] == AND_RW):
            
            backpatch(boolTermTrue, nextQuad());
            newTrue,newFalse = boolfactor();
            
            boolTermFalse = merge(boolTermFalse, newFalse);
            boolTermTrue = newTrue;
        else:
            return boolTermTrue,boolTermFalse;
        
def boolfactor():
    global token;
    
    token = lex();
    if (token[0] == NOT_RW):
        token = lex();
        if (token[0] == OPENING_SQUARED_BRACKETS):
            boolFactorFalse,boolFactorTrue = condition();
            
            if (not(token[0] == CLOSING_SQUARED_BRACKETS)):
                perror("Expected ']' after '[' found '" + str(token[1]));
                
        else:
            perror("Expected '[' after 'not' found '" + str(token[1]));
            
        token = lex();
    elif (token[0] == OPENING_SQUARED_BRACKETS):
        
        boolFactorTrue,boolFactorFalse = condition();
        
        if (not(token[0] == CLOSING_SQUARED_BRACKETS)):
            perror("Expected ']' after '[' found '" + str(token[1]));
        
        token = lex();
    else:
        bool1 = expression();
        operator = relationaloper();
        token = lex();
        bool2 = expression();
        
        boolFactorTrue = makeList(nextQuad());
        genQuad(operator, bool1, bool2, '_');
        
        boolFactorFalse = makeList(nextQuad());
        genQuad('jump', '_', '_', '_');
        
    return boolFactorTrue,boolFactorFalse;

def expression():
    global token;
    
    sign = optionalsign();
    num1 = sign + term();
    
    
    while (1):
        if ((token[0] == PLUS_OPERATOR) or (token[0] == MINUS_OPERATOR)):
            operator = addoper();
            token = lex();
            num2 = term();
            w = newTemp();
            genQuad(operator, num1, num2, w);
            num1 = w;
        else:
            return num1;
            
def term():
    global token;

    num1 = factor();
    while (1):
        if ((token[0] == MULTIPLY_OPERATOR) or (token[0] == DIVISION_OPERATOR)):
            operator = muloper();
            token = lex();
            num2 = factor();
            w = newTemp();
            genQuad(operator, num1, num2, w);
            num1 = w;
        else:
            return num1;
        
def factor():
    global token;
    
    if (token[0] == CONSTANT):
        constantRet =  token[1];
        token = lex();
        return constantRet;
    elif (token[0] == OPENING_PARENTHESES):
        token = lex();
        expressionRet = expression();
        if (not(token[0] == CLOSING_PARENTHESES)):
            perror("Expected ')' found '" + str(token[1]));
            
        token = lex();
        return expressionRet;
    elif (token[0] == IDENTIFIER_ID):
        idtailRet = idtail();
        return idtailRet;
    else:
        perror("Expected a constant or '(' or an ID found '" + str(token[1]));
        
def idtail():
    global token;
    
    identifier = token[1];
    
    token = lex();
    if (token[0] == OPENING_PARENTHESES):

        actualpars(identifier);
        token = lex();
        
        w = newTemp();
        genQuad('par', w, 'RET', '_');
        genQuad('call', identifier, '_', '_');
        
        return w;
    else:
        searchForVariable(identifier);
    
    return identifier;
        
def relationaloper():
    global token;
    
    if (not((token[0] == EQUAL_TO_OPERATOR) or (token[0] == LESS_THAN_OPERATOR) or (token[0] == LESS_EQUAL_OPERATOR) or (token[0] == NOT_EQUAL_OPERATOR) or (token[0] == GREATER_EQUAL_OPERATOR) or (token[0] == GREATER_THAN_OPERATOR))):
        perror("Expected '=' or '<' or '<=' or '<>' or '>=' or '>' found '" + str(token[1]));
        
    return token[1];
        
def addoper():
    global token;
    
    if (not((token[0] == PLUS_OPERATOR) or (token[0] == MINUS_OPERATOR))):
        perror("Expected '+' or '-' found '" + str(token[1]));
        
    return token[1];
        
def muloper():
    global token;

    if (not((token[0] == MULTIPLY_OPERATOR) or (token[0] == DIVISION_OPERATOR))):
        perror("Expected '*' or '/' found '" + str(token[1]));

    return token[1];
    
def optionalsign():
    global token;

    if ((token[0] == PLUS_OPERATOR) or (token[0] == MINUS_OPERATOR)):
        addoperRet = addoper();
        token = lex();
        return addoperRet;
    else:
        return "";


#===============================================================================
# </Syntax Analyzer Functions>
#===============================================================================

    
def printObjectCode(fname):
    global objectCodeList;
    
    f = open(str(fname)+'.asm','w');
    
    for line in objectCodeList:
        if (not line.endswith(":")):
            f.write("\t")
        f.write(line+"\n");
    f.close();
    
def printSymbolTable():
    global scopeList;
    
    f = open('symbolTable.txt','a');
    
    f.write("\n\tNew Print\n");
    
    for i in range(len(scopeList)-1,-1,-1):
            f.write('\n'+str(scopeList[i])+'\n\n');
            for j in range(len(scopeList[i].enclosingScope)-1,-1,-1):
                f.write(str(scopeList[i].enclosingScope[j])+'\n');
    f.close();
    
def translateIntermediateToC(fname):
    global variableList;
    
    f = open(fname+'.c','w');
    
    f.write("#include <stdio.h>\n\nint main(void){\n");
    
    for x in variableList:
        f.write("\tint "+str(x)+";\n");
    f.write("\n");
    
    with open(fname+'.int') as fd:
        for line in fd:
            lineNumber = line.split(':',1)[0];
            f.write('\tL'+str(lineNumber)+": ");
            nextCommand = [x.strip() for x in line.split(' ',1)[1].split(',')];
            if (nextCommand[0] == ':='):
                f.write(str(nextCommand[3])+" = "+str(nextCommand[1])+"; // " + str(nextCommand) + "\n");
            elif (nextCommand[0] == 'begin_block' or nextCommand[0] == 'end_block' or nextCommand[0] == 'halt'):
                f.write("// " + str(nextCommand) +"\n");
            elif (nextCommand[0] == 'jump'):
                f.write("goto L"+str(nextCommand[3])+"; // " + str(nextCommand) + "\n");
            elif (nextCommand[0] in arithmeticOperatorList):
                f.write(str(nextCommand[3])+" = "+str(nextCommand[1])+" "+str(nextCommand[0])+" "+str(nextCommand[2])+"; // " + str(nextCommand) + "\n");
            elif (nextCommand[0] in comparisonOperatorList):
                if (nextCommand[0] == '<>'):
                    f.write("if ("+str(nextCommand[1])+" != "+str(nextCommand[2])+") goto L"+str(nextCommand[3])+"; // " + str(nextCommand) + "\n");
                elif (nextCommand[0] == '='):
                    f.write("if ("+str(nextCommand[1])+" == "+str(nextCommand[2])+") goto L"+str(nextCommand[3])+"; // " + str(nextCommand) + "\n");
                else:
                    f.write("if ("+str(nextCommand[1])+" "+str(nextCommand[0])+" "+str(nextCommand[2])+") goto L"+str(nextCommand[3])+"; // " + str(nextCommand) + "\n");
            elif (nextCommand[0] == 'print'):
                f.write("printf(\"%d\\n\","+str(nextCommand[1])+"); // " + str(nextCommand) + "\n");
            else:
                f.write("// " + str(nextCommand) + "\n");
    
    f.write("\n\treturn 0;\n}");
    f.close();
    
#if(len(sys.argv) != 2):
#    print("You must enter a filename.");
#    sys.exit();
    
#filename = str(sys.argv[1]);
filename = input("Please enter the filename : ");
f = open(filename, "r+");

fname = filename.split('.')[0];

f1 = open('symbolTable.txt','w');
f1.truncate();
f1.close();

program();

saveFile = open(fname+".int","w");
saveFile.truncate();

lineCounter = 1;
for quad in quadList:
    saveFile.write(str(lineCounter)+": "+str(quad[0])+","+str(quad[1])+","+str(quad[2])+","+str(quad[3])+"\n");
    lineCounter += 1;
    
saveFile.close();

translateIntermediateToC(fname);

printObjectCode(fname);

