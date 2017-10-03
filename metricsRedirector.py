#!/usr/bin/env python3

from metricsSource.graphiteLoader import GraphiteLoader
from metricsDestination.googleSheetsSaver import GoogleSheetsSaver

class MetricsRedirector:
    metrics_sources = {
        'graphite': (lambda settings: GraphiteLoader(settings))
    }

    metrics_destinations = {
        'googleSheets': (lambda settings: GoogleSheetsSaver(settings))
    }

    def __init__(self, settings):
        self.source = self._create(self.metrics_sources, settings['source'])
        self.destination = self._create(self.metrics_destinations, settings['destination'])

    @property
    def metrics_source(self):
        return self.source

    @property
    def metrics_destination(self):
        return self.destination

    async def export(self):
        metrics = [ metric async for metric in self.source.load() ]
        self.destination.save(metrics)

    def _create(self, dict, settings):
        return dict[settings['type']](settings)