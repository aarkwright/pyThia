# -*- encoding: utf-8 -*-
import hashlib
import hmac
import json
from datetime import datetime
from time import mktime
from string import ascii_letters, digits
from random import SystemRandom
from pathlib import Path
from classes import config
# from classes.db import MongoDB


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


class ESIBase:
    def __init__(self, app, client):
        self.app = app
        self.client = client

        # Generics
        self.region_theforge = 10000002
        self.region_domain = 10000043
        self.station_jita = 60003760
        self.station_amarr = 60008494
        self.file_wallet = './data/wallet.json'
        self.file_orders = './data/orders.json'
        self.wars = './data/wars.json'

        self.links = {
            'history': 'get_markets_region_id_history',
            'orders_char': 'get_characters_character_id_orders',
            'orders_history': 'get_characters_character_id_orders_history',
            'orders_region': 'get_markets_region_id_orders',
            'types': 'get_markets_region_id_types',
            'wallet': 'get_characters_character_id_wallet',
            'wallet_journal': 'get_characters_character_id_wallet_journal',
            'wallet_transactions': 'get_characters_character_id_wallet_transactions',
            'war': 'get_war_war_id',
            'war_kills': 'wars_war_id_killmails',
            'wars': 'get_wars',
        }

    @staticmethod
    def read_json_data(file):
        if Path(file).is_file():
            try:
                with open(file, 'r') as fp:
                    return json.load(fp)
            except IOError as e:
                raise e

    @staticmethod
    def write_json_data(file, data):
        try:
            with open(file, 'w') as fp:
                json.dump(data, fp, sort_keys=True)
        except IOError as e:
            raise e

    def _validate_call_type(self, call_type):
        # Check if key correct
        if call_type in self.links.keys():
            link = self.links[call_type]
        else:
            raise KeyError
        return link
