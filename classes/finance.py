# -*- encoding: utf-8 -*-

import json
from .helpers import *

from pathlib import Path
from classes.db import MongoDB


class Finance:
    def __init__(self, id_char, esiapp, esiclient):
        self.id_char = id_char
        self.esiapp = esiapp
        self.esiclient = esiclient
        self.db = MongoDB()

        # Generics
        self.file_wallet = './data/wallet.json'
        self.file_orders = './data/orders.json'

        # Scope links
        self.links = {
            'wallet': 'get_characters_character_id_wallet',
            'wallet_journal': 'get_characters_character_id_wallet_journal',
            'wallet_transactions': 'get_characters_character_id_wallet_transactions',
            'orders': 'get_characters_character_id_orders',
            'orders_history': 'get_characters_character_id_orders_history'
        }

        # Get total amount now in wallet
        self.wallet_total = self.get_data("wallet")

    def esiop_char(self, api):
        operation = self.esiapp.op[api](character_id=self.id_char)
        return self.esiclient.request(operation)

    def get_data(self, call_type):
        # Check if key correct
        if call_type in self.links.keys():
            link = self.links[call_type]
        else:
            raise KeyError

        # Store the 'data' key from response
        try:
            data = self.esiop_char(api=link).data
            headers = self.esiop_char(api=link).header
        except Exception as e:
            raise e

        if isinstance(data, float):
            # Assume Wallet total value
            return data
        else:
            results = []

            # Convert to dict
            for entry in data:
                if not isinstance(entry['date'], float):
                    entry['date'] = ts_to_unix(entry['date'].v.timetuple())

                results.append(entry)

            # self.write_wallet(results)

            return results, headers

    #
    # def get_wallet(self):
    #     return self.esiop_char('get_characters_character_id_wallet').data
    #
    # def get_wallet_journal(self):
    #     data = self.esiop_char('get_characters_character_id_wallet_journal').data
    #     results = {}
    #
    #     # Convert to dict
    #     for entry in data:
    #         unix_timestamp = ts_to_unix(entry['date'].v.timetuple())
    #         del entry['date']
    #         results[unix_timestamp] = dict(entry)
    #
    #     # self.write_wallet(results)
    #
    #     return results
    #
    # def get_wallet_transactions(self):
    #     data = self.esiop_char('get_characters_character_id_wallet_transactions').data
    #     results = {}
    #
    #     # Convert to dict
    #     for entry in data:
    #         unix_timestamp = ts_to_unix(entry['date'].v.timetuple())
    #         del entry['date']
    #         results[unix_timestamp] = dict(entry)
    #
    #     # self.write_wallet(results)
    #
    #     return results
    #
    # def get_orders(self):
    #     return self.esiop_char('get_characters_character_id_orders').data
    #
    # def get_orders_history(self):
    #     return self.esiop_char('get_characters_character_id_orders_history').data

    def read_json_data(self, file):
        if Path(file).is_file():
            try:
                with open(file, 'r') as fp:
                    return json.load(fp)
            except IOError as e:
                raise e

    def write_json_data(self, file, new_data):
        data = self.read_json_data(file)
        data.update(new_data)

        try:
            with open(file, 'w') as fp:
                json.dump(data, fp, sort_keys=True)
        except IOError as e:
            raise e

    def read_mongo_data(self, table):
        return self.db.get_table(table=table)

    def write_mongo_data(self, table, new_data, update=False):

        if not update:
        #     # data = self.read_mongo_data(db_name=db_name, db_table=db_table)
        #     # data += new_data
            self.db.insert_table(table=table, data=new_data, unique='date')#, unique=new_data.keys())
        else:
            self.db.update_table(table=table, data=new_data)
