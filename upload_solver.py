#!/usr/bin/env python

import os
import os.path
import sys
import argparse
import requests
import base64

def main():
    parser = argparse.ArgumentParser(description="Upload solver binary to SMTLab")
    parser.add_argument('--verbose', action='store_true', default=False)
    parser.add_argument('--endpoint', help="Base URL of API endpoint", default="http://127.0.0.1:5000")
    parser.add_argument('--arguments', help="Default command-line arguments for solver")
    parser.add_argument('--validation', action='store_true', default=False, help="Mark this solver as a validation solver")
    parser.add_argument("name", help="name of the solver to upload")
    parser.add_argument("path", help="path to solver binary")

    username = os.environ['SMTLAB_USERNAME']
    password = os.environ['SMTLAB_PASSWORD']

    args = parser.parse_args()
    new_solver_rq = {'name': args.name, 'validation_solver': args.validation}
    if args.arguments:
        new_solver_rq['default_arguments'] = args.arguments
    with open(args.path, 'rb') as solver_file:
        new_solver_rq['base64_binary'] = base64.b64encode(solver_file.read()).decode('ascii')
    r = requests.post(args.endpoint + "/solvers", json=new_solver_rq, auth=(username, password))
    if r.status_code != requests.codes.ok:
        print(r.json())
        r.raise_for_status()
    if args.verbose:
        print("Created solver {}.".format(r.json()['id']))

if __name__ == '__main__':
    main()
