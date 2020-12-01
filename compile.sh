#!/bin/bash

# work in source_code
cd source_code
# build all C++ files into object files
g++ *.cc -lspot -lbddx -c

# compile 2detTELA
g++ 2detTELA.cc my_determinization.o remfin.o -lspot -lbddx -O2 -o 2detTELA

g++ benchmarkA.cc my_determinization.o remfin.o -lspot -lbddx -O2 -o benchmarkA

# return to parent dictionary
cd ..
