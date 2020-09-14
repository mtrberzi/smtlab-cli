#!/usr/bin/env python

import os
import os.path
import sys
import argparse
import requests

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def main():
    parser = argparse.ArgumentParser(description="Upload SMT2 benchmarks to SMTLab")
    parser.add_argument('--id', help="ID number of existing benchmark to add to")
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--endpoint', help="Base URL of API endpoint", default="http://127.0.0.1:5000")
    parser.add_argument("name", help="name of the benchmark to upload")
    parser.add_argument("path", help="path to benchmark folder; all .smt2 files under this path will be uploaded")

    username = os.environ['SMTLAB_USERNAME']
    password = os.environ['SMTLAB_PASSWORD']
    
    args = parser.parse_args()
    benchmark_id = None
    if args.id:
        r = requests.get(args.endpoint + "/benchmarks/{}".format(args.id), auth=(username,password))
        if r.status_code != requests.codes.ok:
            print(r.json())
            r.raise_for_status()
        response = r.json()
        if args.verbose:
            print("Adding to benchmark with ID {}".format(response['id']))
        benchmark_id = args.id
    else:
        new_benchmark_rq = {'name': args.name}
        r = requests.post(args.endpoint + "/benchmarks", json=new_benchmark_rq, auth=(username,password))
        if r.status_code != requests.codes.ok:
            print(r.json())
            r.raise_for_status()
        response = r.json()
        if args.verbose:
            print("Created benchmark with ID {}".format(response['id']))
        benchmark_id = response['id']
    # collect all instances
    instances = []
    for subdir, dirs, files in os.walk(args.path):
        for f in files:
            filepath = subdir + os.sep + f
            subpath = os.path.relpath(subdir, args.path)
            if subpath == ".":
                subpath = f
            else:
                subpath = subpath + os.sep + f
            with open(filepath, "r") as f_instance:
                instance = {"name": subpath, "body": f_instance.read()}
                instances.append(instance)
    if args.verbose:
        print("Uploading {} instances.".format(len(instances)))
    # POST instances to /benchmarks/{benchmark_id}
    for chunk in chunks(instances, 10):
        if args.verbose:
            for inst in chunk:
                print(inst["name"])
        r = requests.post(args.endpoint + "/benchmarks/{}".format(benchmark_id), json=chunk, auth=(username,password))
        if r.status_code != requests.codes.ok:
            print(r.json())
            r.raise_for_status()

if __name__ == '__main__':
    main()
