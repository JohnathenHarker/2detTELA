# imputs evaluation .csv files and produces .csv files for the output graphs
import csv
import statistics # for median calculation
import math


def read_csv(filepath):
    with open(filepath, mode='r') as csv_file:
        data = csv.DictReader(csv_file , delimiter=';')
        data =  list(data)
       # print(data[1])
        return list(data)

# writes data from dictionary into .csv file
def write_csv(filepath, data):
    with open(filepath, mode='w') as csv_file:
        fieldnames = list(data[0].keys())
        #print(fieldnames)
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=';')

        writer.writeheader()
        for row in data:
            writer.writerow(row)

# find the correct bucket for the element 
def find_bucket(element, limits):  
    bucket = 0
    for i in range(len(limits)):
        if limits[i] <= element:
            # take care of the cases where we are interested in a bucket representing one single element
            if i == 0 or element > limits[i-1]:
                bucket = i+1
            #elif element < limits[i]:
            #    bucket = i+1

    return bucket


# adds one more approach to the data, comparing spot and compare
def histogram_add_column(data, input, type, base,  compare, limits, min_acc, max_acc):
    """
    adds one more approach to the data, comparing spot and compare

    Parameters
    ----------
    data :      list of dictionaries
                contains row with the labels of the buckets of the histogram
                stores the resulting data for the histogram
    input :     list of dictionaries
                'raw data' from the benchmark
    type :      string
                type of the input that is compared, e.g. 'states', 'time', 'acc'
    base :      string
                approach that is used to compare with, mostly 'spot'
    compare :   string
                approach that is compared with 'base', e.g. 'product', 'me1'
    limits :    list of floats
                limits of the buckets
    min_acc :   int
                lower limit for the size of the acceptance condition of the original automaton
    max_acc :   int
                upper limit for the size of the acceptance condition of the original automaton
    """
    column = type+'_'+compare
    no_out = 0  # counts the number of rows where no timeout or memout occurs
    for i in range(len(data)):
        data[i][column] = 0
    for i in range(len(input)):
        # add one row
        row = input[i]
        # check, that now timeout occurs
        if int(row['old_acc']) >= min_acc and int(row['old_acc']) <= max_acc:
            if row['timeout_'+base] == 'False' and row['timeout_'+compare] == 'False':
                if row['memout_' + base] == 'False' and row['memout_'+compare] == 'False':
                    no_out += 1
                    diff = float(row[column]) / float(row[type+'_' + base])
                    data[find_bucket(diff, limits)][column] += 1

    # use relative values
    for i in range(len(data)):
        data[i][column] = float(data[i][column]) / float(no_out)
    
    return data          
    
# calculates the median value of the ratio of compare with base
def median(input, type, base, compare, min_acc, max_acc):
    """
    calculates the median value of the ratio of compare with base

    Parameters
    ----------
    input :     list of dictionaries
                'raw data' from the benchmark
    type :      string
                type of the input that is compared, e.g. 'states', 'time', 'acc'
    base :      string
                approach that is used to compare with, mostly 'spot'
    compare :   string
                approach that is compared with 'base', e.g. 'product', 'me1'
    min_acc :   int
                lower limit for the size of the acceptance condition of the original automaton
    max_acc :   int
                upper limit for the size of the acceptance condition of the original automaton
    """
    # list to store all the different ratios; we will return its median in the end
    ratios = []
    column = type+'_'+compare
    for i in range(len(input)):
        # current row that is processed
        row = input[i]
        #print("row:", row)
        # check, that now timeout occurs
        if int(row['old_acc']) >= min_acc and int(row['old_acc']) <= max_acc:
            if row['timeout_'+base] == 'False' and row['memout_' + base] == 'False':
                if row['timeout_'+compare] == 'False' and row['memout_'+compare] == 'False':
                    # no time/menout
                    diff = float(row[column]) / float(row[type+'_' + base])
                    ratios.append(diff)
        #        else:
        #            # only compare has time/memout
        #            ratios.append(float("inf"))
        #    elif row['timeout_'+compare] == 'False' and row['memout_'+compare] == 'False':
        #        # only base has time/memout
        #        ratios.append(-float("inf"))
    if len(ratios) > 0:
        return statistics.median(ratios)
    else:
        return -1

