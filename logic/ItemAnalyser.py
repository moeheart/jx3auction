# Created by moeheart at 12/01/2022
# 物品分析. 实现一个物品分析类，一次性调用所有资源，并且可以在线调用.

import re

ATTRIB_TYPE = {
    # 会心
    "atAllTypeCriticalStrike": ["会心", 1, 1, 1, 1, 1, 1, 0],
    "atPhysicsCriticalStrike": ["会心", 1, 1, 0, 0, 0, 0, 0],
    "atMagicCriticalStrike": ["会心", 1, 0, 1, 1, 1, 1, 0],
    "atSolarCriticalStrike": ["会心", 1, 0, 1, 0, 0, 0, 0],
    "atLunarCriticalStrike": ["会心", 1, 0, 0, 1, 0, 0, 0],
    "atNeutralCriticalStrike": ["会心", 1, 0, 0, 0, 1, 0, 0],
    "atPoisonCriticalStrike": ["会心", 1, 0, 0, 0, 0, 1, 0],
    "atSolarAndLunarCriticalStrike": ["会心", 1, 0, 1, 1, 0, 0, 0],
    "atPhysicsCriticalStrikeBaseRate": ["会心", 1, 1, 0, 0, 0, 0, 0.0001],
    "atSolarCriticalStrikeBaseRate": ["会心", 1, 0, 1, 0, 0, 0, 0.0001],
    "atLunarCriticalStrikeBaseRate": ["会心", 1, 0, 0, 1, 0, 0, 0.0001],
    "atNeutralCriticalStrikeBaseRate": ["会心", 1, 0, 0, 0, 1, 0, 0.0001],
    "atPoisonCriticalStrikeBaseRate": ["会心", 1, 0, 0, 0, 0, 1, 0.0001],
    # 会心效果
    "atCriticalDamagePowerBase": ["会心效果", 1, 1, 1, 1, 1, 1, 0],
    "atPhysicsCriticalDamagePowerBase": ["会心效果", 1, 1, 0, 0, 0, 0, 0],
    "atMagicCriticalDamagePowerBase": ["会心效果", 1, 0, 1, 1, 1, 1, 0],
    "atSolarCriticalDamagePowerBase": ["会心效果", 1, 0, 1, 0, 0, 0, 0],
    "atLunarCriticalDamagePowerBase": ["会心效果", 1, 0, 0, 1, 0, 0, 0],
    "atNeutralCriticalDamagePowerBase": ["会心效果", 1, 0, 0, 0, 1, 0, 0],
    "atPoisonCriticalDamagePowerBase": ["会心效果", 1, 0, 0, 0, 0, 1, 0],
    "atSolarAndLunarCriticalDamagePowerBase": ["会心效果", 1, 0, 1, 1, 0, 0, 0],
    "atPhysicsCriticalDamagePowerBaseKiloNumRate": ["会心效果", 1, 1, 0, 0, 0, 0, 1/1024],
    "atMagicCriticalDamagePowerBaseKiloNumRate": ["会心效果", 1, 0, 1, 1, 1, 1, 1/1024],
    "atSolarCriticalDamagePowerBaseKiloNumRate": ["会心效果", 1, 0, 1, 0, 0, 0, 1/1024],
    "atLunarCriticalDamagePowerBaseKiloNumRate": ["会心效果", 1, 0, 0, 1, 0, 0, 1/1024],
    "atNeutralCriticalDamagePowerBaseKiloNumRate": ["会心效果", 1, 0, 0, 0, 1, 0, 1/1024],
    "atPoisonCriticalDamagePowerBaseKiloNumRate": ["会心效果", 1, 0, 0, 0, 0, 1, 1/1024],
    # 破防
    "atPhysicsOvercomeBase": ["破防", 1, 1, 0, 0, 0, 0, 0],
    "atMagicOvercome": ["破防", 1, 0, 1, 1, 1, 1, 0],
    "atSolarOvercomeBase": ["破防", 1, 0, 1, 0, 0, 0, 0],
    "atLunarOvercomeBase": ["破防", 1, 0, 0, 1, 0, 0, 0],
    "atNeutralOvercomeBase": ["破防", 1, 0, 0, 0, 1, 0, 0],
    "atPoisonOvercomeBase": ["破防", 1, 0, 0, 0, 0, 1, 0],
    "atSolarAndLunarOvercomeBase": ["破防", 1, 0, 1, 1, 0, 0, 0],
    "atPhysicsOvercomePercent": ["破防", 0, 1, 0, 0, 0, 0, 1/1024],
    "atSolarOvercomePercent": ["破防", 0, 0, 1, 0, 0, 0, 1/1024],
    "atLunarOvercomePercent": ["破防", 0, 0, 0, 1, 0, 0, 1/1024],
    "atNeutralOvercomePercent": ["破防", 0, 0, 0, 0, 1, 0, 1/1024],
    "atPoisonOvercomePercent": ["破防", 0, 0, 0, 0, 0, 1, 1/1024],
    # 加速
    "atHasteBase": ["加速", 1, 1, 1, 1, 1, 1, 0],
    "atHasteBasePercentAdd": ["加速", 0, 1, 1, 1, 1, 1, 1/1024],
    "atUnlimitHasteBasePercentAdd": ["加速", 0, 1, 1, 1, 1, 1, 1/1024],
    # 治疗
    "atTherapyPowerBase": ["治疗", 1, 1, 1, 1, 1, 1, 0],
    "atTherapyPowerPercent": ["治疗", 0, 1, 1, 1, 1, 1, 1/1024],
    # 主属性
    "atVitalityBase": ["体质", 1, 1, 1, 1, 1, 1, 0],
    "atStrengthBase": ["力道", 1, 1, 1, 1, 1, 1, 0],
    "atAgilityBase": ["身法", 1, 1, 1, 1, 1, 1, 0],
    "atSpunkBase": ["元气", 1, 1, 1, 1, 1, 1, 0],
    "atSpiritBase": ["根骨", 1, 1, 1, 1, 1, 1, 0],
    "atVitalityBasePercentAdd": ["体质", 0, 1, 1, 1, 1, 1, 1/1024],
    "atStrengthBasePercentAdd": ["力道", 0, 1, 1, 1, 1, 1, 1/1024],
    "atAgilityBasePercentAdd": ["身法", 0, 1, 1, 1, 1, 1, 1/1024],
    "atSpunkBasePercentAdd": ["元气", 0, 1, 1, 1, 1, 1, 1/1024],
    "atSpiritBasePercentAdd": ["根骨", 0, 1, 1, 1, 1, 1, 1/1024],
    "atBasePotentialAdd": ["全属性", 1, 1, 1, 1, 1, 1, 0],
    # 攻击
    "atPhysicsAttackPowerBase": ["攻击", 1, 1, 0, 0, 0, 0, 0],
    "atMagicAttackPowerBase": ["攻击", 1, 0, 1, 1, 1, 1, 0],
    "atSolarAttackPowerBase": ["攻击", 1, 0, 1, 0, 0, 0, 0],
    "atLunarAttackPowerBase": ["攻击", 1, 0, 0, 1, 0, 0, 0],
    "atNeutralAttackPowerBase": ["攻击", 1, 0, 0, 0, 1, 0, 0],
    "atPoisonAttackPowerBase": ["攻击", 1, 0, 0, 0, 0, 1, 0],
    "atSolarAndLunarAttackPowerBase": ["攻击", 1, 0, 1, 1, 0, 0, 0],
    "atPhysicsAttackPowerPercent": ["攻击", 0, 1, 0, 0, 0, 0, 1/1024],
    "atMagicAttackPowerPercent": ["攻击", 0, 0, 1, 1, 1, 1, 1/1024],
    "atSolarAttackPowerPercent": ["攻击", 0, 0, 1, 0, 0, 0, 1/1024],
    "atLunarAttackPowerPercent": ["攻击", 0, 0, 0, 1, 0, 0, 1/1024],
    "atNeutralAttackPowerPercent": ["攻击", 0, 0, 0, 0, 1, 0, 1/1024],
    "atPoisonAttackPowerPercent": ["攻击", 0, 0, 0, 0, 0, 1, 1/1024],
    # 无双
    "atStrainBase": ["无双", 1, 1, 1, 1, 1, 1, 0],
    "atStrainPercent": ["无双", 0, 1, 1, 1, 1, 1, 1/1024],
    # 破招
    "atSurplusValueBase": ["破招", 1, 1, 1, 1, 1, 1, 0],
    # 防御
    "atPhysicsShieldBase": ["防御", 1, 1, 0, 0, 0, 0, 0],
    "atSolarShieldBase": ["防御", 1, 1, 1, 0, 0, 0, 0],
    "atLunarShieldBase": ["防御", 1, 1, 0, 1, 0, 0, 0],
    "atNeutralShieldBase": ["防御", 1, 1, 0, 0, 1, 0, 0],
    "atPoisonShieldBase": ["防御", 1, 1, 0, 0, 0, 1, 0],
    "atPhysicsShieldAdditional": ["防御", 0, 1, 0, 0, 0, 0, 0],
    "atMagicShield": ["防御", 0, 0, 1, 1, 1, 1, 0],
    "atPhysicsShieldPercent": ["防御%", 0, 1, 0, 0, 0, 0, 1/1024],
    "atSolarMagicShieldPercent": ["防御%", 0, 0, 1, 0, 0, 0, 1/1024],
    "atLunarMagicShieldPercent": ["防御%", 0, 0, 0, 1, 0, 0, 1/1024],
    "atNeutralMagicShieldPercent": ["防御%", 0, 0, 0, 0, 1, 0, 1/1024],
    "atPoisonMagicShieldPercent": ["防御%", 0, 0, 0, 0, 0, 1, 1/1024],
    # 招架
    "atParryBase": ["招架", 1, 1, 1, 1, 1, 1, 0],
    "atParryBaseRate": ["招架", 0, 1, 1, 1, 1, 1, 0.0001],
    # 拆招
    "atParryValueBase": ["拆招", 1, 1, 1, 1, 1, 1, 0],
    "atParryValuePercent": ["拆招", 0, 1, 1, 1, 1, 1, 1/1024],
    # 闪避
    "atDodge": ["闪避", 1, 1, 1, 1, 1, 1, 0],
    "atDodgeBaseRate": ["闪避", 0, 1, 1, 1, 1, 1, 0.0001],
    # 御劲
    "atToughnessBase": ["御劲", 1, 1, 1, 1, 1, 1, 0],
    "atToughnessBaseRate": ["御劲", 0, 1, 1, 1, 1, 1, 0.0001],
    # 化劲
    "atDecriticalDamagePowerBase": ["化劲", 1, 1, 1, 1, 1, 1, 0],
    "atDecriticalDamagePowerPercent": ["化劲", 0, 1, 1, 1, 1, 1, 1/1024],
    # 仇恨
    "atActiveThreatCoefficient": ["仇恨", 0, 1, 1, 1, 1, 1, 1/1024],

    #### 不属于属性的增益
    "atAllDamageAddPercent": ["伤害变化", 1, 1, 1, 1, 1, 1, 0],
    "atAllPhysicsDamageAddPercent": ["伤害变化", 1, 1, 0, 0, 0, 0, 0],
    "atAllMagicDamageAddPercent": ["伤害变化", 1, 0, 1, 1, 1, 1, 0],
    "atPhysicsDamageCoefficient": ["受伤增加", 0, 1, 0, 0, 0, 0, 1/1024],
    "atSolarDamageCoefficient": ["受伤增加", 0, 0, 1, 0, 0, 0, 1/1024],
    "atLunarDamageCoefficient": ["受伤增加", 0, 0, 0, 1, 0, 0, 1/1024],
    "atNeutralDamageCoefficient": ["受伤增加", 0, 0, 0, 0, 1, 0, 1/1024],
    "atPoisonDamageCoefficient": ["受伤增加", 0, 0, 0, 0, 0, 1, 1/1024],
    "atAllShieldIgnorePercent": ["无视防御A", 1, 1, 1, 1, 1, 1, 0],
}

