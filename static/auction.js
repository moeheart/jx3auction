
AUCTION_BY_BOSS = {};
AUCTION_BY_ID = {};
ITEM_OPEN = {};
CURRENT_ID = -1;
COPIED = {};
PLAYER_INFO = {};
PLAYER_INFO_UPDATED = 0;

$(document).ready(function () {
    namespace = '/auction_info';
    var socket = io.connect(location.protocol + "//" + document.domain + ":" + location.port + namespace);

    socket.on('connect', () => {
      // Automatically connect to general channel
      socket.emit('join',{"channel": DUNGEON_ID, "username":PLAYER_NAME});
    });

    socket.on('bid', function(res) {
        console.log("[Socketio] bid");
        console.log(res);
        // 添加变化的内容
        var item = AUCTION_BY_ID[res["itemID"]];
        var bids = item["bids"];
        bids.push({
            "player": res["player"],
            "price": res["price"],
            "time": res["time"],
        })
        bids.sort((x, y) => {return -x["price"] + x["time"]/1e+10 + y["price"] - y["time"]/1e+10})
        var itemNum = 1;
        if (item["simulID"] != -1) {
            itemNum = SIMUL_CONTENT[item["simulID"]];
        }
        // 重新计算这次拍卖的最高价，与最低出价
        item["currentOwner"].length = 0;
        item["currentPrice"].length = 0;
        item["lowestPrice"] = item["basePrice"];
        for (var i in bids) {
            bids[i]["bidID"] = i;
            if (i < itemNum) {
                item["currentOwner"].push(bids[i]["player"])
                item["currentPrice"].push(bids[i]["price"])
                if (i == itemNum - 1) {
                    item["lowestPrice"] = item["basePrice"] + item["minimalStep"];
                }
                bids[i]["available"] = 1;
            } else {
                bids[i]["available"] = 0;
            }
        }
        if (res["player"] == PLAYER_NAME && FAVORITE_ITEM[res["itemID"]] == 0) {
            FAVORITE_ITEM[res["itemID"]] = 1;
            activate_favorite(res["itemID"], 0);
        }
        if (item["currentOwner"].indexOf(PLAYER_NAME) != -1) {
            $(`#item-${res["itemID"]}`).addClass("owner");
        } else {
            $(`#item-${res["itemID"]}`).removeClass("owner");
        }
        get_lowest_price(res["itemID"]);
        // 刷新时间
        if (item["countdownBase"] != -1) {
            item["remainTime"] = Math.max(0, item["countdownBase"] - 2);
        }
        // 有出价说明物品已经解锁
        item["lock"] = 0;
        var obj = $(`#lock-${item["itemID"]}`);
        obj.addClass("hidden");
        $(`#item-${item["itemID"]}`).removeClass("disable-color");

        // 计算总和
        V_summary.personal_sum = 0;
        V_summary.group_sum = 0;
        for (var i in AUCTION_BY_ID) {
            var item = AUCTION_BY_ID[i];
            for (var j in item["bids"]) {
                var bid = item["bids"][j];
                if (j < itemNum) {
                    $(`#bid-${i}-${j}`).addClass("available-bid");
                    V_summary.group_sum += bid["price"];
                    if (bid["player"] == PLAYER_NAME) {
                        V_summary.personal_sum += bid["price"];
                    }
                }
            }
        }
        V_treasure_list.reloadBids();
    });

    socket.on('clear', function(res) {
        console.log("[Socketio] clear");
        console.log(res);
        var item = AUCTION_BY_ID[res["itemID"]];
        if (item["groupID"] != -1 && item["groupID"] != item["itemID"]) {
            return;
        }
        if (item["simulID"] != -1 && item["simulID"] != item["itemID"]) {
            return;
        }
        item["bids"].length = 0;
        item["currentOwner"].length = 0;
        item["currentPrice"].length = 0;
        item["lowestPrice"] = item["basePrice"];
        $(`#item-${res["itemID"]}`).removeClass("owner");
        get_lowest_price(res["itemID"]);
        V_treasure_list.reloadBids();
    });

    socket.on('clear_boss', function(res) {
        console.log("[Socketio] clear_boss");
        console.log(res);
        if (!(res["boss"] in AUCTION_BY_BOSS))
            return;
        for (var item of AUCTION_BY_BOSS[res["boss"]]) {
            if (item["groupID"] != -1 && item["groupID"] != item["itemID"]) {
                continue;
            }
            if (item["simulID"] != -1 && item["simulID"] != item["itemID"]) {
                continue;
            }
            item["bids"].length = 0;
            item["currentOwner"].length = 0;
            item["currentPrice"].length = 0;
            item["lowestPrice"] = item["basePrice"];
            $(`#item-${item["itemID"]}`).removeClass("owner");
            get_lowest_price(item["itemID"]);
            V_treasure_list.reloadBids();
        }
    });

    socket.on('lock', function(res) {
        console.log("[Socketio] lock");
        console.log(res);
        var item = AUCTION_BY_ID[res["itemID"]];
        if (item["groupID"] != -1 && item["groupID"] != item["itemID"]) {
            return;
        }
        if (item["simulID"] != -1 && item["simulID"] != item["itemID"]) {
            return;
        }
        if (res["switch"] == 0) {
            // 上锁
            item["lock"] = 1;
            $(`#clock-${item["itemID"]}`).addClass("hidden");
            item["countdownBase"] = -1;
            item["remainTime"] = -1;
            var obj = $(`#lock-${item["itemID"]}`);
            obj.removeClass("hidden");
            obj.attr("data-toggle", "tooltip");
            obj.attr("data-placement", "top");
            obj.attr("title", "这件物品已经锁定，不能再出价。");
            $(`#item-${item["itemID"]}`).addClass("disable-color");
        } else {
            // 解锁
            item["lock"] = 0;
            $(`#clock-${item["itemID"]}`).addClass("hidden");
            item["countdownBase"] = -1;
            item["remainTime"] = -1;
            var obj = $(`#lock-${item["itemID"]}`);
            obj.addClass("hidden");
            $(`#item-${item["itemID"]}`).removeClass("disable-color");
        }
        V_treasure_list.reloadBids();
    });

    socket.on('lock_boss', function(res) {
        console.log("[Socketio] lock_boss");
        console.log(res);
        if (!(res["boss"] in AUCTION_BY_BOSS))
            return;
        for (var item of AUCTION_BY_BOSS[res["boss"]]) {
            if (item["groupID"] != -1 && item["groupID"] != item["itemID"]) {
                continue;
            }
            if (item["simulID"] != -1 && item["simulID"] != item["itemID"]) {
                continue;
            }
            if (res["switch"] == 0) {
                // 上锁
                item["lock"] = 1;
                $(`#clock-${item["itemID"]}`).addClass("hidden");
                item["countdownBase"] = -1;
                item["remainTime"] = -1;
                var obj = $(`#lock-${item["itemID"]}`);
                obj.removeClass("hidden");
                obj.attr("data-toggle", "tooltip");
                obj.attr("data-placement", "top");
                obj.attr("title", "这件物品已经锁定，不能再出价。");
                $(`#item-${item["itemID"]}`).addClass("disable-color");

            } else {
                // 解锁
                item["lock"] = 0;
                $(`#clock-${item["itemID"]}`).addClass("hidden");
                item["countdownBase"] = -1;
                item["remainTime"] = -1;
                var obj = $(`#lock-${item["itemID"]}`);
                obj.addClass("hidden");
                $(`#item-${item["itemID"]}`).removeClass("disable-color");
            }
        }
        V_treasure_list.reloadBids();
    });

    socket.on('countdown', function(res) {
        console.log("[Socketio] countdown");
        console.log(res);
        var item = AUCTION_BY_ID[res["itemID"]];
        if (item["groupID"] != -1 && item["groupID"] != item["itemID"]) {
            return;
        }
        if (item["simulID"] != -1 && item["simulID"] != item["itemID"]) {
            return;
        }
        item["countdownBase"] = res["countdownBase"];
        item["remainTime"] = Math.max(0, res["countdownBase"] - 2);
        var obj = $(`#clock-${item["itemID"]}`);
        obj.removeClass("hidden");
        obj.attr("data-toggle", "tooltip");
        obj.attr("data-placement", "top");
        obj.attr("title", "这件物品处于倒计时中，倒计时结束后会锁定，出价可以刷新倒计时。\n由于网络延迟等原因，卡秒出价可能会导致出价失败。");
        V_treasure_list.reloadBids();
    });

    socket.on('countdown_boss', function(res) {
        console.log("[Socketio] countdown_boss");
        console.log(res);
        if (!(res["boss"] in AUCTION_BY_BOSS))
            return;
        for (var item of AUCTION_BY_BOSS[res["boss"]]) {
            if (item["groupID"] != -1 && item["groupID"] != item["itemID"]) {
                continue;
            }
            if (item["simulID"] != -1 && item["simulID"] != item["itemID"]) {
                continue;
            }
            if (item["lock"] == 1) {
                continue;
            }
            item["countdownBase"] = res["countdownBase"];
            item["remainTime"] = Math.max(0, res["countdownBase"] - 2);
            var obj = $(`#clock-${item["itemID"]}`);
            obj.removeClass("hidden");
            obj.attr("data-toggle", "tooltip");
            obj.attr("data-placement", "top");
            obj.attr("title", "这件物品处于倒计时中，倒计时结束后会锁定，出价可以刷新倒计时。\n由于网络延迟等原因，卡秒出价可能会导致出价失败。");
        }
        V_treasure_list.reloadBids();
    });

});

