ERROR_CONTENT = {
    "0": "成功。",
    "100": "未知的参数错误。",
    "101": "缺少参数。",
    "102": "参数格式不正确。",
    "103": "position必须是1-25之间的整数。",
    "104": "掉落的格式不正确",
    "200": "未知的逻辑错误。",
    "201": "秘境ID不存在。",
    "202": "团长权限验证失败。",
    "203": "成员权限验证失败。",
    "204": "地图验证失败。",
    "205": "BOSS名称验证失败。",
    "206": "角色名已经被注册，请换一个角色名。",
    "207": "位置已经被占用，请换一个位置。",
    "208": "拍卖已经开始，无法再次开始。",
    "209": "拍卖还未开始，无法进行拍卖操作。",
    "210": "拍卖已经结束，无法进行拍卖操作。",
    "211": "物品不存在。",
    "212": "出价低于起拍价。",
    "213": "出价不是最小加价的整数倍。",
    "214": "不能在在打包拍卖或者同步拍卖的非主物品上操作。",
    "215": "同步出价的数量大于可用数量。",
    "300": "未知的结果错误。",
    "301": "结果为空。"
}

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
            analyse_treasure(result);
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

function analyse_treasure(result){
    console.log(result);
    if (result["status"] != "0") {
        error(result["status"], "alert1");
    } else {
        var DungeonID = result["DungeonID"]
        var AdminToken = result["AdminToken"]
        var msg = `上传${CURRENT_BOSS}的记录成功！其他队友可以在团员界面看到所有的掉落，你可以继续上传其它BOSS，或者开始拍卖。`;
        $("#alert2 p").html(msg);
        $("#alert2").show(msg);
    }
}

V_treasure = new Vue({
  el: '#form-startauction',
  delimiters: ['[[',']]'],
  data: {
    baseNormal: 2000,
    baseCoupon: 20000,
    baseWeapon: 15000,
    baseJingjian: 30000,
    baseTexiaoyaozhui: 3000,
    baseTexiaowuqi: 30000,
    stepEquip: 1000,
    baseMaterials: 500,
    stepMaterials: 500,
    baseCharacter: 100,
    stepCharacter: 100,
    combineCharacter: true,
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
    combineHanzi: true
  },
  methods: {
    submit: function() {

    }
  }
});



$("#alert1").hide();
$("#alert2").hide();
$("#alert3").hide();
$("#alert4").hide();



