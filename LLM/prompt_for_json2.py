import json

# 描述性json -> 代码
prompt_template_json3 = """
你是一个优化专家团队中的专业程序员。团队的目标是解决一个能源系统设备容量规划的最优化问题。您的责任是根据用户需求和模型参数的描述json，构建一个模型参数数据json文件。\
现在给出案例，请学习如何根据新的文本生成新的json。
```
**输入**：
{example_user_input}
{example_para_input}
**输出**：
=====
{example_output}
=====
```

由---分隔的是输入的用户需求和模型参数描述json。
---
{user_input}
{para_input}
---

请注意：
- 只生成json文件，不要生成其他文本。

现在，请深呼吸，逐步完成这个任务。

"""

solver = "gurobipy"

example_user_input = {
    "项目描述": "本项目为榆林科创新城零碳分布式智慧能源中心示范项目，为运动员村进行供冷、供热以及供电服务。运动员村项目包括酒店、运动 员餐厅、办公、教育、住宅、公寓、体育等建筑。项目建设用地面积93347.47 m2，总建筑面积20.6万m2，地上建筑面积14万m2，其中住宅5.6万m2，办公4.9 万m2，酒店及运动员餐厅2.1万m2，健身中心0.5万m2，配套0.9万m2。由于DK1-13#楼酒店及运动员餐厅仅大堂地暖需能源站供应，实际供能面积约为12万m2。",
    "项目地理位置":"陕西省榆林市",
    "土地使用情况":"供能面积约为12万m2",
    "项目供能对象描述": "为运动员村进行供冷、供热以及供电服务",
    "项目预期描述": "最大化系统经济型，实现零碳供应能量，设备包括但不限于光伏、燃料电池、地源热泵、电解槽、电锅炉、热泵、地热井、储氢罐、蓄水箱。"
}
example_para_input = {
    "参数": [
        {
            "类别": "load",
            "内容": "包括建筑类型、冷负荷峰值、电负荷峰值、热负荷峰值、供热月份、供冷月份、供热面积、供电面积、供冷面积"
        },
        {
            "类别": "price",
            "内容": "分时电价、卖电价格、供热单价、供冷单价、氢气价格"
        },
        {
            "类别": "device-pv",
            "内容": "光伏装机上限、光伏装机下限、光伏板单价、光伏板寿命、光伏板效率",
            "符号": "p_max, p_min, cost, life, k_pv",
        },
        {
            "类别": "device-sc",
            "内容": "太阳能集热器装机上限、太阳能集热器装机下限、太阳能集热器单价、太阳能集热器寿命、太阳能集热器效率",
            "符号": "g_max, g_min, cost, life, k_sc",
        },
        {
            "类别": "device-fc",
            "内容": "燃料电池装机上限、燃料电池装机下限、燃料电池单价、燃料电池寿命、燃料电池效率",
            "符号": "p_max, p_min, cost, life, k_fc_p, k_fc_g",
        },
        {
            "类别": "device-el",
            "内容": "电解槽装机上限、电解槽装机下限、电解槽单价、电解槽寿命、电解槽效率",
            "符号": "p_max, p_min, cost, life, k_el",
        },
        {
            "类别": "device-eb",
            "内容": "电锅炉装机上限、电锅炉装机下限、电锅炉单价、电锅炉寿命、电锅炉效率",
            "符号": "p_max, p_min, cost, life, k_eb",
        },
        {
            "类别": "device-hp",
            "内容": "热泵装机上限、热泵装机下限、热泵单价、热泵寿命、热泵效率",
            "符号": "p_max, p_min, cost, life, k_hp_g, k_hp_q",
        },
        {
            "类别": "device-ghp",
            "内容": "地源热泵装机上限、地源热泵装机下限、地源热泵单价、地源热泵寿命、地源热泵效率",
            "符号": "p_max, p_min, cost, life, k_ghp_g, k_ghp_q",
        },
        {
            "类别": "device-gtw",
            "内容": "地热井最大数量、地热井单价、地热井寿命、单个地热井的功率",
            "符号": "number_max, cost, life, g_gtw",
        },
        {
            "类别": "device-hst",
            "内容": "储氢罐最大容量、储氢罐最小容量、储氢罐单价、储氢罐寿命",
            "符号": "h_max, h_min, cost, life",
        },
        {
            "类别": "device-ht",
            "内容": "热水箱最大容量、热水箱最小容量、热水箱单价、热水箱寿命、热水箱最高温度、热水箱最低温度、热水箱损失系数",
            "符号": "m_max, h=m_min, cost, life, g_ht",
        },
        {
            "类别": "carbon",
            "内容": "氢气、电、天然气的碳排放因子"
        },
    ],
}

