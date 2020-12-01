# 2detTELA
Program to determinise transition-based Emerson-Lei automata

## Requirements
You need 
- the g++ compiler to compile the source code 
- a version of Python 3 to run the experiments. 
- the Spot library **Note:** you need to configure Spot in such a way that it uses more acceptance sets than usual to run the experiments.

## Installation
### Install Spot 

You need Spot to execute the program. The software was tested with **Spot 2.9.4**. The esiest way is to run the skript `./install.sh`. This downloads and installs
- curl
- g++ 
- make
- Spot 2.9.4 from [this](https://www.lrde.epita.fr/dload/spot/) website
- configures Spot with `--enable-max-accsets=256 --disable-python`

You need to approve some of the steps to install curl, g++ and make.
 
If you have problems with Spot, you might consult [this page](https://spot.lrde.epita.fr/install.html) or Spot's webpage related to problems with [compiling C++ code](https://spot.lrde.epita.fr/compile.html).

### Compile the source code
I you used `./install.sh` you can skip this step. Otherwise, compile the source code  by executing `./compile.sh`. 
## Run Experiments
TODO: how to run the skript with the experiments: different skirpts for different data sets
TODO: where are the .hoa files stored
TODO: where is the result (.csv) stored
