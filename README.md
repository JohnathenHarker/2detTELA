# 2detTELA
Program to determinise transition-based Emerson-Lei automata

## Requirements
You need the g++ compiler to compile the source code and a version of Python 3 to run the experiments. Additionally you need Spot, which can be installed using the following instructions. **Note:** you need to configure Spot in such a way that it uses more acceptance sets than usual to run the experiments.

## Installation
### Install Spot 
You need Spot to execute the program. The software was tested with **Spot 2.9.4**. 
First, download Spot from its [website](https://www.lrde.epita.fr/dload/spot/).

Perform the following steps to install Spot:  
1.`cd` to the directory containing the package's source code  
2. run the following commands:  

    ./configure  --enable-max-accsets=256  
    make  
    make install
 
If you have problems with Spot, you might consult [this page](https://spot.lrde.epita.fr/install.html) or Spot's webpage related to problems with [compiling C++ code](https://spot.lrde.epita.fr/compile.html).

### Compile the source code
Compile the source code  by executing `./compile.sh`.

## Run Experiments
TODO: how to run the skript with the experiments: different skirpts for different data sets
TODO: where are the .hoa files stored
TODO: where is the result (.csv) stored
