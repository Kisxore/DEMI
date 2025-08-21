# DEMI - Distributed Exploitation and Multi-protocol Intelligence

A fast, multi-threaded credential brute force tool supporting multiple protocols including SSH, FTP, HTTP Basic Auth, and HTTP Form authentication.

## Features

- **Multi-protocol support**: SSH, FTP, HTTP Basic Auth, HTTP Form Auth
- **Multi-threaded**: Configurable number of worker threads for fast execution
- **Flexible authentication**: Support for username/password lists or pre-defined pairs
- **Smart detection**: Automatic success/failure detection with customizable regex patterns
- **Proxy support**: HTTP proxy support for web-based attacks
- **Robust error handling**: Handles network timeouts, connection errors gracefully
- **Detailed logging**: Progress tracking and detailed result reporting

## Installation

### Prerequisites

- Python 3.6 or higher
- pip package manager

### Install Dependencies

```bash
# Install required Python packages
pip install -r requirements.txt

# Or install individually:
pip install paramiko requests urllib3
```

### Directory Structure

Create the following directory structure:

```
demi/
├── cli.py                    # Main CLI entry point
├── demi/
│   ├── __init__.py          # Package initialization
│   ├── engine.py            # Core brute force engine
│   ├── utils.py             # Utility functions
│   └── modules/
│       ├── __init__.py      # Modules package init
│       ├── ssh.py           # SSH module
│       ├── ftp.py           # FTP module
│       ├── http_basic.py    # HTTP Basic Auth module
│       └── http_form.py     # HTTP Form Auth module
├── requirements.txt         # Python dependencies
├── setup.py                 # Package setup
└── README.md               # This file
```

### Make CLI Executable

```bash
chmod +x cli.py
```

## Usage

### Basic Usage

```bash
# SSH brute force
python cli.py -m ssh -t 192.168.1.100 -U userlist.txt -P passlist.txt

# FTP brute force
python cli.py -m ftp -t ftp.example.com -U users.txt -P passwords.txt --threads 8

# HTTP Basic Auth
python cli.py -m http-basic -t http://example.com/admin -U users.txt -P passwords.txt

# HTTP Form Auth
python cli.py -m http-form -t http://example.com/login \
  --user-field username --pass-field password \
  -U users.txt -P passwords.txt
```

### Using Credential Pairs

```bash
# Use a file with username:password pairs
python cli.py -m ssh -t 192.168.1.100 --pairs credentials.txt

# Example credentials.txt:
# admin:admin
# root:password
# user:123456
```

### Advanced Options

```bash
# Stop after first success
python cli.py -m ssh -t 192.168.1.100 -U users.txt -P passwords.txt -f

# Custom port and timeout
python cli.py -m ssh -t 192.168.1.100 --port 2222 --timeout 10 \
  -U users.txt -P passwords.txt

# HTTP Form with custom patterns
python cli.py -m http-form -t http://example.com/login \
  --user-field email --pass-field passwd \
  --success-re "dashboard" --fail-re "invalid.*credentials" \
  -U emails.txt -P passwords.txt

# Using HTTP proxy
python cli.py -m http-basic -t http://internal.company.com \
  --proxy http://127.0.0.1:8080 \
  -U users.txt -P passwords.txt
```

## Command Line Options

### Required Arguments
- `-m, --module`: Protocol module (ssh, ftp, http-basic, http-form)
- `-t, --target`: Target IP/hostname

### Authentication Options
- `-U, --userlist`: File containing usernames
- `-P, --passlist`: File containing passwords  
- `--pairs`: File containing username:password pairs

### Engine Options
- `--threads`: Number of worker threads (default: 4)
- `-f, --stop-on-success`: Stop after first valid credential

### Protocol Options
- `--port`: Target port (default varies by protocol)
- `--timeout`: Connection timeout in seconds (default: 5.0)

### HTTP-Specific Options
- `--path`: URL path (e.g., /admin, /login)
- `--user-field`: Username field name (for http-form)
- `--pass-field`: Password field name (for http-form)  
- `--method`: HTTP method GET/POST (default: POST)
- `--success-re`: Success detection regex
- `--fail-re`: Failure detection regex
- `--proxy`: HTTP proxy URL

## Creating Wordlists

### Username Lists (users.txt)
```
admin
administrator
root
user
guest
test
demo
```

### Password Lists (passwords.txt)
```
admin
password
123456
admin123
letmein
welcome
default
changeme
```

### Credential Pairs (pairs.txt)
```
admin:admin
root:password
user:user123
guest:guest
demo:demo
```

## Examples

### SSH Brute Force
```bash
# Basic SSH attack
python cli.py -m ssh -t 192.168.1.100 -U users.txt -P passwords.txt

# SSH with custom port
python cli.py -m ssh -t 192.168.1.100 --port 2222 -U users.txt -P passwords.txt
```

### FTP Brute Force
```bash
# FTP attack
python cli.py -m ftp -t ftp.example.com -U users.txt -P passwords.txt

# Test anonymous FTP access
echo "anonymous" > users.txt
echo "anonymous@example.com" > passwords.txt
python cli.py -m ftp -t ftp.example.com -U users.txt -P passwords.txt
```

