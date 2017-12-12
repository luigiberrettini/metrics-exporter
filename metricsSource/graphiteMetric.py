#!/usr/bin/env python3

import logging
import csv

class GraphiteMetric:
    def __init__(self, item_to_load, to_graphite_date, session):
        self.logger = logging.getLogger(__name__)
        self.metric_name = item_to_load['name']
        self.metric_target = item_to_load['target'].replace("{","{{").replace("}","}}")
        self.metric_values = []
        self.start_date = to_graphite_date(item_to_load['start_date'])
        self.end_date = to_graphite_date(item_to_load['end_date'])
        self.session = session

    @property
    def name(self):
        return self.metric_name

    @property
    def values(self):
        return self.metric_values

    async def load(self):
        url_template = "render?format=csv&from=00:00_{:s}&until=00:00_{:s}&target=alias({:s}, '{:s}')"
        metric_resource = url_template.format(self.start_date, self.end_date, self.metric_target, self.name)
        try:
            metric_contents = await self.session.get_resource_at_once(metric_resource)
            self._values_from_csv_contents(metric_contents)
        except Exception as exception:
            self.logger.error('{}\r\n\tMetric: {:s}\r\n\tResource: {:s}'.format(exception, self.metric_name, metric_resource))

    def _values_from_csv_contents(self, contents):
        self.metric_values = []
        for line in csv.reader(contents.decode('UTF-8').splitlines()):
            name, date, value = line
            if (value):
                self.metric_values.append(int(value))