#!/bin/bash

# work in source_code
cd source_code
# build all C++ files into object files
g++ *.cc -lspot -lbddx -c

# compile 2detTELA
g++ 2detTELA.cc my_determinization.o remfin.o -lspot -lbddx -O2 -o 2detTELA

# compile for benchmark generations
g++ benchmarkA.cc my_determinization.o remfin.o -lspot -lbddx -O2 -o benchmarkA
g++ benchmarkB.cc my_determinization.o remfin.o -lspot -lbddx -O2 -o benchmarkB

# return to parent dictionary
cd ..
