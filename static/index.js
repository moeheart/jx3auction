
V_manager = new Vue({
  el: '#form-manager',
  delimiters: ['[[',']]'],
  data: {
    invcode: "",
    map: "25人普通武狱黑牢",
    maps:[
      "25人普通西津渡",
      "25人英雄西津渡",
      "25人普通武狱黑牢",
      "25人英雄武狱黑牢",
    ]
  },
  methods: {
    submit: function() {
        $.get(`/createDungeon?map=${this.map}&code=${this.invcode}`, function(result){
            analyse_create(result);
        });
    }
  }
});

V_member = new Vue({
  el: '#form-member',
  delimiters: ['[[',']]'],
  data: {
    dungeon: "",
    name: "",
    xinfa: "花间游",
    group: "1",
    position: "1",
    xinfas:[
        "花间游",
        "离经易道",
        "冰心诀",
        "云裳心经",
        "紫霞功",
        "太虚剑意",
        "傲血战意",
        "铁牢律",
        "易筋经",
        "洗髓经",
        "问水诀",
        "山居剑意",
        "毒经",
        "补天诀",
        "惊羽诀",
        "天罗诡道",
        "焚影圣诀",
        "明尊琉璃体",
        "笑尘诀",
        "分山劲",
        "铁骨衣",
        "莫问",
        "相知",
        "北傲诀",
        "凌海诀",
        "隐龙诀",
        "太玄经",
        "无方",
        "灵素",
        "孤锋诀",
    ]
  },
  methods: {
    submit: function() {
        var pos = (parseInt(this.group)-1) * 5 + parseInt(this.position);
        CURRENT_NAME = this.name;
        CURRENT_DUNGEON = this.dungeon;
        $.get(`/registerTeam?DungeonID=${this.dungeon}&playerName=${this.name}&xinfa=${this.xinfa}&position=${pos}`, function(result){
            console.log("2");
            analyse_register(result, this.name, this.dungeon);
        });
    }
  }
});

function error(code, targetID) {
    var msg = "错误" + code + "：未知错误";
    if (code in ERROR_CONTENT) {
        msg = "错误" + code + "：" + ERROR_CONTENT[code];
    }
    $(`#${targetID} p`).html(msg);
    $(`#${targetID}`).show();
}

function analyse_create(result){
    console.log(result);
    if (result["status"] != "0") {
        error(result["status"], "alert1");
    } else {
        var DungeonID = result["DungeonID"]
        var AdminToken = result["AdminToken"]
        var msg = `创建成功！你的副本编号为：${DungeonID}，团长令牌为：${AdminToken}，点击<a href="/manage.html?AdminToken=${AdminToken}&DungeonID=${DungeonID}" class="alert-link" target="_blank">此处</a>进入管理页面。`;
        $("#alert2 p").html(msg);
        $("#alert2").show(msg);
    }
}

function analyse_register(result, playerName, DungeonID){
    console.log(result);
    if (result["status"] != "0") {
        error(result["status"], "alert3");
    } else {
        var msg = `加入团队成功！点击<a href="/treasure.html?playerName=${CURRENT_NAME}&DungeonID=${CURRENT_DUNGEON}" class="alert-link" target="_blank">此处</a>进入掉落页面。`;
        $("#alert4 p").html(msg);
        $("#alert4").show(msg);
    }
}
$("#alert1").hide();
$("#alert2").hide();
$("#alert3").hide();
$("#alert4").hide();