function timepass(){
    // 每经过1秒，尝试减少倒计时的时间
    for (var i in AUCTION_BY_ID) {
        var item = AUCTION_BY_ID[i];
        if (item["remainTime"] == 0) {
            $(`#clock-${i}`).addClass("hidden");
            // 将其锁定
            item["lock"] = 1;
            var obj = $(`#lock-${i}`);
            obj.removeClass("hidden");
            obj.attr("data-toggle", "tooltip");
            obj.attr("data-placement", "top");
            obj.attr("title", "这件物品已经锁定，不能再出价。");
            $(`#item-${i}`).addClass("disable-color");
        }
        if (item["remainTime"] != -1) {
            item["remainTime"] -= 1;
        }
    }
    V_treasure_list.loadAuction();
}

function show_attrib(){
    var group_content = {};
    SIMUL_CONTENT = {};
    FAVORITE_ITEM = {};
    ITEM_OPEN = {};
    LOWEST_PRICE = {};
    // 展示打包拍卖、同步拍卖等特殊情况
    for (var i in AUCTION_BY_ID) {
        var item = AUCTION_BY_ID[i];
        ITEM_OPEN[i] = 1;
        COPIED[i] = 0;
        // 判断打包拍卖
        if (item["groupID"] != -1 && item["groupID"] != i) {
            // 添加打包拍卖的显示
            var obj = $(`#bag-${i}`);
            obj.removeClass("hidden");
            obj.attr("data-toggle", "tooltip");
            obj.attr("data-placement", "top");
            obj.attr("title", "这件物品是打包拍卖的从属物品。\n只有赢得主要物品的拍卖才能获取这件物品，点击前往对应的主要物品。");
            $(`#item-${i}`).addClass("disable-color");
            $(`#item-${i}`).click(item["groupID"], function (event) {
                window.location.href = `#item-${event.data}`;
            });
            $(`#subcollapse-${i}`).removeAttr("data-toggle");
            // 为主要物品增加内容
            if (!(item["groupID"] in group_content)) {
                group_content[item["groupID"]] = {}
            }
            if (!(item["name"] in group_content[item["groupID"]])) {
                group_content[item["groupID"]][item["name"]] = 1;
            } else {
                group_content[item["groupID"]][item["name"]] += 1;
            }
            // 同步这件物品的属性，实际上是软拷贝，后续不需要再调整
            item["currentOwner"] = AUCTION_BY_ID[item["groupID"]]["currentOwner"];
            ITEM_OPEN[i] = 0;
            COPIED[i] = 1;
        }
        // 判断同步拍卖
        if (item["simulID"] != -1 && item["simulID"] != i) {
            // 添加同步拍卖的显示
            var obj = $(`#sync-${i}`);
            obj.removeClass("hidden");
            obj.attr("data-toggle", "tooltip");
            obj.attr("data-placement", "top");
            obj.attr("title", "这件物品是同步拍卖的从属物品。\n拍卖在主要物品中进行，复数个最高出价都有效，点击前往对应的主要物品。");
            $(`#item-${i}`).addClass("disable-color");
            $(`#item-${i}`).click(item["simulID"], function (event) {
                console.log(event);
                window.location.href = `#item-${event.data}`;
            });
            $(`#subcollapse-${i}`).removeAttr("data-toggle");
            // 为主要物品增加内容
            if (!(item["simulID"] in SIMUL_CONTENT)) {
                SIMUL_CONTENT[item["simulID"]] = 1;
            }
            SIMUL_CONTENT[item["simulID"]] += 1;
            // 同步这件物品的属性，实际上是软拷贝，后续不需要再调整
            item["currentOwner"] = AUCTION_BY_ID[item["simulID"]]["currentOwner"];
            item["currentPrice"] = AUCTION_BY_ID[item["simulID"]]["currentPrice"];
            ITEM_OPEN[i] = 0;
            COPIED[i] = 1;
        }
    }
    // 展示打包拍卖、同步拍卖的主要物品
    for (var i in AUCTION_BY_ID) {
        var item = AUCTION_BY_ID[i];
        // 判断打包拍卖
        if (item["groupID"] == i) {
            // 添加打包拍卖的显示
            var obj = $(`#bag-${i}`);
            obj.removeClass("hidden");
            obj.attr("data-toggle", "tooltip");
            obj.attr("data-placement", "top");
            var resArray = [];
            for (var key in group_content[i]) {
                resArray.push("[" + key + "]*" + group_content[i][key])
            }
            var resText = resArray.join(",");
            obj.attr("title", "这件物品是打包拍卖的主要物品。\n赢得这件物品的拍卖时，还会额外获得：\n" + resText);
        }
        // 判断同步拍卖
        if (item["simulID"] == i) {
            // 添加同步拍卖的显示
            var obj = $(`#sync-${i}`);
            obj.removeClass("hidden");
            obj.attr("data-toggle", "tooltip");
            obj.attr("data-placement", "top");
            obj.attr("title", "这件物品是同步拍卖的主要物品。\n这件物品的" + SIMUL_CONTENT[i] + "个最高出价都有效，每个出价都会分得一件。");
        }
    }
    V_summary.personal_sum = 0;
    V_summary.group_sum = 0;
    for (var i in AUCTION_BY_ID) {
        // 计算初始时的各项属性
        FAVORITE_ITEM[i] = 0;
        var item = AUCTION_BY_ID[i];
        var itemNum = 1;
        if (item["simulID"] != -1) {
            itemNum = SIMUL_CONTENT[item["simulID"]];
        }
        for (var j in item["bids"]) {
            var bid = item["bids"][j];
            if (bid["player"] == PLAYER_NAME) {
                FAVORITE_ITEM[i] = 1;
                activate_favorite(i, 0);
            }
            if (j < itemNum) {
                bid["available"] = 1;
                $(`#bid-${i}-${j}`).addClass("available-bid");
                V_summary.group_sum += bid["price"];
                if (bid["player"] == PLAYER_NAME) {
                    V_summary.personal_sum += bid["price"];
                }
            } else {
                $(`#bid-${i}-${j}`).removeClass("available-bid");
            }
        }
        if (item["currentOwner"].indexOf(PLAYER_NAME) != -1) {
            $(`#item-${i}`).addClass("owner");
        }
        if (item["lock"] == 1) {
            var obj = $(`#lock-${i}`);
            obj.removeClass("hidden");
            obj.attr("data-toggle", "tooltip");
            obj.attr("data-placement", "top");
            obj.attr("title", "这件物品已经锁定，不能再出价。");
            $(`#item-${i}`).addClass("disable-color");
        }
        if (item["remainTime"] != -1) {
            var obj = $(`#clock-${i}`);
            obj.removeClass("hidden");
            obj.attr("data-toggle", "tooltip");
            obj.attr("data-placement", "top");
            obj.attr("title", "这件物品处于倒计时中，倒计时结束后会锁定，出价可以刷新倒计时。\n由于网络延迟等原因，卡秒出价可能会导致出价失败。");
        }
        // 计算最小出价
        get_lowest_price(i);
    }
    timepass();
    setInterval(timepass, 1000);
    V_summary.load_summary = true;
    // 刷新一次，有的属性没有同步到页面上
    V_treasure_list.loadAuction();
}

