#!/usr/bin/env python3
"""
DEMI SSH Module - SSH credential brute force module
Requires: pip install paramiko
"""

import paramiko
import socket
import time

class SSHModule:
    """SSH credential testing module"""
    
    def __init__(self, port=22, timeout=5, **kwargs):
        """
        Initialize SSH module
        
        :param port: SSH port (default: 22)
        :param timeout: Connection timeout in seconds
        """
        self.port = port
        self.timeout = timeout
        
        # Disable paramiko logging to reduce noise
        import logging
        logging.getLogger("paramiko").setLevel(logging.WARNING)

    def login(self, target, username, password):
        """
        Attempt SSH login with given credentials
        
        :param target: target hostname or IP
        :param username: username to test
        :param password: password to test
        :return: True if login successful, False otherwise
        """
        client = None
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Attempt connection
            client.connect(
                hostname=target,
                port=self.port,
                username=username,
                password=password,
                timeout=self.timeout,
                allow_agent=False,          # Don't use SSH agent
                look_for_keys=False,        # Don't look for SSH keys
                banner_timeout=30,          # Timeout for banner exchange
                auth_timeout=30,            # Timeout for authentication
                compress=False              # Disable compression
            )
            
            # If we get here, authentication succeeded
            return True
            
        except paramiko.AuthenticationException:
            # Authentication failed - this is expected for wrong credentials
            return False
            
        except paramiko.SSHException as e:
            # SSH-specific errors (protocol issues, etc.)
            if "Authentication failed" in str(e):
                return False
            # Other SSH errors might indicate connectivity issues
            return False
            
        except socket.timeout:
            # Connection timeout
            return False
            
        except socket.error as e:
            # Network errors (connection refused, host unreachable, etc.)
            return False
            
        except Exception as e:
            # Catch-all for other errors
            return False
            
        finally:
            # Always close the connection
            if client:
                try:
                    client.close()
                except:
                    pass

    def test_connectivity(self, target):
        """
        Test if target is reachable on the SSH port
        
        :param target: target hostname or IP
        :return: True if port is open, False otherwise
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((target, self.port))
            sock.close()
            return result == 0
        except Exception:
            return False

# Utility functions for SSH module
def get_ssh_banner(target, port=22, timeout=5):
    """
    Get SSH banner from target
    
    :param target: target hostname or IP
    :param port: SSH port
    :param timeout: connection timeout
    :return: SSH banner string or None
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((target, port))
        banner = sock.recv(1024).decode('utf-8').strip()
        sock.close()
        return banner
    except Exception:
        return None

if __name__ == "__main__":
    # Simple test
    import sys
    if len(sys.argv) != 4:
        print("Usage: python ssh.py <target> <username> <password>")
        sys.exit(1)
    
    target, username, password = sys.argv[1:4]
    
    module = SSHModule()
    print(f"Testing SSH login: {username}:{password}@{target}")
    
    if module.test_connectivity(target):
        print("[+] Target is reachable")
        banner = get_ssh_banner(target)
        if banner:
            print(f"[*] SSH Banner: {banner}")
    else:
        print("[-] Target is not reachable")
        sys.exit(1)
    
    result = module.login(target, username, password)
    if result:
        print("[+] Login successful!")
    else:
        print("[-] Login failed")
