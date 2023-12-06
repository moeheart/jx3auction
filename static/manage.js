V_treasure = new Vue({
  el: '#form-treasure',
  delimiters: ['[[',']]'],
  data: {
    invcode: "",
    boss: "其它",
    treasure: "",
    bosses:[
        "其它", "时风", "乐临川", "牛波", "和正", "关卡", "武云阙", "翁幼之",
        "魏华", "钟不归", "岑伤", "鬼筹", "麒麟", "月泉淮"
        // "张景超", "刘展", "苏凤楼", "韩敬青", "藤原佑野", "李重茂",
    ]
  },
  methods: {
    submit: function() {
        CURRENT_BOSS = this.boss;
        $.get(`/setTreasure?AdminToken=${ADMIN_TOKEN}&DungeonID=${DUNGEON_ID}&boss=${this.boss}&treasure=${this.treasure}`, function(result){
            if (result["status"] != 0) {
                error(result["status"]);
            } else {
                analyse_treasure(result);
            }
        });
    }
  }
});

ALERT_VISIBLE = [0, 0, 0, 0, 0];
TREASURE_BY_BOSS = {};
TREASURE_BY_ID = {};

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

function analyse_treasure(result){
    console.log(result);
    if (result["status"] != "0") {
        error(result["status"]);
    } else {
        var DungeonID = result["DungeonID"]
        var AdminToken = result["AdminToken"]
        var msg = `上传${CURRENT_BOSS}的记录成功！其他队友可以在团员界面看到所有的掉落，你可以继续上传其它BOSS，或者开始拍卖。`;
        if (result["replace"] == 1) {
            var msg = `覆盖${CURRENT_BOSS}的记录成功！其他队友可以在团员界面看到所有的掉落，你可以继续上传其它BOSS，或者开始拍卖。`;
        }
        $("#alert2 p").html(msg);
        $("#alert2").show();
    }
}