function activate_favorite(itemID, isPress){
    $(`#item-${itemID}`).addClass("favorite");
    $(`#lowest-${itemID}`).removeAttr("disabled");
    if (isPress == 0) {
        $(`#favorite-${itemID}`).addClass("active");
        $(`#favorite-${itemID}`).attr("aria-pressed", "true");
    }
}

function deactivate_favorite(itemID, isPress){
    $(`#item-${itemID}`).removeClass("favorite");
    $(`#lowest-${itemID}`).attr("disabled", 1);
    if (isPress == 0) {
        $(`#favorite-${itemID}`).removeClass("active");
        $(`#favorite-${itemID}`).attr("aria-pressed", "false");
    }
}

function favorite(itemID) {
    // 切换收藏状态，也即同时处理开/关两种情况。
    if (FAVORITE_ITEM[itemID] == 0) {
        FAVORITE_ITEM[itemID] = 1;
        activate_favorite(itemID, 1);
    } else {
        FAVORITE_ITEM[itemID] = 0;
        deactivate_favorite(itemID, 1);
    }
}

function analyse_auction(auctionInfo){
    console.log(auctionInfo);
    var res = auctionInfo["treasure"];
    for (var i in res) {
        var item = res[i];
        var boss = item["boss"];
        for (var i in item["bids"]) {
            item["bids"][i]["bidID"] = i;
        }
        if (!(boss in AUCTION_BY_BOSS)) {
            AUCTION_BY_BOSS[boss] = [];
        }
        AUCTION_BY_BOSS[boss].push(item);
        AUCTION_BY_ID[item["itemID"]] = item;
    }
    console.log(AUCTION_BY_BOSS);
    V_treasure_list.loadAuction();
    PLAYER_XINFA = auctionInfo["xinfa"];

    setTimeout("show_attrib()", 500);
}

