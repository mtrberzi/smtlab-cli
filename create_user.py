#!/usr/bin/env python

import argparse
import requests
import sys
import os
import secrets
import getpass

roles = {}
roles['readonly'] = ['read']
roles['user'] = ['read', 'upload_benchmark', 'upload_solver', 'start_run', 'change_password']
roles['admin'] = ['read', 'upload_benchmark', 'upload_solver', 'start_run', 'change_password', 'change_other_password', 'admin_user']
roles['scheduler'] = ['read', 'start_run', 'post_results', 'message_queue']
roles['worker'] = ['read', 'message_queue']

def mkpasswd(length=32):
    return secrets.token_urlsafe(length)
    
def main():
    parser = argparse.ArgumentParser(description='Create an SMTLab user')
    parser.add_argument('--endpoint', help="Base URL of API endpoint", default="http://127.0.0.1:5000")
    parser.add_argument('-r', '--role', type=str, default=None, help="Role (quick permissions) for account: readonly, user, admin, scheduler, worker")
    parser.add_argument('-p', '--password', default=False, action='store_true', help="Prompt for password (otherwise, randomly generate one)")
    parser.add_argument('username', type=str, help="Username of the new account")

    auth_username = os.environ['SMTLAB_USERNAME']
    auth_password = os.environ['SMTLAB_PASSWORD']
    
    args = parser.parse_args()
    if args.role is None:
        # TODO
        pass
    else:
        if args.role not in roles:
            print(f"Error: role {args.role} not defined")
            sys.exit(1)
        perms = roles[args.role]
    if args.password:
        while True:
            pw = getpass.getpass(prompt="Enter a password for the new user: ")
            pw_verify = getpass.getpass(prompt="Confirm password: ")
            if pw != pw_verify:
                print("Passwords do not match.")
            else:
                break
    else:
         pw = mkpasswd()
    request_body = {'username': args.username, 'password': pw, 'permissions': perms}
    r = requests.post(args.endpoint + "/users/create", json=request_body, auth=(auth_username, auth_password))
    if r.status_code != requests.codes.ok:
        print(r.json())
        r.raise_for_status()
    print(f"Created user {args.username}.")
    if not args.password:
        print("The generated password for this account is:")
        print(f"{pw}")

if __name__ == '__main__':
    main()
