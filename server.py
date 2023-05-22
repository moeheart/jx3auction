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
EDITION = "0.0.0"

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
    if map not in ["25人普通西津渡", "25人英雄西津渡", "25人普通武狱黑牢", "25人英雄武狱黑牢"]:
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
        if boss not in ["张景超", "刘展", "苏凤楼", "韩敬青", "藤原佑野", "李重茂", "其它", "关卡", "时风", "乐临川", "牛波", "和正", "武云阙", "翁幼之"]:
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
        if len(treasureList) == 0:
            return jsonify({'status': 104})
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
            sql = '''INSERT INTO treasure VALUES (%d, %d, %d, "%s", "%s", -1, -1, 0, 0);''' % (num, int(DungeonID), itemID, singleTreasure, boss)
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

    return jsonify({'status': 0, 'treasure': treasureRes, 'xinfa': xinfa})


AUCTION_PARAMS = ["baseNormal", "baseCoupon", "baseWeapon", "baseJingjian", "baseTexiaoyaozhui", "baseTexiaowuqi",
                  "stepEquip", "baseMaterials", "stepMaterials", "combineCharacter", "baseCharacter", "stepCharacter",
                  "baseXiaofumo", "stepXiaofumo", "baseDafumo", "stepDafumo", "baseXiaotie", "stepXiaotie",
                  "baseDatie", "stepDatie", "baseOther", "stepOther", "combineHanzi", "baseHanzi", "stepHanzi"]

