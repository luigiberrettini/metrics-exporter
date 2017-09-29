#!/usr/bin/env python3

import asyncio

from configuration.settings import Settings
from metricsRedirector import MetricsRedirector

class Main:
    def export_metrics(self):
        redirector_factory = lambda x: MetricsRedirector(x)
        self.metrics_redirectors = list(map(redirector_factory, Settings().metrics_redirections))
        for redirector in self.metrics_redirectors:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(redirector.export())
            loop.close()



Main().export_metrics()