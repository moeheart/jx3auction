$("#form-manager").submit(function(){

});

V_manager = new Vue({
  el: '#form-manager',
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
        console.log("Click!");
        console.log(this.invcode);
        console.log(this.map);
    }
  }
});

V_member = new Vue({
  el: '#form-member',
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
        "无方",
        "灵素",
        "孤风诀",
    ]
  },
  methods: {
    submit: function() {
        console.log("Click!");
    }
  }
});