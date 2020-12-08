# 2detTELA
Program to determinise transition-based Emerson-Lei automata

## Requirements
You need 
- the g++ compiler to compile the source code 
- a version of Python 3 to run the experiments. 
- the Spot library **Note:** you need to configure Spot in such a way that it uses more acceptance sets than usual to run the experiments.

## Installation
### Install Spot 

You need Spot to execute the program. The software was tested with **Spot 2.9.4**. The esiest way is to run the skript `./install.sh`. This requires
- curl
- g++ 
- make  

The skrip downloads
- Spot 2.9.4 from [this](https://www.lrde.epita.fr/dload/spot/) website
- configures Spot with `--prefix = ~/usr --enable-max-accsets=256 --disable-python`

Spot is installed locally in the home directory. If you have problems with Spot, you might consult [this page](https://spot.lrde.epita.fr/install.html) or Spot's webpage related to problems with [compiling C++ code](https://spot.lrde.epita.fr/compile.html).

### Compile the source code
If you used `./install.sh`, you can skip this step. Otherwise, compile the source code  by executing `./compile.sh`. 
## Run Experiments
Call `Python3 benchmarkname.py` to run a benchmark.  
Each benchmark skript contains the variables `TIMEOUT` and `CORES`. Change these to adjust the timeout of the determinisations and the number of parallel executions.  Keep an eye on the RAM of your machine: my computer allows every parallel part of the program to allocate ~2GB of memory per minute. This might lead to problems, if the timeout is set to high. 

The `.hoa` files of the automata for each benchmark get stored in a seperate folder in the folder `temp_hoas`.  
The `.csv` file with the evaluation of the benchmark gets stored in the folder `results`.  
After finishing the first determinisation, the skrip shows the progress of the determinisations.  

Each Python skrip runs one benchmark:
- `benchmarkCheckInstallation.py`: fast skript to test, if the installation and the linking was successfull. 20 automata with 12 states. Time limit is 10s.
- `benchmarkA.py`: 2000 automata with 12 states and 1.12 nondeterministic choices (avg.) per state. Random acceptance conditions range from length 2 to 21 (in DNF). The timeout is 120s. Compares Spot and determinisation via product.  
- `benchmarkB.py`: 500 automata with 12 states and 1.12 nondeterministic choices (avg.) per state. Acceptance condition where Spot struggles. The timeout is 300s. Compares Spot and determinisation via product.
- `benchmarkC.py`: 2000 automata with 12 states and 0.17 nondeterministic choices (avg.) per state. Random acceptance conditions range from length 2 to 21 (in DNF). The timeout is 120s. Compares Spot and determinisation via product.
