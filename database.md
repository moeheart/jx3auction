# 数据库定义

这个文件中定义了所有后端可能会用到的数据库格式，同时提供其对应的SQL创建语句。

## dungeon

副本表。

- `id` 主键。副本表的ID。
- `createTime` 创建时间。时间戳格式。
- `adminToken` 团长令牌。
- `auctionStart` 开始拍卖的时间。如果未开始则为0。
- `auctionEnd` 结束拍卖的时间。如果未结束则为0。

``CREATE TABLE dungeon (
         id INT PRIMARY KEY,
         createTime INT,
         adminToken VARCHAR(32),
         auctionStart INT,
         auctionEnd INT
) DEFAULT CHARSET utf8mb4;``

## player

玩家表。用于记录副本中的每个队员，同时也对应了每个参与拍卖的玩家。

- `id` 主键。队伍表的ID。
- `dungeonID` 对应的dungeon表主键.
- `position` 位置（应该是1-25之间）。
- `playerName` 玩家名。注意和大部分数据库中的`playerID`区分，后者一般表示`player`表的ID。
- `xinfa` 玩家的心法.

``CREATE TABLE player (
         id INT PRIMARY KEY,
         dungeonID INT,
         position INT,
         playerName VARCHAR(32),
         xinfa VARCHAR(32)
) DEFAULT CHARSET utf8mb4;``

## treasure

掉落表。用于记录副本的掉落。

- `id` 主键。掉落表的ID。
- `dungeonID` 对应的dungeon表主键.
- `itemID` 物品ID。表示每个副本内的掉落编号。
- `name` 掉落名称。这个名称在数据库中按原名记录，其展示通过上层的方法实现。
- `boss` 掉落对应的BOSS。
- `groupID` 打包拍卖的主元素itemID。如果为-1表示不是打包拍卖。
- `simulID` 同步拍卖的主元素itemID。如果为-1表示不是同步拍卖。

``CREATE TABLE treasure (
         id INT PRIMARY KEY,
         dungeonID INT,
         itemID INT,
         name VARCHAR(32),
         boss VARCHAR(32),
         groupID INT,
         simulID INT
) DEFAULT CHARSET utf8mb4;``

## auction

拍卖表。用于记录所有的出价信息。

- `id` 主键。拍卖表的ID。
- `playerID` 对应的player表主键。
- `treasureID` 对应的treasure表主键。
- `time` 进行出价操作的时间。
- `price` 出价的价格。
- `effective` 出价是否仍有效。
- `auto` 是否来源于自动出价。

``CREATE TABLE auction (
         id INT PRIMARY KEY,
         playerID INT,
         treasureID INT,
         time INT,
         price INT,
         effective INT,
         auto INT
) DEFAULT CHARSET utf8mb4;``

## autobid

自动出价记录表。用于记录自动出价信息。这个表会实时更新，无效的自动出价操作需要被删除。

- `id` 主键。拍卖表的ID。
- `playerID` 对应的player表主键。
- `treasureID` 对应的treasure表主键。
- `time` 进行出价操作的时间。
- `price` 出价的价格。
- `num` 需求的数量，用于同步出价。

``CREATE TABLE autobid (
         id INT PRIMARY KEY,
         playerID INT,
         treasureID INT,
         time INT,
         price INT,
         num INT
) DEFAULT CHARSET utf8mb4;``