LONGNAME_DICT = {"会心": "会心等级",
                 "治疗": "治疗成效",
                 "攻击": "攻击",
                 "破防": "破防等级",
                 "无双": "无双等级",
                 "会心效果": "会心效果等级",
                 "破招": "破招值",
                 "防御": "防御等级",
                 "加速": "加速等级",
                 "招架": "招架等级",
                 "闪避": "闪避等级",
                 "拆招": "拆招值",
                 "仇恨": "招式产生威胁",
                 }

QUALITY_CODE = {
    "1": "白色",
    "2": "绿色",
    "3": "蓝色",
    "4": "紫色",
    "5": "橙色",
}

SUBTYPE_CODE = {
    "0": "近身武器",
    "1": "远程武器",
    "2": "衣服",
    "3": "帽子",
    "4": "项链",
    "5": "戒指",
    "6": "腰带",
    "7": "腰坠",
    "8": "裤子",
    "9": "鞋子",
    "10": "护腕",
}

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
    "太玄经": "衍天",
    "无方": "药宗",
    "灵素": "药宗",
    "孤锋诀": "刀宗",
}

def getAttributeDesc(attrib):
    '''
    获取属性字段的中文描述.
    '''
    if attrib in ATTRIB_TYPE:
        singleAttrib = ATTRIB_TYPE[attrib]
        name = singleAttrib[0]
        prefix = "？"
        longname = name
        if name in LONGNAME_DICT:
            longname = LONGNAME_DICT[name]
        if name not in ["会心", "破防", "攻击", "会心效果", "防御"]:
            prefix = ""
        elif singleAttrib[2] == 1 and singleAttrib[3] == 1:
            prefix = "全"
        elif singleAttrib[2] == 1:
            prefix = "外功"
        elif singleAttrib[3] == 1 and singleAttrib[4] == 1 and singleAttrib[5] == 1 and singleAttrib[6] == 1:
            prefix = "内功"
        elif singleAttrib[3] == 1 and singleAttrib[4] == 1:
            prefix = "阴阳内功"
        elif singleAttrib[3] == 1:
            prefix = "阳性内功"
        elif singleAttrib[4] == 1:
            prefix = "阴性内功"
        elif singleAttrib[5] == 1:
            prefix = "混元内功"
        elif singleAttrib[6] == 1:
            prefix = "毒性内功"
        full_name = prefix + longname
        return name, full_name
    else:
        return attrib, attrib

