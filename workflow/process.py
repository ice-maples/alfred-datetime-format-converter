# -*- coding: utf-8 -*-

import alfred
import calendar
from delorean import parse, epoch, Delorean
from tzlocal import get_localzone
from datetime import timedelta

tz = get_localzone().zone


def process(query_str):
    """ Entry point """
    value = parse_query_value(query_str)
    if value is not None:
        results = alfred_items_for_value(value)
        xml = alfred.xml(results)  # compiles the XML answer
        alfred.write(xml)  # writes the XML back to Alfred


def parse_query_value(query_str):
    """ Return value for the query string """
    try:
        query_str = str(query_str).strip('"\' ')
        if query_str == 'now':
            d = Delorean(timezone=tz)
        elif query_str.startswith('y'):
            d = Delorean(Delorean(timezone=tz).midnight)
            d -= timedelta(days=len(query_str))
        elif query_str.startswith('t'):
            d = Delorean(Delorean(timezone=tz).midnight)
            d += timedelta(days=len(query_str) - 1)
        else:
            # Parse datetime string or timestamp
            try:
                ts = float(query_str)
                if ts >= 1000000000000:
                    ts /= 1000
                d = epoch(float(ts))
                d.shift(tz)
            except ValueError:
                d = parse(str(query_str), tz, dayfirst=False)
    except (TypeError, ValueError):
        d = None
    return d


def alfred_items_for_value(value):
    """
    Given a delorean datetime object, return a list of
    alfred items for each of the results
    """

    index = 0
    results = []
    subtitle = tz + ' Timestamp'

    # First item as timestamp
    item_value = calendar.timegm(value.datetime.utctimetuple()) * 1000
    results.append(alfred.Item(
        title=str(item_value),
        subtitle=subtitle,
        attributes={
            'uid': alfred.uid(index),
            'arg': item_value,
        },
        icon='icon.png',
    ))
    index += 1

    # Various formats
    formats = [
        # 1937-01-01 12:00:27
        ("%Y-%m-%d %H:%M:%S", ''),
        # 19 May 2002 15:21:36
        ("%d %b %Y %H:%M:%S", ''),
        # Sun, 19 May 2002 15:21:36
        ("%a, %d %b %Y %H:%M:%S", ''),
        # 1937-01-01T12:00:27
        ("%Y-%m-%dT%H:%M:%S", ''),
        # 1996-12-19T16:39:57-0800
        ("%Y-%m-%dT%H:%M:%S%z", ''),
    ]
    for format, description in formats:
        item_value = value.datetime.strftime(format)
        results.append(alfred.Item(
            title=str(item_value),
            subtitle=description,
            attributes={
                'uid': alfred.uid(index),
                'arg': item_value,
            },
            icon='icon.png',
        ))
        index += 1

    return results


if __name__ == "__main__":
    try:
        query_str = alfred.args()[0]
    except IndexError:
        query_str = None
    process(query_str)
