import glob
from subprocess import Popen, PIPE
from time import sleep, perf_counter
import csv
import os



# timeout for the determinisation in s
TIMEOUT = 60

# path where the automata for the benchmark are stored

path = "temp_hoas/benchmarkA"
path_evaluation = "results"


def popen_evaluation(command):
    # default values
    states = -1
    time = -1
    acc = -1

    p = Popen(command, stdout=PIPE, stderr=PIPE)
    tic = perf_counter()
    toc = perf_counter()
    while (toc-tic) < TIMEOUT:
        if p.poll() is not None:
            output = p.communicate()[0].decode('UTF-8').split()
            #print(output)
           # print(output[0].decode('UTF-8').split())
            for i in range(len(output)):
                if (output[i] == 'states:'):
                    states = int(output[i+1])
                if (output[i] == 'time:'):
                    time = float(output[i+1])
                if (output[i] == 'acc:'):
                    acc = int(output[i+1])
            return (False, states, time, acc)
        sleep(0.1)
        toc = perf_counter()
    p.kill()
    return (True, states, time, acc)


#### main part ###

## create directories

if not os.path.exists(path):
    os.makedirs(path)

if not os.path.exists(path_evaluation):
    os.makedirs(path_evaluation)




## produce examples

p = Popen(['source_code/benchmarkA', '--file', path+"/automaton", '--n', '1500', '--l', '2', '--u', '15'])
p.wait()



# extract all .hoa files from the dictionary
automata = glob.glob(path+"/*.hoa")

## run evaluation
with open(path_evaluation+'/benchmarkA.csv', mode='w') as out_csv:

    csv_writer = csv.writer(out_csv, delimiter= ';')
    csv_writer.writerow(['old_acc', 'timeout_spot', 'states_spot', 'time_spot', 'acc_spot', 'timeout_product', 'states_product', 'time_product', 'acc_product'])
    for aut in automata:
        print('process automaton ' + aut) # call program instead to determinise automaton
        (_, _, _, old_acc) = popen_evaluation(['source_code/2detTELA', '--file', aut, '--type', 'old_aut'])
        (timeout_s, states_s, time_s, acc_s) = popen_evaluation(['source_code/2detTELA', '--file', aut, '--type', 'spot'])
        (timeout_p, states_p, time_p, acc_p) = popen_evaluation(['source_code/2detTELA', '--file', aut, '--type', 'product'])
        csv_writer.writerow([old_acc, timeout_s, states_s, time_s, acc_s, timeout_p, states_p, time_p, acc_p])