### HTTP Basic Auth
```bash
# Basic auth on web directory
python cli.py -m http-basic -t http://example.com/admin -U users.txt -P passwords.txt

# Basic auth with custom path
python cli.py -m http-basic -t https://example.com --path /secure -U users.txt -P passwords.txt
```

### HTTP Form Auth
```bash
# Login form brute force
python cli.py -m http-form -t http://example.com/login \
  --user-field username --pass-field password \
  -U users.txt -P passwords.txt

# WordPress login
python cli.py -m http-form -t http://wordpress.com/wp-login.php \
  --user-field log --pass-field pwd \
  --success-re "dashboard" --fail-re "ERROR" \
  -U users.txt -P passwords.txt

# Custom form with additional data
python cli.py -m http-form -t http://example.com/login \
  --user-field email --pass-field passwd \
  --method POST \
  -U emails.txt -P passwords.txt
```

## Protocol-Specific Notes

### SSH Module
- Default port: 22
- Automatically handles SSH key negotiation
- Supports password authentication only
- Timeouts handle slow SSH handshakes

### FTP Module  
- Default port: 21
- Supports both active and passive mode
- Automatically detects anonymous access
- Handles FTP-specific error codes

### HTTP Basic Auth Module
- Supports both HTTP and HTTPS
- Automatically handles redirects
- Ignores SSL certificate errors
- Detects authentication realms

### HTTP Form Auth Module
- Supports GET and POST methods
- Automatic form field discovery
- Flexible success/failure detection
- Custom regex pattern support
- Handles JavaScript redirects

## Security Considerations

**IMPORTANT**: This tool is intended for:
- Authorized penetration testing
- Security assessments of your own systems
- Educational purposes

**DO NOT USE** for unauthorized access to systems you don't own. Unauthorized access to computer systems is illegal in most jurisdictions.

### Responsible Use
- Only test systems you own or have explicit permission to test
- Be mindful of rate limiting and system load
- Follow responsible disclosure for any vulnerabilities found
- Respect terms of service and legal boundaries

## Troubleshooting

### Common Issues

#### "Module not found" errors
```bash
# Make sure you're in the correct directory
cd /path/to/demi
python cli.py ...

# Or use absolute paths
python /path/to/demi/cli.py ...
```

#### Connection timeouts
```bash
# Increase timeout for slow connections
python cli.py -m ssh -t 192.168.1.100 --timeout 15 -U users.txt -P passwords.txt
```

#### Too many connection errors
```bash
# Reduce thread count to avoid overwhelming target
python cli.py -m ssh -t 192.168.1.100 --threads 2 -U users.txt -P passwords.txt
```

#### HTTP form not working
```bash
# Test form field discovery first
python -c "
from demi.modules.http_form import HTTPFormModule
module = HTTPFormModule(path='/login')
fields = module.discover_form_fields('http://example.com')
print('Discovered fields:', fields)
"
```

### Debug Mode
For debugging issues, you can modify the modules to enable verbose logging:

```python
# Add to any module for debugging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Tips

### Optimal Thread Count
- **SSH**: 4-8 threads (SSH handshakes are slow)
- **FTP**: 8-16 threads (faster than SSH)
- **HTTP**: 16-32 threads (fastest protocol)
- **Start low and increase** based on target response

### Network Considerations
- **Local networks**: Higher thread counts work well
- **Internet targets**: Use fewer threads to avoid triggering defenses
- **Proxied connections**: Reduce threads significantly

### Wordlist Optimization
- **Order by probability**: Most common credentials first
- **Use targeted lists**: Protocol-specific wordlists perform better
- **Remove duplicates**: Clean your wordlists for efficiency

## Development

### Adding New Modules

To add support for a new protocol:

1. Create a new module file in `demi/modules/`
2. Implement a class with a `login(target, username, password)` method
3. Add the module to `MODULES` dict in `cli.py`
4. Update `demi/modules/__init__.py`

Example module template:
```python
class NewProtocolModule:
    def __init__(self, port=1234, timeout=5, **kwargs):
        self.port = port
        self.timeout = timeout
    
    def login(self, target, username, password):
        """Return True if login successful, False otherwise"""
        # Your protocol implementation here
        pass
```

### Testing

Test individual modules:
```bash
# Test SSH module directly
python -m demi.modules.ssh 192.168.1.100 admin admin123

# Test HTTP Basic Auth
python -m demi.modules.http_basic http://example.com admin admin123

# Test HTTP Form
python -m demi.modules.http_form http://example.com username password admin admin123
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is provided for educational and authorized testing purposes only. Users are responsible for complying with applicable laws and regulations. The authors are not responsible for any misuse of this tool.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues, questions, or contributions:
- Check existing issues before creating new ones
- Provide detailed error messages and system information
- Include steps to reproduce problems

---

**Remember**: Always use this tool responsibly and only on systems you own or have explicit permission to test.
