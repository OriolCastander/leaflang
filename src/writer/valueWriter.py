

import src.compiler.structures as structures


from src.utils import ALLOCATION, PASSING



##TODO: to revise



def writeLeafChain(leafChain: structures.LeafChain, selfString: str | None = None) -> str:
    """Outputs the c string representation of a leaf chain"""

    if len(leafChain.elements) == 0: raise Exception("Must have at least one element in a chain")
    
    string = ""
    currentPassing: PASSING = PASSING.VALUE

    for i, element in enumerate(leafChain.elements):

        if type(element) == structures.LeafMention:
            if currentPassing == PASSING.VALUE:
               string += f"{element.cName}" if element.allocation == ALLOCATION.HEAP else f"{element.cName}"##PROBABLY NOT A MAINTAINABLE FIX
            elif currentPassing == PASSING.REFERENCE:
               string += f"->{element.cName}"

            currentPassing = element.passing
            
        
        
        elif type(element) == structures.LeafFunctionCall:
            ##TODO: if method, pass the self (current string) as argument
            #probably writeMethodCall?
            functionCallString = writeLeafFunctionCall(element, selfString)
            if currentPassing == PASSING.VALUE:
                string += f"{functionCallString}"
            elif currentPassing == PASSING.REFERENCE:
                string += f"->{functionCallString}"

            currentPassing = element.leafFunction.ret.passing
        
        elif type(element) == int:
            ##CURRENTLY CHAINS CAN ONLY CONTAIN 1 PRIMITIVE
            return f"{element}"
        
        elif type(element) == float:
            return f"{element}"
    
    
        else:
            raise NotImplementedError(f"Invalid type  to write {type(element)}")
    
    return string
    



def writeLeafFunctionCall(leafFunctionCall: structures.LeafFunctionCall, selfString: str | None = None) -> str:
    """Outputs the c string representation of a leaf function call"""

    if leafFunctionCall.leafFunction.customSignature is not None:
        return leafFunctionCall.leafFunction.customSignature(*leafFunctionCall.arguments)

    string = f"{leafFunctionCall.leafFunction.cName}(__LEAF_SCOPES, __LEAF_HEAP_ALLOCATIONS"

    

    if leafFunctionCall.leafFunction.constructorOf is not None:
        if selfString is None: raise Exception("Self string is required for constructor calls")
        string += ", " + selfString


    elif leafFunctionCall.leafFunction.methodOf is not None:
        ##TODO: pass the variable that is calling the method as argument in the c call
        raise NotImplementedError()
    
    for argument, parameter in zip(leafFunctionCall.arguments, leafFunctionCall.leafFunction.parameters):
        string += ", "
        argumentString = argument.write()

        ##TODO: PUT THIS SOMEWHERE ELSE BECAUSE WE'LL NEED TO REUSE IT
        if type(argument) == structures.LeafChain:
            if len(argument.elements) == 1 and type(argument.elements[0]) in [int, float]:
                string += f"{argumentString}"
                continue
        
        argumentPassing = argument.getFinalPassing()

        if parameter.passing == PASSING.REFERENCE and argumentPassing == PASSING.REFERENCE:
            string += argumentString
        elif parameter.passing == PASSING.VALUE and argumentPassing == PASSING.REFERENCE:
            string += "*" + argumentString
        elif parameter.passing == PASSING.REFERENCE and argumentPassing == PASSING.VALUE:
            raise NotImplementedError("Cannot pass value by reference")
        elif parameter.passing == PASSING.VALUE and argumentPassing == PASSING.VALUE:
            string += argumentString
    string += ")"
    return string