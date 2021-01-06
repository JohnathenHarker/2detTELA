
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

# IDs of the cores that the program should use; the first two cores are used for the wathchdog processes, the other cores for the parallel determinisation
CORES = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
# memory limit for the processes in kB
MEM_LIMIT = 20000000 # 20 GB

# path where the automata for the benchmark are stored

path = "temp_hoas/benchmarkG"
path_evaluation = "results"

# set path variable for the process (and thereofre all its children)
lib_path = os.environ['LD_LIBRARY_PATH']
home = os.environ['HOME']
os.environ['LD_LIBRARY_PATH'] = '%s/usr/lib:%s' % (home,lib_path)

# pin this and watchdog processes to core 0 and 1
os.system("taskset -p -c " + str(CORES[0]) +","+ str(CORES[1]) + " %d" % os.getpid())

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
    spot = popen_evaluation(['source_code/2detTELA', '--file', aut, '--type', 'spot'], core)
    product = popen_evaluation(['source_code/2detTELA', '--file', aut, '--type', 'product'], core)
    me1 = popen_evaluation(['source_code/2detTELA', '--file', aut, '--type', 'me1'], core)
    me2 = popen_evaluation(['source_code/2detTELA', '--file', aut, '--type', 'me2'], core)
    me3 = popen_evaluation(['source_code/2detTELA', '--file', aut, '--type', 'me3'], core)
    limited = popen_evaluation(['source_code/2detTELA', '--file', aut, '--type', 'limited'], core)
    return [core, aut,old_automaton, spot, product, me1, me2, me3, limited]


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
idleCores = CORES[2:]

## create directories

if not os.path.exists(path):
    os.makedirs(path)

if not os.path.exists(path_evaluation):
    os.makedirs(path_evaluation)


## produce examples
start_time = datetime.now()
print('starting at', start_time.strftime('%Y-%m-%d %H:%M:%S'))
print('Generating automata')

# upper bound of the number of states
n = 50

# call program to produce automata
p = Popen(['source_code/benchmarkG', '--file', path+"/automaton", '--n', str(n)])
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



print('write result into ', path_evaluation +'/benchmarkG.csv')
## run evaluation
with open(path_evaluation+'/benchmarkG.csv', mode='w') as out_csv:
    csv_writer = csv.writer(out_csv, delimiter= ';')
    csv_writer.writerow(['aut','old_acc',
    'timeout_spot', 'memout_spot', 'states_spot', 'time_spot', 'acc_spot',
    'timeout_product', 'memout_product', 'states_product', 'time_product', 'acc_product',
    'timeout_me1', 'memout_me1', 'states_me1', 'time_me1', 'acc_me1',
    'timeout_me2', 'memout_me2', 'states_me2', 'time_me2', 'acc_me2',
    'timeout_me3', 'memout_me3', 'states_me3', 'time_me3', 'acc_me3',
    'timeout_limited', 'memout_limited', 'states_limited', 'time_limited', 'acc_limited',])
    for row in evaluation:
        aut = row[0]
        old_automaton = row[1]
        spot = row[2]
        product = row[3]
        me1 = row[4]
        me2 = row[5]
        me3 = row[6]
        limited = row[7]
        csv_writer.writerow([aut, old_automaton['acc'], 
        spot['timeout'], spot['memout'], spot['states'], spot['time'], spot['acc'], 
        product['timeout'], product['memout'], product['states'], product['time'], product['acc'],
        me1['timeout'], me1['memout'], me1['states'], me1['time'], me1['acc'],
        me2['timeout'], me2['memout'], me2['states'], me2['time'], me2['acc'],
        me3['timeout'], me3['memout'], me3['states'], me3['time'], me3['acc'],
        limited['timeout'], limited['memout'], limited['states'], limited['time'], limited['acc']])

print('finished at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))