#!/usr/bin/env python3
"""
DEMI HTTP Form Module - HTTP Form-based authentication brute force module
Requires: pip install requests
"""

import requests
import re
from urllib.parse import urljoin
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class HTTPFormModule:
    """HTTP Form-based authentication testing module"""
    
    def __init__(self, timeout=6.0, method="POST", path=None, user_field=None, 
                 pass_field=None, headers=None, data_overrides=None,
                 success_re=None, fail_re=None, proxy=None, **kwargs):
        """
        Initialize HTTP Form Auth module
        
        :param timeout: Request timeout in seconds
        :param method: HTTP method (GET or POST)
        :param path: URL path to test (e.g., '/login', '/admin/login')
        :param user_field: Name of the username field in the form
        :param pass_field: Name of the password field in the form
        :param headers: Additional HTTP headers as dict
        :param data_overrides: Additional form data as dict
        :param success_re: Regex pattern indicating successful login
        :param fail_re: Regex pattern indicating failed login
        :param proxy: HTTP proxy URL (e.g., 'http://127.0.0.1:8080')
        """
        self.timeout = timeout
        self.method = method.upper()
        self.path = path or "/login"
        self.user_field = user_field
        self.pass_field = pass_field
        self.headers = headers or {}
        self.data_overrides = data_overrides or {}
        self.proxy = proxy
        
        # Compile regex patterns
        self.success_re = self._compile_regex(success_re) if success_re else None
        self.fail_re = self._compile_regex(fail_re) if fail_re else None
        
        # Setup proxies dict
        self.proxies = {"http": proxy, "https": proxy} if proxy else None
        
        # Create session for connection reuse
        self.session = requests.Session()
        self.session.verify = False  # Ignore SSL certificate errors
        
        # Set default headers
        default_headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        default_headers.update(self.headers)
        self.session.headers.update(default_headers)

    def _compile_regex(self, pattern):
        """Compile regex pattern safely"""
        try:
            return re.compile(pattern, re.IGNORECASE | re.MULTILINE)
        except re.error:
            return None

    def login(self, target, username, password):
        """
        Attempt HTTP form login with given credentials
        
        :param target: target URL (e.g., 'http://example.com' or 'https://example.com')
        :param username: username to test
        :param password: password to test
        :return: True if authentication successful, False if failed, None if inconclusive
        """
        if not self.user_field or not self.pass_field:
            raise ValueError("HTTP form module requires user_field and pass_field to be set")
        
        try:
            # Ensure target starts with http:// or https://
            if not target.startswith(('http://', 'https://')):
                target = 'http://' + target
            
            # Build full URL
            url = urljoin(target.rstrip('/') + '/', self.path.lstrip('/'))
            
            # Prepare form data
            data = self.data_overrides.copy()
            data[self.user_field] = username
            data[self.pass_field] = password
            
            # Make the request
            if self.method == "GET":
                response = self.session.get(
                    url,
                    params=data,
                    timeout=self.timeout,
                    proxies=self.proxies,
                    allow_redirects=True
                )
            else:  # POST
                response = self.session.post(
                    url,
                    data=data,
                    timeout=self.timeout,
                    proxies=self.proxies,
                    allow_redirects=True
                )
            
            # Get response body
            body = response.text or ""
            
            # Check for explicit failure patterns first
            if self.fail_re and self.fail_re.search(body):
                return False
            
            # Check for explicit success patterns
            if self.success_re and self.success_re.search(body):
                return True
            
            # Fallback heuristics if no explicit patterns are set
            return self._analyze_response(response, body, url)
            
        except requests.exceptions.Timeout:
            return False
        except requests.exceptions.ConnectionError:
            return False
        except requests.exceptions.RequestException:
            return False
        except Exception:
            return False

    def _analyze_response(self, response, body, original_url):
        """
        Analyze response to determine if login was successful
        Uses various heuristics when explicit success/fail patterns aren't provided
        """
        # Check status codes
        if response.status_code in [401, 403]:
            return False
        
        # Check if we were redirected away from login page
        current_url = response.url
        if response.history and current_url != original_url:
            # We were redirected - this often indicates success
            # Check common redirect destinations that indicate success
            success_paths = ['/dashboard', '/admin', '/home', '/index', '/welcome', '/main']
            for path in success_paths:
                if path in current_url.lower():
                    return True
            
            # If redirected but not to an obvious failure page, assume success
            failure_paths = ['/login', '/signin', '/auth', '/error']
            for path in failure_paths:
                if path in current_url.lower():
                    return False
            
            # Generic redirect away from login page - likely success
            return True
        
        # Check for common success indicators in response body
        success_indicators = [
            r'welcome\s+(?:back\s+)?(?:to\s+)?',
            r'dashboard',
            r'logout',
            r'sign\s*out',
            r'profile',
            r'settings',
            r'administration',
            r'successfully\s+(?:logged\s+in|authenticated)',
            r'login\s+successful'
        ]
        
        for pattern in success_indicators:
            if re.search(pattern, body, re.IGNORECASE):
                return True
        
        # Check for common failure indicators
        failure_indicators = [
            r'invalid\s+(?:username|password|credentials|login)',
            r'(?:username|password)\s+(?:is\s+)?(?:incorrect|wrong|invalid)',
            r'authentication\s+failed',
            r'login\s+failed',
            r'access\s+denied',
            r'bad\s+(?:username|password|credentials)',
            r'try\s+again',
            r'error.*(?:username|password|login|authentication)',
            r'please\s+check\s+your\s+(?:username|password|credentials)'
        ]
        
        for pattern in failure_indicators:
            if re.search(pattern, body, re.IGNORECASE):
                return False
        
        # Check for presence of login form (indicates failure)
        login_form_indicators = [
            r'<input[^>]*(?:type=["\']password["\']|name=["\'](?:pass|password)["\'])',
            r'<form[^>]*(?:login|signin|auth)',
            r'type=["\']password["\']',
            r'name=["\'](?:username|user|login|email)["\']'
        ]
        
        for pattern in login_form_indicators:
            if re.search(pattern, body, re.IGNORECASE):
                return False
        
        # If we can't determine, return None (inconclusive)
        return None

    def test_connectivity(self, target):
        """Test if target is reachable"""
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

    def discover_form_fields(self, target):
        """
        Attempt to discover form field names by analyzing the login page
        
        :param target: target URL
        :return: dict with discovered field names or None
        """
        try:
            if not target.startswith(('http://', 'https://')):
                target = 'http://' + target
                
            url = urljoin(target.rstrip('/') + '/', self.path.lstrip('/'))
            
            response = self.session.get(
                url,
                timeout=self.timeout,
                proxies=self.proxies,
                allow_redirects=True
            )
            
            body = response.text or ""
            
            # Look for common username field patterns
            username_patterns = [
                r'<input[^>]*name=["\']([^"\']*(?:user|login|email|account)[^"\']*)["\'][^>]*>',
                r'<input[^>]*name=["\']([^"\']*)["\'][^>]*type=["\'](?:text|email)["\'][^>]*>',
            ]
            
            # Look for password field patterns
            password_patterns = [
                r'<input[^>]*name=["\']([^"\']*(?:pass|pwd)[^"\']*)["\'][^>]*type=["\']password["\']',
                r'<input[^>]*type=["\']password["\'][^>]*name=["\']([^"\']*)["\']',
            ]
            
            username_field = None
            password_field = None
            
            for pattern in username_patterns:
                match = re.search(pattern, body, re.IGNORECASE)
                if match:
                    username_field = match.group(1)
                    break
            
            for pattern in password_patterns:
                match = re.search(pattern, body, re.IGNORECASE)
                if match:
                    password_field = match.group(1)
                    break
            
            if username_field and password_field:
                return {
                    'user_field': username_field,
                    'pass_field': password_field
                }
                
        except Exception:
            pass
        
        return None