# calculates the mean value of the ratio of compare with base
def mean(input, type, base, compare, min_acc, max_acc):
    """
    calculates the mean value of the ratio of compare with base

    Parameters
    ----------
    input :     list of dictionaries
                'raw data' from the benchmark
    type :      string
                type of the input that is compared, e.g. 'states', 'time', 'acc'
    base :      string
                approach that is used to compare with, mostly 'spot'
    compare :   string
                approach that is compared with 'base', e.g. 'product', 'me1'
    min_acc :   int
                lower limit for the size of the acceptance condition of the original automaton
    max_acc :   int
                upper limit for the size of the acceptance condition of the original automaton
    """
    # list to store all the different ratios; we will return its median in the end
    ratios = []
    column = type+'_'+compare
    for i in range(len(input)):
        # current row that is processed
        row = input[i]
        #print("row:", row)
        # check, that now timeout occurs
        if int(row['old_acc']) >= min_acc and int(row['old_acc']) <= max_acc:
            if row['timeout_'+base] == 'False' and row['memout_' + base] == 'False':
                if row['timeout_'+compare] == 'False' and row['memout_'+compare] == 'False':
                    # no time/menout
                    diff = math.log(float(row[column]) / float(row[type+'_' + base]))
                    ratios.append(diff)
    if len(ratios) > 0:
        return math.exp(statistics.mean(ratios)) 
    else:
        return -1

# counts the number of timeouts
def number_of_timeouts(input, base):
    n = 0
    if 'timeout_'+base in input[0]:
        for i in range(len(input)):
            # current row that is processed
            row = input[i]
            # check, wether timeout occurs            
            if row['timeout_'+base] == 'True':
                n = n+1
    else:
        return '-', '-'
    return n, n/len(input)

# counts the number of memouts
def number_of_memouts(input, base):
    n = 0
    if 'memout_'+base in input[0]:
        for i in range(len(input)):
            # current row that is processed
            row = input[i]
            # check, wether memout occurs            
            if row['memout_' + base] == 'True':
                n = n+1
    else:
        return '-', '-'
    return n, n/len(input)

# produces a .csv file for a histogram with buckets with base 4
def produce_time_histogram_all_approaches(input):
    # limits for the buckets
    limits = [0.015625, 0.03125, 0.0625, 0.25,  1, 4, 16, 32, 64]
    data=[]
    for i in range(len(limits)):
        data.append({})
        data[i]['limit'] = limits[i]
    data.append({})
    data[len(limits)]['limit'] = limits[-1]+1

    histogram_add_column(data, input, 'time', 'spot', 'product', limits, 0, 50)
    histogram_add_column(data, input, 'time', 'spot', 'me1', limits, 0, 50)
    histogram_add_column(data, input, 'time', 'spot', 'me2', limits, 0, 50)
    histogram_add_column(data, input, 'time', 'spot', 'me3', limits, 0, 50)
    histogram_add_column(data, input, 'time', 'spot', 'limited', limits, 0, 50)
    return data

# produces a .csv file for a histogram with buckets with base 10
def produce_states_histogram_all_approaches(input):
    # limits for the buckets
    #limits = [0.015625, 0.03125, 0.0625, 0.25,  1, 4, 16, 32, 64]
    limits = [0.01, 0.1, 1, 1.0, 10,  100]
    data=[]
    for i in range(len(limits)):
        data.append({})
        data[i]['limit'] = limits[i]
    data.append({})
    data[len(limits)]['limit'] = limits[-1]+1

    histogram_add_column(data, input, 'states', 'spot', 'product', limits, 0, 50)
    histogram_add_column(data, input, 'states', 'spot', 'me1', limits, 0, 50)
    histogram_add_column(data, input, 'states', 'spot', 'me2', limits, 0, 50)
    histogram_add_column(data, input, 'states', 'spot', 'me3', limits, 0, 50)
    histogram_add_column(data, input, 'states', 'spot', 'limited', limits, 0, 50)
    return data

# produces a .csv file for a histogram with buckets with base 4
def produce_acc_histogram_all_approaches(input):
    # limits for the buckets
    limits = [0.5, 1, 2, 3, 4, 5]
    data=[]
    for i in range(len(limits)):
        data.append({})
        data[i]['limit'] = limits[i]
    data.append({})
    data[len(limits)]['limit'] = limits[-1]+1

    histogram_add_column(data, input, 'acc', 'spot', 'product', limits, 0, 50)
    histogram_add_column(data, input, 'acc', 'spot', 'me1', limits, 0, 50)
    histogram_add_column(data, input, 'acc', 'spot', 'me2', limits, 0, 50)
    histogram_add_column(data, input, 'acc', 'spot', 'me3', limits, 0, 50)
    histogram_add_column(data, input, 'acc', 'spot', 'limited', limits, 0, 50)
    return data