ALERT_VISIBLE = [0, 0, 0, 0, 0];

function showError(msg, i) {
    $(`#alert-${i} p`).html(msg);
    $(`#alert-${i}`).show();
}

function error(code) {
    var msg = "错误" + code + "：未知错误";
    if (code in ERROR_CONTENT) {
        msg = "错误" + code + "：" + ERROR_CONTENT[code];
    }
    var i = ALERT_VISIBLE.indexOf(0);
    if (i == -1) {
        i = 4;
    }
    ALERT_VISIBLE[i] = 1;
    showError(msg, i+1);
}

function auto_bid(itemID){

}

function bid_implement(itemID, price) {
    var str = `/bid?playerName=${PLAYER_NAME}&DungeonID=${DUNGEON_ID}&itemID=${itemID}&price=${price}&num=1&PlayerToken=${PLAYER_TOKEN}`;
    $.get(str, function(result){
        if (result["status"] != 0) {
            error(result["status"]);
        } else if (result["success"] == 0) {
            error(302);
        }
        console.log(result);
    });
}

function bid(itemID, ensure=0){
    var lowestPrice = LOWEST_PRICE[itemID];
    var price = $(`#bidnum-${itemID}`).val();
    if (AUCTION_BY_ID[itemID]["lock"] == 1) {
        error(902);
        return;
    }
    if (price < lowestPrice) {
        error(901);
        return;
    } else if (price >= 10 * lowestPrice && ensure == 0) {
        CURRENT_ID = itemID;
        $('#bid-verify-num').html(price);
        $('#bid-modal').modal();
        return;
    }
    bid_implement(itemID, price);
}

