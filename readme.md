
# Leaflang

  

The awesomest programming language.
A language with a syntax similar to typescript that is transpiled directly to C for blazingly fast speeds. Ideal for whatever you want to do with it.
You can contribute via...

  
  
  

## Usage

**IMPORTANT:** after cloning the repo, compile the corresponding C files that will then need to be linked. In unix based systems, you can do this by running the `compile.sh` script.

```bash
cd c_libraries
./compile.sh
```

  

### Standard usage

In unix based systems, you can do the transpilation + running (remember to compile the c libraries first) via:
```bash
python main.py /path/to/your/file.lf
```
With this, the C program is compiled and  run with gcc. If you just want to translate the program to C but do not want to run it, use the ``` --only-compile ``` flag. To see all the available flags, see ```main.py```.

### Testing

I've implemented some rudimentary testing, that compares the output (as in what is piped to stdout) of leaf programs with the expected stuff that should happen. You can run all the tests with:
```bash
python runTests.py
```



## Features

In development, check out the tests folders to see the current capabilities of the language.

## To do

Stuff that is currently under development / under the intention of being developed.

 - Multiplication operator for ints.
 - Methods for classes (done?).
 - Multiple files, imports.