V_treasure = new Vue({
  el: '#form-startauction',
  delimiters: ['[[',']]'],
  data: {
    baseNormal: 2000,
    baseCoupon: 10000,
    multiplierCouponRaw: "1/2/2/2/3",
    multiplierCoupon: "1,2,2,2,3",
    baseWeapon: 30000,
    baseJingjian: 20000,
    baseWutiJingjian: 30000,
    baseTexiaoyaozhui: 30000,
    baseTexiaowuqi: 50000,
    stepEquip: 1000,
    baseMaterials: 500,
    stepMaterials: 500,
    baseCharacter: 100,
    stepCharacter: 100,
    combineCharacterRaw: true,
    combineCharacter: 1,
    baseXiaofumo: 100,
    stepXiaofumo: 100,
    baseDafumo: 1000,
    stepDafumo: 1000,
    baseXiaotie: 6000,
    stepXiaotie: 3000,
    baseDatie: 0,
    stepDatie: 10000,
    baseOther: 0,
    stepOther: 1000,
    baseHanzi: 100,
    stepHanzi: 100,
    combineHanziRaw: true,
    combineHanzi: 1,
    tnHalfRaw: true,
    tnHalf: 1,
  },
  methods: {
    submit: function() {
      var str = `/startAuction?AdminToken=${ADMIN_TOKEN}&DungeonID=${DUNGEON_ID}`;
      this.combineCharacter = this.combineCharacterRaw ? 1 : 0;
      this.combineHanzi = this.combineHanziRaw ? 1 : 0;
      this.tnHalf = this.tnHalfRaw ? 1 : 0;
      this.multiplierCoupon = this.multiplierCouponRaw.replace(/\//g, ',');
      dataArray = [
          "baseNormal",
          "baseCoupon",
          "multiplierCoupon",
          "baseWeapon",
          "baseJingjian",
          "baseWutiJingjian",
          "baseTexiaoyaozhui",
          "baseTexiaowuqi",
          "stepEquip",
          "baseMaterials",
          "stepMaterials",
          "baseCharacter",
          "stepCharacter",
          "combineCharacter",
          "baseXiaofumo",
          "stepXiaofumo",
          "baseDafumo",
          "stepDafumo",
          "baseXiaotie",
          "stepXiaotie",
          "baseDatie",
          "stepDatie",
          "baseOther",
          "stepOther",
          "baseHanzi",
          "stepHanzi",
          "combineHanzi",
          "tnHalf",
      ];
      for (var i in dataArray) {
        var s = dataArray[i];
        var value = eval(`this.${s}`);
        str += `&${s}=${value}`;
      }
      $.get(str, function(result){
          start_auction(result);
      });
    }
  }
});

function start_auction(result){
    console.log(result);
    if (result["status"] != "0") {
        error(result["status"], "alert3");
    } else {
        var msg = `拍卖已开始！请通知团员刷新界面，或是尽快进入系统。`;
        $("#alert4 p").html(msg);
        $("#alert4").show(msg);
    }
}

$("#alert2").hide();
$("#alert4").hide();

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

PLAYER_LIST = {}

function refresh_player(){
    $.get(`/getTeamExtend?DungeonID=${DUNGEON_ID}&AdminToken=${ADMIN_TOKEN}`, function(result){
        console.log(result);
        if (result["status"] != 0) {
            error(result["status"]);
        } else {
            PLAYER_LIST = {};
            for (var i = 1; i <= 25; i++) {
                PLAYER_LIST[i] = {"playerName": "", "xinfa": "", "bill": 0, "paid": false}
            }
            for (var player of result["team"]) {
                var pos = player["position"];
                PLAYER_LIST[pos] = player;
            }
            V_player.load();
        }
    });
}

KICK_TARGET = 0;

function kick() {
    $.get(`/kickPlayer?DungeonID=${DUNGEON_ID}&AdminToken=${ADMIN_TOKEN}&position=${KICK_TARGET}`, function(result){
        console.log(result);
        if (result["status"] != 0) {
            error(result["status"]);
        } else {
            setTimeout("refresh_player()", 500);
        }
    });
}

function start_kick(pos){
    // 尝试踢人，弹出窗口确认一下
    KICK_TARGET = pos;
    V_player.kickTarget = PLAYER_LIST[pos]["playerName"];
}

function pay(pos){
    // 在已付款与未付款状态切换
    PLAYER_LIST[pos]["paid"] = !PLAYER_LIST[pos]["paid"];
    V_player.load();
}

$(document).ready(function () {
    for (var i = 1; i <= 25; i++) {
        PLAYER_LIST[i] = {"playerName": "", "xinfa": "", "bill": 0, "paid": false}
    }
    refresh_player();
    refresh_treasure();
});

V_player = new Vue({
  el: '#player-list',
  delimiters: ['[[',']]'],
  data: {
    reload_player: false,
    kickTarget: "",
  },
  methods: {
    load: function(){
        this.reload_player = false;
        this.$nextTick(function() {
            this.reload_player = true;
        })
    },
    reload: function(){
        refresh_player();
    },
  }
});

V_item = new Vue({
  el: '#item-list',
  delimiters: ['[[',']]'],
  data: {
    reload_item: false,
  },
  methods: {
    load: function(){
        this.reload_item = false;
        this.$nextTick(function() {
            this.reload_item = true;
        })
    },
  }
});

function store_treasure(treasure){
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

function refresh_treasure(){
    $.get(`/getTreasure?DungeonID=${DUNGEON_ID}&AdminToken=${ADMIN_TOKEN}`, function(result){
        if (result["status"] != 0) {
            error(result["status"]);
        } else {
            store_treasure(result);
        }
    });
}

function clear(itemID){
    // 重置某个物品
    $.get(`/clearAuction?DungeonID=${DUNGEON_ID}&AdminToken=${ADMIN_TOKEN}&itemID=${itemID}`, function(result){
        if (result["status"] != 0) {
            error(result["status"]);
        } else {
            $(`#iteminfo-${itemID}`).html("重置成功！");
        }
    });
}

function clear_boss(boss){
    // 重置某个BOSS的全部物品
    $.get(`/clearAuction?DungeonID=${DUNGEON_ID}&AdminToken=${ADMIN_TOKEN}&boss=${boss}`, function(result){
        if (result["status"] != 0) {
            error(result["status"]);
        } else {
            for (var item of TREASURE_BY_BOSS[boss]) {
                var itemID = item["itemID"];
                $(`#iteminfo-${itemID}`).html("重置成功！");
            }
        }
    });
}

function lock(itemID){
    // 锁定某个物品
    $.get(`/lockAuction?DungeonID=${DUNGEON_ID}&AdminToken=${ADMIN_TOKEN}&itemID=${itemID}&switch=1`, function(result){
        if (result["status"] != 0) {
            error(result["status"]);
        } else {
            $(`#iteminfo-${itemID}`).html("锁定成功！");
        }
    });
}

function lock_boss(boss){
    // 锁定某个BOSS的全部物品
    $.get(`/lockAuction?DungeonID=${DUNGEON_ID}&AdminToken=${ADMIN_TOKEN}&boss=${boss}&switch=1`, function(result){
        if (result["status"] != 0) {
            error(result["status"]);
        } else {
            for (var item of TREASURE_BY_BOSS[boss]) {
                var itemID = item["itemID"];
                $(`#iteminfo-${itemID}`).html("锁定成功！");
            }
        }
    });
}

function unlock(itemID){
    // 解锁某个物品
    $.get(`/lockAuction?DungeonID=${DUNGEON_ID}&AdminToken=${ADMIN_TOKEN}&itemID=${itemID}&switch=0`, function(result){
        if (result["status"] != 0) {
            error(result["status"]);
        } else {
            $(`#iteminfo-${itemID}`).html("解锁成功！");
        }
    });
}

function unlock_boss(boss){
    // 解锁某个BOSS的全部物品
    $.get(`/lockAuction?DungeonID=${DUNGEON_ID}&AdminToken=${ADMIN_TOKEN}&boss=${boss}&switch=0`, function(result){
        if (result["status"] != 0) {
            error(result["status"]);
        } else {
            for (var item of TREASURE_BY_BOSS[boss]) {
                var itemID = item["itemID"];
                $(`#iteminfo-${itemID}`).html("解锁成功！");
            }
        }
    });
}

function countdown(itemID){
    // 倒数某个物品
    time = V_treasure_list.countdownValue;
    $.get(`/countdownAuction?DungeonID=${DUNGEON_ID}&AdminToken=${ADMIN_TOKEN}&itemID=${itemID}&time=${time}`, function(result){
        console.log(result);
        if (result["status"] != 0) {
            error(result["status"]);
        } else {
            for (var itemID of result["success"]) {
                $(`#iteminfo-${itemID}`).html("倒数成功！");
            }
        }
    });
}

function countdown_boss(boss){
    // 倒数某个BOSS的全部物品
    time = V_treasure_list.countdownValue;
    $.get(`/countdownAuction?DungeonID=${DUNGEON_ID}&AdminToken=${ADMIN_TOKEN}&boss=${boss}&time=${time}`, function(result){
        console.log(result);
        if (result["status"] != 0) {
            error(result["status"]);
        } else {
            for (var itemID of result["success"]) {
                $(`#iteminfo-${itemID}`).html("倒数成功！");
            }
        }
    });
}

V_treasure_list = new Vue({
    el: '#treasure-div',
    delimiters: ['[[',']]'],
    data: {
        reload_treasure: false,
        bosses: [],
        countdownValue: 20,
    },
    methods: {
        load: function(){
            this.bosses = [];
    	    for (var key in TREASURE_BY_BOSS) {
    	        this.bosses.push(key)
    	    }
    	    this.reload_treasure = true;
        },
    }
});


