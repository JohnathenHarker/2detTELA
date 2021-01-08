#include <iostream>
#include <fstream>
#include <string>
#include <map>
#include <algorithm>
#include <time.h> 


#include <spot/parseaut/public.hh>

#include <spot/twaalgos/hoa.hh>
#include <spot/twaalgos/totgba.hh>
#include <spot/twaalgos/determinize.hh>
#include <spot/twaalgos/sum.hh>
#include <spot/twaalgos/dot.hh>
#include <spot/twaalgos/remfin.hh>
#include <spot/twaalgos/degen.hh>
#include <spot/twaalgos/contains.hh>
#include <spot/twaalgos/isdet.hh>
#include <spot/twaalgos/lbtt.hh>
#include <spot/twaalgos/cleanacc.hh>
#include <spot/twaalgos/randomgraph.hh>
#include <spot/twaalgos/product.hh>

#include <spot/twa/twagraph.hh>
#include <spot/twa/acc.hh>

#include "remfin.hh"


using namespace std;


void 
send_to_temp_dot_file(const spot::const_twa_graph_ptr& in)
{
  std::ofstream temp;
  temp.open ("temp.dot", std::ofstream::out | std::ofstream::trunc);
  if (temp.is_open())
  {
    spot::print_dot(temp, in);
    temp.close();
  }
  else std::cout << "Unable to open file";
}

void 
send_to_temp_hoa_file(const spot::const_twa_graph_ptr& in)
{
  std::ofstream temp;
  temp.open ("temp.hoa", std::ofstream::out | std::ofstream::trunc);
  if (temp.is_open())
  {
    spot::print_hoa(temp, in);
    temp.close();
  }
  else std::cout << "Unable to open file";
}

// returns the size of the acc condition: number of sets/ size of the tree
unsigned
size_of_acc_condition(const spot::acc_cond::acc_code acc)
{
  //cout << "called with acc: " << acc <<endl;
  unsigned len = 0;
  if (acc.is_t()  || acc.is_f()) // atomic acc sets
    return 1;
  else
  {
    auto sub_accs = acc.top_conjuncts();
    if (sub_accs.size() > 1)
    {
      // more than one conjunct
      for (auto sacc : sub_accs)
      {
        len += size_of_acc_condition(sacc);
      }
    }
    else
    {
      // more than one disjunct
      sub_accs = acc.top_disjuncts();
      if (sub_accs.size() < 2)
        // atomic acc condition 
        return 1;
      for (auto sacc: sub_accs)
      {
        len += size_of_acc_condition(sacc);
      }
    }
    
  }
  
  return len;
}

// copmare two automata: use number of states
bool compare_aut(const spot::twa_graph_ptr& aut1, const spot::twa_graph_ptr& aut2)
{
  return aut1->num_states() < aut2->num_states();
}

spot::twa_graph_ptr
to_deterministic_tgba(const spot::const_twa_graph_ptr& in, const bool optimisations)
{
  auto gen_buchi = spot::to_generalized_buchi(in);
  auto det_aut = spot::tgba_determinize(gen_buchi, false, optimisations, optimisations, optimisations);
  return det_aut;
}

