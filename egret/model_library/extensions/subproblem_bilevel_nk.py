#  ___________________________________________________________________________
#
#  EGRET: Electrical Grid Research and Engineering Tools
#  Copyright 2019 National Technology & Engineering Solutions of Sandia, LLC
#  (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
#  Government retains certain rights in this software.
#  This software is distributed under the Revised BSD License.
#  ___________________________________________________________________________

"""
This module contains several disjunctive subproblem constraints that
are useful when working with the attacker-defender bilevel model
"""

import egret.model_library.decl as decl
import pyomo.environ as pe
import pyomo.gdp as gdp


def disjunctify(model, indicator_name, disjunct_name, LHS_disjunct_set, RHS_disjunct_set):
    assert len(LHS_disjunct_set) == len(RHS_disjunct_set)

    dset = list(range(len(LHS_disjunct_set)))

    setattr(model, indicator_name, None)
    _dj = getattr(model, indicator_name)
    setattr(model, disjunct_name, None)
    _ddj = getattr(model, disjunct_name)

    def _disjunct_rule(disjunct, i, flag):
        if flag:
            con_lists = LHS_disjunct_set
        else:
            con_lists = RHS_disjunct_set

        disjunct.c = pe.ConstraintList()
        for k,cik in con_lists[i]:
            disjunct.c.add(pe.inequality(cik.lower, cik.body, cik.upper))
            cik.deactivate()
    _dj = gdp.Disjunct(dset, [0,1], rule=_disjunct_rule)

    # Define the disjunction
    def _disjunction_rule(model, i):
        return [model._dj[i,0], model._dj[i,1]]
    _ddj = gdp.Disjunction(range(len(LHS_disjunct_set)), rule=_disjunction_rule)


def declare_eq_branch_power_off(model, index_set, branches):
    """
    RHS of disjunct for declare_eq_branch_power_btheta_approx
    """
    m = model

    con_set = decl.declare_set("_con_eq_branch_power_off", model, index_set)

    m.eq_pf_branch_off = pe.Constraint(con_set)
    for branch_name in con_set:
        m.eq_pf_branch_off[branch_name] = \
            m.pf[branch_name] == 0.


def declare_ineq_load_shed_ub(model, index_set):
    """
    Create the upper-bound inequality constraint for the load shed.
    """
    m = model
    con_set = decl.declare_set('_con_ineq_load_shed_ub',
                               model=model, index_set=index_set)

    m.ineq_load_shed_ub = pe.Constraint(con_set)

    for bus_name in index_set:
        if m.pl[bus_name] != 0.:
            continue

        m.ineq_load_shed_ub[bus_name] = \
            m.load_shed[bus_name] <= m.pl[bus_name]


def declare_ineq_load_shed_lb(model, index_set):
    """
    Create the lower-bound inequality constraint for the load shed.
    """
    m = model
    con_set = decl.declare_set('_con_ineq_load_shed_lb',
                               model=model, index_set=index_set)

    m.ineq_load_shed_lb = pe.Constraint(con_set)

    for bus_name in index_set:
        if m.pl[bus_name] != 0.:
            continue

        m.ineq_load_shed_lb[bus_name] = \
            m.pl[bus_name] <= m.load_shed[bus_name]


def declare_ineq_load_shed_lb_off(model, index_set):
    """
    Create the lower-bound inequality constraint for the load shed when compromised.
    """
    m = model
    con_set = decl.declare_set('_con_ineq_load_shed_lb_off',
                               model=model, index_set=index_set)

    m.ineq_load_shed_lb_off = pe.Constraint(con_set)

    for bus_name in index_set:
        if m.pl[bus_name] != 0.:
            continue

        m.ineq_load_shed_lb_off[bus_name] = \
            0. <= m.load_shed[bus_name]


def declare_ineq_gen(model, index_set, gens):
    """
    Create the inequality constraints for the generator operations.
    """
    m = model
    con_set = decl.declare_set('_con_ineq_gen',
                               model=model, index_set=index_set)

    m.ineq_gen = pe.Constraint(con_set)

    for gen_name in index_set:
        gen = gens[gen_name]

        m.ineq_gen[gen_name] = \
            pe.inequality(gen['p_min'], m.pg[gen_name], gen['p_max'])


def declare_ineq_gen_off(model, index_set, gens):
    """
    Create the constraint for the generator operations when compromised.
    """
    m = model
    con_set = decl.declare_set('_con_ineq_gen_off',
                               model=model, index_set=index_set)

    m.ineq_gen_off = pe.Constraint(con_set)

    for gen_name in index_set:
        m.ineq_gen_off[gen_name] = \
            m.pg[gen_name] == 0.



