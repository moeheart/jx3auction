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

from logic.ItemAnalyser import ItemAnalyser

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
    # http://127.0.0.1:8009/createDungeon?map=25%E4%BA%BA%E8%8B%B1%E9%9B%84%E8%A5%BF%E6%B4%A5%E6%B8%A1
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


@app.route('/registerTeam', methods=['GET'])
def registerTeam():
    # http://127.0.0.1:8009/registerTeam?DungeonID=2&playerName=%E8%8A%B1%E5%A7%90&xinfa=%E4%B8%87%E8%8A%B1&position=24
    try:
        DungeonID = request.args.get('DungeonID')
        playerName = request.args.get('playerName')
        xinfa = request.args.get('xinfa')
        position = request.args.get('position')
        if DungeonID is None:
            return jsonify({'status': 101})
        if playerName is None:
            return jsonify({'status': 101})
        if xinfa is None:
            return jsonify({'status': 101})
        if position is None:
            return jsonify({'status': 101})
        if int(position) < 1 or int(position) > 25:
            return jsonify({'status': 103})
    except:
        return jsonify({'status': 100})

    name = config.get('jx3auction', 'username')
    pwd = config.get('jx3auction', 'password')
    db = pymysql.connect(host=IP, user=name, password=pwd, database="jx3auction", port=3306, charset='utf8mb4')
    cursor = db.cursor()

    try:
        num = 1
        sql = '''SELECT MAX(id) FROM player;'''
        cursor.execute(sql)
        result = cursor.fetchall()

        if result and result[0][0] is not None:
            num = result[0][0] + 1

        # 检测秘境ID是否存在
        sql = '''SELECT id FROM dungeon WHERE id=%d;''' % int(DungeonID)
        cursor.execute(sql)
        result = cursor.fetchall()
        if not result:
            return jsonify({'status': 201})

        # 检测角色ID是否出现过
        sql = '''SELECT playerName FROM player WHERE dungeonID=%d AND playerName="%s";''' % (int(DungeonID), playerName)
        cursor.execute(sql)
        result = cursor.fetchall()
        if result:
            return jsonify({'status': 206})

        # 检测位置是否已经被占用
        sql = '''SELECT position FROM player WHERE dungeonID=%d AND position=%d;''' % (int(DungeonID), int(position))
        cursor.execute(sql)
        result = cursor.fetchall()
        if result:
            return jsonify({'status': 207})

        sql = '''INSERT INTO player VALUES (%d, %d, %d, "%s", "%s", "无");''' % (num, int(DungeonID), int(position), playerName, xinfa)
        cursor.execute(sql)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 200})

    finally:
        db.commit()
        db.close()

    return jsonify({'status': 0})

@app.route('/getTeam', methods=['GET'])
def getTeam():
    # http://127.0.0.1:8009/getTeam?DungeonID=2
    try:
        DungeonID = request.args.get('DungeonID')
        if DungeonID is None:
            return jsonify({'status': 101})
    except:
        return jsonify({'status': 100})

    name = config.get('jx3auction', 'username')
    pwd = config.get('jx3auction', 'password')
    db = pymysql.connect(host=IP, user=name, password=pwd, database="jx3auction", port=3306, charset='utf8mb4')
    cursor = db.cursor()

    try:
        # 检测秘境ID是否存在
        sql = '''SELECT id FROM dungeon WHERE id=%d;''' % int(DungeonID)
        cursor.execute(sql)
        result = cursor.fetchall()
        if not result:
            return jsonify({'status': 201})

        # 进行查询
        sql = '''SELECT position, playerName, xinfa, profile FROM player WHERE dungeonID=%d;''' % (int(DungeonID))
        cursor.execute(sql)
        result = cursor.fetchall()

        team = []
        for line in result:
            team.append({
                "position": line[0],
                "playerName": line[1],
                "xinfa": line[2],
                "profile": line[3]
            })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 200})

    finally:
        db.commit()
        db.close()

    return jsonify({'status': 0, 'team': team})