function verify_bid() {
    bid(CURRENT_ID, 1);
}

function get_lowest_price(itemID){
    var item = AUCTION_BY_ID[itemID];
    var bids = item["bids"];
    var lowestPrice = item["basePrice"];
    var itemNum = 1;
    if (item["simulID"] != -1) {
        itemNum = SIMUL_CONTENT[item["simulID"]];
    }
    for (var i in bids) {
        if (i < itemNum) {
            if (i == itemNum - 1) {
                lowestPrice = bids[i]["price"] + item["minimalStep"];
            }
        }
    }
    LOWEST_PRICE[itemID] = lowestPrice;
    $(`#lowest-${itemID}`).html("最小出价：" + lowestPrice);
}

function bid_low(itemID){
    if (AUCTION_BY_ID[itemID]["lock"] == 1) {
        error(902);
        return;
    }
    bid_implement(itemID, LOWEST_PRICE[itemID]);
}

function render_desc(desc_id, property){
    var obj = $(desc_id);
    var text_line = $("<div></div>");
    text_line.html(property["name"]);
    text_line.addClass("text-"+property["quality"]);
    text_line.appendTo($(desc_id));

    if (property["type"] == "equipment") {
        var text_line = $("<div></div>");
        text_line.html(property["subtype"] + `（最大精炼：${property["maxlevel"]}）`);
        text_line.addClass("text-gray");
        text_line.appendTo($(desc_id));
        // attribute-base
        for (var i in property["attribute"]["base"]) {
            var text_line = $("<div></div>");
            var line = property["attribute"]["base"][i];
            text_line.html(line);
            text_line.addClass("text-white");
            text_line.appendTo($(desc_id));
        }
        // attribute-extra
        for (var i in property["attribute"]["extra"]) {
            var text_line = $("<div></div>");
            var line = property["attribute"]["extra"][i];
            text_line.html(line);
            text_line.addClass("text-green");
            text_line.appendTo($(desc_id));
        }
        // attribute-plug
        for (var i in property["attribute"]["plug"]) {
            var text_line = $("<div></div>");
            var line = property["attribute"]["plug"][i];
            text_line.html(line);
            text_line.addClass("text-gray");
            text_line.appendTo($(desc_id));
        }
        // attribute-special
        for (var i in property["attribute"]["special"]) {
            var text_line = $("<div></div>");
            var line = property["attribute"]["special"][i];
            text_line.html(line);
            text_line.addClass("text-green");
            text_line.appendTo($(desc_id));
        }
        // attribute-suit
        for (var i in property["attribute"]["suit"]) {
            var text_line = $("<div></div>");
            var line = property["attribute"]["suit"][i];
            text_line.html(line);
            text_line.addClass("text-green");
            text_line.appendTo($(desc_id));
        }
        var text_line = $("<div></div>");
        line = "品质等级"+property["level"];
        text_line.html(line);
        text_line.addClass("text-yellow");
        text_line.appendTo($(desc_id));
    }

    for (var i in property["desc"]) {
        var line = property["desc"][i];
        var text_line = $("<div></div>");
        var text = line[0].replace(/\\*n/g, "");
        text_line.html(text);
        text_line.addClass("text-"+line[1]);
        text_line.appendTo($(desc_id));
    }
}

