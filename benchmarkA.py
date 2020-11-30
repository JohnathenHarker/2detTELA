import glob
from subprocess import Popen, PIPE
from time import sleep
import csv

# path where the automata for the benchmark are stored
path = "temp_hoas/benchmarkA"

# timeout for the determinisation in s
TIMEOUT = 60

# extract all .hoa files from the dictionary
automata = glob.glob(path+"/*.hoa")


def popen_timeout(command):
    # default values
    states = -1
    time = -1
    acc = -1
    old_acc = -1

    p = Popen(command, stdout=PIPE, stderr=PIPE)
    for t in range(TIMEOUT*10):
        sleep(0.1)
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
                if (output[i] == 'old_acc:'):
                    old_acc = int(output[i+1])
            return (False, states, time, acc, old_acc)
    p.kill()
    return (True, states, time, acc, old_acc)


#### main part ###

with open('results/benchmarkA.csv', mode='w') as out_csv:

    csv_writer = csv.writer(out_csv, delimiter= ';')
    csv_writer.writerow(['old_acc', 'timeout_spot', 'states_spot', 'time_spot', 'acc_spot', 'timeout_product', 'states_product', 'time_product', 'acc_product'])
    for aut in automata:
        print(aut) # call program instead to determinise automaton
        (timeout_s, states_s, time_s, acc_s, old_acc) = popen_timeout(['source_code/2detTELA', '--file', aut, '--type', 'spot'])
        (timeout_p, states_p, time_p, acc_p, old_acc) = popen_timeout(['source_code/2detTELA', '--file', aut, '--type', 'product'])
        #print(timeout, states, time, acc, old_acc)
        csv_writer.writerow([old_acc, timeout_s, states_s, time_s, acc_s, timeout_p, states_p, time_p, acc_p])
