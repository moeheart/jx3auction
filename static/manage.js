V_treasure = new Vue({
  el: '#form-treasure',
  delimiters: ['[[',']]'],
  data: {
    invcode: "",
    boss: "其它",
    treasure: "",
    bosses:[
        "其它", "时风", "乐临川", "牛波", "和正", "关卡", "武云阙", "翁幼之",
        "张景超", "刘展", "苏凤楼", "韩敬青", "藤原佑野", "李重茂",
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
    baseCoupon: 20000,
    baseWeapon: 30000,
    baseJingjian: 30000,
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
      dataArray = [
          "baseNormal",
          "baseCoupon",
          "baseWeapon",
          "baseJingjian",
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
    $.get(`/getTeam?DungeonID=${DUNGEON_ID}`, function(result){
        console.log(result);
        if (result["status"] != 0) {
            error(result["status"]);
        } else {
            PLAYER_LIST = {};
            for (var i = 1; i <= 25; i++) {
                PLAYER_LIST[i] = {"playerName": "", "xinfa": ""}
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

$(document).ready(function () {
    for (var i = 1; i <= 25; i++) {
        PLAYER_LIST[i] = {"playerName": "", "xinfa": ""}
    }
    refresh_player();
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


