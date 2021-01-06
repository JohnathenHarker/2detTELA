// is called from the benchmark files

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

// generates an automaton that is the critical example from the Thesis with n+1 states
spot::twa_graph_ptr
critical_example(const unsigned n)
{
  spot::bdd_dict_ptr dict = spot::make_bdd_dict();
  // This creates an empty automaton that we have yet to fill.
  spot::twa_graph_ptr aut = make_twa_graph(dict);

  // Since a BDD is associated to every atomic proposition, the
  // register_ap() function returns a BDD variable number
  // that can be converted into a BDD using bdd_ithvar().
  bdd a = bdd_ithvar(aut->register_ap("a"));

  // add states
  aut->new_states(n+1);

  auto acc = spot::acc_cond::acc_code("f");
  // add edges
  for (unsigned i = 0; i <n; ++i)
  {
    aut->new_edge(i, i+1, a, {2*i});
    aut->new_edge(i, i+1, !a, {2*i+1});
    acc = acc | (spot::acc_cond::acc_code::inf({2*i}) & spot::acc_cond::acc_code::inf({2*i+1}));
  }
  aut->new_edge(n, 0, a, {2*n});
  aut->new_edge(n, 0, !a, {2*n+1});
  acc = acc | (spot::acc_cond::acc_code::inf({2*n}) & spot::acc_cond::acc_code::inf({2*n+1}));


  aut->new_edge(0,0, a|!a);

  aut->set_acceptance(acc);

  return aut;
}

void produce_automata(const unsigned number_of_examples, const string path){
    for (unsigned i = 0; i <number_of_examples ; ++i)
    {
        spot::twa_graph_ptr aut = critical_example(i);
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
    unsigned n = 0, l = 0, u = 0;
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