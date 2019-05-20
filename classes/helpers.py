# -*- encoding: utf-8 -*-
import hashlib
import hmac
from datetime import datetime
from time import mktime
from string import ascii_letters, digits
from random import SystemRandom

from classes import config


def ts_to_unix(ts):
    return mktime(ts)


def ts_from_unix(ts):
    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')


def generate_state_token():
    """Generates a non-guessable OAuth token"""
    chars = (ascii_letters + digits)
    rand = SystemRandom()
    random_string = ''.join(rand.choice(chars) for _ in range(len(chars)))
    return hmac.new(
        config.SECRET_KEY.encode('utf-8'),
        random_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
