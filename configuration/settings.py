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
        logging.config.dictConfig(self.settings_dict['logging'])

    @property
    def metrics_redirections(self):
        return self.settings_dict['metrics_redirections']

    def _load_from_file(self):
        settings_directory = path.dirname(path.realpath(__file__))
        settings_file = path.join(settings_directory, 'settings.json')
        with open(settings_file) as file_contents:
            return json.load(file_contents)