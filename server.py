# coding:utf-8
from flask import Flask, render_template, url_for, request, redirect, session, make_response, jsonify, abort
from flask import request    
from flask import make_response,Response
from flask_cors import CORS
import urllib
import json
import re
import pymysql
import random
import time
import urllib.request
import hashlib
import configparser
import os
import traceback

IP = "120.48.95.56"  # IP
announcement = "全新的DPS统计已出炉，大家可以关注一下，看一下各门派的表现~"
app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

def Response_headers(content):
    resp = Response(content)    
    resp.headers['Access-Control-Allow-Origin'] = '*'    
    return resp

def generateToken():
    s = str(random.randint(0, 999999))
    while len(s) < 6:
        s = '0' + s
    return s

@app.route('/createDungeon', methods=['GET'])
def createDungeon():
    try:
        map = request.args.get('map')
        if map is None:
            return jsonify({'status': 101})
    except:
        return jsonify({'status': 100})

    if map not in ["25人普通西津渡", "25人英雄西津渡"]:
        return jsonify({'status': 102})

    name = config.get('jx3auction', 'username')
    pwd = config.get('jx3auction', 'password')
    db = pymysql.connect(host=IP, user=name, password=pwd, database="jx3auction", port=3306, charset='utf8mb4')
    cursor = db.cursor()

    try:
        num = 1

        sql = '''SELECT MAX(id) FROM dungeon;'''
        cursor.execute(sql)
        result = cursor.fetchall()

        if result and result[0][0] is not None:
            num = result[0][0] + 1

        nowTime = time.time()
        adminToken = generateToken()

        sql = '''INSERT INTO dungeon VALUES (%d, %d, "%s", "%s", 0, 0);''' % (num, nowTime, adminToken, map)
        cursor.execute(sql)
    except:
        return jsonify({'status': 200})
    finally:
        db.commit()
        db.close()

    return jsonify({'status': 0, 'DungeonID': num, 'AdminToken': adminToken})

if __name__ == '__main__':
    import signal
    
    config = configparser.RawConfigParser()
    config.read_file(open('./settings.cfg'))
    
    app.dbname = config.get('jx3auction', 'username')
    app.dbpwd = config.get('jx3auction', 'password')
    app.debug = config.getboolean('jx3auction', 'debug')
    
    app.run(host='0.0.0.0', port=8009, debug=app.debug, threaded=True)

