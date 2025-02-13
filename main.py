
import os
import argparse

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

    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str, help="The path to the file to compile")
    parser.add_argument('--print-tokens', action='store_true', help="Print the tokens")
    parser.add_argument('--print-sentences', action='store_true', help="Print the sentences")
    parser.add_argument('--print-c-program', action='store_true', help="Print the c program")
    parser.add_argument('--maintain-c-file', action='store_true', help="Delete the c file")
    parser.add_argument('--debug', action='store_true', help="Full debug mode (print tokens, sentences, c program)")

    args = parser.parse_args()

    if args.debug:
        args.print_tokens = True
        args.print_sentences = True
        args.print_c_program = True


    ast = compile(args.file, printTokens=args.print_tokens, printSentences=args.print_sentences)
    write(ast, args.file.replace(".lf", ".c"), printCProgram=args.print_c_program)

    run(args.file.replace(".lf", ".c"), args.file.replace(".lf", ""), deleteCFile= not args.maintain_c_file)





if __name__ == "__main__":
    main()