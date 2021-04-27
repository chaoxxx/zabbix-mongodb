#!/usr/bin/env python
# coding=utf-8
"""
Date: 25/04/2021
Author: Cosmo zhu
Description: get mongodb port in machine
Requires: MongoClient
"""

import json
from pymongo import MongoClient, errors
import os
import ConfigParser

ret_process = os.popen("ps -ef|grep -w mongod|grep -v grep|awk '{ print $2 }'|awk ' { printf (\"%s,\", $0)} END {printf (\"\") } '")
process = ret_process.read()

config = ConfigParser.ConfigParser()
config.read('config.properties')

"""Mongodb 用户名"""
mongo_user = config.get("MONGODB","user")

"""Mongodb 密码"""
mongo_password = config.get("MONGODB","password")

process_array = process.split(",")

rtn_ports = {}
port_list = []

rtn_ports["key"] = "mongodport.discover"
rtn_ports["value"] = {"data": port_list}

with open("/tmp/mongo_port.log","w") as mongoFile:

    for pid in process_array:
        if (pid is not None) and (pid is not ""):
            try:
                print_pid = "ss -tunple | grep %s | awk '{ print $5 }'" % pid
                ret = os.popen(print_pid)
                port = ret.read().replace("*:","").strip()
                url = 'mongodb://%s:%s@%s:%s' % (mongo_user, mongo_password, "127.0.0.1", port)
                conn = MongoClient(url,serverSelectionTimeoutMS=3000)
                conn.list_database_names()
                port_info = {'{#MONGODPORT}': port}
                port_list.append(port_info)
                mongoFile.write(port+",")
            except errors.PyMongoError as py_mongo_error:
                continue

    print('- ' + rtn_ports["key"] + ' ' + json.dumps(rtn_ports["value"]))
