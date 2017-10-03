#!/usr/bin/env python3

import parsedatetime
import tzlocal

def date_parse_lambda_factory():
    calendar = parsedatetime.Calendar()
    local_timezone = tzlocal.get_localzone()
    return lambda date_string: calendar.parseDT(datetimeString = date_string, tzinfo = local_timezone)[0]