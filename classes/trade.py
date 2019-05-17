# -*- encoding: utf-8 -*-

import json
from .helpers import *

from pathlib import Path
from classes.db import MongoDB


class Markets:
    def __init__(self, esiapp, esiclient):
        self.esiapp = esiapp
        self.esiclient = esiclient
        self.db = MongoDB()

        # Generics
        self.market = './data/market.json'
        self.region_theforge = 10000002 # Jita - station: 60003760
        self.region_domain = 10000043 # Amarr - station: 60008494

        # Scope links
        self.links = {
            'market_history': 'get_markets_region_id_history',
            'market_types': 'get_markets_region_id_types',
            'market_orders': 'get_markets_region_id_orders'
        }

        # Test
        # self.get_data('market_history')

    def esiop_char(self, api):
        operation = self.esiapp.op[api](character_id=self.id_char)
        return self.esiclient.request(operation)

    def get_region(self, api, region_id):  # region_id defaults to The Forge
        region_market = []
        operation = self.esiapp.op[api](region_id=region_id, page=1)
        pages = self.esiclient.request(operation).header['x-pages'][0]

        for i in range(1, int(pages)+1):
            print('page', i)
            op_types = self.esiapp.op[api](region_id=region_id, page=i)
            data = self.esiclient.request(op_types).data

            region_market.append(data)

        # flatten the list:
        region_market = [item for sublist in region_market for item in sublist]

        return region_market

    def get_data(self, call_type, region_id):
        # Check if key correct
        if call_type in self.links.keys():
            link = self.links[call_type]
        else:
            raise KeyError

        # Store the 'data' key from response
        try:
            data = self.get_region(api=link, region_id=region_id)
        except Exception as e:
            raise e

        if isinstance(data, float):
            # Assume Wallet total value
            return data
        else:
            results = []

            # Convert to dict
            for entry in data:
                if not isinstance(entry['issued'], float):
                    entry['date'] = ts_to_unix(entry['issued'].v.timetuple())

                results.append(entry)

            # self.write_wallet(results)

            return results

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
            self.db.insert_table(table=table, data=new_data, unique='date')  # , unique=new_data.keys())
        else:
            self.db.update_table(table=table, data=new_data)
