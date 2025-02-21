
from enum import IntEnum
import src.compiler.structures as structures
import src.compiler.nodes as nodes

import src.parser.words as words
import src.parser.sentences as sentences

from src.utils import OperatorKind

class CompilerError:

    def __init__(self, line: int, causingNode: nodes.TreeNode, message: str) -> None:
        self.line = line
        self.causingNode = causingNode
        self.message = message


    def __repr__(self) -> str:
        return f"Compiler error at line {self.line}: {self.message}"
    


class _InvalidGenericErrorReason(IntEnum):

    NOT_SINGLE_MENTION = 0
    EXISTING_CLASS_OR_FUNCTION = 1


class InvalidGenericError(CompilerError):
    """An error that occurs when a generic is invalid"""

    def __init__(self, line: int, causingNode: nodes.TreeNode | nodes.ScaffoldingNode, generic: words.Chain, reason: _InvalidGenericErrorReason) -> None:
        

        super().__init__(line, causingNode, f"Invalid generic {generic}: {reason.name}")
        
        self.reason: _InvalidGenericErrorReason = reason



class InvalidNameError(CompilerError):
    """An error that occurs when a name is invalid"""

    def __init__(self, line: int, causingNode: nodes.TreeNode | nodes.ScaffoldingNode, name: words.Chain) -> None:
        super().__init__(line, causingNode, f"Invalid name {name}")



class InvalidParameterNameError(CompilerError):
    """An error that occurs when a parameter name is invalid"""

    def __init__(self, line: int, causingNode: nodes.TreeNode | nodes.ScaffoldingNode, name: str) -> None:
        super().__init__(line, causingNode, f"Invalid parameter name {name}")




class LeafClassNotFoundError(CompilerError):
    """An error that occurs when a leaf class is not found"""

    def __init__(self, line: int, causingNode: nodes.TreeNode | nodes.ScaffoldingNode, chain: words.Chain) -> None:
        super().__init__(line, causingNode, f"Leaf class {chain} not found")




class InvalidStructureError(CompilerError):
    """An error that occurs when a structure is invalid"""

    def __init__(self, line: int, causingNode: nodes.TreeNode | nodes.ScaffoldingNode, chain: words.Chain, expectedType: type, actualType: type) -> None:
        super().__init__(line, causingNode, f"Invalid structure {chain}: expected {expectedType}, got {actualType}")



class LeafClassMismatchError(CompilerError):
    """Error when classes that are expected equal are not"""

    def __init__(self, line: int, causingNode: nodes.TreeNode, expectedLeafClass: structures.LeafClass, actualLeafClass: structures.LeafClass) -> None:
        super().__init__(line, causingNode, f"Invalid class: expected {expectedLeafClass.name}, got {actualLeafClass.name}")



class InvalidOperatorError(CompilerError):
    """Error when an operator is invalid"""

    def __init__(self, line: int, causingNode: nodes.TreeNode, leafClass: structures.LeafClass, operatorKind: OperatorKind) -> None:
        super().__init__(line, causingNode, f"Invalid operator {operatorKind} for class {leafClass.name}")



class InvalidSentenceError(CompilerError):
    """Error when a structure is invalid"""

    def __init__(self, line: int, causingNode: nodes.TreeNode, sentence: sentences.Sentence) -> None:
        super().__init__(line, causingNode, f"Invalid sentence {sentence}")
