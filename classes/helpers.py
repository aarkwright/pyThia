# -*- encoding: utf-8 -*-
from datetime import datetime
from time import mktime


def ts_to_unix(ts):
    return mktime(ts)

def ts_from_unix(ts):
    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')