// custom function to add states to the automaton without changing the label of the edges
// input: result, automaton that is added, (new) acceptance condition of aut
spot::twa_graph_ptr
my_add_twa(spot::twa_graph_ptr& res, spot::twa_graph_ptr& aut, spot::acc_cond acc)
{
  

  // add new states of the old automaton
  // the usage of 'offset' is a bit hacky and might not always work, if aut has holes in the state numbering
  int offset = res->new_states(aut->states().size());
  unsigned initial = aut->get_init_state_number();
  
  // create dictionary to look for the new edge names, such that they are labelled with 0,1,2,.. in the end
  std::map<unsigned, unsigned> new_label;
  auto used_sets = acc.get_acceptance().used_sets();
  unsigned i = 0;
  for (auto label: used_sets.sets())
  {
    new_label.insert(std::make_pair(label, i++));
  }
  // find the largest number of acc-sets
  unsigned res_acc_size = res->get_acceptance().used_sets().count();
  unsigned max = std::max((unsigned)new_label.size(), res_acc_size);

  // acc-cond to fill um the copy, if needed
  auto fill = spot::acc_cond::mark_t();
  if (max > new_label.size())
  {
    // aut uses fewer acc-sets than res
    // fill with acceptance marks, if aut uses fewer acc-sets than res
    
    for (unsigned i = new_label.size(); i < max; ++i)
    {
      fill.set(i);
    }
  }
  if (max > res_acc_size)
  {
    // res uses fewer acc-sets than aut
    // expand all labels in res

    // make new copy of the automaton with new edges
    spot::twa_graph_ptr res_new = make_twa_graph(res->get_dict());
    res_new->new_states(res->num_states());
    res_new->set_init_state(res->get_init_state_number());

    auto fill_res = spot::acc_cond::mark_t();
    for (unsigned i =res_acc_size; i < max; ++i)
    {
      fill_res.set(i);
    }
    for (auto edge: res->edges())
    {
      for (unsigned i : fill_res.sets())
      {
        edge.acc.set(i);
        res_new->new_edge(edge.src, edge.dst, edge.cond, edge.acc);
      }
    }
    res = res_new;
  }
  
  // run over all edges and add them to 'res'
  for (auto edge: aut->edges())
  {

    // collect all acc-labels for the edge in acc
    auto acc = spot::acc_cond::mark_t();
    // iterate over all labels of the edge
    for (auto label: edge.acc.sets())
    {
      // only use the label, if it is part of the acceptance condition
      if (used_sets.has(label))
      {
        acc.set(new_label[label]);
      }
    }
    // add additional edge label, if needed
    if (acc.count() > 0)
    {
      for (unsigned i : fill.sets())
      {
        acc.set(i);
      }
    }

    int src = edge.src + offset;
      
    // use initial state of the res-automaton
    if (edge.src == initial)
    {
      // add two edges: the initial one, and the one for the loops
      res->new_edge(res->get_init_state_number(), edge.dst + offset, edge.cond, acc);
      res->new_edge(src, edge.dst + offset, edge.cond, acc);
    }
    else
    {
      res->new_edge(src, edge.dst + offset, edge.cond, acc);
    }
  }

  // set the acceptance condition for res
  res->set_generalized_buchi(max);
  return res;
}


// custom function to add limited automaton to other automaton
// acc condition of the second automaton gets shifted before disjunction
spot::twa_graph_ptr
my_add_limited_twa(spot::twa_graph_ptr& res, spot::twa_graph_ptr& aut, spot::acc_cond acc)
{
  // if aut does not accept anything, we return the input
  if (aut->get_acceptance().is_f())
    return res;

  // add new states of the old automaton
  // the usage of 'offset' is a bit hacky and might not always work, if aut has holes in the state numbering
  int offset = res->new_states(aut->states().size());
  unsigned initial = aut->get_init_state_number();
  
  // create dictionary to look for the new edge names, such that they are labelled with 0,1,2,.. in the end
  std::map<unsigned, unsigned> new_label;
  auto used_sets = acc.get_acceptance().used_sets();
  unsigned i = 0;
  for (auto label: used_sets.sets())
  {
    new_label.insert(std::make_pair(label, i++));
  }

  // find the number of acc-sets of the first automaton
  unsigned acc_shift = res->get_acceptance().used_sets().count();
  //cout << "acc shift: "<<acc_shift<<endl;
  
  // acceptance set that is added to every transition in aut
  auto add_acc = spot::acc_cond::inf({acc_shift});
  // need to shift one step further, because we will add "add_acc" to every transition of aut
  acc_shift++;
  // run over all edges and add them to 'res'
  for (auto edge: aut->edges())
  {
    // collect all acc-labels for the edge in acc
    auto acc = spot::acc_cond::mark_t();
    // iterate over all labels of the edge
    for (auto label: edge.acc.sets())
    {
      // only use the label, if it is part of the acceptance condition
      if (used_sets.has(label))
      {
        // apply shifting of the acc condition
        acc.set(new_label[label] + acc_shift );
      }
    }
    acc.set(acc_shift-1);
    int src = edge.src + offset;
      
    // use initial state of the res-automaton
    if (edge.src == initial)
    {
      // add two edges: the initial one, and the one for the loops
      res->new_edge(res->get_init_state_number(), edge.dst + offset, edge.cond, acc);
      res->new_edge(src, edge.dst + offset, edge.cond, acc);
    }
    else
    {
      res->new_edge(src, edge.dst + offset, edge.cond, acc);
    }
  }

  // set the acceptance condition for res
 // cout<< "res acc: " << res->get_acceptance() << " aut acc: "<< aut->get_acceptance() << " add_acc: " << add_acc<< endl;
  auto shifted_aut_acc = aut->get_acceptance() << acc_shift;
  //cout<< "res acc: " << res->get_acceptance() << " shifted aut acc: "<< shifted_aut_acc << " add_acc: " << add_acc<< endl;
  res->set_acceptance(res->get_acceptance() | (shifted_aut_acc & add_acc));
 // cout << "acceptance: " << res->get_acceptance()<< endl;
  return res;
}

