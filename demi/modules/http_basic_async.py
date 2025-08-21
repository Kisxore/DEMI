#!/usr/bin/env python3

"""
DEMI Async HTTP Basic Auth Module
Requires: pip install aiohttp
"""

import aiohttp
import asyncio
from urllib.parse import urljoin

class HTTPAsyncBasicModule:
    def __init__(self, timeout=5.0, proxy=None, **kwargs):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.proxy = proxy

    async def login(self, target, username, password):
        url = target if target.startswith(('http://', 'https://')) else 'http://' + target
        url = urljoin(url.rstrip('/') + '/', '')  # Ensure trailing slash
        auth = aiohttp.BasicAuth(username, password)
        connector = aiohttp.TCPConnector(ssl=False)
        try:
            async with aiohttp.ClientSession(timeout=self.timeout, connector=connector) as session:
                async with session.get(url, auth=auth, proxy=self.proxy, allow_redirects=False) as resp:
                    if resp.status in (200, 302, 303, 307, 308):
                        return True
                    elif resp.status == 401:
                        return False
                    else:
                        return False
        except Exception:
            return False

if __name__ == "__main__":
    async def test():
        module = HTTPAsyncBasicModule()
        result = await module.login('http://example.com', 'admin', 'admin')
        print(f"Result: {result}")
    asyncio.run(test())
