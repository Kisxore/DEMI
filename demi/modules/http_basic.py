#!/usr/bin/env python3
"""
DEMI HTTP Basic Auth Module - HTTP Basic Authentication brute force module
Requires: pip install requests
"""

import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import urljoin
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class HTTPBasicModule:
    """HTTP Basic Authentication testing module"""
    
    def __init__(self, timeout=6.0, path=None, proxy=None, **kwargs):
        """
        Initialize HTTP Basic Auth module
        
        :param timeout: Request timeout in seconds
        :param path: URL path to test (e.g., '/admin', '/login')
        :param proxy: HTTP proxy URL (e.g., 'http://127.0.0.1:8080')
        """
        self.timeout = timeout
        self.path = path or "/"
        self.proxy = proxy
        
        # Setup proxies dict
        self.proxies = {"http": proxy, "https": proxy} if proxy else None
        
        # Create session for connection reuse
        self.session = requests.Session()
        self.session.verify = False  # Ignore SSL certificate errors
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def login(self, target, username, password):
        """
        Attempt HTTP Basic Auth login with given credentials
        
        :param target: target URL (e.g., 'http://example.com' or 'https://example.com')
        :param username: username to test
        :param password: password to test
        :return: True if authentication successful, False otherwise
        """
        try:
            # Ensure target starts with http:// or https://
            if not target.startswith(('http://', 'https://')):
                target = 'http://' + target
            
            # Build full URL
            url = urljoin(target.rstrip('/') + '/', self.path.lstrip('/'))
            
            # Make request with basic auth
            response = self.session.get(
                url,
                auth=HTTPBasicAuth(username, password),
                timeout=self.timeout,
                proxies=self.proxies,
                allow_redirects=False  # Don't follow redirects initially
            )
            
            # Check response status
            if response.status_code == 200:
                # Success - authenticated successfully
                return True
            elif response.status_code == 401:
                # Unauthorized - wrong credentials
                return False
            elif response.status_code == 403:
                # Forbidden - might be valid creds but access denied
                return True  # Consider this a successful auth
            elif response.status_code in [301, 302, 303, 307, 308]:
                # Redirect - might indicate successful auth
                # Follow the redirect and check again
                redirect_response = self.session.get(
                    url,
                    auth=HTTPBasicAuth(username, password),
                    timeout=self.timeout,
                    proxies=self.proxies,
                    allow_redirects=True
                )
                # If redirected to a different page and no 401, likely success
                return redirect_response.status_code != 401
            else:
                # Other status codes - inconclusive
                return False
                
        except requests.exceptions.Timeout:
            # Request timeout
            return False
        except requests.exceptions.ConnectionError:
            # Connection error (target unreachable, etc.)
            return False
        except requests.exceptions.RequestException:
            # Other request-related errors
            return False
        except Exception:
            # Catch-all for other errors
            return False

    def test_connectivity(self, target):
        """
        Test if target is reachable
        
        :param target: target URL
        :return: True if target is reachable, False otherwise
        """
        try:
            if not target.startswith(('http://', 'https://')):
                target = 'http://' + target
                
            url = urljoin(target.rstrip('/') + '/', self.path.lstrip('/'))
            
            response = self.session.head(
                url,
                timeout=self.timeout,
                proxies=self.proxies,
                allow_redirects=True
            )
            return True
        except:
            return False

    def requires_auth(self, target):
        """
        Check if target requires authentication
        
        :param target: target URL
        :return: True if authentication is required, False otherwise
        """
        try:
            if not target.startswith(('http://', 'https://')):
                target = 'http://' + target
                
            url = urljoin(target.rstrip('/') + '/', self.path.lstrip('/'))
            
            response = self.session.get(
                url,
                timeout=self.timeout,
                proxies=self.proxies,
                allow_redirects=False
            )
            
            # If we get 401 Unauthorized, auth is required
            return response.status_code == 401
        except:
            return False

    def get_auth_realm(self, target):
        """
        Get the authentication realm from WWW-Authenticate header
        
        :param target: target URL
        :return: realm string or None
        """
        try:
            if not target.startswith(('http://', 'https://')):
                target = 'http://' + target
                
            url = urljoin(target.rstrip('/') + '/', self.path.lstrip('/'))
            
            response = self.session.get(
                url,
                timeout=self.timeout,
                proxies=self.proxies,
                allow_redirects=False
            )
            
            if response.status_code == 401:
                auth_header = response.headers.get('WWW-Authenticate', '')
                if 'realm=' in auth_header:
                    realm_part = auth_header.split('realm=')[1]
                    realm = realm_part.split(',')[0].strip('"\'')
                    return realm
        except:
            pass
        return None

# Common HTTP Basic Auth usernames and passwords
COMMON_HTTP_USERS = [
    "admin", "administrator", "root", "user", "test", "guest",
    "demo", "service", "api", "web", "www", "default", "operator"
]

COMMON_HTTP_PASSWORDS = [
    "", "admin", "administrator", "password", "123456", "admin123",
    "root", "user", "test", "guest", "demo", "service", "api", 
    "web", "www", "default", "changeme", "letmein", "welcome"
]

if __name__ == "__main__":
    # Simple test
    import sys
    if len(sys.argv) < 2:
        print("Usage: python http_basic.py <target> [username] [password] [path]")
        sys.exit(1)
    
    target = sys.argv[1]
    username = sys.argv[2] if len(sys.argv) > 2 else "admin"
    password = sys.argv[3] if len(sys.argv) > 3 else "admin"
    path = sys.argv[4] if len(sys.argv) > 4 else "/"
    
    module = HTTPBasicModule(path=path)
    print(f"Testing HTTP Basic Auth on {target}{path}")
    
    if module.test_connectivity(target):
        print("[+] Target is reachable")
        
        if module.requires_auth(target):
            print("[+] Target requires authentication")
            realm = module.get_auth_realm(target)
            if realm:
                print(f"[*] Auth Realm: {realm}")
        else:
            print("[-] Target does not require authentication")
            sys.exit(1)
    else:
        print("[-] Target is not reachable")
        sys.exit(1)
    
    print(f"Testing login: {username}:{password}")
    result = module.login(target, username, password)
    if result:
        print("[+] Authentication successful!")
    else:
        print("[-] Authentication failed")
