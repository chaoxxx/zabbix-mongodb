#!/usr/bin/env python
# coding=utf-8
"""
Date: 22/04/2021
Author: Cosmo zhu
Description: A script get mongos metrics
Requires: MongoClient in python
"""
import ConfigParser
import json
import sys

from pymongo import MongoClient, errors


class MongoDB(object):
    """main script class"""

    def __init__(self, port):
        config = ConfigParser.ConfigParser()
        config.read('config.properties')
        self.mongo_port = port
        self.mongo_host = "127.0.0.1"
        self.mongo_user = config.get("MONGODB", "user")
        self.mongo_password = config.get("MONGODB", "password")
        self.mongo_db = ["admin", ]
        self.__conn = None
        self.__dbnames = None
        self.__metrics = []

    def connect(self):
        """Connect to MongoDB"""
        if self.__conn is None:
            if self.mongo_user is None:
                try:
                    url = 'mongodb://%s:%s' % (self.mongo_host, self.mongo_port)
                    self.__conn = MongoClient(url,serverSelectionTimeoutMS=3000)
                    self.__conn.list_database_names()
                except errors.PyMongoError as py_mongo_error:
                    print('Error in MongoDB connection: %s' %
                          str(py_mongo_error))

                    sys.exit(-1)
            else:
                try:
                    url = 'mongodb://%s:%s@%s:%s/?connectTimeoutMS=300;socketTimeoutMS=300' % (
                    self.mongo_user, self.mongo_password, self.mongo_host, self.mongo_port)
                    self.__conn = MongoClient(url,serverSelectionTimeoutMS=3000)
                    self.__conn.list_database_names()
                except errors.PyMongoError as py_mongo_error:
                    print('Error in MongoDB connection: %s' %
                          str(py_mongo_error))
                    sys.exit(-1)

    def add_metrics(self, k, v):
        """add each metric to the metrics list"""
        dict_metrics = {}
        dict_metrics['key'] = k
        dict_metrics['value'] = v
        self.__metrics.append(dict_metrics)

    def print_metrics(self):
        """print out all metrics"""
        metrics = self.__metrics
        for metric in metrics:
            zabbix_item_key = str(metric['key'])
            zabbix_item_value = str(metric['value'])
            print('- ' + zabbix_item_key + ' ' + zabbix_item_value)

    def get_db_names(self):
        """get a list of DB names"""
        if self.__conn is None:
            self.connect()
        db_names = self.__conn.database_names()
        self.__dbnames = db_names


    def get_mongo_db_lld(self):
        """print DB list in json format, to be used for
        mongo db discovery in zabbix"""
        if self.__dbnames is None:
            db_names = self.get_db_names()
        else:
            db_names = self.__dbnames
        dict_metrics = {}
        db_list = []
        dict_metrics['key'] = 'mongodb.discovery'
        dict_metrics['value'] = {"data": db_list}
        if db_names is not None:
            for db_name in db_names:
                dict_lld_metric = {}
                dict_lld_metric['{#MONGODBNAME}'] = db_name
                db_list.append(dict_lld_metric)
            dict_metrics['value'] = '{"data": ' + json.dumps(db_list) + '}'
        self.__metrics.insert(0, dict_metrics)

    def get_db_stats_metrics(self):
        """get DB stats for each DB"""
        if self.__conn is None:
            self.connect()
        if self.__dbnames is None:
            self.get_db_names()
        if self.__dbnames is not None:
            for mongo_db in self.__dbnames:
                db_handler = self.__conn[mongo_db]
                dbs = db_handler.command('dbstats')
                for k, v in dbs.items():
                    if k in ['storageSize', 'ok', 'avgObjSize', 'indexes',
                             'objects', 'collections', 'fileSize',
                             'numExtents', 'dataSize', 'indexSize',
                             'nsSizeMB']:
                        self.add_metrics('mongodb.stats.' + k +
                                         '[' + mongo_db + ']', int(v))

    def close(self):
        """close connection to mongo"""
        if self.__conn is not None:
            self.__conn.close()


if __name__ == '__main__':
    mongodb = MongoDB("22222")
    mongodb.get_db_names()
    mongodb.get_mongo_db_lld()
    mongodb.get_db_stats_metrics()
    mongodb.print_metrics()
    mongodb.close()