example_output = {
    "load": {
        "building_type": "Hotel",
        "p_max":300,
        "g_max":1000,
        "q_max":200,
        "g_month":[11,12,1,2,3],
        "q_month":[6,7,8],
        "p_area": 123967.0,
        "g_area": 43967.0,
        "q_area": 123967.0
    },
    "price": {
        "TOU_power": [
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515
        ],
        "p_sel_price": 0,
        "g_price": 5.4,
        "q_price": 9.5,
        "h_price": 17.92
    },
    "device": {
        "pv": {
            "_comment": "photovoltaic, 光伏板",
            "description": "",
            "p_max": 50000,
            "p_min": 0,
            "cost": 700,
            "life": 20,
            "k_pv": 0.21
        },
        "sc": {
            "_comment": "solar collector, 太阳能集热器",
            "description": "",
            "g_max": 0,
            "g_min": 0,
            "cost": 800,
            "life": 20,
            "k_sc": 0.72
        },
        "fc": {
            "_comment": "fuel cell, 燃料电池",
            "description": "",
            "p_max": 10000,
            "p_min": 0,
            "cost": 8000,
            "life": 10,
            "k_fc_p": 15,
            "k_fc_g": 22
        },
        "el": {
            "_comment": "electrolyzer, 电解槽",
            "description": "",
            "p_max": 1000,
            "p_min": 0,
            "cost": 2240,
            "life": 7,
            "k_el": 0.0182
        },
        "eb": {
            "_comment": "electric boiler, 电锅炉",
            "description": "",
            "p_max": 10000,
            "p_min": 0,
            "cost": 500,
            "life": 10,
            "k_eb": 0.9
        },
        "hp": {
            "_comment": "heat pump, 热泵",
            "description": "",
            "p_max": 1000,
            "p_min": 0,
            "cost": 68000,
            "life": 15,
            "k_hp_g": 4.59,
            "k_hp_q": 0
        },
        "ghp": {
            "_comment": "ground source heat pump, 地源热泵",
            "description": "",
            "p_max": 1000,
            "p_min": 0,
            "cost": 3000,
            "life": 15,
            "k_ghp_g": 3.54,
            "k_ghp_q": 4.5
        },
        "gtw": {
            "_comment": "ground thermal well, 地热井",
            "description": "",
            "number_max": 2680,
            "cost": 20000,
            "life": 30,
            "g_gtw": 7
        },
        "hst": {
            "_comment": "hydrogen storage tank, 储氢罐",
            "description": "",
            "h_max": 2000,
            "h_min": 0,
            "cost": 3000,
            "life": 15
        },
        "ht": {
            "_comment": "heat storage tank, 热水箱",
            "description": "",
            "m_max": 10000,
            "m_min": 0,
            "cost": 0.5,
            "life": 20,
            "t_max": 80,
            "t_min": 20,
            "miu_loss": 0.01
        },
        "ct": {
            "_comment": "cool storage tank, 冷水箱",
            "description": "",
            "m_max": 500000,
            "m_min": 0,
            "cost": 0.5,
            "life": 15,
            "t_max": 13,
            "t_min": 4,
            "miu_loss": 0.01
        }
    },
    "carbon": {
        "alpha_h2":1.74,
        "alpha_e":0.5839,
        "alpha_EO":0.8922,
        "alpha_gas":1.535
    }
}

user_input = {
    "项目描述": "本项目为榆林科创新城零碳分布式智慧能源中心示范项目，为运动员村进行供冷、供热以及供电服务。运动员村项目包括酒店、运动 员餐厅、办公、教育、住宅、公寓、体育等建筑。项目建设用地面积93347.47 m2，总建筑面积20.6万m2，地上建筑面积14万m2，其中住宅5.6万m2，办公4.9 万m2，酒店及运动员餐厅2.1万m2，健身中心0.5万m2，配套0.9万m2。由于DK1-13#楼酒店及运动员餐厅仅大堂地暖需能源站供应，实际供能面积约为12万m2。",
    "项目地理位置":"陕西省榆林市",
    "土地使用情况":"供能面积约为12万m2",
    "项目供能对象描述": "为运动员村进行供冷、供热以及供电服务",
    "项目预期描述": "最大化系统经济型，实现零碳供应能量，设备包括但不限于光伏、燃料电池、地源热泵、电解槽、电锅炉、热泵、地热井、储氢罐、蓄水箱。但是燃料电池容量不低于500kW。光伏板装机不超过2000kW,燃料电池的装机容量等于电解槽的装机容量。"
}
para_input = {
        "参数": [
        {
            "类别": "load",
            "内容": "包括建筑类型、冷负荷峰值、电负荷峰值、热负荷峰值、供热月份、供冷月份、供热面积、供电面积、供冷面积"
        },
        {
            "类别": "price",
            "内容": "分时电价、卖电价格、供热单价、供冷单价、氢气价格"
        },
        {
            "类别": "device-pv",
            "内容": "光伏装机上限、光伏装机下限、光伏板单价、光伏板寿命、光伏板效率",
            "符号": "p_max, p_min, cost, life, k_pv"
        },
        {
            "类别": "device-fc",
            "内容": "燃料电池装机上限、燃料电池装机下限、燃料电池单价、燃料电池寿命、燃料电池效率",
            "符号": "p_max, p_min, cost, life, k_fc_p, k_fc_g"
        },
        {
            "类别": "device-el",
            "内容": "电解槽装机上限、电解槽装机下限、电解槽单价、电解槽寿命、电解槽效率",
            "符号": "p_max, p_min, cost, life, k_el"
        },
        {
            "类别": "device-eb",
            "内容": "电锅炉装机上限、电锅炉装机下限、电锅炉单价、电锅炉寿命、电锅炉效率",
            "符号": "p_max, p_min, cost, life, k_eb"
        },
        {
            "类别": "device-hp",
            "内容": "热泵装机上限、热泵装机下限、热泵单价、热泵寿命、热泵效率",
            "符号": "p_max, p_min, cost, life, k_hp_g, k_hp_q"
        },
        {
            "类别": "device-ghp",
            "内容": "地源热泵装机上限、地源热泵装机下限、地源热泵单价、地源热泵寿命、地源热泵效率",
            "符号": "p_max, p_min, cost, life, k_ghp_g, k_ghp_q"
        }
    ]
}

prompt = prompt_template_json3.format(
    solver=solver,
    example_user_input = json.dumps(example_user_input, ensure_ascii=False),
    example_para_input = json.dumps(example_para_input, ensure_ascii=False),
    example_output=json.dumps(example_output, ensure_ascii=False),
    user_input = json.dumps(user_input, ensure_ascii=False),
    para_input = json.dumps(para_input, ensure_ascii=False)
    )

print(prompt)
