#!/usr/bin/env python3

"""
DEMI Async HTTP Form Auth Module
Requires: pip install aiohttp
"""

import aiohttp
import asyncio
from urllib.parse import urljoin

class HTTPAsyncFormModule:
    def __init__(self, method='POST', path='/login', user_field='username', pass_field='password', 
                 headers=None, data_overrides=None, proxy=None, timeout=5.0, **kwargs):
        self.method = method.upper()
        self.path = path
        self.user_field = user_field
        self.pass_field = pass_field
        self.headers = headers or {}
        self.data_overrides = data_overrides or {}
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.proxy = proxy

    async def login(self, target, username, password):
        url = target if target.startswith(('http://', 'https://')) else 'http://' + target
        url = urljoin(url.rstrip('/') + '/', self.path.lstrip('/'))
        data = self.data_overrides.copy()
        data[self.user_field] = username
        data[self.pass_field] = password
        connector = aiohttp.TCPConnector(ssl=False)
        try:
            async with aiohttp.ClientSession(timeout=self.timeout, headers=self.headers, connector=connector) as session:
                if self.method == 'GET':
                    session_func = session.get
                    kwargs = {'params': data}
                else:
                    session_func = session.post
                    kwargs = {'data': data}
                async with session_func(url, proxy=self.proxy, **kwargs) as resp:
                    return resp.status in (200, 302, 303, 307, 308)
        except Exception:
            return False

if __name__ == "__main__":
    async def test():
        module = HTTPAsyncFormModule(
            user_field='username', pass_field='password',
            headers={'User-Agent': 'DEMI ASync'}
        )
        result = await module.login('http://example.com/login', 'admin', 'admin')
        print(f"Result: {result}")
    asyncio.run(test())