function item_over(e){
    t = e.target;
    $("#desc-tooltip").css("display", "block");
    $("#desc-tooltip").css("left", e.pageX + 50);
    $("#desc-tooltip").css("top", e.pageY + 30);
    $("#desc-tooltip-content").html("");
    property = AUCTION_BY_ID[$(t).attr("itemID")]["property"];

    render_desc("#desc-tooltip-content", property);

    var nowX = e.pageX + 50 + $("#desc-tooltip-content").width() + 30;

    for (var i in property["related"]) {
        var desc_top_id = `#desc-tooltip-${parseInt(i)+1}`;
        var desc_id = `#desc-tooltip-content-${parseInt(i)+1}`;
        $(desc_id).html("");
        $(desc_top_id).css("display", "block");
        $(desc_top_id).css("left", nowX);
        $(desc_top_id).css("top", e.pageY + 30);
        render_desc(desc_id, property["related"][i]);
        nowX += $(desc_top_id).width() + 30;
    }
}

function item_out(e){
    $("#desc-tooltip").css("display", "none");
    $("#desc-tooltip-1").css("display", "none");
    $("#desc-tooltip-2").css("display", "none");
}

function refresh_page(){
//    $.get(`/getTreasure?DungeonID=${DUNGEON_ID}&playerName=${PLAYER_NAME}`, function(result){
//        analyse_treasure(result);
//    });
    $.get(`/getAuction?DungeonID=${DUNGEON_ID}&playerName=${PLAYER_NAME}&PlayerToken=${PLAYER_TOKEN}`, function(result){
        if (result["status"] != 0) {
            error(result["status"]);
        } else {
            analyse_auction(result);
        }
    });
}