// deletes Fin-sets and produces generalized buchi automaton
spot::twa_graph_ptr
my_to_generalized_buchi(const spot::const_twa_graph_ptr& in, const bool check_result)
{
  auto finless_in = mod_spot::remove_fin(in);
  // make sure, that acceptance condition is in dnf, should be the case anyway
  auto cnf = finless_in->get_acceptance().to_dnf();
  // split the accetance condition (in dnf) into disjuncts
  auto disjuncts = cnf.top_disjuncts();
 

  // creating an empty TwA 'res' for the result with the same bdd
  spot::twa_graph_ptr res = make_twa_graph(finless_in->get_dict());

  // register all atomic propositions of the old automaton
  for (auto ap : finless_in->ap())
  {
    res->register_ap(ap);
  }

  // the sum requires at least one state
  res->new_states(1);
  
  // check, if we do not need to copy the automaton multiple times
   if (disjuncts.size() == 1)
  {
    res = spot::make_twa_graph(finless_in, {true, true, true, true, true, true});
  }
  else 
  {
    for (auto acc: disjuncts)
    {
      // create copy of the automaton with the same properties as 'in'
      auto copy = spot::make_twa_graph(finless_in, {true, true, true, true, true, true});

      // add copy to result
      res = my_add_twa(res, copy, acc);

    }
  }
  
  // try to simplify the automaton
  res->purge_dead_states();
  spot::cleanup_acceptance_here(res);

  if (check_result)
  {
    if (! spot::are_equivalent(res, in))
    {
      std::cout << "ERROR in my_to_generalized_buchi" << std::endl;
    }
  }

  return res;
}



// prduces a deterministig tgba
spot::twa_graph_ptr
my_to_deterministic_tgba(const spot::const_twa_graph_ptr& in, const bool optimisations, const bool check_result)
{
  auto res = my_to_generalized_buchi(in, check_result);
  auto det_aut = spot::tgba_determinize(res, false, optimisations, optimisations, optimisations);
  if (check_result)
  {
    if (! spot::are_equivalent(det_aut, in))
    {
      std::cout << "ERROR in my_to_deterministic_tgba" << std::endl;
    }
  }
  return det_aut;
}

