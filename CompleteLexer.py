class Regex:
    def __init__(self, pred , next, value):
        self.pred = pred
        self.next = next
        self.value = value

    def __str__(self):
        my_str = ""

        if (self.value == "STAR"):
            my_str += "STAR("
            if(self.next != None):
                my_str += str(self.next)
            my_str += ")"

            return my_str

        elif (self.value == "PLUS"):
            my_str += "PLUS("
            if(self.next != None):
                my_str += str(self.next)
            my_str += ")"

            return my_str
            
        elif (self.value == "CONCAT"):
            my_str += "CONCAT("

            if(self.next != None):
                my_str += str(self.next[0]) + "," + str(self.next[1])

            my_str += ")"

            return my_str
            
        elif (self.value == "UNION"):
            my_str += "UNION("

            if(self.next != None):
                my_str += str(self.next[0]) + "," + str(self.next[1])

            my_str += ")"

            return my_str
            
        else:
            return self.value

class DFA:
    def __init__(self, nfa, name):
        eps_cls = []
        for i in range(0, nfa.no_states):
            act_eps_cls = set()
            act_eps_cls.add(i)

            state_queue = [i]
            visited = [0] * nfa.no_states

            while len(state_queue) > 0:
                act_state = state_queue.pop(0)

                if ((act_state, None) in nfa.delta_func):
                    next_states = nfa.delta_func[(act_state, None)]

                    for next_s in next_states:
                        if visited[next_s] == 0:
                            state_queue.append(next_s)
                            visited[next_s] = 1
                            act_eps_cls.add(next_s)

            eps_cls.append(list(act_eps_cls))

        aux_dic = []
        states_queue = [eps_cls[0]]

        myAlfabet = list(nfa.alfabet)
        myAlfabet.sort()

        while(len (states_queue) > 0):
            act_states = states_queue.pop(0)
            aux_dic.append((act_states, []))

            for act_char in myAlfabet:
                new_states = set()
                for act_s in act_states:
                    if((act_s, act_char) in nfa.delta_func):
                        for new_s in nfa.delta_func[(act_s, act_char)]:
                            for s in eps_cls[new_s]:
                                new_states.add(s)
                
                if(len(new_states) == 0):
                    aux_dic[-1][1].append(None)
                else:
                    aux_dic[-1][1].append(list(new_states))

                    found = False
                    for d in aux_dic:
                        if d[0] == list(new_states):
                            found = True
                            break
                    if not found:
                        states_queue.append(list(new_states))

        self.name = name
        self.initial_state = 0
        self.delta_func = {}
        self.non_sink_states = []
        self.final_states = set()
        self.alfabet = myAlfabet
        self.no_states = len(aux_dic) + 1

        for i in range(0, len(aux_dic)):
            for k in range(0, len(aux_dic[i][1])):
                states = aux_dic[i][1][k]

                index = len(aux_dic)
                for j in range(0, len(aux_dic)):
                    if (states == aux_dic[j][0]):
                        index = j
                        break

                self.delta_func[i, myAlfabet[k]] = index

        for i in range(0, len(aux_dic)):
            states = aux_dic[i][0]
            is_final = False

            for s in states:
                if s == nfa.final_state:
                    is_final = True
                    break
            
            if is_final:
                self.final_states.add(i)

        for state in range(0, self.no_states):
            ok = False
            for c in myAlfabet:
                if (state, c) in self.delta_func:
                    if self.delta_func[state, c] != state:
                        ok = True
                        break
            if ok:
                self.non_sink_states.append(state)


        for c in myAlfabet:
            self.delta_func[len(aux_dic), c] = len(aux_dic)
            
    def NextConfig(self, input):
        state = input[0]
        word = input[1]

        if(word == ""):
            if (list(self.final_states).count(state) > 0):
                return True
            elif (self.non_sink_states.count(state) > 0):
                return ""
            else:
                return False

        act_char = word[0]
        next_state = None
        
        for c in self.delta_func:
            if c == (state, act_char):
                next_state = self.delta_func[c]

        if next_state == None:
            return False

        return (next_state, word[1:])

    def Accept(self, word):
        next_conf = self.NextConfig((self.initial_state, word))
        while((next_conf != True) & (next_conf != False)):
            next_conf = self.NextConfig(next_conf)

        return next_conf

    def __str__(self):
        return str(self.name) + " " + str(self.initial_state) + " " + str(self.delta_func) \
         + " " + str(self.final_states) + " " + str(self.non_sink_states)

