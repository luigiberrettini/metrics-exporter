#!/usr/bin/env python3

from metricsSource.graphiteMetric import GraphiteMetric

class GraphiteLoader:
    def __init__(self, settings):
        pass

    def load(self):
        return GraphiteMetric()

#import aiohttp
#async def testAsync(self):
#    async with aiohttp.ClientSession() as session:
#        async with session.get(url) as resp:
#            contents = await resp.content.read()
#            decoded = contents.decode('UTF-8')
#            print(decoded.rstrip())