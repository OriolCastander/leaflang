

import src.compiler.structures as structures


from src.utils import ALLOCATION, PASSING



##TODO: to revise



def writeLeafChain(leafChain: structures.LeafChain) -> str:
    """Outputs the c string representation of a leaf chain"""

    if len(leafChain.elements) == 0: raise Exception("Must have at least one element in a chain")
    
    string = ""
    currentPassing: PASSING = PASSING.VALUE

    for i, element in enumerate(leafChain.elements):

        if type(element) == structures.LeafMention:
            if currentPassing == PASSING.VALUE:
               string += f"{element.cName}"
            elif currentPassing == PASSING.REFERENCE:
               string += f"->{element.cName}"

            currentPassing = element.passing
            
        
        
        elif type(element) == structures.LeafFunctionCall:
            ##TODO: if method, pass the self (current string) as argument
            #probably writeMethodCall?
            functionCallString = writeLeafFunctionCall(element)
            if currentPassing == PASSING.VALUE:
                string += f"{functionCallString}"
            elif currentPassing == PASSING.REFERENCE:
                string += f"->{functionCallString}"

            currentPassing = element.leafFunction.ret.passing
        
        elif type(element) == int:
            ##CURRENTLY CHAINS CAN ONLY CONTAIN 1 PRIMITIVE
            return f"{element}"
        
    
    
        else:
            raise NotImplementedError(f"Invalid type  to write {type(element)}")
        
    return string
    



def writeLeafFunctionCall(leafFunctionCall: structures.LeafFunctionCall) -> str:
    """Outputs the c string representation of a leaf function call"""

    if leafFunctionCall.leafFunction.customSignature is not None:
        return leafFunctionCall.leafFunction.customSignature(*leafFunctionCall.arguments)

    string = f"{leafFunctionCall.leafFunction.cName}("

    if leafFunctionCall.leafFunction.methodOf is not None:
        ##TODO: pass the variable that is calling the method as argument in the c call
        raise NotImplementedError()
    
    for i, (argument, parameter) in enumerate(zip(leafFunctionCall.arguments, leafFunctionCall.leafFunction.parameters)):
        if i>0: string += ", "
       
        argumentString = argument.write()

        ##TODO: PUT THIS SOMEWHERE ELSE BECAUSE WE'LL NEED TO REUSE IT
        if type(argument) == structures.LeafChain:
            if len(argument.elements) == 1 and type(argument.elements[0]) in [int, float]:
                string += f"{argumentString}"
                continue

        if parameter.passing == PASSING.REFERENCE:
            string += argumentString
        elif parameter.passing == PASSING.VALUE:
            string += "*" + argumentString

    string += ")"
    return string