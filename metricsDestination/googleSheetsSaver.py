#!/usr/bin/env python3

import logging
import re
import tzlocal

from datetime import datetime

from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http
from apiclient import discovery

from metricsSource.graphiteMetric import GraphiteMetric
from utils import date_parse_lambda_factory

class GoogleSheetsSaver:
    row_numeric_label_reg_ex = re.compile(r'^[1-9]\d*$')
    col_alpha_label_reg_ex = re.compile(r'^[A-Za-z]+$')
    google_api_scope = ['https://www.googleapis.com/auth/spreadsheets']

    def __init__(self, settings):
        self.logger = logging.getLogger(__name__)
        self.credentials = settings['credentials']
        self.spreadsheet_id = settings['spreadsheet_id']
        self.worksheet_name = settings['worksheet_name']
        self.initial_row_lookup = settings['initial_row_lookup']
        self.initial_column_lookup = settings['initial_column_lookup']
        self.write_dimension = settings['write_dimension'].upper()
        self.parse_date = date_parse_lambda_factory()

    def save(self, metrics):
        self._init_gspred_client()
        find_row = self._find_lambda_factory(self.initial_row_lookup)
        find_col = self._find_lambda_factory(self.initial_column_lookup)
        for metric in metrics:
            self._save_single_metric(metric, find_row, find_col)

    def _init_gspred_client(self):
        try:
            credentials = ServiceAccountCredentials.from_json_keyfile_dict(self.credentials, self.google_api_scope)
            #delegated_credentials = credentials.create_delegated(self.credentials['email_for_impersonation'])
            #self.gspread_client = discovery.build('sheets', 'v4', http = delegated_credentials.authorize(Http()))
            self.gspread_client = discovery.build('sheets', 'v4', http = credentials.authorize(Http()))
        except Exception as exception:
            self.logger.error('Google API authentication error: {}'.format(exception))
            raise exception

    def _find_lambda_factory(self, lookup_settings):
        method_name = '_{:s}_{:s}_finder'.format(lookup_settings['mode'], lookup_settings['type'])
        lookup_context = '{:s}!{:s}'.format(self.worksheet_name, lookup_settings['context'])
        lookup_dimension = lookup_settings['dimension'].upper()
        lookup_value = lookup_settings['value']
        return lambda x: getattr(self, method_name)(lookup_context, lookup_dimension, lookup_value if lookup_value else x)

    def _header_constant_finder(self, lookup_context, lookup_dimension, lookup_value):
        return self._a1_to_number(lookup_value)

    def _a1_to_number(self, coordinate):
        if row_numeric_label_reg_ex.match(coordinate):
            return int(coordinate)
        if col_alpha_label_reg_ex.match(coordinate):
            col = 0
            for i, c in enumerate(reversed(column_label)):
                col += (ord(c) - 64) * (26 ** i)
            return col
        raise ValueError('Wrong coordinate format: {} '.format(coordinate))

    def _contents_constant_finder(self, lookup_context, lookup_dimension, lookup_value):
        return self._find_initial_row_or_col(lookup_context, lookup_dimension, lookup_value)

    def _contents_metric_finder(self, lookup_context, lookup_dimension, lookup_value):
        return self._find_initial_row_or_col(lookup_context, lookup_dimension, lookup_value)

    def _contents_date_finder(self, lookup_context, lookup_dimension, lookup_value):
        adapted_lookup_value = self._to_spreadsheet_datetime(self.parse_date(lookup_value))
        return self._find_initial_row_or_col(lookup_context, lookup_dimension, adapted_lookup_value)

    def _to_spreadsheet_datetime(self, original_datetime):
        delta = original_datetime - datetime(1899, 12, 30, tzinfo = tzlocal.get_localzone())
        return float(delta.days) + (float(delta.seconds) / 86400)

    def _find_initial_row_or_col(self, lookup_context, lookup_dimension, lookup_value):
        values = self._get_values(lookup_context, lookup_dimension)
        index = self._index_in_list(lookup_value, values)
        return index

    def _get_values(self, a1_coordinates, major_dimension):
        values_resource = self.gspread_client.spreadsheets().values()
        get_operation = values_resource.get(
            spreadsheetId = self.spreadsheet_id,
            range = a1_coordinates,
            majorDimension = major_dimension,
            valueRenderOption = 'UNFORMATTED_VALUE')
        response = get_operation.execute()
        return response.get('values', [])[0]

    def _index_in_list(self, lookup_value, items):
        for index, item in enumerate(items):
            if item == lookup_value:
                return index + 1
        raise LookupError("Value '{}' not found".format(lookup_value))

    def _save_single_metric(self, metric, find_row, find_col):
        try:
            row = find_row(metric.name)
            col = find_col(metric.name)
            a1_coordinates = self._numbers_to_a1(row, col)
            self._write_values(a1_coordinates, metric.values)
        except Exception as exception:
            self.logger.error('{}\r\n\tMetric to save: {:s}'.format(exception, metric.name))

    def _numbers_to_a1(self, row, col):
        quotient = col
        col_label = ''
        while quotient:
            (quotient, remainder) = divmod(quotient, 26)
            if remainder == 0:
                remainder = 26
                quotient -= 1
            col_label = chr(remainder + 64) + col_label
        return '{:s}!{:s}{:d}'.format(self.worksheet_name, col_label, row)

    def _write_values(self, a1_coordinates, values):
        value_range = {
            "range": a1_coordinates,
            "majorDimension": self.write_dimension,
            "values": [ values ],
        }
        values_resource = self.gspread_client.spreadsheets().values()
        get_operation = values_resource.update(
            spreadsheetId = self.spreadsheet_id,
            range = a1_coordinates,
            valueInputOption = 'RAW',
            body = value_range)
        response = get_operation.execute()