@app.route('/startAuction', methods=['GET'])
def startAuction():
    '''http://127.0.0.1:8009/startAuction?DungeonID=2&AdminToken=628546&baseNormal=2000&baseCoupon=10000&baseWeapon=20000&baseJingjian=10000&baseTexiaoyaozhui=10000&baseTexiaowuqi=30000&
stepEquip=1000&baseMaterials=1000&stepMaterials=500&combineCharacter=1&baseCharacter=0&stepCharacter=0&baseXiaofumo=0&stepXiaofumo=500&baseDafumo=1000&stepDafumo=1000&
baseXiaotie=6000&stepXiaotie=3000&baseDatie=0&stepDatie=10000&baseOther=0&stepOther=1000&combineHanzi=1&baseHanzi=0&stepHanzi=0'''
    try:
        AdminToken = request.args.get('AdminToken')
        DungeonID = request.args.get('DungeonID')
        if AdminToken is None:
            return jsonify({'status': 101})
        if DungeonID is None:
            return jsonify({'status': 101})
        params = {}
        for param in AUCTION_PARAMS:
            params[param] = request.args.get(param)
            if params[param] is None:
                return jsonify({'status': 101})
            params[param] = int(params[param])
    except:
        return jsonify({'status': 100})

    name = config.get('jx3auction', 'username')
    pwd = config.get('jx3auction', 'password')
    db = pymysql.connect(host=IP, user=name, password=pwd, database="jx3auction", port=3306, charset='utf8mb4')
    cursor = db.cursor()

    try:
        # 检验团长权限
        sql = '''SELECT id, auctionStart, map FROM dungeon WHERE id=%d AND adminToken="%s";''' % (int(DungeonID), AdminToken)
        cursor.execute(sql)
        result = cursor.fetchall()
        if not result:
            return jsonify({'status': 202})

        # 检测拍卖是否已经开始
        if result[0][1] > 0:
            return jsonify({'status': 208})

        map = result[0][2]

        # 检验每一个属于这个拍卖的物品，并为之赋予状态.
        sql = '''SELECT itemID, name FROM treasure WHERE dungeonID=%d;''' % int(DungeonID)
        cursor.execute(sql)
        result = cursor.fetchall()

        # 获取所有掉落的详细信息.
        allTreasures = {}
        for line in result:
            itemID = line[0]
            name = line[1]
            allTreasures[str(itemID)] = app.item_analyser.GetSingleItemByName({"name": name, "map": map, "xinfa": "unknown"})

        # 判断是否存在打包拍卖.
        group_first = {"materials": -1, "character": -1, "xiaotie": -1, "hanzi": -1}
        group_id = {}
        for key in allTreasures:
            treasure = allTreasures[key]
            if treasure["available"] and treasure["type"] == "item" and treasure["class"] in ["materials", "character", "xiaotie", "hanzi"]:
                base_type = treasure["class"]
                if base_type == "character" and params["combineCharacter"]:
                    base_type = "materials"
                if base_type == "hanzi" and params["combineHanzi"]:
                    base_type = "materials"
                if group_first[base_type] == -1:
                    group_first[base_type] = int(key)
                else:
                    # 更新打包拍卖
                    group_id[key] = group_first[base_type]
                    group_id[str(group_first[base_type])] = group_first[base_type]

        # 判断是否存在同步拍卖.
        name_first = {}
        simul_id = {}
        for key in allTreasures:
            treasure = allTreasures[key]
            if treasure["available"] and key not in group_id:
                # 判断其名称.
                name = treasure["name"]
                if name not in name_first:
                    name_first[name] = int(key)
                else:
                    # 更新同步拍卖
                    simul_id[key] = name_first[name]
                    simul_id[str(name_first[name])] = name_first[name]

        # 逐个为物品确定起拍价和最小加价，并记入数据库.
        for key in allTreasures:
            treasure = allTreasures[key]
            base = 0
            step = 0
            if not treasure["available"]:
                continue
            if treasure["type"] == "equipment":
                step = params["stepEquip"]
                if treasure["subtype"] == "武器":
                    if "特效" in treasure["sketch"]:
                        base = params["baseTexiaowuqi"]
                    else:
                        base = params["baseWeapon"]
                elif treasure["subtype"] == "腰坠" and "特效" in treasure["sketch"]:
                    base = params["baseTexiaoyaozhui"]
                elif "精简" in treasure["sketch"]:
                    base = params["baseJingjian"]
                else:
                    base = params["baseNormal"]
            elif treasure["type"] == "coupon":
                step = params["stepEquip"]
                if "神兵玉匣" in treasure["name"]:
                    if "·奇" in treasure["name"]:
                        base = params["baseTexiaowuqi"]
                    else:
                        base = params["baseWeapon"]
                else:
                    base = params["baseCoupon"]
            else:
                if treasure["class"] == "materials":
                    base = params["baseMaterials"]
                    step = params["stepMaterials"]
                elif treasure["class"] == "character":
                    base = params["baseCharacter"]
                    step = params["stepCharacter"]
                elif treasure["class"] == "enchant":
                    if "天堑" in treasure["name"]:
                        base = params["baseDafumo"]
                        step = params["stepDafumo"]
                    else:
                        base = params["baseXiaofumo"]
                        step = params["stepXiaofumo"]
                elif treasure["class"] == "xiaotie":
                    base = params["baseXiaotie"]
                    step = params["stepXiaotie"]
                elif treasure["class"] == "datie":
                    base = params["baseDatie"]
                    step = params["stepDatie"]
                elif treasure["class"] == "hanzi":
                    base = params["baseHanzi"]
                    step = params["stepHanzi"]
                else:
                    base = params["baseOther"]
                    step = params["stepOther"]
            groupID = -1
            simulID = -1
            if key in group_id:
                groupID = group_id[key]
            if key in simul_id:
                simulID = simul_id[key]

            sql = '''UPDATE treasure SET groupID=%d, simulID=%d, basePrice=%d, minimalStep=%d WHERE dungeonID=%d AND itemID=%d;''' % \
                  (groupID, simulID, base, step, int(DungeonID), int(key))
            cursor.execute(sql)

        # 更新拍卖状态，但是放到最后
        sql = '''UPDATE dungeon SET auctionStart=%d WHERE id=%d;''' % (int(time.time()), int(DungeonID))
        cursor.execute(sql)

    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 200})

    finally:
        db.commit()
        db.close()

    return jsonify({'status': 0})

