#!/usr/bin/env python3

from utils import date_parse_lambda_factory
from metricsSource.urlBuilder import UrlBuilder
from metricsSource.session import Session
from metricsSource.graphiteMetric import GraphiteMetric

class GraphiteLoader:
    def __init__(self, settings):
        self.items_to_load = settings['items_to_load']
        url_builder = UrlBuilder(settings['server_url'])
        headers = { 'Accept': 'text/csv'}
        user = settings['user'] if 'user' in settings else None
        password_or_auth_token = settings['password_or_auth_token'] if 'password_or_auth_token' in settings else None
        verify_ssl_certs = settings['verify_ssl_certs'] if 'verify_ssl_certs' in settings else False
        self.session_factory = lambda: Session(url_builder, headers, user, password_or_auth_token, verify_ssl_certs)

    async def load(self):
        parse_date = date_parse_lambda_factory()
        to_graphite_date = lambda date_string: parse_date(date_string).strftime('%Y%m%d')
        async with self.session_factory() as session:
            metrics = list(map(lambda item_to_load: GraphiteMetric(item_to_load, to_graphite_date, session), self.items_to_load))
            for metric in metrics:
                await metric.load()
                if metric.values:
                    yield metric