class NFA:
    def __init__(self, regex, offset):
        if (regex.value == "UNION"):
            nfa_1 = NFA(regex.next[0], offset + 2)
            nfa_2 = NFA(regex.next[1], offset + 2 + nfa_1.no_states)

            self.initial_state = offset + 0
            self.delta_func = {}
            self.final_state = offset + 1
            self.alfabet = set()

            for a in nfa_1.alfabet:
                self.alfabet.add(a)

            for a in nfa_2.alfabet:
                self.alfabet.add(a)

            self.no_states = 2 + nfa_1.no_states + nfa_2.no_states

            self.delta_func[(self.initial_state, None)] = [nfa_1.initial_state, nfa_2.initial_state]
            nfa_1.delta_func[(nfa_1.final_state, None)] = [self.final_state]
            nfa_2.delta_func[(nfa_2.final_state, None)] = [self.final_state]

            self.delta_func = {**self.delta_func, **nfa_1.delta_func}
            self.delta_func = {**self.delta_func, **nfa_2.delta_func}

        elif (regex.value == "CONCAT"):
            nfa_1 = NFA(regex.next[0], offset)
            nfa_2 = NFA(regex.next[1], offset + nfa_1.no_states)

            self.initial_state = nfa_1.initial_state
            self.delta_func = {}
            self.final_state = nfa_2.final_state
            self.alfabet = set()

            for a in nfa_1.alfabet:
                self.alfabet.add(a)

            for a in nfa_2.alfabet:
                self.alfabet.add(a)

            self.no_states = nfa_1.no_states + nfa_2.no_states

            self.delta_func[(nfa_1.final_state, None)] = [nfa_2.initial_state]

            self.delta_func = {**self.delta_func, **nfa_1.delta_func}
            self.delta_func = {**self.delta_func, **nfa_2.delta_func}
        
        elif (regex.value == "STAR"):
            nfa_1 = NFA(regex.next, offset + 2)

            self.initial_state = offset + 0
            self.delta_func = {}
            self.final_state = offset + 1
            self.alfabet = set()

            for a in nfa_1.alfabet:
                self.alfabet.add(a)

            self.no_states = 2 + nfa_1.no_states

            self.delta_func[(self.initial_state, None)] = [self.final_state, nfa_1.initial_state]

            nfa_1.delta_func[(nfa_1.final_state, None)] = [nfa_1.initial_state, self.final_state]

            self.delta_func = {**self.delta_func, **nfa_1.delta_func}

        elif (regex.value == "PLUS"):
            nfa_1 = NFA(regex.next, offset + 2)

            self.initial_state = offset + 0
            self.delta_func = {}
            self.final_state = offset + 1
            self.alfabet = set()

            for a in nfa_1.alfabet:
                self.alfabet.add(a)

            self.no_states = 2 + nfa_1.no_states

            self.delta_func[(self.initial_state, None)] = [nfa_1.initial_state]

            nfa_1.delta_func[(nfa_1.final_state, None)] = [nfa_1.initial_state, self.final_state]

            self.delta_func = {**self.delta_func, **nfa_1.delta_func}

        else:
            self.initial_state = offset + 0
            self.delta_func = {}
            self.final_state = offset + 1

            self.alfabet = set()
            self.alfabet.add(regex.value)

            self.no_states = 2

            self.delta_func[(self.initial_state, regex.value)] = [self.final_state]

    def __str__(self):
        myStr = "NFA:\n\tInitial state: " + str(self.initial_state) + "\n\tFinal State: " + str(self.final_state) + "\n"
        myStr += str(self.delta_func)

        return myStr

def getOrdValue(regex):
    if regex.value == "STAR":
        return 1
    elif regex.value == "PLUS":
        return 1
    elif regex.value == "CONCAT":
        return 0
    elif regex.value == "UNION":
        return 0
    elif regex.value == "(":
        return 0
    elif regex.value == ")":
        return 0

# Connect operator 'reg' with the regex in regexStack.
def updateRegexStack(regexStack, reg):
    if (reg.value == "PLUS") | (reg.value == "STAR"):
        r = regexStack.pop()
        reg.next = r
        regexStack.append(reg)

    elif (reg.value == "CONCAT") | (reg.value == "UNION"):
        r1 = regexStack.pop()
        r2 = regexStack.pop()
        reg.next = (r2, r1)
        regexStack.append(reg)
    return regexStack

# Compute "(e)" regex if it's that case. Check operators precedence in opStack.
def updateStacks(regexStack, opStack):
    if (len(opStack) == 0):
        return (regexStack, opStack)

    if (opStack[-1].value == ")"):
        actOp = opStack.pop()
        actOp = opStack.pop()

        while (actOp.value != "("):
            regexStack = updateRegexStack(regexStack, actOp)
            actOp = opStack.pop()

    while(len(opStack) > 1):
        opTop = opStack.pop()
        opDown = opStack.pop()

        if((opTop.value == "(") | (opTop.value == ")") | (opDown.value == "(") | (opDown.value == ")")):
            opStack.append(opDown)
            opStack.append(opTop)
            break

        if(getOrdValue(opTop) <= getOrdValue(opDown)):
            regexStack = updateRegexStack(regexStack, opDown)
            opStack.append(opTop)
        else:
            opStack.append(opDown)
            opStack.append(opTop)
            break

    return (regexStack, opStack)

