

import src.compiler.structures as structures


from src.utils import ALLOCATION, PASSING



##TODO: to revise



def writeLeafChain(leafChain: structures.LeafChain) -> str:
    """Outputs the c string representation of a leaf chain"""

    if len(leafChain.elements) == 0: raise Exception("Must have at least one element in a chain")
    if len(leafChain.elements) > 1: raise NotImplementedError()

    if type(leafChain.elements[0]) == structures.LeafMention:
        return leafChain.elements[0].cName
    
    
    elif type(leafChain.elements[0]) == structures.LeafFunctionCall:
        return writeLeafFunctionCall(leafChain.elements[0])
    
    elif type(leafChain.elements[0]) == int:
        return f"{leafChain.elements[0]}"
    
    else:
        raise NotImplementedError(f"Invalid type  to write {type(leafChain.elements[0])}")
    



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