# -*- encoding: utf-8 -*-

import json
import os
import threading
from multiprocessing.dummy import Pool as ThreadPool
from .helpers import *
from .static import Search

from pathlib import Path
# from classes.db import MongoDB


class Markets:
    def __init__(self, esiapp, esiclient):
        self.esiapp = esiapp
        self.esiclient = esiclient
        self.search = Search(self.esiapp, self.esiclient)
        self.max_threads = os.cpu_count()
        self.lock = threading.Lock()
        # self.db = MongoDB()

        # Generics
        self.region_theforge = 10000002
        self.region_domain = 10000043
        self.station_jita = 60003760
        self.station_amarr = 60008494

        # Debug
        self.remaining = 0

        # Market data results
        self.market_jita = []
        self.market_amarr = []

        # Scope links
        self.links = {
            'history': 'get_markets_region_id_history',
            'types': 'get_markets_region_id_types',
            'orders': 'get_markets_region_id_orders'
        }

    def get_region(self, api, region_id, order_type):  # region_id defaults to The Forge
        # region_market = []

        op = self.esiapp.op[api](region_id=region_id, order_type=order_type, page=1)
        # pages = self.esiclient.request(operation).header['x-pages'][0]
        res = self.esiclient.head(op)

        if res.staus == 200:
            pages = res.header['X-Pages']

            operations = []
            for page in range(1, pages+1):
                operations.append(
                    self.esiapp.op[api](region_id=region_id, order_type=order_type, page=page)
                )

            res = self.esiclient.multi_request(
                reqs_and_resps=operations,
                thread=100  # default 20
            )

            # flatten the list:
            # region_market = [item for sublist in region_market for item in sublist]

            return res.data

    def get_data(self, call_type, region_id, order_type):
        link = self._validate_call_type(call_type)

        # Store the 'data' key from response
        try:
            data = self.get_region(api=link, region_id=region_id, order_type=order_type)
        except Exception as e:
            raise e

        results = []

        # Convert to dict
        for entry in data:
            # Drop unwanted keys
            entry.pop('issued', None)
            # entry.pop('duration', None)
            # entry.pop('range', None)
            # entry.pop('volume_total', None)
            # entry.pop('min_volume', None)
            # entry.pop('system_id', None)

            # Correct wording: volume to quantity
            entry['quantity_remaining'] = entry['volume_remain']
            entry.pop('volume_remain', None)

            # Filter by buy/sell and add to results
            results.append(entry)

        # Temporary call; remove later
        # self.write_json_data(file='./data/%s.json' % region_id, data=results)

        return results

    # Compare Jita-Amar:
    def get_space_rich(self):
        # Profit
        results = []
        POOL = ThreadPool(self.max_threads)

        ############## Buy in Jita - Sell in Amarr ##############
        # Get station orders
        jita = self.get_orders_jita(order_type='sell')
        amarr = self.get_orders_amarr(order_type='buy')
        # DEBUG ONLY
        # jita = self.read_json_data('./data/getrich_jita_buy.json')
        # amarr = self.read_json_data('./data/getrich_amarr_sell.json')

        # Get common types:
        types_jita = set([e['type_id'] for e in jita['sell']])
        types_amarr = set([e['type_id'] for e in amarr['buy']])
        types_common = list(types_jita.intersection(types_amarr))

        # Get top 10 items to trade
        def thread(type_id):
            # print('[+] Type: %s (%s/%s)' % (type_id, types_common.index(type_id), len(types_common)))

            # Get type info
            # type_info = self.search.get_type_info(type_id=type_id)

            orders_jita = [e for e in jita['sell'] if e['type_id'] == type_id]
            orders_amarr = [e for e in amarr['buy'] if e['type_id'] == type_id]

            jita_sell = sorted(orders_jita, key=lambda k: k['price'])[0]
            amarr_buy = sorted(orders_amarr, key=lambda k: k['price'], reverse=True)[0]

            if amarr_buy['price'] > jita_sell['price']:
                order_tradable = min(jita_sell['quantity_remaining'], amarr_buy['quantity_remaining'])
                order_profit = (amarr_buy['price'] - jita_sell['price']) * order_tradable

                self.lock.acquire()
                results.append({
                    # 'info': type_info,
                    'profit': order_profit,
                    'quantity': order_tradable,
                    'type_id': type_id
                })
                self.lock.release()

        POOL.map(thread, types_common)
        POOL.close()
        POOL.join()

        # for type_id in types_common:
        #     print('[+] Type: %s (%s/%s)' % (type_id, types_common.index(type_id), len(types_common)))
        #
        #     # Get type info
        #     type_info = self.search.get_type_info(type_id=type_id)
        #
        #     orders_jita = [e for e in jita['sell'] if e['type_id'] == type_id]
        #     orders_amarr = [e for e in amarr['buy'] if e['type_id'] == type_id]
        #
        #     jita_sell = sorted(orders_jita, key=lambda k: k['price'])[0]
        #     amarr_buy = sorted(orders_amarr, key=lambda k: k['price'], reverse=True)[0]
        #
        #     order_tradable = min(jita_sell['quantity_remaining'], amarr_buy['quantity_remaining'])
        #     order_profit = (jita_sell['price'] - amarr_buy['price']) * order_tradable
        #
        #     results.append({
        #         'info': type_info,
        #         'profit': order_profit,
        #         'quantity': order_tradable,
        #         'type_id': type_id
        #     })

        #
        #
        # for type_id in types_common:
        #     # Used numbers
        #     total_profit = .0
        #     total_price_buy = .0
        #     total_price_sell = .0
        #     total_quantity = .0
        #     # total_volume = .0  # Need to calculate this at some point
        #
        #     # Get the lowest selling price of type in Jita
        #     jita_buy = [e for e in jita['sell'] if e['type_id'] == type_id]
        #     jita_tradable = sum([e['quantity_remaining'] for e in jita_buy])
        #     jita_buy = sorted(jita_buy, key=lambda k: k['price'])
        #
        #     # Get the highest buying price in Amarr
        #     amarr_sell = [e for e in amarr['buy'] if e['type_id'] == type_id]
        #     amarr_tradable = sum([e['quantity_remaining'] for e in amarr_sell])
        #     amarr_sell = sorted(amarr_sell, key=lambda k: k['price'], reverse=True)
        #
        #     max_orders = min(len(jita_buy), len(amarr_sell))
        #     tradable_quantity = float(min(jita_tradable, amarr_tradable))
        #
        #     if total_quantity <= tradable_quantity:
        #         for i in range(len(jita_buy)):
        #
        #             # Only consider prices that provide a profit margin
        #             # TODO: Integrate broker fees and other taxes
        #             if jita_buy[i]['price'] < amarr_sell[i]['price']:
        #
        #                 total_quantity += jita_buy[i]['quantity_remaining']
        #
        #                 price_buy = jita_buy[i]['price'] * jita_buy[i]['quantity_remaining']
        #                 total_price_buy += total_price_buy
        #
        #                 price_sell = amarr_sell[i]['price'] * amarr_sell[i]['quantity_remaining']
        #                 total_price_sell += total_price_sell
        #
        #                 profit = price_sell - price_buy
        #
        #                 # total_volume +=
        #                 total_profit += profit
        #
        #             else:
        #                 break
        #
        #         results.append({
        #             'type_id': type_id,
        #             'profit': total_profit,
        #             'quantity': total_quantity,
        #             # 'volume': total_volume
        #         })

        results = sorted(results, key=lambda k: k['profit'], reverse=True)
        print(results[:9])
        # Get top

        ############## Buy in Amarr - Sell in Jita ##############
        for order in amarr['sell']:
            pass

    def get_orders_jita(self, order_type):
        results = {
            'buy': [],
            'sell': []
        }

        # Get all region data
        self.market_jita = self.get_data(call_type='orders', region_id=self.region_theforge, order_type=order_type)

        for order in self.market_jita:
            if order['location_id'] == self.station_jita:
                if order['is_buy_order']:
                    results['buy'].append(order)
                else:
                    results['sell'].append(order)

        return results

    def get_orders_amarr(self, order_type):
        results = {
            'buy': [],
            'sell': []
        }

        self.market_amarr = self.get_data(call_type='orders', region_id=self.region_domain, order_type=order_type)

        for order in self.market_amarr:
            if order['location_id'] == self.station_amarr:
                if order['is_buy_order']:
                    results['buy'].append(order)
                else:
                    results['sell'].append(order)

        return results

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

    # def read_mongo_data(self, table):
    #     return self.db.get_table(table=table)
    #
    # def write_mongo_data(self, table, new_data, update=False):
    #     if not update:
    #         #     # data = self.read_mongo_data(db_name=db_name, db_table=db_table)
    #         #     # data += new_data
    #         self.db.insert_table(table=table, data=new_data, unique='date')  # , unique=new_data.keys())
    #     else:
    #         self.db.update_table(table=table, data=new_data)

    def _validate_call_type(self, call_type):
        # Check if key correct
        if call_type in self.links.keys():
            link = self.links[call_type]
        else:
            raise KeyError
        return link