refresh_page();

V_treasure_list = new Vue({
    el: '#treasure-list',
    delimiters: ['[[',']]'],
    data: {
        reload_auction: false,
        reload_bids: true,
        bosses: [],
    },
    methods: {
        loadAuction: function(){
            this.bosses = [];
    	    for (var key in AUCTION_BY_BOSS) {
    	        this.bosses.push(key)
    	    }
    	    this.reload_auction = true;
        },
        getSketch: function(item){
            var str = "";
            if ("main" in item["property"]) {
                str = item["property"]["main"] + " " + item["property"]["sketch"].join(" ");
            }
            return str;
        },
        reloadBids: function() {
            this.reload_bids = false;
            this.$nextTick(function() {
                this.reload_bids = true;
            })
        }
    }
});

function xinfa_match(xinfa, property){
    if (xinfa == "") {
        return false;
    }
    var school = MENPAI_DICT[xinfa];
    var attrib = ATTRIB_DICT[xinfa];
    var attrib_extend = attrib;
    if (attrib_extend == "力道" || attrib_extend == "身法") {
        attrib_extend = "外功";
    } else if (attrib_extend == "元气" || attrib_extend == "根骨") {
        attrib_extend = "内功";
    }
    if (property["type"] == "coupon" || (property["type"] == "equipment" && property["subtype"] == "近身武器")) {
        return (school == property["school"] || property["school"] == "通用");
    } else {
        return attrib == property["main"] || attrib_extend == property["main"];
    }
}

function reload_filter(){
    console.log("reload!");
    for (var id in AUCTION_BY_ID) {
        var item = AUCTION_BY_ID[id];
        var display = 1;
        if (item["property"]["type"] == "item") {
            if (V_filter.ignoreMaterials) {
                display = 0;
            }
        } else if (V_filter.schoolOnly || V_filter.xinfaOnly) {
            var baseXinfa = PLAYER_XINFA;
            var secondXinfa = "";
            if (!V_filter.xinfaOnly) {
                for (var xinfa in MENPAI_DICT) {
                    if (xinfa != baseXinfa && MENPAI_DICT[xinfa] == MENPAI_DICT[baseXinfa]) {
                        secondXinfa = xinfa;
                    }
                }
            }
            if (xinfa_match(baseXinfa, item["property"])) {
                display = 1;
            } else if (xinfa_match(secondXinfa, item["property"])) {
                display = 1;
            } else {
                display = 0;
            }
        }
        if (V_filter.fmOnly && item["property"]["class"] != "enchant") {
            display = 0;
        }
        if (V_filter.favoriteOnly && FAVORITE_ITEM[id] == 0) {
            display = 0;
        }
        if (V_filter.openOnly && (ITEM_OPEN[id] == 0 || item["lock"] == 1)) {
            display = 0;
        }
        if (display == 1) {
            $(`#item-${id}`).removeClass("d-none");
        } else  {
            $(`#item-${id}`).addClass("d-none");
        }
    }
}