// determinizes an EL-automaton by splitting => fin-removal => unification
spot::twa_graph_ptr
my_to_generalized_buchi_2(const spot::const_twa_graph_ptr& in,  const bool check_result)
{
  auto dnf = in->get_acceptance().to_dnf();
  auto disjuncts = dnf.top_disjuncts();

  // check, if dnf has only one disjunct
  if (disjuncts.size() <= 1)
  {
    // no copying needed, we use the determinization approach of spot
    return spot::to_generalized_buchi(in);
  }
  else
  {
    // creating an empty TwA 'res' for the result with the same bdd
    spot::twa_graph_ptr res = make_twa_graph(in->get_dict());

    // register all atomic propositions of the old automaton
    for (auto ap : in->ap())
    {
      res->register_ap(ap);
    }

    // the sum requires at least one state
    res->new_states(1);

    unsigned n = in->num_sets()-1;
    auto add_acc = spot::acc_cond::acc_code::fin({n}) & spot::acc_cond::acc_code::inf({n}); // add useless condition to keep the number of acc-sets maximal
    for (auto acc : disjuncts)
    {       
      // create copy of the automaton with the same properties as 'in'
      auto copy = spot::make_twa_graph(in, {true, true, true, true, true, true});

      copy->set_acceptance(acc | add_acc);
      auto finless_copy = spot::remove_fin(copy);

      //cout << "acc: "<< copy->get_acceptance()<< " acc finless: "<< finless_copy->get_acceptance() << endl;
      /*
      if (!spot::are_equivalent(copy, finless_copy))
      {
        cout << " ERROR in to_generalized_buchi2: the finless copy is not the same" << endl;
      }
      */
      // register all aps from the copy that are not already registered by res
      for (auto ap : finless_copy->ap())
      {
        bool found = false;
        for (auto ap_res : res->ap())
        {
          if (ap_res == ap)
          {
            found = true;
          }
        }
        if (!found)
        {
          res->register_ap(ap);
        }
        
      }

      // add copy to result
      res = my_add_twa(res, finless_copy, finless_copy->get_acceptance());
      //out << "acc res: " << res->get_acceptance()<< " states res" << res->num_states() << endl;
    }
    
    // try to simplify the automaton
    res->purge_dead_states();
    spot::cleanup_acceptance_here(res);
    //send_to_temp_dot_file(res);
    if (check_result)
    {
      if (! spot::are_equivalent(res, in))
      {
        std::cout << "ERROR in my_to_generalized_buchi_2" << std::endl;
      }
    }
    // check, if the acc condition is f
     if (res->acc().is_f())
        {
          // "f" is not generalized-Büchi.  Just return an
          // empty automaton instead.
          auto res2 = make_twa_graph(res->get_dict());
          res2->set_generalized_buchi(0);
          res2->set_init_state(res2->new_state());
          res2->prop_stutter_invariant(true);
          res2->prop_weak(true);
          res2->prop_complete(false);
          return res2;
        }
    return res;
  }
}

// prduces a deterministig tgba by using the second to_generalized_buchi function
spot::twa_graph_ptr
my_to_deterministic_tgba_2(const spot::const_twa_graph_ptr& in, const bool optimisations, const bool check_result)
{
  auto res = my_to_generalized_buchi_2(in, check_result);
  //cout << "acc: " << res->get_acceptance() << endl;
  if (check_result) 
    assert(spot::are_equivalent(in, res));
  auto det_aut = spot::tgba_determinize(res, false, optimisations, optimisations, optimisations);
  if (check_result)
  {
    if (! spot::are_equivalent(det_aut, in))
    {
      std::cout << "ERROR in my_to_deterministic_tgba_2" << std::endl;
      send_to_temp_hoa_file(in);
    }
  }
  return det_aut;
}

spot::twa_graph_ptr
my_to_deterministic_tgba_3(const spot::const_twa_graph_ptr& in, const bool optimisations, const bool check_result)
{
  auto res = mod_spot::remove_fin_and_generalize(in);
  auto det_aut = spot::tgba_determinize(res, false, optimisations, optimisations, optimisations);
  if (check_result)
  {
    if (! spot::are_equivalent(det_aut, in))
    {
      std::cout << "ERROR in my_to_deterministic_tgba" << std::endl;
    }
  }
  return det_aut;
}