def parseRegex(regexValue):
    regexStack = []
    opStack = []
    concat = False

    index = 0
    while (index < len(regexValue)):
        actChar = regexValue[index]
        if actChar.isalnum():
            if concat:
                opStack.append(Regex(None, None, "CONCAT"))
                ans = updateStacks(regexStack, opStack)
                regexStack = ans[0]
                opStack = ans[1]

            regexStack.append(Regex(None, None, actChar))

            concat = True
        elif actChar == '\'':
            if concat:
                opStack.append(Regex(None, None, "CONCAT"))
                ans = updateStacks(regexStack, opStack)
                regexStack = ans[0]
                opStack = ans[1]

            value = ""
            index += 1
            while(regexValue[index] != '\''):
                value += regexValue[index]
                index += 1

            if value == "\\n":
                regexStack.append(Regex(None, None, "\n"))
            else:
                regexStack.append(Regex(None, None, value))
            concat = True
        
        elif actChar == '+':
            opStack.append(Regex(None, None, "PLUS"))

        elif actChar == '*':
            opStack.append(Regex(None, None, "STAR"))

        elif actChar == '|':
            opStack.append(Regex(None, None, "UNION"))
            concat = False

        elif actChar == '(':
            if concat:
                opStack.append(Regex(None, None, "CONCAT"))
                ans = updateStacks(regexStack, opStack)
                regexStack = ans[0]
                opStack = ans[1]

            opStack.append(Regex(None, None, "("))
            concat = False

        elif actChar == ')':
            opStack.append(Regex(None, None, ")"))

        ans = updateStacks(regexStack, opStack)
        regexStack = ans[0]
        opStack = ans[1]
        index += 1

    while (len(opStack) > 0):
        actOp = opStack.pop()
        regexStack = updateRegexStack(regexStack, actOp)

    return regexStack[0]

def lexer(dfas, word):
    indexFirst = 0
    indexLast = 1
    indexAccept = 0

    lexems = []
    lastAccDFAs = []
    activeDFAs = dfas

    while(indexLast <= len(word) + 1):
        actLex = word[indexFirst : indexLast]

        acceptDFAs = []
        runningDFAs = []
        
        for d in activeDFAs:
            next_conf = d.NextConfig((d.initial_state, actLex))
            while((next_conf != True) & (next_conf != False) & (next_conf != "")):
                next_conf = d.NextConfig(next_conf)

            if (next_conf == ""):
                runningDFAs.append(d)

            if (next_conf == True):
                acceptDFAs.append(d)
                indexAccept = indexLast

        if(len(acceptDFAs) > 0):
            indexAccept = indexLast
        
        if((len(acceptDFAs) == 0) & (len(runningDFAs) == 0)):
            if len(lastAccDFAs) == 0:
                return indexLast - 1

            actualLastDfa = None
            for actDFA in dfas:
                if actDFA in lastAccDFAs:
                    actualLastDfa = actDFA
                    break

            lexems.append((actualLastDfa.name, word[indexFirst : indexAccept]))

            indexFirst = indexAccept
            indexAccept = indexFirst
            indexLast = indexFirst
            lastAccDFAs = []

            activeDFAs = dfas
        else:
            activeDFAs = acceptDFAs + runningDFAs
            

        if(len(acceptDFAs) > 0):
            lastAccDFAs = acceptDFAs

        indexLast += 1
        
    if len(lastAccDFAs) != 0:
        actualLastDfa = None
        for actDFA in dfas:
            if actDFA in lastAccDFAs:
                actualLastDfa = actDFA
                break

        lexems.append((actualLastDfa.name, word[indexFirst : indexLast - 1]))
    else:
        return -1

    return lexems

def runcompletelexer(specFileName, inputFileName, outputFileName):
    specFile = open(specFileName, mode='r')
    mySpec = specFile.read()
    specFile.close()

    inputFile = open(inputFileName, mode='r')
    myInput = inputFile.read()
    inputFile.close()

    regexStrs = mySpec.split("\n")

    outputFile = open(outputFileName, mode = 'w')
    myDFAs = []

    for i in range(0, len(regexStrs)):
        if regexStrs[i] != "":
            indexSpace = regexStrs[i].find(' ')
            indexEnd = regexStrs[i].find(';')
            regexName = regexStrs[i][0 : indexSpace]
            regexValue = regexStrs[i][indexSpace + 1 : indexEnd]

            regexObj = parseRegex(regexValue)

            myNFA = NFA(regexObj, 0)
            myDFA = DFA(myNFA, regexName)
            myDFAs.append(myDFA)

    ans = lexer(myDFAs, myInput)

    if not isinstance(ans, list):
        outputFile.write("No viable alternative at character " + ("EOF" if (ans == -1) else str(ans)) + ", line 0")
        return 

    for line in ans:
        outputFile.write(line[0] + " ")
        for t in line[1]:
            if t == '\n':
                outputFile.write('\\n')
            else:
                outputFile.write(t)
        outputFile.write('\n')

    outputFile.close()