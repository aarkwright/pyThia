import json
from pathlib import Path


class Regions():
    def __init__(self, esiapp, esiclient):
        ### Get all regions
        self.op_regions = esiapp.op['get_universe_regions']()
        self.region_ids = esiclient.request(self.op_regions)
        self.esiapp = esiapp
        self.esiclient= esiclient

    def get_regions(self, file='./data_temp/regions.json', load=False, save=False):
        # Get constellation info
        # Temporary stuff, will refactor to DB storage.
        if load and Path(file).is_file():
            # Get from JSON file
            with open(file, 'r') as fp:
                data = json.load(fp)

            return data

        if save:
            # regions_data = dict.fromkeys(list(region_ids.data), 0)
            regions = {}

            # Save JSON to file
            for region_id in list(self.region_ids.data):
                op_regions_info = self.esiapp.op['get_universe_regions_region_id'](region_id=region_id)
                region_info = self.esiclient.request(op_regions_info)

                # Add the name key
                region_name = region_info.data['name']
                regions[region_name] = {
                    'id': region_id,
                    'constellations': {},
                }

                for constell_id in list(region_info.data['constellations']):
                    op_constell_info = self.esiapp.op['universe_constellations_constellation_id'](
                        constellation_id=constell_id)
                    constell_info = self.esiclient.request(op_constell_info)

                    constell_name = constell_info.data['name']
                    print(region_name, constell_name)
                    regions[region_name]['constellations'][constell_name] = {
                        'id': constell_id
                    }

            with open(file, 'w') as fp:
                json.dump(regions, fp, sort_keys=True)

            return regions