spot::twa_graph_ptr
my_to_deterministic_tgba_4(const spot::const_twa_graph_ptr& in, const bool optimisations, const bool check_result)
{
  auto dnf = in->get_acceptance().to_dnf();
  auto disjuncts = dnf.top_disjuncts();

  // check, if dnf has only one disjunct
  if (disjuncts.size() <= 1)
  {
    // no copying needed, we use the determinization approach of spot
    return to_deterministic_tgba(in, optimisations);
  }
  else
  {
    // creating an empty TwA 'res' for the result with the same bdd
    spot::twa_graph_ptr res = make_twa_graph(in->get_dict());

    // register all atomic propositions of the old automaton
    for (auto ap : in->ap())
    {
      res->register_ap(ap);
    }

    // the product requires at least one state
    res->new_states(1);
    res->set_acceptance(spot::acc_cond::acc_code("f"));

    unsigned n = in->num_sets();
    auto add_acc = spot::acc_cond::acc_code::fin({n}) & spot::acc_cond::acc_code::inf({n}); // add useless condition to keep the number of acc-sets maximal

    vector<spot::twa_graph_ptr> det_automata; 
    for (auto acc : disjuncts)
    {
      //cout << "acc: " << acc << endl;
      // create copy of the automaton with the same properties as 'in'
      auto copy = spot::make_twa_graph(in, {true, true, true, true, true, true});
      /*
      for (auto ap : in->ap())
      {
        bool found = false;
        for (auto ap_res : copy->ap())
        {temp_hoas/benchmarkE/automatonD307.hoa	9	FALSCH	FALSCH	942	0,00938	11	FALSCH	FALSCH	488666	1,38305	53	FALSCH	FALSCH	21418	0,600396	27	FALSCH	FALSCH	1512656	64,8671	27	FALSCH	FALSCH	4325119	190,953	31	FALSCH	FALSCH	8568	0,416623	58

          if (ap_res == ap)
          {
            found = true;
          }
        }
        if (!found)
        {
          copy->register_ap(ap);
        }
      }*/
      //cout << "num acc sets: " << copy->num_sets() << endl;
      spot::cleanup_acceptance_here(copy);
      //cout << "num acc sets2: " << copy->num_sets() << endl;
      auto mod_acc = acc| add_acc;
      //cout << "dnf of mod_acc: " << mod_acc.to_dnf() << endl;
      copy->set_acceptance(mod_acc);
     // cout << "num acc sets3: " << copy->num_sets() << endl;
      auto det_copy = to_deterministic_tgba(copy, optimisations);

      // register all aps from the copy that are not already registered by res
      for (auto ap : det_copy->ap())
      {
        bool found = false;
        for (auto ap_res : res->ap())
        {
          if (ap_res == ap)
          {
            found = true;
          }
        }
        if (!found)
        {
          res->register_ap(ap);
        }
        
      }
      
      det_automata.push_back(det_copy);

    }

    std::sort(det_automata.begin(), det_automata.end(), compare_aut);
    if (det_automata.size() > 0)
    {
      res = det_automata[0];
    }
    // build product of the deterministic automata
    for (auto det_aut : det_automata)
    {
      // add copy to result
      // check if one automaton accepts a supersset of the other one
      //cout << det_aut->num_states() << endl;
      if (spot::contains(det_aut, res))
      {
        // det_aut contains res
        if (spot::contains(res, det_aut))
        {
          // automata are equivalent
          if (det_aut->num_states() < res->num_states())
          {
            // automata are equivalent and det_aut is smaller
            res = det_aut;
          }
        }
        else
        {
          // det_aut contains res, but not the other way around
          res = det_aut;
        }
      }
      else if (!spot::contains(res, det_aut))
      {
        res = spot::product_or(res, det_aut);
      }
      // implicit case: if automata are equal and res is smaller
      // OR res contains det_aut, but not the other way around:
      // keept res as it is
    }

    
    // try to simplify the automaton
    res->purge_dead_states();
    spot::cleanup_acceptance_here(res);

    if (check_result)
    {
      if (! spot::are_equivalent(res, in))
      {
        std::cout << "ERROR in my_to_generalized_buchi_4" << std::endl;
      }
    }
    return res;
  }
}