# produces a .csv file for the bar chart with the median values for the number of states
def produce_csv_median_mean(input, ap1, ap2):
    """
    produces a .csv file for the bar chart with the median values for the number of states

    Parameters
    ----------
    input:  list of .csv files
            list of files for automata models with differrent amout of nondeterminism
            should be sorted such, that fewest nondeterminism is first and most nondeterminism is last
    """
    # stores the resulting .csv that is returned
    result = []

    # amount of nondeterminism in the benchmarks
    nondet = [0.17, 1.12, 2.28]
    # make first row
    data = []
    for i in range(len(input)):
        data.append(read_csv(input[i]))
    for i in range(len(input)):
        result.append({})
        result[i]['nondet'] = nondet[i]
        # results for number of states
        result[i]['median_states_low_acc'] = median(data[i], 'states', ap1, ap2, 2, 11)
        result[i]['median_states_high_acc'] = median(data[i], 'states', ap1, ap2, 12, 21)
        result[i]['mean_states_low_acc'] = mean(data[i], 'states', ap1, ap2, 2, 11)
        result[i]['mean_states_high_acc'] = mean(data[i], 'states', ap1, ap2, 12, 21)

        # results for time
        result[i]['median_time_low_acc'] = median(data[i], 'time', ap1, ap2, 2, 11)
        result[i]['median_time_high_acc'] = median(data[i], 'time', ap1, ap2, 12, 21)
        result[i]['mean_time_low_acc'] = mean(data[i], 'time', ap1, ap2, 2, 11)
        result[i]['mean_time_high_acc'] = mean(data[i], 'time', ap1, ap2, 12, 21)

        # results for size of acc
        result[i]['median_acc_low_acc'] = median(data[i], 'acc', ap1, ap2, 2, 11)
        result[i]['median_acc_high_acc'] = median(data[i], 'acc', ap1, ap2, 12, 21)
        result[i]['mean_acc_low_acc'] = mean(data[i], 'acc', ap1, ap2, 2, 11)
        result[i]['mean_acc_high_acc'] = mean(data[i], 'acc', ap1, ap2, 12, 21)

    return result

# produces scatter plot for states of ap1 and ap2
def produce_scatter_plot(input, type, ap1, ap2):
    """
    produces scatter plot for states of ap1 and ap2

    Parameters
    ----------
    input:  list of dictionaries
            'raw data' from the benchmark
    type :  string
            type of the input that is compared, e.g. 'states', 'time', 'acc'
    ap1 :   string
            approach 1, e.g. 'product', 'spot'
    ap2 :   string
            approach 2, e.g. 'product', 'spot'
    """
    # stores the result
    result = []
    for i in range(len(input)):
        # test that no time/memout has occured
        row = input[i]
        if row['timeout_'+ap1] == 'False' and row['memout_' + ap1] == 'False':
            if row['timeout_'+ap2] == 'False' and row['memout_'+ap2] == 'False':
                result.append({})
                result[-1][ap1] = row[type + '_' + ap1]
                result[-1][ap2] = row[type + '_' + ap2]
    return result

# produces a .csv file for the mean values of the example where Spot sturggles
def produce_csv_median_mean_complex_cnf(input, ap1, ap2):
    """
    produces a .csv file for the bar chart with the median values for the number of states

    Parameters
    ----------
    input:  'raw' data of the benchmark
    """
    # stores the resulting .csv that is returned
    result = []

    # amount of nondeterminism in the benchmarks
    nondet = [0.17, 1.12, 2.28]

    result.append({})
    # results for number of states
    result[0]['median_states_'] = median(input, 'states', ap1, ap2, 0, 20)
    result[0]['mean_states'] = mean(input, 'states', ap1, ap2, 0, 20)

    # results for time
    result[0]['median_time'] = median(input, 'time', ap1, ap2, 0, 20)
    result[0]['mean_time'] = mean(input, 'time', ap1, ap2, 0, 20)
    

    # results for size of acc
    result[0]['median_acc'] = median(input, 'acc', ap1, ap2, 0, 20)
    result[0]['mean_acc'] = mean(input, 'acc', ap1, ap2, 0, 20)
 

    return result

# produces
def produce_histogram(input, type, base, compare):
    """
    produces histogram comparing two approaches

    Parameters
    ----------
    input :     list of dictionaries
                'raw data' from the benchmark
    type :      string
                type of the input that is compared, e.g. 'states', 'time', 'acc'
    base :      string
                approach that is used to compare with, e.g. 'spot', 'product'
    compare :   string
                approach that is compared with 'base', e.g. 'product', 'me1'
    """
        
    # limits for the buckets
    limits = [0.25, 0.5, 1, 2,  4]
    data=[]
    for i in range(len(limits)):
        data.append({})
        data[i]['limit'] = limits[i]
    data.append({})
    data[len(limits)]['limit'] = limits[-1]+1


    histogram_add_column(data, input, type, base, compare, limits, 0, 50)
    return data

