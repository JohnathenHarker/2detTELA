# test own scheduling algorithm

import glob
from subprocess import Popen, PIPE
from time import sleep, perf_counter
import csv
import os
import psutil
import multiprocessing as mp
from datetime import datetime


# timeout for the determinisation in s
TIMEOUT = 1500

# IDs of the cores that the program should use; the cores are used for the parallel determinisation, if they are not mentioned in WATCHDOG_CORES
CORES = [0,1,2,3,4,5,6,7]

# IDs of cores that are used for whatchdog processes; can be a subset of CORES
# list shuold not be empty, otherwise the whatchdog processes use all cores of the system, which should be avoided
WATCHDOG_CORES = [0]

# memory limit for the processes in kB
MEM_LIMIT = 20000000    # 20 GB

# path where the automata for the benchmark are stored

path = "temp_hoas/benchmarkF"
path_evaluation = "results"

# set path variable for the process (and thereofre all its children)
lib_path = os.environ['LD_LIBRARY_PATH']
home = os.environ['HOME']
os.environ['LD_LIBRARY_PATH'] = '%s/usr/lib:%s' % (home,lib_path)

# pin this and watchdog processes to core 0 and 1
core_numbers = ""
for i in WATCHDOG_CORES:
    core_numbers += str(i) + ","
core_numbers = core_numbers[:-1]    # delete the last ','

os.system("taskset -p -c " + core_numbers + " %d" % os.getpid())

def popen_evaluation(command, core):
    # default values
    result = {}
    result['time'] = -1
    result['states'] = -1
    result['acc'] = -1
    result['timeout'] = False
    result['memout'] = False

    # pin task to CPU 'core'
    taskset = ['taskset', '-c', str(core)]

    command = taskset + command

    # start determinisation
    p = Popen(command, stdout=PIPE, stderr=PIPE)
    
    tic = perf_counter()

    # command to get the memory
    mem_command =['ps -q '+ str(p.pid) + ' -o rss --no-headers']
    mem_command = ['ps', '-p', str(p.pid), '-o', 'rss', '--no-headers']
    memory = 0
    toc = perf_counter()
    while (toc-tic) < TIMEOUT:
        if p.poll() is not None:
            output = p.communicate()[0].decode('UTF-8').split()
            result['timeout'] = False
            for i in range(len(output)):
                if (output[i] == 'states:'):
                    result['states'] = int(output[i+1])
                if (output[i] == 'time:'):
                    result['time'] = float(output[i+1])
                if (output[i] == 'acc:'):
                    result['acc'] = int(output[i+1])
            return result
        # computate the memory of the determinisation process
        memory = Popen( mem_command, stdout=PIPE ).communicate()[0].decode('UTF-8')[:-1]
        try:
            # if process does not exist anymore, this does not work
            mem = int(memory)
        except:
            mem = 0
        if mem > MEM_LIMIT:
            # process needs to much memory
            p.kill()
            result['memout'] = True
            return result
        sleep(0.1)
        toc = perf_counter()
    p.kill()
    result['timeout'] = True
    return result


def evaluate_aut(aut, core):
    old_automaton = popen_evaluation(['source_code/2detTELA', '--file', aut, '--type', 'old_aut'], core)
    limited = popen_evaluation(['source_code/2detTELA', '--file', aut, '--type', 'limited'], core)
    product = popen_evaluation(['source_code/2detTELA', '--file', aut, '--type', 'product'], core)
    return [core, aut,old_automaton, limited, product]


# store the results of the evaluations
evaluation = []

def log_result(result):
    core = result[0]
    idleCores.append(core)
    evaluation.append(result[1:])
    m = len(automata)
    delta = datetime.now() - start_time
    prediction = start_time + 1.0*m/len(evaluation) * delta
    if (m > len(evaluation)):
        print("determinised" , len(evaluation) , "out of", m,  "automata; prediction: finished at", prediction.strftime('%Y-%m-%d %H:%M:%S') , end="\r" )
    else:
        print("determinised" , len(evaluation) , "out of", m,  "automata; prediction: finished at", prediction.strftime('%Y-%m-%d %H:%M:%S'))
    




#### main part ###

# store the cores that are idle
idleCores = list(set(CORES) - set(WATCHDOG_CORES))

## create directories

if not os.path.exists(path):
    os.makedirs(path)

if not os.path.exists(path_evaluation):
    os.makedirs(path_evaluation)


## produce examples
start_time = datetime.now()
print('starting at', start_time.strftime('%Y-%m-%d %H:%M:%S'))
print('Generating automata')

# upper and lower bound of the acc condition
lower_bound = 2
upper_bound = 41
# number of generated automata
n = 2000

# call program to produce automata
p = Popen(['source_code/benchmarkF', '--file', path+"/automaton", '--n', str(n), '--l', str(lower_bound), '--u', str(upper_bound)])
p.wait()



# extract all .hoa files from the dictionary
automata = glob.glob(path+"/*.hoa")


# process evaluations in parallel



pool = mp.Pool(len(idleCores))
pool._maxtasksperchild = 1


print('running', len(idleCores) , 'processes in parallel on the following cores:', idleCores)
for aut in automata:
    while (len(idleCores) <1):
        # wait until a core is idle
        sleep(0.1)
    # start process on the first idle core
    core = idleCores[0]
    idleCores = idleCores[1:]
    pool.apply_async(evaluate_aut, args=(aut, core, ), callback = log_result)
   

pool.close()
pool.join()



print('write result into ', path_evaluation +'/benchmarkF.csv')
## run evaluation
with open(path_evaluation+'/benchmarkF.csv', mode='w') as out_csv:
    csv_writer = csv.writer(out_csv, delimiter= ';')
    csv_writer.writerow(['aut','old_acc', 
    'timeout_limited', 'memout_limited', 'states_limited', 'time_limited', 'acc_limited', 
    'timeout_product', 'memout_product', 'states_product', 'time_product', 'acc_product'])
    for row in evaluation:
        aut = row[0]
        old_automaton = row[1]
        limited = row[2]
        product = row[3]
        csv_writer.writerow([aut, old_automaton['acc'], 
        limited['timeout'], limited['memout'], limited['states'], limited['time'], limited['acc'], 
        product['timeout'], product['memout'], product['states'], product['time'], product['acc'],])

print('finished at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))