@app.route('/getAuction', methods=['GET'])
def getAuction():
    # http://127.0.0.1:8009/getAuction?DungeonID=2&playerName=%E8%8A%B1%E5%A7%90

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
        sql = '''SELECT map, auctionStart, auctionEnd FROM dungeon WHERE id=%d;''' % int(DungeonID)
        cursor.execute(sql)
        result = cursor.fetchall()
        if not result:
            return jsonify({'status': 201})
        map = result[0][0]
        auctionStart = result[0][1]
        auctionEnd = result[0][2]
        if auctionStart == 0:
            return jsonify({'status': 209})
        if auctionEnd != 0:
            return jsonify({'status': 210})

        # 检验成员权限
        sql = '''SELECT id, xinfa FROM player WHERE dungeonID=%d AND playerName="%s";''' % (int(DungeonID), playerName)
        cursor.execute(sql)
        result = cursor.fetchall()
        if not result:
            return jsonify({'status': 203})
        playerID = result[0][0]  # 这里只指向查询人的ID，对应autobid的情况
        xinfa = result[0][1]

        # 获取所有掉落
        treasureRes = []
        sql = '''SELECT itemID, name, boss, id, basePrice, minimalStep, groupID, simulID FROM treasure WHERE dungeonID=%d;''' % int(DungeonID)
        cursor.execute(sql)
        result = cursor.fetchall()

        for treasure in result:
            itemID = treasure[0]
            name = treasure[1]
            boss = treasure[2]
            treasureID = treasure[3]
            basePrice = treasure[4]
            minimalStep = treasure[5]
            groupID = treasure[6]
            simulID = treasure[7]
            print("[Test]", {"name": name, "map": map, "xinfa": xinfa})
            property = app.item_analyser.GetExtendItemByName({"name": name, "map": map, "xinfa": xinfa})

            bids = []
            currentPrice = []
            currentOwner = []
            autobid = -1
            if groupID == -1 and simulID == -1:
                sql = '''SELECT playerID, time, price, effective, playerName FROM auction, player WHERE treasureID=%d AND playerID=player.id;''' % int(treasureID)
                cursor.execute(sql)
                result = cursor.fetchall()
                result.sort(key=lambda x:-x[2])
                for bid in result:
                    bids.append({"player": bid[4],
                                 "price": bid[2],
                                 "time": bid[1]})
                    if bid[3]:  # effective
                        currentPrice.append(bid[2])
                        currentOwner.append(bid[4])

                sql = '''SELECT price FROM autobid WHERE playerID=%d AND treasureID=%d AND effective=1;''' % (int(playerID), int(treasureID))
                cursor.execute(sql)
                result = cursor.fetchall()
                if result:
                    autobid = result[0][0]

            treasureRes.append({"itemID": itemID,
                                "name": name,
                                "boss": boss,
                                "property": property,
                                "bids": bids,
                                "currentPrice": currentPrice,
                                "currentOwner": currentOwner,
                                "basePrice": basePrice,
                                "minimalStep": minimalStep,
                                "groupID": groupID,
                                "simulID": simulID,
                                "autobid": autobid
                                })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 200})

    finally:
        db.commit()
        db.close()

    return jsonify({'status': 0, 'treasure': treasureRes})

