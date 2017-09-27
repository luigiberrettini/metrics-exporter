#!/usr/bin/env python3

#MetricExporter(self.settings.metrics_load_info, metric_source, metric_destination)
# => metrics = metric_source.load(metrics_load_info)
#    creates specialized GraphiteMetric objects with name, url, value
# => metric_destination.save(metrics)
#    saves metrics using name and value

class MetricsRedirector:
    def __init__(self, metrics_load_info, metric_source, metric_destination):
        pass

    async def export(self):
        pass