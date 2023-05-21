
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