# produces
def produce_histogram_equal_1(input, type, base, compare):
    """
    produces histogram comparing two approaches

    Parameters
    ----------
    input :     list of dictionaries
                'raw data' from the benchmark
    type :      string
                type of the input that is compared, e.g. 'states', 'time', 'acc'
    base :      string
                approach that is used to compare with, e.g. 'spot', 'product'
    compare :   string
                approach that is compared with 'base', e.g. 'product', 'me1'
    """
        
    # limits for the buckets
    limits = [0.25, 0.5, 1,1.0, 2,  4]
    data=[]
    for i in range(len(limits)):
        data.append({})
        data[i]['limit'] = limits[i]
    data.append({})
    data[len(limits)]['limit'] = limits[-1]+1


    histogram_add_column(data, input, type, base, compare, limits, 0, 50)
    return data



# counts the number of timeouts and memouts
# input is a list of benchmarks
# names is a list of names for the benchmarks
def count_outs(input, names):
    data=[]
    if len(names) != len(input):
        print("ERROR: list lengths need to be the same")
        return data
    for i in range(len(names)):
        data.append({})
        data[i]['benchmark'] = names[i]
        data[i]['timeout_spot'], data[i]['timeout_spot_relative'] = number_of_timeouts(input[i], 'spot')
        data[i]['memout_spot'], data[i]['memeout_spot_relative'] = number_of_memouts(input[i], 'spot')
        data[i]['timeout_product'], data[i]['timeout_product_relative'] = number_of_timeouts(input[i], 'product')
        data[i]['memout_product'], data[i]['memeout_product_relative'] = number_of_memouts(input[i], 'product')
        data[i]['timeout_limited'], data[i]['timeout_limited_relative'] = number_of_timeouts(input[i], 'limited')
        data[i]['memout_limited'], data[i]['memeout_limited_relative'] = number_of_memouts(input[i], 'limited')
        data[i]['timeout_me1'], data[i]['timeout_me1_relative'] = number_of_timeouts(input[i], 'me1')
        data[i]['memout_me1'], data[i]['memeout_me1_relative'] = number_of_memouts(input[i], 'me1')
        data[i]['timeout_me2'], data[i]['timeout_me2_relative'] = number_of_timeouts(input[i], 'me2')
        data[i]['memout_me2'], data[i]['memeout_me2_relative'] = number_of_memouts(input[i], 'me2')
        data[i]['timeout_me3'], data[i]['timeout_me3_relative'] = number_of_timeouts(input[i], 'me3')
        data[i]['memout_me3'], data[i]['memeout_me3_relative'] = number_of_memouts(input[i], 'me3')

    return data    



####################################################################################

# produce histograms for benchmarkE
dataE = read_csv("results/benchmarkE.csv")
write_csv("figures/benchmarkE_his_states.csv", produce_states_histogram_all_approaches(dataE))
write_csv("figures/benchmarkE_his_time.csv", produce_time_histogram_all_approaches(dataE))
write_csv("figures/benchmarkE_his_acc.csv", produce_acc_histogram_all_approaches(dataE))
write_csv("figures/benchmarkE_scatter_states.csv", produce_scatter_plot(dataE, 'states', 'spot', 'product'))


# produce data for benchmarkA, benchmarkC and benchmarkD
median_states = produce_csv_median_mean(["results/benchmarkC.csv", "results/benchmarkA.csv", "results/benchmarkD.csv"], 'spot', 'product')
write_csv("figures/product_vs_spot.csv", median_states)

# produce scatter plot for bad example of spot vs. product
dataB = read_csv("results/benchmarkB.csv")
write_csv("figures/benchmarkB_scatter_states.csv", produce_scatter_plot(dataB, 'states', 'spot', 'product'))
write_csv("figures/benchmarkB_scatter_time.csv", produce_scatter_plot(dataB, 'time', 'spot', 'product'))
median_statesB = produce_csv_median_mean_complex_cnf(read_csv("results/benchmarkB.csv"), 'spot', 'product')
write_csv("figures/benchmarkB_median_mean.csv", median_statesB)

# produce histograms to compare det. by product with limited det.
dataF = read_csv("results/benchmarkF.csv")
write_csv("figures/benchmarkF_his_states.csv",produce_histogram_equal_1(dataF, 'states', 'product', 'limited'))
write_csv("figures/benchmarkF_his_time.csv", produce_histogram(dataF, 'time', 'product', 'limited'))

# produce histograms to compare det. by product with and without optimisation
write_csv("figures/benchmarkE_his_states_un_vs_opt.csv",produce_histogram_equal_1(dataE, 'states', 'product', 'product_unoptimiesed'))
write_csv("figures/benchmarkE_his_time_un_vs_opt.csv", produce_histogram(dataE, 'time', 'product', 'product_unoptimiesed'))


# produce table with number of timeouts/ memouts
dataG = read_csv("results/benchmarkG.csv")
write_csv("figures/count_timeouts.csv", count_outs([dataE, dataB, dataF, dataG], ["benchmarkE", "benchmarkB", "benchmarkF", "benchmarkG"]))