class ItemAnalyser():
    '''
    物品分析类.
    '''

    def GetMenpai(self, xinfa):
        '''
        通过心法获取门派.
        '''
        if xinfa in MENPAI_DICT:
            return MENPAI_DICT[xinfa]
        else:
            return xinfa

    def GetText(self, rawText):
        '''
        尝试从游戏中的文字描述整理出合适的表现.
        '''
        l = rawText.split('"')
        i = 1
        res = []
        while i + 1 < len(l):
            text = l[i]
            control = l[i+1]
            reResult = re.search("<ENCHANT ([0-9]+)>", text)
            if reResult:
                number = reResult.group(1)
                enchantDesc = "未知"
                # print(number)
                if number in self.enchant:
                    enchantDesc = self.enchant[number]
                text = re.sub("<ENCHANT [0-9]+>", enchantDesc, text)
            if control[1:9] == "font=105":
                res.append([text, "green"])
            elif control[1:9] == "font=100":
                res.append([text, "yellow"])
            else:
                res.append([text, control])
                # print(control)
            i += 2
        return res

    def GetQuality(self, qualityCode):
        '''
        通过品质的数字获取品质.
        '''
        if qualityCode in QUALITY_CODE:
            return QUALITY_CODE[qualityCode]
        else:
            return qualityCode

    def GetSubtype(self, subtypeCode):
        '''
        通过部位的数字获取部位.
        '''
        if subtypeCode in SUBTYPE_CODE:
            return SUBTYPE_CODE[subtypeCode]
        else:
            return subtypeCode

    def GetAttribute(self, input, subtype):
        '''
        根据属性ID获取文字版属性及其类型.
        '''
        # TODO 实现
        if subtype == "belong":
            key = input[0]
            value1 = input[1]
            value2 = input[2]
            if value2 == "" and input[4] != "":
                value2 = "%.1f%%" % (int(input[4]) / 1024 * 100)
        elif input in self.attrib:
            key = self.attrib[input][0]
            value1 = self.attrib[input][1]
            value2 = self.attrib[input][2]
            if value2 == "" and self.attrib[input][4] != "":
                value2 = "%.1f%%" % (int(self.attrib[input][4]) / 1024 * 100)
        else:
            return input, "base"
        attrib, attribDesc = getAttributeDesc(key)
        if key == "atSkillEventHandler":
            desc = ""
            if value2 in ["2399", "2496"]:
                desc = "装备：命中后获得水·百川气劲，自身提升治疗效果，可叠加十层，持续6秒。不可与该类其他气劲并存。"
            elif value2 in ["2400", "2497"]:
                desc = "装备：命中后获得水·灭虚气劲，自身提升内功攻击，可叠加十层，持续6秒。不可与该类其他气劲并存。"
            elif value2 in ["2401", "2498"]:
                desc = "装备：命中后获得水·斩流气劲，自身提升外功攻击，可叠加十层，持续6秒。不可与该类其他气劲并存。"
            elif value2 in ["2402", "2499"]:
                desc = "装备：命中后获得水·封山气劲，自身提升外功防御及内功防御，可叠加十层，持续6秒。不可与该类其他气劲并存。"
            return desc, attrib, "special"

        if subtype == "belong":
            desc = "%s提高%s" % (attribDesc, value2)
            return desc, attrib, "base"
        elif subtype == "extra":
            desc = "%s提高%s" % (attribDesc, value2)
            if attrib in ["力道", "身法", "元气", "根骨", "体质"]:
                return desc, attrib, "base"
            else:
                return desc, attrib, "extra"
        elif subtype == "plug":
            desc = "镶嵌孔：%s提高？" % (attribDesc)
            return desc, attrib, "plug"

        return input, input, "base"


    def GetSingleItemByName(self, input):
        '''
        通过输入掉落的名称，可以获取所有需要进行展示的信息。副本名用于辅助判断一些重名情况。
        如果提供心法名，还可以显示对应的兑换类装备在兑换之后的结果。
        inputs:
            - `name` 装备名。例如`肆级五彩石`。
            - `map` 副本名。例如`25人英雄西津渡`。
            - `xinfa` 心法。例如`冰心诀`。用于实现兑换牌的展示。
        outputs:
            - `available` 是否可用。必定出现。1表示可用，0表示不可用。如果为0，那么接下来的所有属性都不会出现。
            - `name` 与输入相同。但如果有别名，那么返回标准命名。
            - `icon` 图标ID。
            - `quality` 物品的品质，白/绿/蓝/紫/橙。
            - `desc` 物品的描述，用一个数组类型记录所有的描述。每个描述又分为两个部分，其一为文本，其二为颜色。
            - `type` 物品的种类。包括以下几种取值：
                - `equipment` 装备
                - `coupon` 兑换牌，包括门派套装牌子和武器盒子
                - `item` 非装备类型
            - `related` 对兑换牌类的补充，包含其可以换到的装备名，数组格式。如果需要获取其属性则需要重复调用此方法.
            - `class` 对兑换牌/非装备类型的进一步细分，主要用于打包拍卖的场景，包括以下种类
                - `coupon` 兑换牌
                - `materials` 包括五行石、五彩石、生活技能材料
                - `enchant` 包括强化附魔，主要是吃鸡附魔、大附魔（将这些单列出来是由于心法适配的需求）
                - `character` 包括侠客的低阶掉落物品，主要是茶饼、维峰丹
                - `xiaotie` 包括小铁
                - `datie` 包括大铁（这玩意真的会有？）
                - `hanzi` 包括剑侠情缘汉字，在活动期间会出现。
                - `other` 包括不在上面分类中的其它内容。常见的有：侠客秘籍、挂件等特殊掉落。
            - `attribute` 只在装备或兑换牌类型中出现。其内部也是一个pythondict，包括：
                - `base` 白字属性，数组格式，用文字字符串描述。
                - `extra` 绿字属性，数组格式，用文字字符串描述。
                - `plug` 镶嵌栏属性，数组格式，用文字字符串描述。
                - `suit` 套装属性，数组格式，用文字字符串描述。
                - `special` 特效属性，数组格式，用文字字符串描述。
            - `subtype` 装备的子分类，如项链、腰带
            - `level` 装备的品级。
            - `main` 主属性。包括`力道`*4，`防御`，`治疗`，`内功`/`外功`（用于精简)，`武器`，`套装`。
            - `school` 装备的门派。用于在`main`为`套装`或`武器`时区分其适用范围。这个属性在`coupon`类型中也会出现。
            - `sketch` 属性简述，包括`会心`、`纯疗`、`招架`等。
            - 完成情况：治疗心法首饰1、防具1、武器1；输出心法1；防御心法1；特效腰坠1、特效武器1；sketch重写1；精简1；牌子1、武器盒子1；明教1；种类1、部位优化1；文字优化1；
            - 物品对齐：五行石1、五彩石1、玛瑙1、附魔1、茶饼1、小铁1、大铁1、挂件1、汉字1、秘籍1、牌子1、武器盒1、藏剑武器1
        '''

        output = {"available": 0}
        print("[Test2]", input["name"])
        if input["name"] not in self.name:
            return output

        idList = self.name[input["name"]]
        # if len(idList) > 1:
        #     return output

        item = self.item[idList[0]]
        output = {"available": 1,
                  "name": input["name"],
                  "icon": item["iconid"],
                  "quality": self.GetQuality(item.get("quality", "0")),
                  "desc": item["desc"],
                  }
        # 获得物品属性.
        if item["type"] == "equipment":
            # 装备
            output["type"] = "equipment"
            output["subtype"] = item["subtype"]
            output["level"] = item["level"]
            attribute = {}
            baseAttribute = []
            extraAttribute = []
            plugAttribute = []
            suitAttribute = []
            specialAttribute = []
            atkBase = 0
            atkRand = 0
            atkSpeed = 0
            main = "未知"
            sketch = []
            hasZhiLiao = False
            hasSpecial = False
            for attrib in item["belongRaw"]:
                if attrib[0] in ["atMeleeWeaponDamageBase", "atRangeWeaponDamageBase"]:
                    atkBase = int(attrib[1])
                elif attrib[0] in ["atMeleeWeaponDamageRand", "atRangeWeaponDamageRand"]:
                    atkRand = int(attrib[1])
                elif attrib[0] in ["atMeleeWeaponAttackSpeedBase"]:
                    atkSpeed = int(attrib[2])
                    res = "近身伤害提高%d-%d" % (atkBase, atkBase + atkRand)
                    baseAttribute.append(res)
                    res = "每秒伤害%d" % ((atkBase+ atkRand / 2) / atkSpeed * 16)
                    baseAttribute.append(res)
                elif attrib[0] in ["atRangeWeaponAttackSpeedBase"]:
                    atkSpeed = int(attrib[2])
                    res = "远程伤害提高%d-%d" % (atkBase, atkBase + atkRand)
                    baseAttribute.append(res)
                    res = "每秒伤害%d" % ((atkBase+ atkRand / 2) / atkSpeed * 16)
                    baseAttribute.append(res)
                else:
                    res, attName, attType = self.GetAttribute(attrib, "belong")
                    if attType == "base":
                        baseAttribute.append(res)
                    if attName in ["力道", "身法", "元气", "根骨"]:
                        main = attName
            # for attrib in item["baseRaw"]:
            #     res, attType = self.GetAttribute(attrib, "base")
            #     if attType == "base":
            #         baseAttribute.append(res)
            for attrib in item["extraRaw"]:
                res, attName, attType = self.GetAttribute(attrib, "extra")
                if attType == "extra":
                    extraAttribute.append(res)
                    if attName in ["会心", "破防", "无双", "破招", "闪避", "招架", "御劲", "会心效果", "防御", "加速", "治疗"]:
                        if attName == "会心效果":
                            sketch.append("会效")
                        elif attName == "防御":
                            if self.attrib[attrib][0] == "atPhysicsShieldBase":
                                sketch.append("外防")
                            else:
                                sketch.append("内防")
                        elif attName == "治疗":
                            hasZhiLiao = True
                        else:
                            sketch.append(attName)
                elif attType == "base":
                    baseAttribute.append(res)
                elif attType == "special":
                    specialAttribute.append(res)
                    hasSpecial = True
            for plug in item["plugRaw"]:
                res, attName, attType = self.GetAttribute(plug, "plug")
                plugAttribute.append(res)
            # 人工统计特效
            for special in item["specialRaw"]:
                hasSpecial = True
                # if special[0] == "6800":  # 风特效
                #     if special[1] == "101":
                #         specialAttribute.append("使用：大幅度提升自身内功破防等级，持续15秒。")
                #     elif special[1] == "102":
                #         specialAttribute.append("使用：大幅度提升自身外功破防等级，持续15秒。")
                #     elif special[1] == "103":
                #         specialAttribute.append("使用：大幅度提升自身治疗效果，持续15秒。")
                #     elif special[1] == "100":
                #         specialAttribute.append("使用：大幅度提升自身外功防御等级，持续15秒。")
                # elif special[0] == "":
                #     pass
            # 套装效果，东西有点多，还是不写了
            if item["subtype"] == "近身武器":
                main = "武器"
            elif main == "未知":
                if item["setID"] != "":
                    main = "套装"
                else:
                    main = item["magickind"]
            if sketch == [] and hasZhiLiao:
                sketch = ["纯疗"]
            if hasSpecial:
                sketch = ["特效"] + sketch
            if int(item["maxstrengthlevel"]) < 6 and "特效" not in sketch:
                sketch = ["精简"] + sketch
            if item["setID"] != "":
                suitAttribute.append("这件装备有套装效果。")
            attribute = {"base": baseAttribute,
                         "extra": extraAttribute,
                         "plug": plugAttribute,
                         "suit": suitAttribute,
                         "special": specialAttribute,
                         }
            output["attribute"] = attribute
            output["main"] = main
            output["school"] = item["school"]
            output["sketch"] = sketch
            output["related"] = []
            output["maxlevel"] = item["maxstrengthlevel"]
        elif item["type"] == "item":
            output["type"] = "item"
            output["class"] = item.get("class", "other")
            output["related"] = []
        elif item["type"] == "coupon":
            output["type"] = "coupon"
            output["class"] = item.get("class", "other")
            output["related"] = item["related"]
            output["school"] = item["school"]
            name = input["name"]
            # 直接在武器库里寻找对应的装备
            if name in self.weapon:
                menpai = self.GetMenpai(input["xinfa"])
                if menpai in self.weapon[name]:
                    output["related"] = self.weapon[name][menpai]

        # print("==========")
        # for key in output:
        #     print(key, output[key])

        return output

    def GetExtendItemByName(self, input):
        '''
        通过输入掉落的名称，可以获取所有需要进行展示的信息。副本名用于辅助判断一些重名情况。
        如果提供心法名，还可以显示对应的兑换类装备在兑换之后的详细数据。
        方法为在logic.ItemAnalyser.GetSingleItemByName的基础上，将related中的结果替换为独立查询的结果。
        inputs：
        - `name` 装备名。例如`揽江护腕·万花`。
        - `map` 副本名。例如`25人英雄西津渡`。
        - `xinfa` 心法。例如`冰心诀`。用于实现兑换牌的展示。
        outputs：
        - `result` 数组格式，大部分与调用GetSingleItemByName的结果相同.
            - `related` 这里不再是字符串，而是再次调用GetSingleItemByName的结果.
        '''
        output = self.GetSingleItemByName(input)
        for i in range(len(output["related"])):
            equipName = output["related"][i]
            if type(equipName) is type("123"):
                childResult = self.GetSingleItemByName({"name": equipName, "map": input["map"], "xinfa": input["xinfa"]})
                output["related"][i] = childResult
        return output

    def loadSingleFile(self, path, scene):
        '''
        从文件中读取装备，并打上对应的标签保存在data中.
        params:
        - path: 文件路径
        - scene: 表的编号，可能是6,7,8
        '''
        header = []
        header_index = {}
        first = True
        with open(path, 'r', encoding='gbk') as f:
            for line in f:
                if first:
                    header = line.strip('\n').split('\t')
                    for i in range(len(header)):
                        header_index[header[i]] = i
                    first = False
                else:
                    # 记录装备
                    content = line.strip('\n').split('\t')
                    name = content[header_index["Name"]]
                    subtype = content[header_index["SubType"]]
                    level = content[header_index["Level"]]
                    quality = content[header_index["Quality"]]
                    magickind = content[header_index["MagicKind"]]
                    magictype = content[header_index["MagicType"]]
                    uiid = content[header_index["UiID"]]
                    belongRaw = []
                    for i in range(1, 4):
                        # 这些属性先只做记录, 等到生成装备的时候再加载.
                        key = content[header_index["Base%dType" % i]]
                        value1 = content[header_index["Base%dMin" % i]]
                        value2 = content[header_index["Base%dMin" % i]]
                        if key not in ["atInvalid", ""]:
                            belongRaw.append([key, value1, value2])
                    extraRaw = []
                    for i in range(1, 13):
                        # 这些属性先只做记录, 等到生成装备的时候再加载.
                        index = "Magic%dType" % i
                        value = content[header_index[index]]
                        if value not in ["0", ""]:
                            extraRaw.append(value)
                    plugRaw = []
                    for i in range(1, 4):
                        index = "DiamondAttributeID%d" % i
                        value = content[header_index[index]]
                        if value not in ["0", ""]:
                            plugRaw.append(value)
                    specialRaw = []
                    skillid = content[header_index["SkillID"]]
                    skilllevel = content[header_index["SkillLevel"]]
                    if skillid not in ["", "0"]:
                        specialRaw.append([skillid, skilllevel])
                    equip = {"type": "equipment",
                             "subtype": self.GetSubtype(subtype),
                             "level": level,
                             "quality": quality,
                             "magickind": magickind,
                             "magictype": magictype,
                             "uiid": uiid,
                             "belongRaw": belongRaw,
                             "extraRaw": extraRaw,
                             "plugRaw": plugRaw,
                             "specialRaw": specialRaw,
                             "setID": content[header_index["SetID"]],
                             "maxstrengthlevel" : content[header_index["MaxStrengthLevel"]],
                             "school": content[header_index["BelongSchool"]],
                    }
                    self.item[uiid] = equip
                    if name not in self.name:
                        self.name[name] = []
                    self.name[name].append(uiid)
                    # 记录武器
                    if subtype == "0" and content[header_index["GetType"]] == "副本":
                        map = "未知"
                        if level == "10150":
                            map = "神兵玉匣·普通西津渡"
                        elif level == "11150" and content[header_index["MaxStrengthLevel"]] == "6":
                            map = "神兵玉匣·英雄西津渡"
                        elif level == "11150" and content[header_index["MaxStrengthLevel"]] == "4":
                            map = "神兵玉匣·英雄西津渡·奇"
                        elif level == "12450" and content[header_index["MaxStrengthLevel"]] == "6":
                            map = "神兵玉匣·英雄武狱黑牢"
                        elif level == "12450" and content[header_index["MaxStrengthLevel"]] == "4":
                            map = "神兵玉匣·英雄武狱黑牢·奇"
                        menpai = content[header_index["BelongSchool"]]
                        if map in self.weapon:
                            if menpai not in self.weapon[map]:
                                self.weapon[map][menpai] = []
                            self.weapon[map][menpai].append(name)

    def LoadEquipTable(self):
        '''
        读取装备表.
        '''
        TRINKET_PATH = 'resources/Custom_Trinket.tab'
        ARMOR_PATH = 'resources/Custom_Armor.tab'
        WEAPON_PATH = 'resources/Custom_Weapon.tab'
        self.loadSingleFile(TRINKET_PATH, 6)
        self.loadSingleFile(ARMOR_PATH, 7)
        self.loadSingleFile(WEAPON_PATH, 8)

    def LoadAttrib(self):
        '''
        读取属性表. 通常装备表的属性需要从属性表中读取.
        '''
        ATTRIB_PATH = 'resources/Attrib.tab'
        first = True
        with open(ATTRIB_PATH, 'r', encoding='gbk') as f:
            for line in f:
                if first:
                    first = False
                else:
                    content = line.strip('\n').split('\t')
                    self.attrib[content[0]] = [content[2], content[3], content[4], content[5], content[6]]

    def LoadEnchant(self):
        '''
        读取增益表. 通常记录了附魔类的文字描述.
        '''
        ENCHANT_PATH = 'resources/Enchant.tab'
        first = True
        with open(ENCHANT_PATH, 'r', encoding='gbk') as f:
            for line in f:
                if first:
                    first = False
                else:
                    content = line.strip('\n').split('\t')
                    self.enchant[content[0]] = content[3]

    def LoadItem(self):
        '''
        读取物品表. 负责非装备物品的大部分记录，同时还为装备读取图标.
        '''
        ITEM_PATH = 'resources/item.txt'
        header = []
        header_index = {}
        first = True
        with open(ITEM_PATH, 'r', encoding='gbk') as f:
            for line in f:
                if first:
                    header = line.strip('\n').split('\t')
                    for i in range(len(header)):
                        header_index[header[i]] = i
                    first = False
                else:
                    content = line.strip('\n').split('\t')
                    itemid = content[header_index["ItemID"]]
                    iconid = content[header_index["IconID"]]
                    name = content[header_index["Name"]]
                    desc = self.GetText(content[header_index["Desc"]])
                    if itemid in self.item and self.item[itemid].get("type", "") == "equipment":
                        # 是装备类的物品
                        self.item[itemid]["iconid"] = iconid
                        self.item[itemid]["desc"] = desc
                    else:
                        # 是非装备物品，尝试获取更完整的数据.
                        self.item[itemid] = {}
                        self.item[itemid]["iconid"] = iconid
                        self.item[itemid]["desc"] = desc
                        self.item[itemid]["type"] = "item"
                        if name not in self.name:
                            self.name[name] = []
                        self.name[name].append(itemid)
                        self.item[itemid]["quality"] = "4"
                        if name in ["五行石（六级）", "伍级五彩石", "猫眼石"]:
                            self.item[itemid]["class"] = "materials"
                        elif name in ["肆级五彩石", "玛瑙"]:
                            self.item[itemid]["class"] = "materials"
                            self.item[itemid]["quality"] = "3"
                        elif "断流心岩" in name or "天堑奇" in name:
                            self.item[itemid]["class"] = "enchant"
                        elif name in ["上品茶饼", "维峰丹"]:
                            self.item[itemid]["class"] = "character"
                        elif "陨铁" in name:
                            self.item[itemid]["class"] = "xiaotie"
                        elif "玄晶" in name:
                            self.item[itemid]["class"] = "datie"
                            self.item[itemid]["quality"] = "5"
                        elif name in ["剑", "侠", "情", "缘"]:
                            self.item[itemid]["class"] = "hanzi"
                            self.item[itemid]["quality"] = "5"
                        elif "展锋" in name or "揽江" in name or "濯心" in name or "藏剑武器" in name:
                            self.item[itemid]["class"] = "coupon"
                            self.item[itemid]["type"] = "coupon"
                            self.item[itemid]["related"] = []
                            # 调整套装的描述，并根据描述寻找对应的装备
                            newDesc = []
                            for i in range(len(desc)):
                                if i == 0:
                                    newDesc.append(desc[i])
                                if desc[i][0][0] == "[":
                                    newDesc.append([desc[i][0], "purple"])
                                    subname = desc[i][0].strip('[').strip(']')
                                    self.item[itemid]["related"].append(subname)
                            self.item[itemid]["desc"] = newDesc
                            if "藏剑武器" in name:
                                self.item[itemid]["school"] = "藏剑"
                            else:
                                self.item[itemid]["school"] = name.split("·")[1]
                        elif "神兵玉匣" in name:
                            self.item[itemid]["class"] = "coupon"
                            self.item[itemid]["type"] = "coupon"
                            self.item[itemid]["related"] = []
                            self.item[itemid]["school"] = "通用"

    def __init__(self):
        '''
        初始化. 读取与物品相关的几个文件，并获取所有资源.
        '''
        self.name = {}  # 记录名称和物品ID的对应关系.
        self.item = {}
        self.attrib = {}
        self.enchant = {}
        self.weapon = {"神兵玉匣·普通西津渡": {}, "神兵玉匣·英雄西津渡": {}, "神兵玉匣·英雄西津渡·奇": {}, "神兵玉匣·英雄武狱黑牢": {}, "神兵玉匣·英雄武狱黑牢·奇": {}}
        self.LoadAttrib()
        self.LoadEquipTable()
        self.LoadEnchant()
        self.LoadItem()
        # print(self.weapon)

if __name__ == "__main__":
    item_analyser = ItemAnalyser()
    res = item_analyser.GetSingleItemByName({"name": "清蕊指环", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "清蕊坠", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "清蕊下裳", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "丹青誓", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "湘崖坠", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "湘崖护手", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "雪梅寒", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "凝青箭囊", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "怀南靴", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "山灵坠", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "擂川岳", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "笛泣", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "乱山横", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "闲璧裤", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "揽江·落华靴", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "揽江·挽沙靴", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "山灵靴", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "五行石（六级）", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "肆级五彩石", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "玛瑙", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "天堑奇琨·伤·腰", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "断流心岩·戒指（根骨）", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "上品茶饼", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "维峰丹", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "劫烬陨铁", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "太一玄晶", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "五行石（六级）", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "剑", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "《易筋经·秘卷》", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "焚金阙", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "揽江护腕·万花", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "神兵玉匣·英雄西津渡", "map": "25人英雄西津渡", "xinfa": "离经易道"})
    res = item_analyser.GetSingleItemByName({"name": "藏剑武器·满楼行乐", "map": "25人英雄西津渡", "xinfa": "离经易道"})