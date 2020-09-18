#!/usr/bin/env python

import argparse
import requests
import sys
import os
import secrets
import getpass

def mkpasswd(length=32):
    return secrets.token_urlsafe(length)

def main():
    parser = argparse.ArgumentParser(description='Change the password of an SMTLab account')
    parser.add_argument('--endpoint', help="Base URL of API endpoint", default=os.environ['SMTLAB_API_ENDPOINT'])
    parser.add_argument('-g', '--generate', default=False, action='store_true', help="Generate a random password (otherwise, prompt for one)")
    parser.add_argument('username', nargs='?', type=str, default=os.environ['SMTLAB_USERNAME'], help="Username to modify")
    args = parser.parse_args()

    auth_username = os.environ['SMTLAB_USERNAME']
    auth_password = os.environ['SMTLAB_PASSWORD']

    print(f"Changing password for SMTLab user {args.username}")
    if args.generate:
        new_password = mkpasswd()
    else:
        while True:
            new_password = getpass.getpass("Enter new password: ")
            verify_password = getpass.getpass("Confirm password: ")
            if new_password != verify_password:
                print("Passwords do not match.")
            else:
                break
    request_body = {'username': args.username, 'password': new_password}
    r = requests.post(args.endpoint + "/users/change_password", json=request_body)
    r.raise_for_status()
    print("Password successfully changed. You may need to edit configuration files and environment variables to reflect the updated password.")
    if args.generate:
        print("The generated password is:")
        print(f"{new_password}")

if __name__ == '__main__':
    main()
