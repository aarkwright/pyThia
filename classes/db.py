# -*- encoding: utf-8 -*-
import pymongo
import urllib.parse
from classes import config


class MongoDB(object):
    def __init__(self):
        # Initiate the client
        self.client = pymongo.MongoClient("mongodb://%s:%s@%s:%s/" %
                                          (urllib.parse.quote_plus(config.MONGODB_USER),
                                           urllib.parse.quote_plus(config.MONGODB_PASS),
                                           config.MONGODB_HOST,
                                           config.MONGODB_PORT))

        self.dblist = self.client.list_database_names()

    def add(self, database, table, data):
        database = self.client[database]
        collection = database[table]
        collection.insert_one(data)

    def drop_DB(self, database):
        self.client.drop_database(database)

    def drop_table(self, database, table):
        database = self.client[database]
        table = database[table]
        table.drop()

    def delete_entry(self, database, table, query):
        database = self.client[database]
        table = database[table]

        if len(query) == 1:
            table.delete_one(query)
        elif len(query) > 1:
            table.delete_many(query)

    def get_table(self, database, table):
        database = self.client[database]
        table = database[table]

        return [i for i in table.find()]

    def insert_table(self, database, table, data, unique):
        current_data = self.get_table(database, table)

        database = self.client[database]
        _table = database[table]

        if not len(current_data):
            _table.insert_many(data)
        else:
            for item in data:
                if item[unique] not in [e[unique] for e in current_data]:
                    _table.insert_one(item)

    def update_table(self, database, table, data, unique=True):
        # This adds new items only if they're not already in the collection;
        database = self.client[database]
        table = database[table]

        # data must be a list
        for item in data:
            print(item['name'])
            table.update_one({"_id": "*"}, {"$set": data}, upsert=unique)


if __name__ == "__main__":
    db = MongoDB()
