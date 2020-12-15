# imputs evaluation .csv files and produces .csv files for the output graphs
import csv



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

def find_bucket(element, limits):
    # find the correct bucket for the element   
    bucket = 0
    for i in range(len(limits)):
        if limits[i] < element:
            bucket = i
    return bucket

# adds one more approach to the data, comparing spot and compare
def histogram_base4_add_column(data, input, type, compare, limits):
    column = type+'_'+compare
    no_out = 0  # counts the number of rows where no timeout or memout occurs
    for i in range(len(data)):
        data[i][column] = 0
    for i in range(len(input)):
        # add one row
        row = input[i]
        # check, that now timeout occurs
        if row['timeout_spot'] == 'False' and row['timeout_'+compare] == 'False':
            if row['memout_spot'] == 'False' and row['memout_'+compare] == 'False':
                no_out += 1
                diff = float(row[column]) / float(row[type+'_spot'])
                data[find_bucket(diff, limits)][column] += 1

    # use relative values
    for i in range(len(data)):
        data[i][column] = float(data[i][column]) / float(no_out)
    
    return data
    
    

                
                

# produces a .csv file for an histogram with buckets with base 4
def produce_time_histogram_base4_all_approaches(input):
    # limits for the buckets
    limits = [0.015625, 0.03125, 0.0625, 0.25,  1, 4, 16, 32, 64]
    data=[]
    for i in range(len(limits)):
        data.append({})
        data[i]['limit'] = limits[i]

    histogram_base4_add_column(data, input, 'time', 'product', limits)
    histogram_base4_add_column(data, input, 'time', 'me1', limits)
    histogram_base4_add_column(data, input, 'time', 'me2', limits)
    histogram_base4_add_column(data, input, 'time', 'me3', limits)
    histogram_base4_add_column(data, input, 'time', 'limited', limits)

    histogram_base4_add_column(data, input, 'states', 'product', limits)
    histogram_base4_add_column(data, input, 'states', 'me1', limits)
    histogram_base4_add_column(data, input, 'states', 'me2', limits)
    histogram_base4_add_column(data, input, 'states', 'me3', limits)
    histogram_base4_add_column(data, input, 'states', 'limited', limits)

    return data




dataE = read_csv("results/benchmarkE.csv")
histE = produce_time_histogram_base4_all_approaches(dataE)
#print(histE)
write_csv("figures/temp.csv", histE)