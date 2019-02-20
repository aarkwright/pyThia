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

        self.db = self.client['pyThia']
        # self.dblist = self.client.list_database_names()

    def add(self, table, data):
        collection = self.db[table]
        collection.insert_one(data)

    def drop_db(self, database):
        self.client.drop_database(database)

    def drop_table(self,  table):
        table = self.db[table]
        table.drop()

    def delete_entry(self, table, query):
        table = self.db[table]

        if len(query) == 1:
            table.delete_one(query)
        elif len(query) > 1:
            table.delete_many(query)

    def get_table(self, table):
        table = self.db[table]

        return [i for i in table.find()]

    def insert_table(self, table, data, unique):
        current_table_data = self.get_table(table)

        table = self.db[table]

        if not len(current_table_data):
            table.insert_many(data)
        else:
            for item in data:
                if item[unique] not in [e[unique] for e in current_table_data]:
                    table.insert_one(item)

    def update_table(self, table, data, unique=True):
        # This adds new items only if they're not already in the collection;
        table = self.db[table]

        # data must be a list
        for item in data:
            print(item['name'])
            table.update_one({"_id": "*"}, {"$set": data}, upsert=unique)


if __name__ == "__main__":
    db = MongoDB()
