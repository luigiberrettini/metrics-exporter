#!/usr/bin/env python3

import logging
import tzlocal
import parsedatetime
import csv

from datetime import datetime

class GraphiteMetric:
    def __init__(self, item_to_load, session):
        self.logger = logging.getLogger(__name__)
        self.item_to_load = item_to_load
        self.metric_name = self.item_to_load['name']
        self.metric_target = self.item_to_load['target']
        self.metric_values = []
        get_formatted_date = self._formatted_date_lambda()
        self.start_date = get_formatted_date('start_date')
        self.end_date = get_formatted_date('end_date')
        self.session = session

    @property
    def name(self):
        return self.metric_name

    @property
    def values(self):
        return self.metric_values

    async def load(self):
        url_template = 'render?format=csv&from=00:00_{:s}&until=00:00_{:s}&target=alias({:s},{:s})'
        metric_resource = url_template.format(self.start_date, self.end_date, self.name, self.metric_target)
        try:
            metric_contents = await self.session.get_resource_at_once(metric_resource)
            self._values_from_csv_contents(metric_contents)
        except Exception as err:
            self.logger.error('Error loading metric {:s} from resource'.format(self.metric_name, metric_resource))

    def _formatted_date_lambda(self):
        calendar = parsedatetime.Calendar()
        local_timezone = tzlocal.get_localzone()
        return lambda x: calendar.parseDT(datetimeString = self.item_to_load[x], tzinfo = local_timezone)[0].strftime('%Y%m%d')

    def _values_from_csv_contents(self, contents):
        self.metric_values = []
        for line in csv.reader(contents.decode('UTF-8').splitlines()):
            name, date, value = line
            if (value):
                self.metric_values.append(int(value))