
TREASURE_BY_BOSS = {};
TREASURE_BY_ID = {}

function analyse_treasure(treasure){
    console.log(treasure);
    var res = treasure["treasure"];
    for (var i in res) {
        var item = res[i];
        var boss = item["boss"];
        if (!(boss in TREASURE_BY_BOSS)) {
            TREASURE_BY_BOSS[boss] = [];
        }
        TREASURE_BY_BOSS[boss].push({"name": item["name"], "itemID": item["itemID"], "property": item["property"]});
        TREASURE_BY_ID[item["itemID"]] = {"name": item["name"], "boss": item["boss"], "property": item["property"]}
    }
    console.log(TREASURE_BY_BOSS);
    V_treasure_list.load();
    PLAYER_XINFA = treasure["xinfa"];
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
    property = TREASURE_BY_ID[$(t).attr("itemID")]["property"];

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
    $.get(`/getTreasure?DungeonID=${DUNGEON_ID}&playerName=${PLAYER_NAME}`, function(result){
        analyse_treasure(result);
    });
}

refresh_page();

V_treasure_list = new Vue({
    el: '#treasure-list',
    delimiters: ['[[',']]'],
    data: {
        reload_treasure: false,
        bosses: [],
    },
    methods: {
        load: function(){
            this.bosses = [];
    	    for (var key in TREASURE_BY_BOSS) {
    	        this.bosses.push(key)
    	    }
    	    this.reload_treasure = true;
        },
        getSketch: function(item){
            var str = "";
            if ("main" in item["property"]) {
                str = item["property"]["main"] + " " + item["property"]["sketch"].join(" ");
            }
            return str;
        }
    }
});

MENPAI_DICT = {
    "花间游": "万花",
    "离经易道": "万花",
    "冰心诀": "七秀",
    "云裳心经": "七秀",
    "紫霞功": "纯阳",
    "太虚剑意": "纯阳",
    "傲血战意": "天策",
    "铁牢律": "天策",
    "易筋经": "少林",
    "洗髓经": "少林",
    "问水诀": "藏剑",
    "山居剑意": "藏剑",
    "毒经": "五毒",
    "补天诀": "五毒",
    "惊羽诀": "唐门",
    "天罗诡道": "唐门",
    "焚影圣诀": "明教",
    "明尊琉璃体": "明教",
    "笑尘诀": "丐帮",
    "分山劲": "苍云",
    "铁骨衣": "苍云",
    "莫问": "长歌",
    "相知": "长歌",
    "北傲诀": "霸刀",
    "凌海诀": "蓬莱",
    "隐龙诀": "凌雪",
    "无方": "药宗",
    "灵素": "药宗",
    "孤锋诀": "刀宗",
}

ATTRIB_DICT = {
    "花间游": "元气",
    "离经易道": "治疗",
    "冰心诀": "根骨",
    "云裳心经": "治疗",
    "紫霞功": "根骨",
    "太虚剑意": "身法",
    "傲血战意": "力道",
    "铁牢律": "防御",
    "易筋经": "元气",
    "洗髓经": "防御",
    "问水诀": "身法",
    "山居剑意": "身法",
    "毒经": "根骨",
    "补天诀": "治疗",
    "惊羽诀": "力道",
    "天罗诡道": "元气",
    "焚影圣诀": "元气",
    "明尊琉璃体": "防御",
    "笑尘诀": "力道",
    "分山劲": "身法",
    "铁骨衣": "防御",
    "莫问": "根骨",
    "相知": "治疗",
    "北傲诀": "力道",
    "凌海诀": "身法",
    "隐龙诀": "身法",
    "无方": "根骨",
    "灵素": "治疗",
    "孤锋诀": "力道",
}

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
    for (var id in TREASURE_BY_ID) {
        var item = TREASURE_BY_ID[id];
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
        if (display == 1) {
            $(`#item-${id}`).removeClass("d-none");
        } else  {
            $(`#item-${id}`).addClass("d-none");
        }
    }
}

function auto_bid(itemID){

}

function bid(itemID){

}

function bid_low(itemID){

}

V_filter = new Vue({
    el: '#filter-setting',
    delimiters: ['[[',']]'],
    data: {
        ignoreMaterials: false,
        schoolOnly: false,
        xinfaOnly: false,
    },
    methods: {
    }
});

