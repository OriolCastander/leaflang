


from src.tokenizer.token import Token, TokenKind


import src.parser.words as words
import src.parser.sentences as sentences

from src.utils import ALLOCATION



class Parser:

    def __init__(self) -> None:

        self.index: int
        self.tokens: list[Token]
        self.sentences: list[sentences.Sentence]



    def reset(self, tokens: list[Token]) -> None:

        self.index = 0
        self.tokens = tokens
        self.sentences = []


    def parse(self, tokens: list[Token]) -> list[sentences.Sentence]:
        """Parses the tokens, creates a list of sentences"""

        self.reset(tokens)

        while self.index < len(self.tokens):
            sentence = self._parseSentence()
            self.sentences.append(sentence)

        return self.sentences
    



    def _parseSentence(self) -> sentences.Sentence:
        """Parses a sentence"""

        token = self.tokens[self.index]
        ##if var or let, it must be a variable declaration, 
        if token.kind == TokenKind.STRING and token.value in ["var", "let"]:
            return self._parseLeafVariableDeclaration()
        

        
        elif token.kind == TokenKind.STRING and token.value == "class":
            return self._parseLeafClassDeclaration()
            

        elif token.kind == TokenKind.STRING and token.value == "def":
            return self._parseLeafFunctionDeclaration()
        

        elif token.kind == TokenKind.STRING and token.value == "return":
            return self._parseReturnSentence()

        
        elif token.kind == TokenKind.CLOSE_CUR:
            scopeClosure = sentences.ScopeClosure(token.line)
            self.index += 1
            return scopeClosure
        
        elif token.kind == TokenKind.STRING:

            word: words.Chain = self._consumeValue(allowOperators=False, allowBaseValues=False, allowFunctionCalls=True)

            nextToken = self.tokens[self.index]
            if nextToken.kind == TokenKind.SEMICOLON:
                self.index += 1
                return sentences.NakedLeafFunctionCall(token.line, word)
            
            elif nextToken.kind == TokenKind.EQUALS:
                self.index += 1
                value = self._consumeValue(allowOperators=True, allowBaseValues=True, allowFunctionCalls=True)
                closingToken = self.tokens[self.index]
                
                if closingToken.kind != TokenKind.SEMICOLON:
                    print(f"PARSING ERROR (line {closingToken.line}): After assignment, a semicolon is expected.")
                    exit(1)
                
                self.index += 1
                return sentences.Assignment(token.line, word, value)
            
            
            else:
                print(f"PARSING ERROR (line {nextToken.line}): Expected a semicolon or equals sign after the function call.")
                exit(1)

        else:
            raise Exception()



    def _parseLeafVariableDeclaration(self) -> sentences.LeafVariableDeclaration:
        """Parses a variable declaration"""

        ##STEP 1: get allocation
        variableAllocation: ALLOCATION = None
        token = self.tokens[self.index]
        initialLine = token.line

        if token.value == "let": variableAllocation = ALLOCATION.HEAP
        elif token.value == "var": variableAllocation = ALLOCATION.STACK
        else: raise Exception()
        self.index += 1




        ##STEP 2: get variable declaration
        declaration = self._parseDeclaration()

        ##STEP 3: consume the exiting semicolon
        ##TODO: in the future, an = sign and an assignment can be done here as well
        token = self.tokens[self.index]
        if token.kind != TokenKind.SEMICOLON:
            print(f"PARSING ERROR (line {token.line}): Expected a semicolon after the variable declaration.")
            exit(1)
        self.index += 1

        return sentences.LeafVariableDeclaration(initialLine, declaration, variableAllocation)




    def _parseLeafClassDeclaration(self) -> sentences.LeafClassDeclaration:
        """Parses a class declaration"""


        self.index += 1

        ##STEP 1: get name
        token = self.tokens[self.index]
        if token.kind != TokenKind.STRING:
            print(f"PARSING ERROR (line {token.line}): A class name must be a string.")
            exit(1)
        
        className = words.Mention(token.value)


        ##STEP 2: get generics
        generics = []
        self.index += 1
        token = self.tokens[self.index]
        if token.kind == TokenKind.OPEN_ANG:
            self.index += 1
            generics = self._consumeEnumerable(TokenKind.CLOSE_ANG, allowOperators=False, allowBaseValues=False, allowFunctionCalls=False)


        ##STEP 3: get semicolon before type
        token = self.tokens[self.index]


        if token.kind != TokenKind.OPEN_CUR:
            print(f"PARSING ERROR (line {token.line}): After class name, open curly is expected.")
            exit(1)

        self.index += 1

        leafClassDeclaration = sentences.LeafClassDeclaration(token.line, className, generics)
        return leafClassDeclaration




    def _parseLeafFunctionDeclaration(self) -> sentences.LeafFunctionDeclaration:
        """Parses a function declaration"""

        self.index += 1

        ##step 1: get name
        token = self.tokens[self.index]
        if token.kind != TokenKind.STRING:
            print(f"PARSING ERROR (line {token.line}): A function name must be a string.")
            exit(1)
        
        functionName = words.Mention(token.value)


        ##STEP 2: get generics
        generics = []
        self.index += 1
        token = self.tokens[self.index]
        if token.kind == TokenKind.OPEN_ANG:
            self.index += 1
            generics = self._consumeEnumerable(TokenKind.CLOSE_ANG, allowOperators=False, allowBaseValues=False, allowFunctionCalls=False)


        ##step 3: get the open par
        token = self.tokens[self.index]
        if token.kind != TokenKind.OPEN_PAR:
            print(f"PARSING ERROR (line {token.line}): Expected an open parenthesis after the function name.")
            exit(1)
        self.index += 1

        ##step 4: get parameters
        parameters = []
        while True:
            token = self.tokens[self.index]
            if token.kind == TokenKind.CLOSE_PAR:
                self.index += 1
                break
            elif token.kind == TokenKind.COMMA:
                self.index += 1
                continue
            else:
                parameters.append(self._parseDeclaration())

        ##step 5: get the colon
        token = self.tokens[self.index]
        if token.kind != TokenKind.COLON:
            print(f"PARSING ERROR (line {token.line}): Expected a colon after the function parameters.")
            exit(1)
        self.index += 1

        ##step 6: get the return type
        returnType = self._consumeValue(allowOperators=False, allowBaseValues=False, allowFunctionCalls=False)

        ##step 7: get the open cur
        token = self.tokens[self.index]
        if token.kind != TokenKind.OPEN_CUR:
            print(f"PARSING ERROR (line {token.line}): Expected an open curly after the function return type.")
            exit(1)
        self.index += 1

        leafFunctionDeclaration = sentences.LeafFunctionDeclaration(token.line, functionName, generics, parameters, returnType)
        return leafFunctionDeclaration









    def _parseDeclaration(self) -> words.Declaration:
        """Parses a declaration. Does not consume the exiting token, like the comma, semicolon, etc."""

        ##STEP 1: get mention
        mentionToken = self.tokens[self.index]
        if mentionToken.kind != TokenKind.STRING:
            print(f"PARSING ERROR (line {mentionToken.line}): Expected a string.")
            exit(1)
        mention = words.Mention(mentionToken.value)
        self.index += 1

        ##STEP 2: get colon
        colonToken = self.tokens[self.index]
        if colonToken.kind != TokenKind.COLON:
            print(f"PARSING ERROR (line {colonToken.line}): Expected a colon after the mention.")
            exit(1)
        self.index += 1

        ##STEP 3: get class descriptor
        classDescriptor = self._consumeValue(allowOperators=False, allowBaseValues=False, allowFunctionCalls=False)

        ##STEP 4: get generics (if needed)
        genericsOpeningToken = self.tokens[self.index]
        generics: list[words.Chain] = []
        if genericsOpeningToken.kind == TokenKind.OPEN_ANG:
            self.index += 1
            generics = self._consumeEnumerable(TokenKind.CLOSE_ANG, allowOperators=False, allowBaseValues=False, allowFunctionCalls=False)

        return words.Declaration(mention, classDescriptor, generics)




    def _parseReturnSentence(self) -> sentences.ReturnSentence:
        """Parses a return statement"""

        self.index += 1
        value = self._consumeValue(allowOperators=True, allowBaseValues=True, allowFunctionCalls=True)

        token = self.tokens[self.index]
        if token.kind != TokenKind.SEMICOLON:
            print(f"PARSING ERROR (line {token.line}): Expected a semicolon after the return statement.")
            exit(1)
        self.index += 1

        return sentences.ReturnSentence(token.line, value)

    def _consumeEnumerable(self, closingTokenKind: TokenKind, allowOperators: bool = True, allowBaseValues: bool = True, allowFunctionCalls: bool = True) -> list[words.Chain | words.Operator]:
        """
        Consumes a list of values, either chains or operators.
        """

        values = []
        if self.tokens[self.index].kind == closingTokenKind:
            self.index += 1
            return []

        while True:
            value = self._consumeValue(allowOperators=allowOperators, allowBaseValues=allowBaseValues, allowFunctionCalls=allowFunctionCalls)
            values.append(value)
            nextToken = self.tokens[self.index]

            if nextToken.kind == closingTokenKind:
                self.index += 1
                break
            elif nextToken.kind == TokenKind.COMMA:
                self.index += 1
                continue
            else:
                print(f"PARSING ERROR (line {nextToken.line}): Expected a comma or {closingTokenKind.name}, got {nextToken}.")
                exit(1)

        return values






    def _consumeValue(self, allowOperators: bool = True, allowBaseValues: bool = True, allowFunctionCalls: bool = True) -> words.Chain | words.Operator:
        """
        Consumes a value, either a chain or an operator. Does not consume the closure token, like the semicolon.
        TODO: might be bugy as hell, but i dont give a fuck for now
        """

        CLOSURE_TOKEN_KINDS = [TokenKind.SEMICOLON, TokenKind.COMMA, TokenKind.COLON, TokenKind.CLOSE_PAR, TokenKind.EQUALS, TokenKind.CLOSE_ANG, TokenKind.OPEN_ANG, TokenKind.OPEN_CUR]
        OPERATOR_TOKEN_KINDS = [TokenKind.PLUS]

        elements: list[words.Mention | words.LeafFunctionCallWord | str | int | float | bool] = []
        
        while True:
            token = self.tokens[self.index]
            
            if token.kind == TokenKind.NUMBER:
                if len(elements) > 0:
                    print(f"PARSING ERROR (line {token.line}): Expected a mention, not a number.")
                    exit(1)
                    
                if not allowBaseValues:
                    print(f"PARSING ERROR (line {token.line}): Expected a mention, not a number.")
                    exit(1)

                try:
                    value = int(token.value)
                except:
                    value = float(token.value)
                
                self.index += 1
                nextToken = self.tokens[self.index]
                
                if nextToken.kind not in CLOSURE_TOKEN_KINDS: ##TODO: should 4.toFloat() be allowed?
                    if allowOperators and nextToken.kind in OPERATOR_TOKEN_KINDS:
                        operatorKind = words.Operator.tokenToOperatorKind(nextToken)
                        self.index += 1
                        elements.append(value)

                        leftValue = words.Chain(elements)
                        rightValue = self._consumeValue(allowOperators=allowOperators, allowBaseValues=allowBaseValues, allowFunctionCalls=allowFunctionCalls)
                        operator = words.Operator(operatorKind, leftValue, rightValue)
                        return operator

                    print(f"PARSING ERROR (line {nextToken.line}): After number, a closure token is expected.")
                    exit(1)
                
                elements.append(value)
            
            

            
            elif token.kind == TokenKind.STRING:
                self.index += 1
                nextToken = self.tokens[self.index]

                generics = []
                if nextToken.kind == TokenKind.OPEN_ANG:
                    beforePotentialGenericsIndex = self.index
                    generics = self._consumeEnumerable(TokenKind.CLOSE_ANG, allowOperators=False, allowBaseValues=False, allowFunctionCalls=False)
                    self.index = beforePotentialGenericsIndex

                    secondNextToken = self.tokens[self.index]
                    if secondNextToken.kind == TokenKind.OPEN_PAR:
                        if not allowFunctionCalls:
                            print(f"PARSING ERROR (line {secondNextToken.line}): Expected a mention, not a function call.")
                            exit(1)
                        self.index += 1
                        arguments = self._consumeEnumerable(TokenKind.CLOSE_PAR, allowOperators=True, allowBaseValues=True, allowFunctionCalls=True)
                        elements.append(words.LeafFunctionCallWord(words.Mention(token.value), generics, arguments))

                    else:
                        self.index = beforePotentialGenericsIndex
                        return words.Chain([elements])

                elif nextToken.kind == TokenKind.OPEN_PAR:
                    if not allowFunctionCalls:
                        print(f"PARSING ERROR (line {nextToken.line}): Expected a mention, not a function call.")
                        exit(1)
                    self.index += 1
                    arguments = self._consumeEnumerable(TokenKind.CLOSE_PAR, allowOperators=True, allowBaseValues=True, allowFunctionCalls=True)
                    elements.append(words.LeafFunctionCallWord(words.Mention(token.value), generics, arguments))
                
                else:
                    elements.append(words.Mention(token.value))


            elif token.kind == TokenKind.DOT:
                self.index += 1
                continue

            elif allowOperators and token.kind in OPERATOR_TOKEN_KINDS:
                operatorKind = words.Operator.tokenToOperatorKind(token)
                self.index += 1

                if len(elements) == 0:
                    print(f"PARSING ERROR (line {token.line}): Expected a value before the operator.")
                    exit(1)

                leftValue = words.Chain(elements)
                rightValue = self._consumeValue(allowOperators=allowOperators, allowBaseValues=allowBaseValues, allowFunctionCalls=allowFunctionCalls)
                operator = words.Operator(operatorKind, leftValue, rightValue)
                return operator
                

            elif token.kind in CLOSURE_TOKEN_KINDS:
                return words.Chain(elements)
                
            else:
                print(f"PARSING ERROR (line {token.line}): Invalid token {token}.")
                exit(1)

            

        