import glob
from subprocess import Popen, PIPE
from time import sleep, perf_counter
import csv
import os
import multiprocessing as mp
from datetime import datetime


# timeout for the determinisation in s
TIMEOUT = 10

# number of parallel processes
# should be at least one core less than the number of cores of the system, to give the watchdog processes some ressources
# here: leave two cores for the system
CORES = 4

# path where the automata for the benchmark are stored

path = "temp_hoas/benchmarkCheckInstallation"
path_evaluation = "results"

# set path variable for the process (and thereofre all its children)
Popen(['export LD_LIBRARY_PATH=$HOME/usr/lib:$LD_LIBRARY_PATH" '], shell = True)

def popen_evaluation(command):
    # default values

    result = {}
    result['time'] = -1
    result['states'] = -1
    result['acc'] = -1
    result['timeout'] = True

    p = Popen(command, stdout=PIPE, stderr=PIPE)
    tic = perf_counter()
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
        sleep(0.1)
        toc = perf_counter()
    p.kill()
    return result


def evaluate_aut(aut):
    #print('process automaton ' + aut) # call program instead to determinise automaton
    old_automaton = popen_evaluation(['source_code/2detTELA', '--file', aut, '--type', 'old_aut'])
    spot = popen_evaluation(['source_code/2detTELA', '--file', aut, '--type', 'spot'])
    product = popen_evaluation(['source_code/2detTELA', '--file', aut, '--type', 'product'])
    return [aut,old_automaton, spot, product]


# store the results of the evaluations
evaluation = []
def log_result(result):
    evaluation.append(result)
    m = len(automata)
    delta = datetime.now() - start_time
    prediction = start_time + 1.0*m/len(evaluation) * delta
    if (m > len(evaluation)):
        print("determinised" , len(evaluation) , "out of", m,  "automata; prediction: finished at", prediction.strftime('%Y-%m-%d %H:%M:%S') , end="\r" )
    else:
        print("determinised" , len(evaluation) , "out of", m,  "automata; prediction: finished at", prediction.strftime('%Y-%m-%d %H:%M:%S'))





#### main part ###

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
upper_bound = 21
# number of generated automata
n = 20

# call program to produce automata
p = Popen(['source_code/benchmarkA', '--file', path+"/automaton", '--n', str(n), '--l', str(lower_bound), '--u', str(upper_bound)])
p.wait()



# extract all .hoa files from the dictionary
automata = glob.glob(path+"/*.hoa")

#sort automata names
#automata.sort()
#automata.sort(key=len)

# process evaluations in parallel


pool = mp.Pool(CORES) 

print('running', CORES , 'processes in parallel to determinise the automata')
for aut in automata:
    pool.apply_async(evaluate_aut, args=(aut,), callback = log_result)
pool.close()  
pool.join()


print('write result into ', path_evaluation +'/benchmarkCheckInstallation.csv')
## run evaluation
with open(path_evaluation+'/benchmarkCheckInstallation.csv', mode='w') as out_csv:
    csv_writer = csv.writer(out_csv, delimiter= ';')
    csv_writer.writerow(['aut','old_acc', 'timeout_spot', 'states_spot', 'time_spot', 'acc_spot', 'timeout_product', 'states_product', 'time_product', 'acc_product'])
    for row in evaluation:
        aut = row[0]
        old_automaton = row[1]
        spot = row[2]
        product = row[3]
        csv_writer.writerow([aut, old_automaton['acc'], spot['timeout'], spot['states'], spot['time'], spot['acc'], product['timeout'], product['states'], product['time'], product['acc'],])

print('finished at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))