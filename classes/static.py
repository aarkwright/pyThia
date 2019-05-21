# -*- encoding: utf-8 -*-
import json
from pathlib import Path
from classes.helpers import ESIBase


class Search(ESIBase):
    def __init__(self, app, client):
        super().__init__(app, client)

    def get_type_info(self, type_id):
        api = 'universe_types_type_id'

        operation = self.app.op[api](type_id=type_id)
        response = self.client.request(operation)

        # if 'x-pages' in response.header.keys():
        #     pages = response.header['x-pages'][0]
        #
        #     for i in range(1, int(pages) + 1):
        #         operation = self.esiapp.op[api](search=type_id, page=i)
        #         response = self.esiclient.request(operation)
        #         results.append(response.data)
        return response.data


class MarketGroups(ESIBase):
    def __init__(self, app, client):
        super().__init__(app, client)
        self.ids = list(self.get_groups())
        self.data = []
        self.parents = {}
        self.children = {}
        self.file = './data/market_groups.json'


        self.populate()
        self.write_json_data(self.file, self.data)

    def get_groups(self, ):
        api = 'markets_groups'

        op = self.app.op[api]()
        res = self.client.request(op)

        return res.data

    def get_group_info(self, market_group_id):
        api = 'markets_groups_market_group_id'

        op = self.app.op[api](market_group_id=market_group_id)
        res = self.client.request(op)

        return res.data

    def populate(self):
        for mg_id in self.ids:
            data = dict(self.get_group_info(market_group_id=mg_id))
            if 'parent_group_id' not in data.keys():
                # Consider parent
                data_id = data['market_group_id']
                del data['market_group_id']
                del data['description']
                data['types'] = {}
                self.parents[data_id] = data
            else:
                # Consider child
                data_id = data['market_group_id']
                del data['market_group_id']
                del data['description']
                # data['types'] = {}
                self.children[data_id] = data

        # for k, v in self.childrenitems():
        #     parent_id = v['parent_group_id']
        #     del v['parent_group_id']
        #     self.parents[parent_id]['types'][k] = v


class Regions(ESIBase):
    def __init__(self, app, client):
        super().__init__(app, client)

        # Generics
        self.file = './data/static_regions.json'

        # load the regions data
        if Path(self.file).is_file():
            self.data = self.get_regions(load=True)
        else:
            self.data = self.get_regions(save=True)

    def get_regions(self, load=False, save=False):
        op_regions = self.app.op['get_universe_regions']()
        region_ids = self.client.request(op_regions)

        # Get constellation info
        # Temporary stuff, will refactor to DB storage.
        if load and Path(self.file).is_file():
            # Get from JSON file
            with open(self.file, 'r') as fp:
                data = json.load(fp)

            return data

        if save:
            # regions_data = dict.fromkeys(list(region_ids.data), 0)
            data = {}

            # Save JSON to file
            for region_id in list(region_ids.data):
                op_regions_info = self.app.op['get_universe_regions_region_id'](region_id=region_id)
                region_info = self.client.request(op_regions_info)

                # Add the name key
                region_name = region_info.data['name']
                data[region_name] = {
                    'id': region_id,
                    'constellations': {},
                }

                for constell_id in list(region_info.data['constellations']):
                    op_constell_info = self.app.op['universe_constellations_constellation_id'](
                        constellation_id=constell_id)
                    constell_info = self.client.request(op_constell_info)

                    constell_name = constell_info.data['name']
                    print(region_name, constell_name)
                    data[region_name]['constellations'][constell_name] = {
                        'id': constell_id
                    }

            with open(self.file, 'w') as fp:
                json.dump(data, fp, sort_keys=True)

            return data


class TypeIds(ESIBase):
    def __init__(self, app, client):
        super().__init__(app, client)

        # Generics
        self.file = './data/static_types.json'

        # load the regions data
        if Path(self.file).is_file():
            self.data = self.get_types(load=True)
        else:
            self.data = self.get_types(save=True)

    def get_types(self, load=False, save=False):
        type_ids = []
        op_types = self.app.op['get_universe_types'](page=1)
        pages = self.client.request(op_types).header['x-pages'][0]

        for i in range(1, int(pages)+1):
            op_types = self.app.op['get_universe_types'](page=i)
            data = self.client.request(op_types).data

            type_ids.append(data)

        # flatten the list:
        type_ids = [item for sublist in type_ids for item in sublist]

        # Type info
        # Temporary stuff, will refactor to DB storage.
        if load and Path(self.file).is_file():
            # Get from JSON file
            with open(self.file, 'r') as fp:
                data = json.load(fp)

            return data

        if save:
            # regions_data = dict.fromkeys(list(region_ids.data), 0)
            data = {}

            # Save JSON to file
            for type_id in type_ids:
                print("%s/%s" % (type_ids.index(type_id), len(type_ids)))
                op_type_info = self.app.op['get_universe_types_type_id'](type_id=type_id)
                type_info = self.client.request(op_type_info)

                # Add the name key
                data[type_id] = dict(type_info.data)

            with open(self.file, 'w') as f:
                json.dump(data, f, sort_keys=True)
