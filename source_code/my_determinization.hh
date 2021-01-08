// implementation of the different determinization algorithms

#pragma once

#include <spot/twa/twagraph.hh>

void 
send_to_temp_dot_file(const spot::const_twa_graph_ptr& in);

void 
send_to_temp_hoa_file(const spot::const_twa_graph_ptr& in);

unsigned
size_of_acc_condition(const spot::acc_cond::acc_code acc);

spot::twa_graph_ptr
to_deterministic_tgba(const spot::const_twa_graph_ptr& in, const bool optimisations);

// deletes Fin-sets and produces generalized buchi automaton
spot::twa_graph_ptr
my_to_generalized_buchi(const spot::const_twa_graph_ptr& in, const bool check_result);

// prduces a deterministig tgba
spot::twa_graph_ptr
my_to_deterministic_tgba(const spot::const_twa_graph_ptr& in, const bool optimisations, const bool check_result);

// determinizes an EL-automaton by splitting => fin-removal => unification
spot::twa_graph_ptr
my_to_generalized_buchi_2(const spot::const_twa_graph_ptr& in,  const bool check_result);

// prduces a deterministig tgba by using the second to_generalized_buchi function
spot::twa_graph_ptr
my_to_deterministic_tgba_2(const spot::const_twa_graph_ptr& in, const bool optimisations, const bool check_result);

spot::twa_graph_ptr
my_to_deterministic_tgba_3(const spot::const_twa_graph_ptr& in, const bool optimisations, const bool check_result);

spot::twa_graph_ptr
my_to_deterministic_tgba_4(const spot::const_twa_graph_ptr& in, const bool optimisations, const bool check_result);

spot::twa_graph_ptr
my_to_deterministic_tgba_4_unoptimised(const spot::const_twa_graph_ptr& in, const bool optimisations, const bool check_result);

spot::twa_graph_ptr
my_to_limited_deterministic(const spot::const_twa_graph_ptr& in, const bool optimisations, const bool check_result);

float
avg_num_nondet_choices(const spot::const_twa_graph_ptr& in);

void run_ltl_test(const std::string file, const bool optimisations);

void run_test();