spot::twa_graph_ptr
my_to_deterministic_tgba_4_unoptimised(const spot::const_twa_graph_ptr& in, const bool optimisations, const bool check_result)
{
  auto dnf = in->get_acceptance().to_dnf();
  auto disjuncts = dnf.top_disjuncts();

  // check, if dnf has only one disjunct
  if (disjuncts.size() <= 1)
  {
    // no copying needed, we use the determinization approach of spot
    return to_deterministic_tgba(in, optimisations);
  }
  else
  {
    // creating an empty TwA 'res' for the result with the same bdd
    spot::twa_graph_ptr res = make_twa_graph(in->get_dict());

    // register all atomic propositions of the old automaton
    for (auto ap : in->ap())
    {
      res->register_ap(ap);
    }

    // the product requires at least one state
    res->new_states(1);
    res->set_acceptance(spot::acc_cond::acc_code("f"));

    unsigned n = in->num_sets();
    auto add_acc = spot::acc_cond::acc_code::fin({n}) & spot::acc_cond::acc_code::inf({n}); // add useless condition to keep the number of acc-sets maximal

    vector<spot::twa_graph_ptr> det_automata; 
    for (auto acc : disjuncts)
    {
      //cout << "acc: " << acc << endl;
      // create copy of the automaton with the same properties as 'in'
      auto copy = spot::make_twa_graph(in, {true, true, true, true, true, true});
      //cout << "num acc sets: " << copy->num_sets() << endl;
      spot::cleanup_acceptance_here(copy);
      //cout << "num acc sets2: " << copy->num_sets() << endl;
      auto mod_acc = acc| add_acc;
      //cout << "dnf of mod_acc: " << mod_acc.to_dnf() << endl;
      copy->set_acceptance(mod_acc);
     // cout << "num acc sets3: " << copy->num_sets() << endl;
      auto det_copy = to_deterministic_tgba(copy, optimisations);

      // register all aps from the copy that are not already registered by res
      for (auto ap : det_copy->ap())
      {
        bool found = false;
        for (auto ap_res : res->ap())
        {
          if (ap_res == ap)
          {
            found = true;
          }
        }
        if (!found)
        {
          res->register_ap(ap);
        }
        
      }
      
      det_automata.push_back(det_copy);

    }

    if (det_automata.size() > 0)
    {
      res = det_automata[0];
    }
    // build product of the deterministic automata
    for (auto det_aut : det_automata)
    {     
      res = spot::product_or(res, det_aut);
    }

    // try to simplify the automaton
    res->purge_dead_states();
    spot::cleanup_acceptance_here(res);

    if (check_result)
    {
      if (! spot::are_equivalent(res, in))
      {
        std::cout << "ERROR in my_to_generalized_buchi_4" << std::endl;
      }
    }
    return res;
  }
}



