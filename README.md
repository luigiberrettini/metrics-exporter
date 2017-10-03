# Metrics exporter

This software allows to load some metrics from a source and save them to a destination.

It currently supports only Graphite as a source (getting a CSV via a call to the Graphite API) and Google Sheets as a destination.

Google Sheets is accessed by means of Google APIs: follow the [http://developers.google.com/api-client-library/python/auth/service-accounts](OAuth 2.0 for Server to Server Applications guide) to retrieve your credentials.