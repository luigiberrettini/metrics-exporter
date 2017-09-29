#!/usr/bin/env python3

import logging

from metricsSource.urlBuilder import UrlBuilder
from metricsSource.session import Session
from metricsSource.graphiteMetric import GraphiteMetric

class GraphiteLoader:
    def __init__(self, settings):
        self.logger = logging.getLogger(__name__)
        self.items_to_load = settings['items_to_load']
        url_builder = UrlBuilder(settings['server_url'])
        headers = { 'Accept': 'text/csv'}
        user = settings['user'] if 'user' in settings else None
        password_or_auth_token = settings['password_or_auth_token'] if 'password_or_auth_token' in settings else None
        verify_ssl_certs = settings['verify_ssl_certs'] if 'verify_ssl_certs' in settings else False
        self.session_factory = lambda: Session(url_builder, headers, user, password_or_auth_token, verify_ssl_certs)

    async def load(self):
        async with self.session_factory() as session:
            metrics = list(map(lambda item_to_load: GraphiteMetric(item_to_load, session), self.items_to_load))
            for metric in metrics:
                await metric.load()
                yield metric