// is called from the benchmark files: procues only 

#include <stdio.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>

#include <spot/twa/twagraph.hh>
#include <spot/twa/acc.hh>
#include <spot/twaalgos/isdet.hh>
#include <spot/twaalgos/hoa.hh>

// for random graphs
#include <spot/twaalgos/randomgraph.hh>
#include <spot/tl/apcollect.hh>

#include "my_determinization.hh"


using namespace std;

unsigned to_unsigned_int(const char* in)
{
    unsigned n = 0;
    stringstream temp;
    temp << in;
    temp >> n;

    return n;
}

void produce_automata(const unsigned number_of_examples, const string path){
    for (unsigned i = 0; i <number_of_examples ; ++i)
    {
        bool aut_found = false; // indicates whether an automaton has been found
        spot::twa_graph_ptr aut;
        do
        {
            auto acc = spot::acc_cond::acc_code("(Fin(0) & Inf(1) & Inf(2)) | (Fin(3) & Inf(4) & Inf(5)) | (Fin(6) & Inf(7) & Inf(8))");
            auto bdd = spot::make_bdd_dict();
            auto props = spot::create_atomic_prop_set(2);
            aut = spot::random_graph(12, 0.2, &props, bdd, 9, 0.2, 0.5, false, false, false);
            aut->set_acceptance(acc);

            // we search for automata that are non-deterministic and the dnf has a size >=2
            aut_found = (aut->get_acceptance().to_dnf().top_disjuncts().size() > 1) 
                        // automaton should not be deterministic
                        && (!spot::is_universal(aut));
        } while (!aut_found);
        // print automaton to hoa-file
        string filename_output2 = path + to_string(i) + ".hoa";
        std::ofstream temp;
        temp.open (filename_output2, std::ofstream::out | std::ofstream::trunc);
        if (temp.is_open())
        {
            spot::print_hoa(temp, aut);
            temp.close();
        }

    }
}

int main(int argc, char* argv[])
{
    if (argc < 5) {
        cerr << "Usage: " << argv[0] << " --file HOA_FILEs --n NUMBER_OF_AUTOMATA" << endl;
        return 1;
    }
    string path;
    unsigned n = 0;
    for (int i = 1; i < argc; ++i) {
        if (std::string(argv[i]) == "--file") {
            if (i + 1 < argc) { // Make sure we aren't at the end of argv!
                path = argv[++i]; // Increment 'i' so we don't get the argument as the next argv[i].
            } else { // Uh-oh, there was no argument to the destination option.
                  cerr << "--file option requires one argument." << endl;
                return 1;
            }  
        } 
        if (std::string(argv[i]) == "--n") {
            if (i + 1 < argc) { // Make sure we aren't at the end of argv!
                n = to_unsigned_int(argv[++i]); // Increment 'i' so we don't get the argument as the next argv[i].
            } else { // Uh-oh, there was no argument to the destination option.
                  cerr << "--type option requires one argument." << endl;
                return 1;
            }  
        } 
    }
    // produce the automata
    produce_automata(n, path);
}