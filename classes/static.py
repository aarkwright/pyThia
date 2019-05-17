# -*- encoding: utf-8 -*-
import json
from pathlib import Path


class Regions:
    def __init__(self, esiapp, esiclient):
        self.esiapp = esiapp
        self.esiclient = esiclient

        # Generics
        self.file = './data/static_regions.json'

        # load the regions data
        if Path(self.file).is_file():
            self.data = self.get_regions(load=True)
        else:
            self.data = self.get_regions(save=True)

    def get_regions(self, load=False, save=False):
        op_regions = self.esiapp.op['get_universe_regions']()
        region_ids = self.esiclient.request(op_regions)

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
                op_regions_info = self.esiapp.op['get_universe_regions_region_id'](region_id=region_id)
                region_info = self.esiclient.request(op_regions_info)

                # Add the name key
                region_name = region_info.data['name']
                data[region_name] = {
                    'id': region_id,
                    'constellations': {},
                }

                for constell_id in list(region_info.data['constellations']):
                    op_constell_info = self.esiapp.op['universe_constellations_constellation_id'](
                        constellation_id=constell_id)
                    constell_info = self.esiclient.request(op_constell_info)

                    constell_name = constell_info.data['name']
                    print(region_name, constell_name)
                    data[region_name]['constellations'][constell_name] = {
                        'id': constell_id
                    }

            with open(self.file, 'w') as fp:
                json.dump(data, fp, sort_keys=True)

            return data


class TypeIds:
    def __init__(self, esiapp, esiclient):
        self.esiapp = esiapp
        self.esiclient = esiclient

        # Generics
        self.file = './data/static_types.json'

        # load the regions data
        if Path(self.file).is_file():
            self.data = self.get_types(load=True)
        else:
            self.data = self.get_types(save=True)

    def get_types(self, load=False, save=False):
        type_ids = []
        op_types = self.esiapp.op['get_universe_types'](page=1)
        pages = self.esiclient.request(op_types).header['x-pages'][0]

        for i in range(1, int(pages)+1):
            op_types = self.esiapp.op['get_universe_types'](page=i)
            data = self.esiclient.request(op_types).data

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
                op_type_info = self.esiapp.op['get_universe_types_type_id'](type_id=type_id)
                type_info = self.esiclient.request(op_type_info)

                # Add the name key
                data[type_id] = dict(type_info.data)

            with open(self.file, 'w') as fp:
                json.dump(data, fp, sort_keys=True)

            return data
