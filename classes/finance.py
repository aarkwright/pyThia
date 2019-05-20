# -*- encoding: utf-8 -*-


from .helpers import *


class Finance(ESIBase):
    def __init__(self, app, client, id_char):
        super().__init__(app, client)
        self.id_char = id_char

        self.wallet_total = self.get_data("wallet")

    def esiop_char(self, api):
        operation = self.app.op[api](character_id=self.id_char)
        return self.client.request(operation)

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

