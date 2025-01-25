

import src.compiler.structures as structures





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
    
    for i, argument in enumerate(leafFunctionCall.arguments):
        if i>0: string += ", "
        
        if type(argument) == int:
            string += f"{argument}"
        elif type(argument) == float:
            raise NotImplementedError()
        elif type(argument) == structures.LeafValue:
            string += argument.write()

    string += ")"
    return string