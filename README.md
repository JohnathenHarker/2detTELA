# 2detTELA
Program to determinise transition-based Emerson-Lei automata

## Structure  
the folders constain the following files:  
- `source_code`: source files of the program
- `temp_hoas`: sets of the automata that we use in the experiments. The automata are represented by `.hoa`-files.
- `results`: `.csv`-files with the acquired data from the benchmarks
- `figures`: `.tex`-files to produce figures for the thesis and the figures themselves 

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
- configures Spot with `--prefix ~/usr --enable-max-accsets=256 --disable-python`

Spot is installed locally in the home directory. If you have problems with Spot, you might consult [this page](https://spot.lrde.epita.fr/install.html) or Spot's webpage related to problems with [compiling C++ code](https://spot.lrde.epita.fr/compile.html).

### Compile the source code
If you used `./install.sh`, you can skip this step. Otherwise, compile the source code  by executing `./compile.sh`. 
## Run Experiments
Call `python3 benchmarkname.py` to run a benchmark.  
Each benchmark skript contains the variables `TIMEOUT`, `CORES`, `WATCHDOG_CORES` and `MEM_LIMIT`. Change these to adjust:
- the timeout of the determinisations 
- the IDs of the cores that the program uses (and therefore the number of parallel executions). Note: should contain at least one ID that is not part of `WATCHDOG_CORES`
- tht IDs of the cores that are used for the watchdog processes and not for the parallel executions of the determinisation algorithms; amout of elements determins the number of cores for the watchdog processes; can overlap with `CORES`but does not need to do so; should contain at least one element
- the maximum RAM that one of the parallel determinisations can use. Note: you may need about (length(`CORES`))*`MEM_LIMIT` RAM in your machine.




The `.hoa` files of the automata for each benchmark get stored in a seperate folder in the folder `temp_hoas`.  
The `.csv` file with the evaluation of the benchmark gets stored in the folder `results`.  
After finishing the first determinisation, the skrip shows the progress of the determinisations.  

Each Python skrip runs one benchmark:
- `benchmarkCheckInstallation.py`: fast skript to test, if the installation and the linking was successfull. 20 automata with 12 states. Time limit is 10s.
- `benchmarkA.py`: 2000 automata with 12 states and 1.12 nondeterministic choices (avg.) per state. Random acceptance conditions range from length 2 to 21 (in DNF). The timeout is 1500s, the memory limit is 20GB. Compares Spot and determinisation via product.  
- `benchmarkB.py`: 500 automata with 12 states and 1.12 nondeterministic choices (avg.) per state. Acceptance condition where Spot struggles. The timeout is 1500s, the memory limit is 20GB. Compares Spot and determinisation via product.
- `benchmarkC.py`: 2000 automata with 12 states and 0.17 nondeterministic choices (avg.) per state. Random acceptance conditions range from length 2 to 21 (in DNF). The timeout is 1500s, the memory limit is 20GB. Compares Spot and determinisation via product.
- `benchmarkD.py`: 2000 automata with 12 states and 2.28 nondeterministic choices (avg.) per state. Random acceptance conditions range from length 2 to 21 (in DNF). The timeout is 1500s, the memory limit is 20GB. Compares Spot and determinisation via product.
- `benchmarkE.py`: 999 automata with 12 states and 0.17, 1.12 or 2.28 nondeterministic choices (avg.) per state. Random acceptance conditions range from length 2 to 21 (in DNF). The timeout is 1500s, the memory limit is 20GB. Compares all approaches (Spot, determinisation via product, determinisation via product without set-cover optimisation, the three other new determinisation algorithms, limited-deterministic).
- `benchmarkF.py`: 2000 automata with 15 states and 3.3 nondeterministic choices (avg.) per state. Random acceptance conditions range from length 2 to 41 (in DNF). The timeout is 1500s, the memory limit is 20GB. Compares determinisation via product and limited-deterministic.
- `benchmarkG.py`: sequence of 50 automata that are described as an example in the thesis. The timeout is 1500s, the memory limit is 20GB. Compares all approaches (Spot, determinisation via product, the three other new determinisation algorithms, limited-deterministic).

### Corresponding Benchmarks in Thesis
Some of the benchmarks are combined to form the benchmarks in the thesis: 
thesis | repository
-------|---------
benchmark 1 | benchmark E
benchmark 2 | benchmarks A, C, D
benchmark 3 | benchmark G
benchmark 4 | benchmark B
benchmark 5 | benchmark F

## Create Figures
Running `python3 evaluate.py` after running the bechmarks produces a number of `.csv` files in the folder `figures` that are used by the LaTex scripts in the same folder to create all the plots.  
Running `make_figures.sh` in the folder `figures` calls `pdflatex` to produce all the figures from the `.tex` files.
