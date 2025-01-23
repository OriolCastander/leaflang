
import os

from src.tokenizer import Tokenizer
from src.parser import Parser

from src.compiler import Compiler
from src.compiler import nodes

from src.writer import Writer


def compile(programPath: str, printTokens: bool = False, printSentences: bool = False) -> nodes.ScopeNode:
    

    with open(programPath, "r") as file:
        programString = file.read()

    tokenizer = Tokenizer()
    tokens = tokenizer.tokenize(programString)
    
    
    if printTokens:
        print("tokens:")
        for i, token in enumerate(tokens):
            print(f"{i}: {token}")
        print("\n\n")


    parser = Parser()
    sentences = parser.parse(tokens)
    
    
    if printSentences:
        print("sentences:")
        for sentence in sentences:
            print(sentence)
        print("\n\n")

    compiler = Compiler()
    ast = compiler.compile(sentences)
    return ast





def write(ast: nodes.ScopeNode, programPath: str, printCProgram: bool = False) -> None:
    """Writes the ast into a c program"""

    writer = Writer()
    cProgram = writer.write(ast)

    if printCProgram:
        print("c program:")
        print(cProgram)
        print("\n\n")

    with open(programPath, "w") as file:
        file.write(cProgram)



def run(programPath: str, outputPath: str, deleteCFile: bool = False) -> None:
    """Runs the program"""

    os.system(f"gcc {programPath} -Lc_libraries/compiled -lstd -lleaf -o {outputPath} && {outputPath}")
    os.system(f"rm {outputPath}")
    if deleteCFile:
        os.system(f"rm {programPath}")



def main():

    ast = compile("examples/test.lf", printTokens=False, printSentences=True)
    write(ast, "examples/test.c", printCProgram=True)

    run("examples/test.c", "examples/test", deleteCFile=False)





if __name__ == "__main__":
    main()