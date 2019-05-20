# -*- encoding: utf-8 -*-

import os
import threading
from multiprocessing.dummy import Pool as ThreadPool
from .helpers import *
from .static import Search

#


class Markets(ESIBase):
    def __init__(self, app, client):
        super().__init__(app, client)
        self.search = Search(app, client)
        self.max_threads = os.cpu_count()
        self.lock = threading.Lock()

        # Debug
        self.remaining = 0

        # Market data results
        self.market_jita = []
        self.market_amarr = []

    def get_space_rich(self):
        # Profit
        results = []
        pool = ThreadPool(self.max_threads)

        ############## Buy in Jita - Sell in Amarr ##############
        # Get station orders
        jita = self.get_orders_jita(order_type='sell')
        amarr = self.get_orders_amarr(order_type='buy')

        self.write_json_data(data=jita, file='./jita_sell.json')
        self.write_json_data(data=jita, file='./amarr_buy.json')

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

        pool.map(thread, types_common)
        pool.close()
        pool.join()

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
        self.market_jita = self.get_data(call_type='orders_region', region_id=self.region_theforge, order_type=order_type)

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

        self.market_amarr = self.get_data(call_type='orders_region', region_id=self.region_domain, order_type=order_type)

        for order in self.market_amarr:
            if order['location_id'] == self.station_amarr:
                if order['is_buy_order']:
                    results['buy'].append(order)
                else:
                    results['sell'].append(order)

        return results

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

    def get_region(self, api, region_id, order_type):  # region_id defaults to The Forge
        # region_market = []

        op = self.app.op[api](region_id=region_id, order_type=order_type)
        res = self.client.head(op)

        if res.status == 200:
            pages = res.header['x-pages'][0]

            operations = []
            for page in range(1, pages+1):
                operations.append(
                    self.app.op[api](region_id=region_id, order_type=order_type, page=page)
                )

            res = self.client.multi_request(
                reqs_and_resps=operations,
                thread=100  # default 20
            )

            # flatten the list:
            # region_market = [item for sublist in region_market for item in sublist]

            return res.data

