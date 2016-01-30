from __future__ import print_function

import argparse
import sys


from simplesat.dependency_solver import DependencySolver
from simplesat.pool import Pool
from simplesat.sat.policy import InstalledFirstPolicy
from simplesat.test_utils import Scenario
from simplesat.errors import SatisfiabilityError


def solve_and_print(request, remote_repositories, installed_repository,
                    print_ids, prune=True, prefer_installed=True, debug=0,
                    simple=False):
    pool = Pool(remote_repositories)
    pool.add_repository(installed_repository)

    policy = InstalledFirstPolicy(pool, installed_repository,
                                  prefer_installed=prefer_installed)
    solver = DependencySolver(
        pool, remote_repositories, installed_repository,
        policy=policy, use_pruning=prune)

    fmt = "ELAPSED : {description:20} : {elapsed:e}"
    try:
        transaction = solver.solve(request)
        if simple:
            print(transaction.to_simple_string())
        else:
            print(transaction)
    except SatisfiabilityError as e:
        msg = "UNSATISFIABLE: {}"
        print(msg.format(e.unsat.to_string(pool, detailed=debug)))
        print(e.unsat._find_requirement_time.pretty(fmt), file=sys.stderr)

    print(solver._last_rules_time.pretty(fmt), file=sys.stderr)
    print(solver._last_solver_init_time.pretty(fmt), file=sys.stderr)
    print(solver._last_solve_time.pretty(fmt), file=sys.stderr)
    if debug:
        print(solver._policy._log_report(), file=sys.stderr)


def main(argv=None):
    argv = argv or sys.argv[1:]

    p = argparse.ArgumentParser()
    p.add_argument("scenario", help="Path to the YAML scenario file.")
    p.add_argument("--print-ids", action="store_true")
    p.add_argument("--no-prune", dest="prune", action="store_false")
    p.add_argument("--no-prefer-installed", dest="prefer_installed",
                   action="store_false")
    p.add_argument("-d", "--debug", action="count")
    p.add_argument("--simple", action="store_true",
                   help="Show a simpler description of the transaction.")

    ns = p.parse_args(argv)

    scenario = Scenario.from_yaml(ns.scenario)
    solve_and_print(scenario.request, scenario.remote_repositories,
                    scenario.installed_repository, ns.print_ids,
                    prune=ns.prune, prefer_installed=ns.prefer_installed,
                    debug=ns.debug, simple=ns.simple)


if __name__ == '__main__':
    main()
