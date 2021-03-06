#!/usr/bin/env python3

import aiohttp
import logging

from urllib.parse import quote

class Session:
    def __init__(self, url_builder, headers, user = None, password = None, verify_ssl_certs = True):
        self.logger = logging.getLogger(__name__)
        self.url_builder = url_builder
        self.headers = headers
        self.basic_auth_credentials = None if (user is None or password is None) else aiohttp.BasicAuth(login = user, password = password)
        self.verify_ssl_certs = verify_ssl_certs

    async def __aenter__(self):
        tcp_connector = None if self.verify_ssl_certs else aiohttp.TCPConnector(verify_ssl = False)
        self.session = aiohttp.ClientSession(auth = self.basic_auth_credentials, headers = self.headers, connector = tcp_connector)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    async def get_resource_at_once(self, resource):
        relative_url = self.url_builder.relative_url_from_resource(resource)
        absolute_url = self.url_builder.absolute_url_from_relative(relative_url)
        quoted_url = quote(absolute_url, safe = "%/:=&?~#+!$,;@()*[]")
        self.logger.debug('Getting resource at URL: {:s}'.format(absolute_url))
        async with self.session.get(quoted_url) as response:
            return await response.content.read()