spot::twa_graph_ptr
my_to_limited_deterministic(const spot::const_twa_graph_ptr& in, const bool optimisations, const bool check_result)
{
  auto dnf = in->get_acceptance().to_dnf();
  auto disjuncts = dnf.top_disjuncts();

  // check, if dnf has only one disjunct
  if (disjuncts.size() <= 1)
  {
    // no copying needed, we use the determinization approach of spot
    return to_deterministic_tgba(in, optimisations);
  }
  else
  {
    // creating an empty TwA 'res' for the result with the same bdd
    spot::twa_graph_ptr res = make_twa_graph(in->get_dict());

    // register all atomic propositions of the old automaton
    for (auto ap : in->ap())
    {
      res->register_ap(ap);
    }

    // the product requires at least one state
    res->new_states(1);
    res->set_acceptance(spot::acc_cond::acc_code("f"));

    unsigned n = in->num_sets();
    auto add_acc = spot::acc_cond::acc_code::fin({n}) & spot::acc_cond::acc_code::inf({n}); // add useless condition to keep the number of acc-sets maximal

    vector<spot::twa_graph_ptr> det_automata; 
    for (auto acc : disjuncts)
    {
      // create copy of the automaton with the same properties as 'in'
      auto copy = spot::make_twa_graph(in, {true, true, true, true, true, true});
      spot::cleanup_acceptance_here(copy);
      auto mod_acc = acc| add_acc;
      copy->set_acceptance(mod_acc);
      auto det_copy = to_deterministic_tgba(copy, optimisations);

      // register all aps from the copy that are not already registered by res
      for (auto ap : det_copy->ap())
      {
        bool found = false;
        for (auto ap_res : res->ap())
        {
          if (ap_res == ap)
          {
            found = true;
          }
        }
        if (!found)
        {
          res->register_ap(ap);
        }
        
      }
      
      det_automata.push_back(det_copy);

    }

    std::sort(det_automata.begin(), det_automata.end(), compare_aut);
    // build product of the deterministic automata
    for (auto det_aut : det_automata)
    {
      if (!spot::contains(res, det_aut))
      {
        // add copy to result if it is not already contained
        res = my_add_limited_twa(res, det_aut, det_aut->get_acceptance());
      }

    }

    
    // try to simplify the automaton
    res->purge_dead_states();
    spot::cleanup_acceptance_here(res);
    res->prop_universal(false);
    spot::is_universal(res); // set the is_universal() property

    if (check_result)
    {
      if (! spot::are_equivalent(res, in))
      {
        std::cout << "ERROR in my_to_limited_deterministic_new" << std::endl;
      }
    }
    return res;
  }
}

float
avg_num_nondet_choices(const spot::const_twa_graph_ptr& in)
{
  float non_det_choices=0;
  
  for (auto edge1 : in->edges())
  {
    for (auto edge2 : in->edges())
    {
      // edges start in same state
      if (edge1.src == edge2.src)
      {
        // some thing must be different, otherwise we have the same edge
        if (edge1.dst != edge2.dst
          || edge1.cond != edge2.cond
          || edge1.acc != edge2.acc)
        {
          // unnecessary large experession to check, if the edges are a nondet choice
          if ((edge1.cond | edge2.cond) != ((edge1.cond | edge2.cond) - (edge1.cond & edge2.cond) ))
          {
            //cout << "nondet choice found: "<<edge1.src << " " << edge2.src<< " dst: "<< edge1.dst << " " << edge2.dst << endl;
            non_det_choices++;
          }
        }
      }
    }
  }
  non_det_choices /= 2;
  //cout << "choices: " << non_det_choices<< endl;
  return non_det_choices / (float) in->num_states();

}

void run_test() 
{  
  //std::thread::hardware_concurrency(); // number of cores
  // differences that occur
  std::map<int, unsigned> diffs;

  for (int i = 0; i <=218; ++i) 
  {
    std::string file = "hoa_examples/ltl3tela/literature" + std::to_string(i) +".hoa" ;

    spot::parsed_aut_ptr pa = parse_aut(file, spot::make_bdd_dict());
    if (pa->format_errors(std::cerr))
      break; 
    if (pa->aborted)
    {
      std::cerr << "--ABORT-- read\n";
      break;
    }
    //std::cout <<"process file " << file<<std::endl;

    auto spot_aut = to_deterministic_tgba(pa->aut, false);
    auto my_aut = my_to_deterministic_tgba(pa->aut, false, false);
    int diff = (int) spot_aut->num_states() - (int) my_aut->num_states();
    std::cout << "spot: " << spot_aut->num_states()<< "me: "<< my_aut->num_states() << " diff: " << diff <<" file: "<< file<< std::endl;
    diffs[diff] = diffs[diff]+1;

    // test, if the results are correct
    if (! spot::are_equivalent(my_aut, pa->aut))
    {
      std::cout << "ERROR: not equal for file " <<file <<" " <<diff << std::endl;
    }
    if (! spot::are_equivalent(spot_aut, pa->aut))
    {
      std::cout << "ERROR: Spot not equal for file " <<file <<" " <<diff << std::endl;
    }
  }

  for (auto& t : diffs)
  {
    std::cout << t.first <<" " << t.second<< std::endl;
  }

}



