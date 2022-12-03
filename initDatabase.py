# Created by moeheart on 12/03/2022
# 这是数据库的创建流程. 第一次使用会创建数据库, 而后续使用会清除数据库.


import pymysql
import configparser

IP = "120.48.95.56"

print("This operation is DANGEROUS!")
print("To continue, type 'yes':")
res = input()
if (res != "yes"):
    exit
    
config = configparser.RawConfigParser()
config.read_file(open('./settings.cfg'))

name = config.get('jx3auction', 'username')
pwd = config.get('jx3auction', 'password')
db = pymysql.connect(host=IP, user=name, password=pwd, database="jx3auction", port=3306, charset='utf8mb4')

cursor = db.cursor()

cursor.execute("DROP TABLE IF EXISTS dungeon")
cursor.execute("DROP TABLE IF EXISTS player")
cursor.execute("DROP TABLE IF EXISTS treasure")
cursor.execute("DROP TABLE IF EXISTS auction")
cursor.execute("DROP TABLE IF EXISTS autobid")

sql = """CREATE TABLE dungeon (
         id INT PRIMARY KEY,
         createTime INT,
         adminToken VARCHAR(32),
         auctionStart INT,
         auctionEnd INT
) DEFAULT CHARSET utf8mb4;"""
cursor.execute(sql)

sql = """CREATE TABLE player (
         id INT PRIMARY KEY,
         dungeonID INT,
         position INT,
         playerName VARCHAR(32),
         xinfa VARCHAR(32)
) DEFAULT CHARSET utf8mb4;"""
cursor.execute(sql)

sql = """CREATE TABLE treasure (
         id INT PRIMARY KEY,
         dungeonID INT,
         itemID INT,
         name VARCHAR(32),
         boss VARCHAR(32),
         groupID INT,
         simulID INT
) DEFAULT CHARSET utf8mb4;"""
cursor.execute(sql)

sql = """CREATE TABLE auction (
         id INT PRIMARY KEY,
         playerID INT,
         treasureID INT,
         time INT,
         price INT,
         effective INT,
         auto INT
) DEFAULT CHARSET utf8mb4;"""
cursor.execute(sql)

sql = """CREATE TABLE autobid (
         id INT PRIMARY KEY,
         playerID INT,
         treasureID INT,
         time INT,
         price INT,
         num INT
) DEFAULT CHARSET utf8mb4;"""
cursor.execute(sql)

db.commit()
db.close()