@app.route('/bid', methods=['GET'])
def bid():
    # http://127.0.0.1:8009/bid?DungeonID=2&playerName=%E8%8A%B1%E5%A7%90&itemID=1&price=3000&num=1

    try:
        playerName = request.args.get('playerName')
        DungeonID = request.args.get('DungeonID')
        itemID = int(request.args.get('itemID'))
        price = int(request.args.get('price'))
        num = int(request.args.get('num'))
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
        # 检查副本和玩家是否合法
        sql = '''SELECT id, xinfa FROM player WHERE dungeonID=%d AND playerName="%s";''' % (int(DungeonID), playerName)
        cursor.execute(sql)
        result = cursor.fetchall()
        if not result:
            return jsonify({'status': 203})
        playerID = result[0][0]

        # 检查物品是否存在

        sql = '''SELECT id, groupID, simulID, basePrice, minimalStep FROM treasure WHERE dungeonID=%d AND itemID=%d;''' % (int(DungeonID), itemID)
        cursor.execute(sql)
        result = cursor.fetchall()
        if not result:
            return jsonify({'status': 211})
        treasureID = result[0]
        groupID = result[1]
        simulID = result[2]
        basePrice = result[3]
        minimalStep = result[4]
        if price < basePrice:
            return jsonify({'status': 212})
        if price % minimalStep != 0:
            return jsonify({'status': 213})
        if groupID != -1 and groupID != itemID:
            return jsonify({'status': 214})
        if simulID != -1 and simulID != itemID:
            return jsonify({'status': 214})

        # 判断是否是同步拍卖. 如果是，那么记录其数量.
        itemNum = 1
        if simulID != -1:
            sql = '''SELECT id FROM treasure WHERE dungeonID=%d AND (itemID=%d OR simulID=%d);''' % (int(DungeonID), itemID, itemID)
            cursor.execute(sql)
            result = cursor.fetchall()
            itemNum = len(result)

        if num > itemNum:
            return jsonify({'status': 215})

        bids = []
        autobids = {}

        # 获取所有出价信息
        sql = '''SELECT playerID, time, price, effective, playerName, id FROM auction, player WHERE treasureID=%d AND playerID=player.id AND effective=1;''' % int(treasureID)
        cursor.execute(sql)
        result = cursor.fetchall()
        for bid in result:
            bids.append({"playerID": bid[0],
                         "price": bid[2],
                         "auctionID": bid[5],
                         "time": bid[1],
                         "num": 1,
                         "source": "auction"})

        # 获取所有自动出价信息
        sql = '''SELECT price, playerID, id, num, time FROM autobid WHERE treasureID=%d AND effective=1;''' % (int(treasureID))
        cursor.execute(sql)
        result = cursor.fetchall()
        for bid in result:
            autobids[bid[1]] = {
                 "price": bid[0],
                 "autobidID": bid[2],
                 "num": bid[3],
                 "time": bid[4],
            }

        # 记录自己的出价信息
        bids.append({
            "playerID": playerID,
            "price": price,
            "num": num,
            "time": int(time.time()),
            "source": "current",
        })

        # 判断在正常出价中的排名，并移除出价低的
        bids.sort(key=lambda x: x["price"] + {"auction": 0, "current": 0, "autobid": -1, "unavailable": -1}[x["source"]] - x["time"] / 1e+10)

        # 按由低到高的顺序移除出价。需要移除的数量等于添加的数量。
        i = 0
        toRemove = num
        if len(bids) < itemNum:
            toRemove = num - itemNum + len(bids)
        nowNum = 0
        activeNum = num
        autobidAppear = 0
        maxDeleted = 0
        while i < toRemove:
            # 记录中的出价更低，被顶掉
            line = bids[i]
            if line["source"] == "auction":
                sql = '''UPDATE auction SET effective=0 WHERE id=%d;''' % (int(line["auctionID"]))
                cursor.execute(sql)
                maxDeleted = line["price"]
                if line["playerID"] in autobids:
                    # 如果顶掉的这个出价有对应的自动出价，就尝试自动出价.
                    autobid = autobids[line["playerID"]]
                    if autobid["price"] > line["price"]:
                        bids.append({"playerID": line["playerID"],
                                     "price": autobid["price"],
                                     "num": 1,
                                     "source": "autobid"})
                        bids.sort(key=lambda x: x["price"] + {"auction": 0, "current": 0, "autobid": -1, "unavailable": -1}[x["source"]] - x["time"] / 1e+10)
                        autobidAppear = 1
                        toRemove += 1
            # 当前出价，计算可以生效多少个
            elif line["source"] == "current":
                activeNum = max(0, line["num"] - toRemove)
            # 预定自动出价也可能被移除
            elif line["source"] == "current":
                line["source"] = "unavailable"
            i += 1
            nowNum += line["num"]

        auctionNum = 1
        sql = '''SELECT MAX(id) FROM auction;'''
        cursor.execute(sql)
        result = cursor.fetchall()
        if result and result[0][0] is not None:
            auctionNum = result[0][0] + 1

        if activeNum == 0:
            if autobidAppear == 0:
                # 如果出价完全无效
                return jsonify({'status': 0, 'success': 0})
            else:
                # 如果出价有效，但是被自动出价顶掉
                sql = '''INSERT INTO auction VALUES (%d, %d, %d, %d, %d, 0, 0);''' % (auctionNum, int(playerID), int(treasureID), int(time.time()), price)
                cursor.execute(sql)
                auctionNum += 1
                # TODO websocket出价
        else:
            # 如果出价有效并且没有被顶掉
            for i in range(activeNum):
                sql = '''INSERT INTO auction VALUES (%d, %d, %d, %d, %d, 1, 0);''' % (auctionNum, int(playerID), int(treasureID), int(time.time()), price)
                cursor.execute(sql)
                auctionNum += 1
                # TODO websocket出价

        # 考虑成功的自动出价，为其安排最合适的出价
        for line in bids:
            if line["source"] == "autobid":
                sql = '''INSERT INTO auction VALUES (%d, %d, %d, %d, %d, 1, 1);''' % (auctionNum, int(line["playerID"]), int(treasureID), int(time.time()), maxDeleted + minimalStep)
                cursor.execute(sql)
                auctionNum += 1
                # TODO websocket出价

        # 关闭低于阈值的自动出价
        for playerID in autobids:
            line = autobids[playerID]
            if line["price"] <= maxDeleted:
                sql = '''UPDATE autobid SET effective=0 WHERE id=%d;''' % (int(line["autobidID"]))
                cursor.execute(sql)

    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 200})

    finally:
        db.commit()
        db.close()

    return jsonify({'status': 0, 'success': 1})


