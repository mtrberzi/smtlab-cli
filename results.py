#!/usr/bin/env python

import argparse
import requests
import sys

def interact_get_run_id(args):
    # first fetch benchmark names and solver names
    r = requests.get(args.endpoint + "/benchmarks")
    r.raise_for_status()
    benchmark_info = r.json()
    r = requests.get(args.endpoint + "/solvers")
    r.raise_for_status()
    solver_info = r.json()
    
    print("Fetching list of runs from the server.")
    r = requests.get(args.endpoint + "/runs")
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
        print(f"{benchmark['id']}: {solver_name} / {benchmark_name} : {run['arguments']} ({run['description'].strip()})")
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
    r = requests.get(args.endpoint + f"/runs/{run_id}")
    r.raise_for_status()
    run_info = r.json()

    r = requests.get(args.endpoint + f"/benchmarks/{run_info['benchmark_id']}")
    r.raise_for_status()
    benchmark_info = r.json()

    r = requests.get(args.endpoint + f"/solvers/{run_info['solver_id']}")
    r.raise_for_status()
    solver_info = r.json()

    r = requests.get(args.endpoint + f"/benchmarks/{run_info['benchmark_id']}/instances")
    r.raise_for_status()
    benchmark_instances_info = r.json()

    r = requests.get(args.endpoint + f"/runs/{run_id}/results")
    r.raise_for_status()
    result_info = r.json()

    print(f"Run {run_info['id']}: {solver_info['name']} / {benchmark_info['name']}")
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
    

def main():
    parser = argparse.ArgumentParser(description="Get results of SMTLab benchmark runs")
    parser.add_argument('--endpoint', help="Base URL of API endpoint", default="http://127.0.0.1:5000")
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
