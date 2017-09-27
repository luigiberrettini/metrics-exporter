#!/usr/bin/env python3

import asyncio

from configuration.settings import Settings
from metricsSource.graphiteLoader import GraphiteLoader
from metricsDestination.googleSheetsSaver import GoogleSheetsSaver
from metricsRedirector import MetricsRedirector

class Main:
    def __init__(self):
        settings = Settings()
        metrics_source = GraphiteLoader(settings)
        metrics_destination = GoogleSheetsSaver(settings)
        self.metrics_redirector = MetricsRedirector(settings.metrics_load_info, metrics_source, metrics_destination)

    def export_metrics(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.metrics_redirector.export())
        loop.close()



Main().export_metrics()