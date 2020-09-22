#!/usr/bin/env python

import argparse
import requests
import sys
import os

username = os.environ['SMTLAB_USERNAME']
password = os.environ['SMTLAB_PASSWORD']

def interact_get_run_id(args):
    # first fetch benchmark names and solver names
    r = requests.get(args.endpoint + "/benchmarks", auth=(username,password))
    r.raise_for_status()
    benchmark_info = r.json()
    r = requests.get(args.endpoint + "/solvers", auth=(username,password))
    r.raise_for_status()
    solver_info = r.json()
    
    print("Fetching list of runs from the server.")
    r = requests.get(args.endpoint + "/runs", auth=(username,password))
    if r.status_code != requests.codes.ok:
        print(r.json())
        r.raise_for_status()
    run_info = r.json()
    if len(run_info) == 0:
        print("There are no runs available on the server!")
        sys.exit(1)
    valid_ids = []
    for run in run_info:
        benchmark_name = "???"
        for benchmark in benchmark_info:
            if benchmark['id'] == run['benchmark_id']:
                benchmark_name = benchmark['name']
                break
        solver_name = "???"
        for solver in solver_info:
            if solver['id'] == run['solver_id']:
                solver_name = solver['name']
                break
        print(f"{run['id']}: {solver_name} / {benchmark_name} : {run['arguments']} ({run['description'].strip()}) {run['start_date']}")
        valid_ids.append(run['id'])
    print("")
    while True:
        print("Show results from which run ID? ", end="")
        sys.stdout.flush()
        response = sys.stdin.readline().strip()
        try:
            id = int(response)
            if id in valid_ids:
                return id
            else:
                print("Invalid ID specified.")
        except ValueError:
            print("Please enter an integer.")

def display_run(args, run_id):
    r = requests.get(args.endpoint + f"/runs/{run_id}", auth=(username,password))
    r.raise_for_status()
    run_info = r.json()

    r = requests.get(args.endpoint + f"/benchmarks/{run_info['benchmark_id']}", auth=(username,password))
    r.raise_for_status()
    benchmark_info = r.json()

    r = requests.get(args.endpoint + f"/solvers", auth=(username,password))
    r.raise_for_status()
    solver_info = r.json()

    r = requests.get(args.endpoint + f"/benchmarks/{run_info['benchmark_id']}/instances", auth=(username,password))
    r.raise_for_status()
    benchmark_instances_info = r.json()

    r = requests.get(args.endpoint + f"/runs/{run_id}/results", auth=(username,password))
    r.raise_for_status()
    result_info = r.json()

    this_solver_name = "???"
    for solver in solver_info:
        if solver['id'] == run_info['solver_id']:
            this_solver_name = solver['name']
            break
    
    print(f"Run {run_info['id']}: {this_solver_name} / {benchmark_info['name']}")
    print(f"{len(result_info)} results / {len(benchmark_instances_info)} instances in this benchmark")

    # collect summary
    nSAT = 0
    nUNSAT = 0
    nTIMEOUT = 0
    nUNKNOWN = 0
    nERROR = 0

    totalRunTime_ms = 0
    totalRunTime_withoutTimeouts_ms = 0

    for result in result_info:
        totalRunTime_ms += result['runtime']
        if result['result'] != 'timeout':
            totalRunTime_withoutTimeouts_ms += result['runtime']

        if result['result'] == 'sat':
            nSAT += 1
        elif result['result'] == 'unsat':
            nUNSAT += 1
        elif result['result'] == 'timeout':
            nTIMEOUT += 1
        elif result['result'] == 'unknown':
            nUNKNOWN += 1
        elif result['result'] == 'error':
            nERROR += 1

    totalRunTime = float(totalRunTime_ms) * 0.001
    totalRunTime_withoutTimeouts = float(totalRunTime_withoutTimeouts_ms) * 0.001
            
    print(f"SAT: {nSAT} UNSAT: {nUNSAT} TIMEOUT: {nTIMEOUT} UNKNOWN: {nUNKNOWN} ERROR: {nERROR}")
    print(f"Total time: {totalRunTime:.3f} seconds (without timeouts: {totalRunTime_withoutTimeouts:.3f} seconds)")
    print()
    print("Detailed results:")
    print()

    nValidationIssues = 0
    
    for instance in benchmark_instances_info:
        for result in result_info:
            if result['instance_id'] == instance['id']:
                instanceTime = float(result['runtime']) * 0.001
                r = requests.get(args.endpoint + f"/results/{result['id']}", auth=(username,password))
                r.raise_for_status()
                detailed_result_info = r.json()
                validations = detailed_result_info['validations']
                nValidations = len(validations)
                nValidationsOK = 0
                errorValidations = []
                for validation in validations:
                    if 'result' in validation:
                        if validation['result'] == 'unsat' and result['result'] == 'sat':
                            errorValidations.append(validation)
                        else:
                            nValidationsOK += 1
                    elif 'validation' in validation:
                        if validation['validation'] == 'invalid':
                            errorValidations.append(validation)
                        else:
                            nValidationsOK += 1
                print(f"{instance['name']}: {result['result']} ({instanceTime:.3f} seconds) ({nValidationsOK}/{nValidations} without error)")
                if result['result'] == 'error':
                    print(detailed_result_info['stdout'])
                if errorValidations:
                    nValidationIssues += 1
                    for errorValidation in errorValidations:
                        for solver in solver_info:
                            if errorValidation['solver_id'] == solver['id']:
                                solverName = solver['name']
                                break
                        if 'result' in errorValidation:
                            rText = errorValidation['result']
                        elif 'validation' in errorValidation:
                            rText = errorValidation['validation']
                        print(f"- {solverName}: {rText}")

    print()
    print(f"{nValidationIssues} instances had validation issues.")

def main():
    parser = argparse.ArgumentParser(description="Get results of SMTLab benchmark runs")
    parser.add_argument('--endpoint', help="Base URL of API endpoint", default=os.environ['SMTLAB_API_ENDPOINT'])
    parser.add_argument('-i', '--interactive', default=False, action="store_true", help="Display results interactively")
    parser.add_argument("run_id", nargs='?', type=int, default=-1)

    args = parser.parse_args()
    if args.interactive:
        run_id = interact_get_run_id(args)
    else:
        if args.run_id < 0:
            print("error: run ID or '--interactive' must be specified")
            sys.exit(1)
        else:
            run_id = args.run_id

    display_run(args, run_id)

if __name__ == '__main__':
    main()
