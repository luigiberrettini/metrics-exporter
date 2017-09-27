#!/usr/bin/env python3

import logging
import logging.config
import json
import tzlocal

from datetime import datetime, timedelta
from os import path

class Settings:
    def __init__(self):
        self.settings_dict = self._load_from_file()
        self._init_logging()
        self.metrics_load_information = self._metrics_load_info()

    @property
    def metrics_load_info(self):
        return self.metrics_load_information

    def _load_from_file(self):
        settings_directory = path.dirname(path.realpath(__file__))
        settings_file = path.join(settings_directory, 'settings.json')
        with open(settings_file) as file_contents:
            return json.load(file_contents)

    def _init_logging(self):
        logging.config.dictConfig(self.settings_dict['logging'])

    def _metrics_load_info(self):
        url_template = '{:s}/render/?format=csv&from=00:00_{:s}&until=00:00_{:s}&target=alias({:s},{:s})'
        base_url = self.settings_dict['base_url']
        beginning_of_today = datetime.now(tzlocal.get_localzone()).replace(hour = 0, minute = 0, second = 0, microsecond = 0)
        days_from_monday = beginning_of_today.isoweekday() - 1
        monday_of_past_week = beginning_of_today - timedelta(days = days_from_monday + 7)
        monday_of_current_week = beginning_of_today - timedelta(days = days_from_monday)
        start_date = monday_of_past_week.strftime('%Y%m%d')
        end_date = monday_of_current_week.strftime('%Y%m%d')
        url_factory = lambda name, lookup_value: url_template.format(base_url, start_date, end_date, name, lookup_value)
        return { name: url_factory(name, lookup_value) for name, lookup_value in self.settings_dict['metrics_load_info'].items() }