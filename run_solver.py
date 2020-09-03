#!/usr/bin/env python

import argparse
import requests
import sys

def prompt_yes_or_no(prompt):
    while True:
        print(prompt + " ", end="")
        sys.stdout.flush()
        response = sys.stdin.readline().lower().strip()
        if response == "yes" or response == "true" or response == "y":
            return True
        elif response == "no" or response == "false" or response == "n":
            return False
        else:
            print("Please answer 'yes' or 'no'.")

def interact(args):
    # run_parameters must contain:
    # - benchmark_id
    # - solver_id
    # - performance
    # and can contain:
    # - arguments
    # - description
    run_parameters = {}
    if args.benchmark:
        run_parameters['benchmark_id'] = args.benchmark
    else:
        print("Fetching list of benchmarks from the server.")
        r = requests.get(args.endpoint + "/benchmarks")
        if r.status_code != requests.codes.ok:
            print(r.json())
            r.raise_for_status()
        response = r.json()
        if len(response) == 0:
            print("There are no benchmarks available on the server!")
            sys.exit(1)
        valid_ids = []
        for benchmark in response:
            print(f"{benchmark['id']}: {benchmark['name']}")
            valid_ids.append(benchmark['id'])
        print("")
        while True:
            print("Run which benchmark ID? ", end="")
            sys.stdout.flush()
            response = sys.stdin.readline().strip()
            try:
                id = int(response)
                if id in valid_ids:
                    run_parameters['benchmark_id'] = id
                    break
                else:
                    print("Invalid ID specified.")
            except ValueError:
                print("Please enter an integer.")

    if args.solver:
        run_parameters['solver_id'] = args.solver
    else:
        print("Fetching list of solvers from the server.")
        r = requests.get(args.endpoint + "/solvers")
        if r.status_code != requests.codes.ok:
            print(r.json())
            r.raise_for_status()
        response = r.json()
        if len(response) == 0:
            print("There are no solvers available on the server!")
            sys.exit(1)
        valid_ids = []
        for solver in response:
            print(f"{solver['id']}: {solver['name']}")
            valid_ids.append(solver['id'])
        print("")
        while True:
            print("Run which solver ID? ", end="")
            sys.stdout.flush()
            response = sys.stdin.readline().strip()
            try:
                id = int(response)
                if id in valid_ids:
                    run_parameters['solver_id'] = id
                    break
                else:
                    print("Invalid ID specified.")
            except ValueError:
                print("Please enter an integer.")

    run_parameters['performance'] = args.performance
    run_parameters

    custom_arguments = prompt_yes_or_no("Do you want to pass custom arguments to the solver? (If not, the default arguments for this solver will be used.)")
    if custom_arguments:
        custom_args = []
        while True:
            print("Enter arguments, one per line, or a blank line to stop: ", end="")
            sys.stdout.flush()
            response = sys.stdin.readline().strip()
            if response == "":
                break
            else:
                custom_args.append(response)
        run_parameters['arguments'] = json.dumps(custom_args)
    
    print("Enter an optional description for this run: ", end="")
    sys.stdout.flush()
    run_parameters['description'] = sys.stdin.readline().strip()

    return run_parameters

def main():
    parser = argparse.ArgumentParser(description="Run benchmarks on SMTLab")
    parser.add_argument('--endpoint', help="Base URL of API endpoint", default="http://127.0.0.1:5000")
    parser.add_argument("-i", "--interactive", default=False, action="store_true", help="Choose run parameters interactively")
    parser.add_argument("-s", "--solver", type=int, help="ID of solver to run")
    parser.add_argument("-b", "--benchmark", type=int, help="ID of benchmark to run")
    parser.add_argument("-p", "--performance", default=False, action="store_true", help="Start run in performance mode (default is regression mode)")

    args = parser.parse_args()
    run_parameters = {}
    if args.interactive:
        run_parameters = interact(args)
    else:
        # TODO
        pass

    r = requests.post(args.endpoint + "/runs", json=run_parameters)
    if r.status_code != requests.codes.ok:
        print(r.json())
        r.raise_for_status()
    run_id = r.json()['id']
    print(f"Run {run_id} created.")

if __name__ == '__main__':
    main()
