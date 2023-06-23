
AUCTION_BY_BOSS = {};
AUCTION_BY_ID = {};
ITEM_OPEN = {};
CURRENT_ID = -1;

//function analyse_treasure(treasure){
//    console.log(treasure);
//    var res = treasure["treasure"];
//    for (var i in res) {
//        var item = res[i];
//        var boss = item["boss"];
//        if (!(boss in AUCTION_BY_BOSS)) {
//            AUCTION_BY_BOSS[boss] = [];
//        }
//        AUCTION_BY_BOSS[boss].push({"name": item["name"], "itemID": item["itemID"], "property": item["property"]});
//        AUCTION_BY_ID[item["itemID"]] = {"name": item["name"], "boss": item["boss"], "property": item["property"]}
//    }
//    console.log(AUCTION_BY_BOSS);
//    V_treasure_list.loadTreasure();
//    PLAYER_XINFA = treasure["xinfa"];
//}

$(document).ready(function () {
    namespace = '/auction_info';
    var socket = io.connect(location.protocol + "//" + document.domain + ":" + location.port + namespace);

      socket.on('connect', () => {

        // Automatically connect to general channel
        socket.emit('join',{"channel": DUNGEON_ID, "username":PLAYER_NAME});
      });

    socket.on('bid', function(res) {
        console.log("receive from socket");
        console.log(res);
        // 添加这次更新的内容
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
        item["currentOwner"] = [];
        item["currentPrice"] = [];
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
            FAVORITE_ITEM[i] = 1;
            activate_favorite(res["itemID"], 0);
        }
        if (item["currentOwner"].indexOf(PLAYER_NAME) != -1) {
            $(`#item-${res["itemID"]}`).addClass("owner");
        } else {
            $(`#item-${res["itemID"]}`).removeClass("owner");
        }
        V_treasure_list.reloadBids();
    });
});

function show_attrib(){
    var group_content = {};
    SIMUL_CONTENT = {};
    FAVORITE_ITEM = {};
    ITEM_OPEN = {};
    // 展示打包拍卖、同步拍卖等特殊情况
    for (var i in AUCTION_BY_ID) {
        var item = AUCTION_BY_ID[i];
        ITEM_OPEN[i] = 1;
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
            ITEM_OPEN[i] = 0;
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
            ITEM_OPEN[i] = 0;
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
            var resArray = []
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
    // 计算是否在初始时就处于收藏状态与拥有状态
    for (var i in AUCTION_BY_ID) {
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
            } else {
                $(`#bid-${i}-${j}`).removeClass("available-bid");
            }
        }
        if (item["currentOwner"].indexOf(PLAYER_NAME) != -1) {
            $(`#item-${i}`).addClass("owner");
        }
    }
}

function activate_favorite(itemID, isPress){
    $(`#item-${itemID}`).addClass("favorite");
    if (isPress == 0) {
        $(`#favorite-${itemID}`).addClass("active");
        $(`#favorite-${itemID}`).attr("aria-pressed", "true");
    }
}

function deactivate_favorite(itemID, isPress){
    $(`#item-${itemID}`).removeClass("favorite");
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

function bid(itemID, ensure=0){
    var lowestPrice = get_lowest_price(itemID);
    var price = $(`#bidnum-${itemID}`).val();
    if (price < lowestPrice) {
        error(901);
        return;
    } else if (price >= 10 * lowestPrice && ensure == 0) {
        CURRENT_ID = itemID;
        $('#bid-verify-num').html(price);
        $('#bid-modal').modal();
        return;
    }
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
    return lowestPrice;
}

function bid_low(itemID){
    var lowestPrice = get_lowest_price(itemID);
    $(`#bidnum-${itemID}`).val(lowestPrice);
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
    if (property["type"] == "coupon") {
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
        if (V_filter.favoriteOnly && FAVORITE_ITEM[id] == 0) {
            display = 0;
        }
        if (V_filter.openOnly && ITEM_OPEN[id] == 0) {
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
    },
    methods: {
    }
});

Vue.filter('ownerFormat', function(originVal){
    if (originVal.length == 0) return "-";
    else return originVal.join(",");
});

Vue.filter('priceFormat', function(originVal){
    if (originVal.length == 0) return "0";
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