@app.route('/autobid', methods=['GET'])
def autobid():
    # http://127.0.0.1:8009/autobid?DungeonID=2&playerName=%E8%8A%B1%E5%A7%90&itemID=1&price=3000&num=1

    try:
        playerName = request.args.get('playerName')
        DungeonID = request.args.get('DungeonID')
        itemID = int(request.args.get('itemID'))
        price = int(request.args.get('price'))
        num = int(request.args.get('num'))
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
        # 检查副本和玩家是否合法
        sql = '''SELECT id, xinfa FROM player WHERE dungeonID=%d AND playerName="%s";''' % (int(DungeonID), playerName)
        cursor.execute(sql)
        result = cursor.fetchall()
        if not result:
            return jsonify({'status': 203})
        playerID = result[0][0]

        # 检查物品是否存在

        sql = '''SELECT id, groupID, simulID, basePrice, minimalStep FROM treasure WHERE dungeonID=%d AND itemID=%d;''' % (int(DungeonID), itemID)
        cursor.execute(sql)
        result = cursor.fetchall()
        if not result:
            return jsonify({'status': 211})
        treasureID = result[0]
        groupID = result[1]
        simulID = result[2]
        basePrice = result[3]
        minimalStep = result[4]
        if price < basePrice:
            return jsonify({'status': 212})
        if price % minimalStep != 0:
            return jsonify({'status': 213})
        if groupID != -1 and groupID != itemID:
            return jsonify({'status': 214})
        if simulID != -1 and simulID != itemID:
            return jsonify({'status': 214})

        # 判断是否是同步拍卖. 如果是，那么记录其数量.
        itemNum = 1
        if simulID != -1:
            sql = '''SELECT id FROM treasure WHERE dungeonID=%d AND (itemID=%d OR simulID=%d);''' % (int(DungeonID), itemID, itemID)
            cursor.execute(sql)
            result = cursor.fetchall()
            itemNum = len(result)

        if num > itemNum:
            return jsonify({'status': 215})

        bids = []
        autobids = {}

        # 获取所有出价信息
        sql = '''SELECT playerID, time, price, effective, playerName, id FROM auction, player WHERE treasureID=%d AND playerID=player.id AND effective=1;''' % int(treasureID)
        cursor.execute(sql)
        result = cursor.fetchall()
        for bid in result:
            bids.append({"playerID": bid[0],
                         "price": bid[2],
                         "auctionID": bid[5],
                         "time": bid[1],
                         "num": 1,
                         "source": "auction"})

        # 获取所有自动出价信息
        sql = '''SELECT price, playerID, id, num, time FROM autobid WHERE treasureID=%d AND effective=1;''' % (int(treasureID))
        cursor.execute(sql)
        result = cursor.fetchall()
        for bid in result:
            autobids[bid[1]] = {
                 "price": bid[0],
                 "autobidID": bid[2],
                 "num": bid[3],
                 "time": bid[4],
            }

        # 记录自己的出价信息
        bids.append({
            "playerID": playerID,
            "price": price,
            "num": num,
            "time": int(time.time()),
            "source": "current",
        })

        # 判断在正常出价中的排名，并移除出价低的
        bids.sort(key=lambda x: x["price"] + {"auction": 0, "current": 0, "autobid": -1, "unavailable": -1}[x["source"]] - x["time"] / 1e+10)

        # 按由低到高的顺序移除出价。需要移除的数量等于添加的数量。
        i = 0
        toRemove = num
        if len(bids) < itemNum:
            toRemove = num - itemNum + len(bids)
        nowNum = 0
        activeNum = num
        autobidAppear = 0
        maxDeleted = basePrice - minimalStep
        while i < toRemove:
            # 记录中的出价更低，被顶掉
            line = bids[i]
            if line["source"] == "auction":
                sql = '''UPDATE auction SET effective=0 WHERE id=%d;''' % (int(line["auctionID"]))
                cursor.execute(sql)
                maxDeleted = line["price"]
                if line["playerID"] in autobids:
                    # 如果顶掉的这个出价有对应的自动出价，就尝试自动出价.
                    autobid = autobids[line["playerID"]]
                    if autobid["price"] > line["price"]:
                        bids.append({"playerID": line["playerID"],
                                     "price": autobid["price"],
                                     "num": 1,
                                     "source": "autobid"})
                        bids.sort(key=lambda x: x["price"] + {"auction": 0, "current": 0, "autobid": -1, "unavailable": -1}[x["source"]] - x["time"] / 1e+10)
                        autobidAppear = 1
                        toRemove += 1
            # 当前出价，计算可以生效多少个
            elif line["source"] == "current":
                activeNum = max(0, line["num"] - toRemove)
            # 预定自动出价也可能被移除
            elif line["source"] == "current":
                line["source"] = "unavailable"
            i += 1
            nowNum += line["num"]

        auctionNum = 1
        sql = '''SELECT MAX(id) FROM auction;'''
        cursor.execute(sql)
        result = cursor.fetchall()
        if result and result[0][0] is not None:
            auctionNum = result[0][0] + 1

        if activeNum == 0:
            if autobidAppear == 0:
                # 如果出价无效
                return jsonify({'status': 0, 'success': 0})
            else:
                # 如果出价有效，但是被自动出价顶掉
                sql = '''INSERT INTO auction VALUES (%d, %d, %d, %d, %d, 0, 0);''' % (auctionNum, int(playerID), int(treasureID), int(time.time()), price)
                cursor.execute(sql)
                auctionNum += 1
                # TODO websocket出价
        else:
            # 如果出价有效并且没有被顶掉，那么为其安排最合适的出价
            for i in range(activeNum):
                sql = '''INSERT INTO auction VALUES (%d, %d, %d, %d, %d, 1, 0);''' % (auctionNum, int(playerID), int(treasureID), int(time.time()), maxDeleted + minimalStep)
                cursor.execute(sql)
                auctionNum += 1
                # TODO websocket出价

        # 考虑其它成功的自动出价，为其安排最合适的出价
        for line in bids:
            if line["source"] == "autobid":
                sql = '''INSERT INTO auction VALUES (%d, %d, %d, %d, %d, 1, 1);''' % (auctionNum, int(line["playerID"]), int(treasureID), int(time.time()), maxDeleted + minimalStep)
                cursor.execute(sql)
                auctionNum += 1
                # TODO websocket出价

        # 关闭低于阈值的自动出价
        for playerID in autobids:
            line = autobids[playerID]
            if line["price"] <= maxDeleted:
                sql = '''UPDATE autobid SET effective=0 WHERE id=%d;''' % (int(line["autobidID"]))
                cursor.execute(sql)

        # 如果自己的自动出价合适，那么加入到自动出价列表中
        if activeNum == num and price > maxDeleted + minimalStep:
            autobidNum = 1
            sql = '''SELECT MAX(id) FROM autobid;'''
            cursor.execute(sql)
            result = cursor.fetchall()
            if result and result[0][0] is not None:
                autobidNum = result[0][0] + 1
            sql = '''INSERT INTO autobid VALUES (%d, %d, %d, %d, %d, %d);''' % (autobidNum, playerID, int(treasureID), int(time.time()), maxDeleted + minimalStep, num)
            cursor.execute(sql)

    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 200})

    finally:
        db.commit()
        db.close()

    return jsonify({'status': 0})


# 下面是网页

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html", ver=EDITION)

@app.route('/manage.html', methods=['GET'])
def manage():
    AdminToken = request.args.get('AdminToken')
    DungeonID = request.args.get('DungeonID')
    return render_template("manage.html", ver=EDITION, admintoken=AdminToken, dungeonid=DungeonID)

@app.route('/treasure.html', methods=['GET'])
def treasure():
    playerName = request.args.get('playerName')
    DungeonID = request.args.get('DungeonID')
    return render_template("treasure.html", ver=EDITION, playername=playerName, dungeonid=DungeonID)

if __name__ == '__main__':
    import signal
    
    config = configparser.RawConfigParser()
    config.read_file(open('./settings.cfg'))
    
    app.dbname = config.get('jx3auction', 'username')
    app.dbpwd = config.get('jx3auction', 'password')
    app.debug = config.getboolean('jx3auction', 'debug')

    app.item_analyser = ItemAnalyser()
    
    app.run(host='0.0.0.0', port=8030, debug=app.debug, threaded=True)

