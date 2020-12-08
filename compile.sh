#!/bin/bash

# work in source_code
cd source_code
# build all C++ files into object files
g++ -I$HOME/usr/include *.cc -L$HOME/usr/lib -lspot -lbddx -c

# compile 2detTELA
g++ -I$HOME/usr/include 2detTELA.cc my_determinization.o remfin.o -L$HOME/usr/lib -lspot -lbddx -O2 -o 2detTELA

# compile for benchmark generations
g++ -I$HOME/usr/include benchmarkA.cc my_determinization.o remfin.o -L$HOME/usr/lib -lspot -lbddx -O2 -o benchmarkA
g++ -I$HOME/usr/include benchmarkB.cc my_determinization.o remfin.o -L$HOME/usr/lib -lspot -lbddx -O2 -o benchmarkB
g++ -I$HOME/usr/include benchmarkC.cc my_determinization.o remfin.o -L$HOME/usr/lib -lspot -lbddx -O2 -o benchmarkC

# return to parent dictionary
cd ..