V_filter = new Vue({
    el: '#filter-setting',
    delimiters: ['[[',']]'],
    data: {
        ignoreMaterials: false,
        schoolOnly: false,
        xinfaOnly: false,
        favoriteOnly: false,
        openOnly: false,
        fmOnly: false,
    },
    methods: {
    }
});

Vue.filter('ownerFormat', function(originVal){
    if (originVal.length == 0) return "-";
    else return originVal.join(",");
});

Vue.filter('priceFormat', function(originVal){
    if (originVal.length == 0) return "-";
    else return originVal.join(",");
});

Vue.filter('dateFormat', function(originVal){
    const dt = new Date(originVal * 1000);
    const y = dt.getFullYear();
    const M = (dt.getMonth() + 1 + '').padStart(2, '0');
    const d = (dt.getDate() + '').padStart(2, '0');
    const h = (dt.getHours() + '').padStart(2, '0');
    const m = (dt.getMinutes() + '').padStart(2, '0');
    const s = (dt.getSeconds() + '').padStart(2, '0');
    return `${y}-${M}-${d} ${h}:${m}:${s}`;
});

Vue.filter('countdownFormat', function(originVal){
    if (originVal == -1) {
        return "";
    } else {
        const m = (parseInt(originVal / 60) + '').padStart(2, '0');
        const s = (originVal % 60 + '').padStart(2, '0');
        return `${m}:${s}`;
    }
});

V_alert = new Vue({
  el: '#float-alert',
  delimiters: ['[[',']]'],
  data: {
  },
  methods: {
  }
});

for (var i = 0; i <= 4; i++) {
    $(`#alert-${i+1}`).hide();
}

function hideAlert(i){
    $(`#alert-${i}`).hide();
    ALERT_VISIBLE[i-1] = 0;
}

function getRpos(player) {
    if (player in PLAYER_INFO) {
        return RPOS_DICT[PLAYER_INFO[player]];
    } else {
        return "?";
    }
}

function export_boss_handle(boss) {
    var lines = [];
    for (var item of AUCTION_BY_BOSS[boss]) {
        var owners = [];
        for (var i in item["currentOwner"]) {
            var rpos = getRpos(item["currentOwner"][i]);
            var str = `(${rpos})${item["currentOwner"][i]}`;
            if (i < item["currentPrice"].length) {
                str = `(${rpos})${item["currentOwner"][i]} ${item["currentPrice"][i]}`;
            }
            owners.push(str);
        }
        var str = owners.join(',')
        var res = `[${item["name"]}] ${str}`;
        lines.push(res);
    }
    var result = lines.join('<br>');
    $('#copyboard').html(result);
    $('#copyboard-modal').modal();
//    var el = document.createElement('input');
//    el.setAttribute('value', result);
//    document.body.appendChild(el);
//    el.select();
//    document.execCommand('copy');
//    document.body.removeChild(el);
//    alert("已导出到剪贴板！");
}

function export_boss(boss){
    if (PLAYER_INFO_UPDATED == 0) {
        $.get(`/getTeam?DungeonID=${DUNGEON_ID}`, function(result){
            console.log(result);
            if (result["status"] != 0) {
                error(result["status"]);
            } else {
                for (var player of result["team"]) {
                    PLAYER_INFO[player["playerName"]] = player["xinfa"];
                }
            }
            PLAYER_INFO_UPDATED = 1;
            export_boss_handle(boss);
        });
    } else {
        export_boss_handle(boss);
    }
}

V_summary = new Vue({
    el: '#summary',
    delimiters: ['[[',']]'],
    data: {
        personal_sum: 0,
        group_sum: 0,
        load_summary: false,
    },
    methods: {
    }
});