# Common form field names
COMMON_USER_FIELDS = [
    "username", "user", "login", "email", "userid", "account", 
    "admin", "name", "usr", "loginname", "user_name"
]

COMMON_PASS_FIELDS = [
    "password", "pass", "passwd", "pwd", "secret", "key", 
    "passphrase", "admin_pass", "user_pass", "loginpass"
]

# Common success/failure patterns
COMMON_SUCCESS_PATTERNS = [
    r"welcome",
    r"dashboard",
    r"successfully logged in",
    r"authentication successful",
    r"login successful"
]

COMMON_FAILURE_PATTERNS = [
    r"invalid (?:username|password|credentials)",
    r"(?:username|password) (?:is )?(?:incorrect|wrong|invalid)",
    r"authentication failed",
    r"login failed",
    r"access denied",
    r"try again"
]

if __name__ == "__main__":
    # Simple test
    import sys
    if len(sys.argv) < 4:
        print("Usage: python http_form.py <target> <user_field> <pass_field> [username] [password] [path]")
        print("Example: python http_form.py http://example.com username password admin admin123 /login")
        sys.exit(1)
    
    target = sys.argv[1]
    user_field = sys.argv[2]
    pass_field = sys.argv[3]
    username = sys.argv[4] if len(sys.argv) > 4 else "admin"
    password = sys.argv[5] if len(sys.argv) > 5 else "admin"
    path = sys.argv[6] if len(sys.argv) > 6 else "/login"
    
    module = HTTPFormModule(
        path=path,
        user_field=user_field,
        pass_field=pass_field
    )
    
    print(f"Testing HTTP Form Auth on {target}{path}")
    print(f"Form fields: {user_field}={username}, {pass_field}={password}")
    
    if module.test_connectivity(target):
        print("[+] Target is reachable")
        
        # Try to discover form fields if not provided
        discovered = module.discover_form_fields(target)
        if discovered:
            print(f"[*] Discovered form fields: {discovered}")
    else:
        print("[-] Target is not reachable")
        sys.exit(1)
    
    result = module.login(target, username, password)
    if result is True:
        print("[+] Authentication successful!")
    elif result is False:
        print("[-] Authentication failed")
    else:
        print("[?] Authentication result inconclusive")
