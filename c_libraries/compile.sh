#!/bin/bash

##COMPILES ALL LIBRARIES TO .so FILES
NAMES=("std" "leaf")

for name in "${NAMES[@]}"

do
    gcc -c -fPIC code/${name}.c -o compiled/${name}.o
    ar rcs compiled/lib${name}.a compiled/${name}.o
    #gcc -shared -o compiled/lib${name}.so compiled/${name}.o
    rm compiled/${name}.o

done
