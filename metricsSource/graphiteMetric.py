#!/usr/bin/env python3

class GraphiteMetric:
    def __init__(self, name, url, value = 0):
        self.name = name
        self.url = url
        self.value = value

    @property
    def name(self):
        return ''

    @property
    def url(self):
        return ''

    @property
    def value(self):
        return 0