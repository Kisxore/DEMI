#!/usr/bin/env python3

import argparse
import sys
import os
import json

# Import module classes directly
from demi.modules.ssh import SSHModule
from demi.modules.ftp import FTPModule
from demi.modules.http_basic import HTTPBasicModule
from demi.modules.http_form import HTTPFormModule

# Map protocol names to module classes
MODULES = {
    "ssh": SSHModule,
    "ftp": FTPModule,
    "http-basic": HTTPBasicModule,
    "http-form": HTTPFormModule,
}

from demi.smart_interface import SmartDemiEngine

def load_list(filepath):
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    with open(filepath, 'r', encoding="utf-8", errors="replace") as f:
        return [line.strip() for line in f if line.strip()]

def load_pairs(filepath):
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    pairs = []
    with open(filepath, 'r', encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line and ":" in line:
                pairs.append(tuple(line.split(":", 1)))
    return pairs

def main():
    parser = argparse.ArgumentParser(
        prog="DEMI",
        description="Multi-protocol credential brute force tool (SMART EDITION)"
    )

    # Required
    parser.add_argument("-m", "--module", required=True, choices=MODULES.keys(),
        help="Protocol module to use")
    parser.add_argument("-t", "--target", required=True, help="Target IP/hostname/URL")

    # Credentials
    parser.add_argument("-U", "--userlist", help="File with usernames")
    parser.add_argument("-P", "--passlist", help="File with passwords")
    parser.add_argument("--pairs", help="File with user:pass pairs")

    # Engine
    parser.add_argument("--threads", type=int, default=32,
        help="Max worker threads (default: 32)")
    parser.add_argument("--timeout", type=float, default=5.0,
        help="Connection timeout in seconds (default: 5.0)")
    parser.add_argument("-f", "--stop-on-success", action="store_true",
        help="Stop after first valid credential")
    parser.add_argument("--random-delay", action="store_true",
        help="Random delay between attempts (anti-rate-limit)")
    parser.add_argument("--min-delay", type=float, default=0.0,
        help="Minimum random delay (seconds)")
    parser.add_argument("--max-delay", type=float, default=0.5,
        help="Maximum random delay (seconds)")
    parser.add_argument("--log-file", help="Log output to file")
    parser.add_argument("--result-file", help="Save valid credentials to file")

    # Protocol options
    parser.add_argument("--port", type=int, help="Target port (default varies)")
    parser.add_argument("--path", help="URL path (for HTTP)")
    parser.add_argument("--user-field", help="Form username field (http-form)")
    parser.add_argument("--pass-field", help="Form password field (http-form)")
    parser.add_argument("--method", default="POST", choices=["GET", "POST"],
        help="HTTP method (http-form)")
    parser.add_argument("--success-re", help="Success regex (http-form)")
    parser.add_argument("--fail-re", help="Failure regex (http-form)")
    parser.add_argument("--proxy", help="HTTP proxy URL (e.g., http://127.0.0.1:8080)")

    args = parser.parse_args()

    users, passwords, pairs = [], [], []
    try:
        if args.pairs:
            pairs = load_pairs(args.pairs)
        else:
            if args.userlist:
                users = load_list(args.userlist)
            if args.passlist:
                passwords = load_list(args.passlist)
            if not pairs and not (users and passwords):
                print("Error: Must provide --pairs OR both --userlist and --passlist",
                    file=sys.stderr)
                sys.exit(1)
    except Exception as e:
        print(f"Error loading credentials: {e}", file=sys.stderr)
        sys.exit(1)

    module_options = {
        "timeout": args.timeout,
    }

    if args.port:
        module_options["port"] = args.port
    if args.module in ("http-basic", "http-form"):
        if args.path:
            module_options["path"] = args.path
        if args.proxy:
            module_options["proxy"] = args.proxy
    if args.module == "http-form":
        if not args.user_field or not args.pass_field:
            print("Error: http-form requires --user-field and --pass-field",
                file=sys.stderr)
            sys.exit(1)
        module_options.update({
            "user_field": args.user_field,
            "pass_field": args.pass_field,
            "method": args.method,
            "success_re": args.success_re,
            "fail_re": args.fail_re,
        })

    try:
        engine = SmartDemiEngine(
            module_class=MODULES[args.module],
            target=args.target,
            users=users,
            passwords=passwords,
            pairs=pairs,
            max_threads=args.threads,
            timeout=args.timeout,
            stop_on_success=args.stop_on_success,
            module_options=module_options,
            random_delay=args.random_delay,
            min_delay=args.min_delay,
            max_delay=args.max_delay,
            log_file=args.log_file,
            result_file=args.result_file,
        )
        results = engine.run()
        if results:
            print("\n[+] VALID CREDENTIALS:")
            for user, passwd in results:
                print(f"  {user}:{passwd}")
        else:
            print("\n[-] No valid credentials found.")
    except Exception as e:
        print(f"\n[!] FATAL: {e}\n", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