@app.route('/setTreasure', methods=['GET'])
def setTreasure():
    # http://127.0.0.1:8009/setTreasure?DungeonID=2&AdminToken=628546&boss=%E5%BC%A0%E6%99%AF%E8%B6%85&treasure=[%E6%B8%85%E8%95%8A%E5%9D%A0][%E6%8F%BD%E6%B1%9F%E6%8A%A4%E8%85%95%C2%B7%E4%B8%87%E8%8A%B1][%E4%BA%94%E8%A1%8C%E7%9F%B3%EF%BC%88%E5%85%AD%E7%BA%A7%EF%BC%89]
    try:
        AdminToken = request.args.get('AdminToken')
        DungeonID = request.args.get('DungeonID')
        boss = request.args.get('boss')
        treasure = request.args.get('treasure')
        if AdminToken is None:
            return jsonify({'status': 101})
        if DungeonID is None:
            return jsonify({'status': 101})
        if boss is None:
            return jsonify({'status': 101})
        if boss not in ["张景超", "刘展", "苏凤楼", "韩敬青", "藤原佑野", "李重茂"]:
            return jsonify({'status': 205})
        if treasure is None:
            return jsonify({'status': 101})
        treasureList = []
        nowTreasure = ""
        for c in treasure:
            if c == "[":
                nowTreasure = ""
            elif c == "]":
                treasureList.append(nowTreasure)
            else:
                nowTreasure += c
    except:
        return jsonify({'status': 100})

    name = config.get('jx3auction', 'username')
    pwd = config.get('jx3auction', 'password')
    db = pymysql.connect(host=IP, user=name, password=pwd, database="jx3auction", port=3306, charset='utf8mb4')
    cursor = db.cursor()

    try:
        # 检验团长权限
        sql = '''SELECT id FROM dungeon WHERE id=%d AND adminToken="%s";''' % (int(DungeonID), AdminToken)
        cursor.execute(sql)
        result = cursor.fetchall()
        if not result:
            return jsonify({'status': 202})

        # 添加treasure表的元素
        num = 1
        sql = '''SELECT MAX(id) FROM treasure;'''
        cursor.execute(sql)
        result = cursor.fetchall()
        if result and result[0][0] is not None:
            num = result[0][0] + 1
        itemID = 1
        sql = '''SELECT MAX(itemID) FROM treasure WHERE dungeonID=%d;''' % int(DungeonID)
        cursor.execute(sql)
        result = cursor.fetchall()
        if result and result[0][0] is not None:
            itemID = result[0][0] + 1
        for singleTreasure in treasureList:
            sql = '''INSERT INTO treasure VALUES (%d, %d, %d, "%s", "%s", -1, -1);''' % (num, int(DungeonID), itemID, singleTreasure, boss)
            cursor.execute(sql)
            itemID += 1
            num += 1

    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 200})

    finally:
        db.commit()
        db.close()

    return jsonify({'status': 0})


@app.route('/getTreasure', methods=['GET'])
def getTreasure():
    # http://127.0.0.1:8009/getTreasure?DungeonID=2&playerName=%E8%8A%B1%E5%A7%90
    try:
        playerName = request.args.get('playerName')
        DungeonID = request.args.get('DungeonID')
        if playerName is None:
            return jsonify({'status': 101})
        if DungeonID is None:
            return jsonify({'status': 101})
    except:
        return jsonify({'status': 100})

    name = config.get('jx3auction', 'username')
    pwd = config.get('jx3auction', 'password')
    db = pymysql.connect(host=IP, user=name, password=pwd, database="jx3auction", port=3306, charset='utf8mb4')
    cursor = db.cursor()

    try:
        # 获取副本地图
        sql = '''SELECT map FROM dungeon WHERE id=%d;''' % int(DungeonID)
        cursor.execute(sql)
        result = cursor.fetchall()
        if not result:
            return jsonify({'status': 201})
        map = result[0][0]

        # 检验成员权限
        sql = '''SELECT xinfa FROM player WHERE dungeonID=%d AND playerName="%s";''' % (int(DungeonID), playerName)
        cursor.execute(sql)
        result = cursor.fetchall()
        if not result:
            return jsonify({'status': 203})
        xinfa = result[0][0]

        # 获取所有掉落
        treasureRes = []
        sql = '''SELECT itemID, name, boss FROM treasure WHERE dungeonID=%d;''' % int(DungeonID)
        cursor.execute(sql)
        result = cursor.fetchall()

        for treasure in result:
            itemID = treasure[0]
            name = treasure[1]
            boss = treasure[2]
            property = app.item_analyser.GetExtendItemByName({"name": name, "map": map, "xinfa": xinfa})
            treasureRes.append({"itemID": itemID, "name": name, "boss": boss, "property": property})

    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 200})

    finally:
        db.commit()
        db.close()

    return jsonify({'status': 0, 'treasure': treasureRes})


if __name__ == '__main__':
    import signal
    
    config = configparser.RawConfigParser()
    config.read_file(open('./settings.cfg'))
    
    app.dbname = config.get('jx3auction', 'username')
    app.dbpwd = config.get('jx3auction', 'password')
    app.debug = config.getboolean('jx3auction', 'debug')

    app.item_analyser = ItemAnalyser()
    
    app.run(host='0.0.0.0', port=8009, debug=app.debug, threaded=True)

