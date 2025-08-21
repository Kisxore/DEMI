# demi/utils.py
"""
DEMI Utility Functions
"""

import re
import os
import sys

def compile_regex(pattern):
    """
    Safely compile a regex pattern
    
    :param pattern: regex pattern string
    :return: compiled regex object or None if invalid
    """
    if not pattern:
        return None
    
    try:
        return re.compile(pattern, re.IGNORECASE | re.MULTILINE)
    except re.error as e:
        print(f"[-] Invalid regex pattern '{pattern}': {e}")
        return None

def read_wordlist(filepath):
    """
    Read a wordlist file and return list of entries
    
    :param filepath: path to wordlist file
    :return: list of strings
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    entries = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#'):  # Skip empty lines and comments
                    entries.append(line)
    except UnicodeDecodeError:
        # Try with different encoding
        with open(filepath, 'r', encoding='latin1') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    entries.append(line)
    
    return entries

def read_pairs(filepath):
    """
    Read a file with username:password pairs
    
    :param filepath: path to pairs file
    :return: list of (username, password) tuples
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    pairs = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#') and ':' in line:
                    username, password = line.split(':', 1)
                    pairs.append((username, password))
                elif line and not line.startswith('#'):
                    print(f"[-] Warning: Invalid format in pairs file line {line_num}: {line}")
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='latin1') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#') and ':' in line:
                    username, password = line.split(':', 1)
                    pairs.append((username, password))
    
    return pairs

def validate_target(target):
    """
    Validate target format
    
    :param target: target hostname or IP
    :return: True if valid, False otherwise
    """
    # Basic validation - could be enhanced
    if not target or len(target) < 1:
        return False
    
    # Remove protocol if present for validation
    clean_target = target
    if target.startswith(('http://', 'https://')):
        clean_target = target.split('://', 1)[1]
    
    # Check for valid characters
    if not re.match(r'^[a-zA-Z0-9.-]+(?::\d+)?$', clean_target.split('/')[0]):
        return False
    
    return True

def print_banner():
    """Print DEMI banner"""
    banner = """
    ╔══════════════════════════════════════╗
    ║              DEMI v1.0               ║
    ║  Distributed Exploitation and        ║
    ║    Multi-protocol Intelligence       ║
    ╚══════════════════════════════════════╝
    """
    print(banner)

def format_results(results, target, module):
    """
    Format and display results
    
    :param results: list of (username, password) tuples
    :param target: target that was tested
    :param module: module name that was used
    """
    if not results:
        print(f"\n[-] No valid credentials found for {target} ({module})")
        return
    
    print(f"\n[+] Found {len(results)} valid credential(s) for {target} ({module}):")
    print("=" * 50)
    
    for i, (username, password) in enumerate(results, 1):
        print(f"{i:2d}. {username}:{password}")
    
    print("=" * 50)

# Common wordlists for different protocols
DEFAULT_USERS = [
    "admin", "administrator", "root", "user", "test", "guest", 
    "demo", "service", "operator", "manager", "support", "web",
    "www", "ftp", "mail", "email", "db", "database", "backup"
]

DEFAULT_PASSWORDS = [
    "", "admin", "administrator", "password", "123456", "admin123",
    "root", "user", "test", "guest", "demo", "service", "default",
    "changeme", "letmein", "welcome", "qwerty", "abc123", "12345",
    "password123", "pass", "secret", "login", "god", "love"
]

# Protocol-specific defaults
SSH_USERS = DEFAULT_USERS + ["ubuntu", "centos", "debian", "pi", "oracle", "postgres"]
SSH_PASSWORDS = DEFAULT_PASSWORDS + ["raspberry", "ubuntu", "centos", "debian"]

FTP_USERS = DEFAULT_USERS + ["ftpuser", "anonymous", "upload", "download"]
FTP_PASSWORDS = DEFAULT_PASSWORDS + ["ftp", "ftpuser", "anonymous", "upload"]

HTTP_USERS = DEFAULT_USERS + ["webadmin", "httpd", "apache", "nginx", "tomcat"]
HTTP_PASSWORDS = DEFAULT_PASSWORDS + ["webadmin", "apache", "nginx", "tomcat"]
