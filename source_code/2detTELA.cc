// is called from the benchmark files


#include <iostream>
#include <string>
#include <time.h> 
#include <ctime>

#include <spot/parseaut/public.hh>
//#include <spot/twaalgos/hoa.hh>

#include "my_determinization.hh"


using namespace std;

int main(int argc, char* argv[])
{
    if (argc < 5) {
        cerr << "Usage: " << argv[0] << " --file HOA_FILE --type TYPE_OF_DETERMINISATION" << endl;
        return 1;
    }
    string hoa_file;
    string type;
    for (int i = 1; i < argc; ++i) {
        if (std::string(argv[i]) == "--file") {
            if (i + 1 < argc) { // Make sure we aren't at the end of argv!
                hoa_file = argv[++i]; // Increment 'i' so we don't get the argument as the next argv[i].
            } else { // Uh-oh, there was no argument to the destination option.
                  cerr << "--file option requires one argument." << endl;
                return 1;
            }  
        } 
        if (std::string(argv[i]) == "--type") {
            if (i + 1 < argc) { // Make sure we aren't at the end of argv!
                type = argv[++i]; // Increment 'i' so we don't get the argument as the next argv[i].
            } else { // Uh-oh, there was no argument to the destination option.
                  cerr << "--type option requires one argument." << endl;
                return 1;
            }  
        } 
    }
    int states = 0;
    float time = 0;
    int acc = -1;

    // read automaton from file
    spot::parsed_aut_ptr pa = parse_aut(hoa_file, spot::make_bdd_dict());
    if (pa->format_errors(std::cerr))
        return 1;
    if (pa->aborted)
    {
        std::cerr << "--ABORT-- read\n";
        return 1;
    }


    clock_t t;
    if (type == "spot")
    {
        t = clock();
        auto res =  to_deterministic_tgba(pa->aut, true);
        t = clock() -t;
        states = res->num_states();
        time = ((float)t)/CLOCKS_PER_SEC;
        acc = size_of_acc_condition(res->get_acceptance());
    }

    if (type == "product" || type == "me4")
    {
        t = clock();
        auto res =  my_to_deterministic_tgba_4(pa->aut, true, false);
        t = clock() -t;
        states = res->num_states();
        time = ((float)t)/CLOCKS_PER_SEC;
        acc = size_of_acc_condition(res->get_acceptance());
    }

    if (type == "product_unoptimised" || type == "me4_unoptimised")
    {
        t = clock();
        auto res =  my_to_deterministic_tgba_4_unoptimised(pa->aut, true, false);
        t = clock() -t;
        states = res->num_states();
        time = ((float)t)/CLOCKS_PER_SEC;
        acc = size_of_acc_condition(res->get_acceptance());
    }

    if (type == "limited" || type == "limited-deterministic")
    {
        t = clock();
        auto res =  my_to_limited_deterministic(pa->aut, true, false);
        t = clock() -t;
        states = res->num_states();
        time = ((float)t)/CLOCKS_PER_SEC;
        acc = size_of_acc_condition(res->get_acceptance());
    }

    if (type == "me1" || type == "Me1")
    {
        t = clock();
        auto res =  my_to_deterministic_tgba(pa->aut, true, false);
        t = clock() -t;
        states = res->num_states();
        time = ((float)t)/CLOCKS_PER_SEC;
        acc = size_of_acc_condition(res->get_acceptance());
    }

    if (type == "me2" || type == "Me2")
    {
        t = clock();
        auto res =  my_to_deterministic_tgba_2(pa->aut, true, false);
        t = clock() -t;
        states = res->num_states();
        time = ((float)t)/CLOCKS_PER_SEC;
        acc = size_of_acc_condition(res->get_acceptance());
    }

    if (type == "me3" || type == "Me3")
    {
        t = clock();
        auto res =  my_to_deterministic_tgba_3(pa->aut, true, false);
        t = clock() -t;
        states = res->num_states();
        time = ((float)t)/CLOCKS_PER_SEC;
        acc = size_of_acc_condition(res->get_acceptance());
    }

    if (type == "old_aut")
    {
        states = pa->aut->num_states();
        acc = size_of_acc_condition(pa->aut->get_acceptance().to_dnf());
    }

    cout << " states: " << states << " time: " << time << " acc: " << acc <<endl;
    //cout << 10 <<" times more data" << endl;
}