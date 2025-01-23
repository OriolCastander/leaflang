"""
Various checks to make sure that words are written correctly, do not overlap...
"""

import src.compiler.compilerErrors as compilerErrors
import src.compiler.nodes as nodes
import src.compiler.structures as structures

import src.parser.sentences as sentences
import src.parser.words as words




def checkGeneric(line: int, node: nodes.ScaffoldingNode, generic: words.Chain) -> compilerErrors.CompilerError | None:
    """Checks if a generic is valid"""


    if len(generic.elements) != 1:
        return compilerErrors.InvalidGenericError(line, node, generic, compilerErrors._InvalidGenericErrorReason.NOT_SINGLE_MENTION)
    
    if type(generic.elements[0]) != words.Mention:
        return compilerErrors.InvalidGenericError(line, node, generic, compilerErrors._InvalidGenericErrorReason.NOT_SINGLE_MENTION)
    
    name = generic.elements[0].value
    
    element: sentences.LeafClassDeclaration | sentences.LeafFunctionDeclaration = node.element
    if type(element) not in [sentences.LeafClassDeclaration, sentences.LeafFunctionDeclaration]:
        raise Exception(f"Invalid element type: {type(element)}")
    
    if name == element.name.value:
        return compilerErrors.InvalidGenericError(line, node, generic, compilerErrors._InvalidGenericErrorReason.EXISTING_CLASS_OR_FUNCTION)
    
    ##check that is not an existing class or function
    if name in [structure.name for structure in node.getAll(structures.LeafClass, recursive=True, includeBase=True)]:
        return compilerErrors.InvalidGenericError(line, node, generic, compilerErrors._InvalidGenericErrorReason.EXISTING_CLASS_OR_FUNCTION)
    
    return None

