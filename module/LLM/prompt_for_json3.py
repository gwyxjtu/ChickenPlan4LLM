import json

# 描述性json -> 代码
prompt_template_json3 = """
你是一个优化专家团队中的专业程序员。团队的目标是解决一个能源系统设备容量规划的最优化问题。您的责任是根据两个json文件编写{solver}代码。其中第一个文件是模型参数、优化变量、约束、目标函数的json文件，第二个文件是模型参数数据json文件。\
现在给出案例，请学习如何根据新的文本生成新的{solver}代码。
```
**输入**：
{example_describe_input}
{example_para_input}

**输出**：
=====
{example_output}
=====
```

由---分隔的是输入的设备信息，包括背景知识、设备描述、约束条件、参数和变量。您需要根据这些信息，编写{solver}代码。
---
{describe_input}
{para_input}
---

请注意：
- 只生成代码和"====="行，不要生成其他文本。
- 假定参数和变量已经定义，并且已经导入了gurobipy作为gp。现在根据此生成代码，并将其放在"====="行之间。

现在，请深呼吸，逐步完成这个任务。

"""

solver = "gurobipy"
example_describe_input = {
    "问题描述": "重要！！！",
    "背景知识": "构建能源系统规划问题，在满足设备运行约束、能量平衡约束的前提下，构建经济最优目标函数，计算得到设备容量和全年运行数据",
    "约束条件": [
        "设备容量约束：光伏板装机容量 p_pv_installed 不得大于 2000kW",
        "设备容量约束：氢燃料电池装机容量 p_fc_installed 不得小于 500kW",
        "设备容量约束：氢燃料电池装机容量 p_fc_installed 等于电解槽装机容量 p_el_installed",
        "设备容量约束：各时段光伏板装机容量 p_pv_installed 不得大于其最大装机容量 p_pv_max",
        "设备容量约束：各时段太阳能集热器装机容量 g_sc_installed 不得大于其最大装机容量 g_sc_max",
        "设备容量约束：各时段氢燃料电池装机容量 p_fc_installed 不得大于其最大装机容量 p_fc_max",
        "设备容量约束：各时段电解槽装机容量 p_el_installed 不得大于其最大装机容量 p_el_max",
        "设备容量约束：各时段电锅炉装机容量 p_eb_installed 不得大于其最大装机容量 p_eb_max",
        "设备容量约束：各时段热泵装机容量 p_hp_installed 不得大于其最大装机容量 p_hp_max",
        "设备容量约束：各时段地源热泵装机容量 p_ghp_installed 不得大于其最大装机容量 p_ghp_max",
        "设备容量约束：各时段储氢罐装机容量 h_hstorage_installed 不得大于其最大装机容量 h_hstorage_max",
        "设备容量约束：各时段蓄水箱装机容量 m_tank_installed 不得大于其最大装机容量 m_tank_max",
        "设备运行约束：各时段光伏板产电量 p_pv 不得大于其转换效率 k_pv、装机容量 p_pv_installed 和当前太阳辐射强度 r_solar 的乘积",
        "设备运行约束：各时段太阳能集热器产热量 g_sc 不得大于其转换效率 k_sc、装机容量 g_sc_installed 和当前太阳辐射强度 r_solar 的乘积",
        "设备运行约束：各时段氢燃料电池产电量 p_fc 等于其电转换效率 k_fc_p 和耗氢量 h_fc 的乘积",
        "设备运行约束：各时段氢燃料电池产热量 g_fc 等于其热交换效率 eta_fc、热转换效率 k_fc_g 和耗氢量 h_fc 的乘积",
        "设备运行约束：各时段氢燃料电池发电量 p_fc 不得大于其装机容量 p_fc_installed",
        "设备运行约束：各时段电解槽产氢量 h_el 不得大于其转换效率 k_el 和电解槽耗电量 p_el 的乘积",
        "设备运行约束：各时段电解槽耗电量 p_el 不得大于其装机容量 p_el_installed",
        "设备运行约束：各时段电锅炉产热量 g_eb 等于其转换效率 k_eb 和耗电量 p_eb 的乘积",
        "设备运行约束：各时段电锅炉耗电量 p_eb 不得大于其装机容量 p_eb_installed",
        "设备运行约束：各时段热泵产热量 g_hp 等于其热转换效率 k_hp_g 和耗电量 p_hp 的乘积",
        "设备运行约束：各时段热泵产冷量 q_hp 等于其冷转换效率 k_hp_q 和耗电量 p_hp 的乘积",
        "设备运行约束：各时段热泵耗电量 p_hp 不得大于其装机容量 p_hp_installed",
        "设备运行约束：各时段地源热泵产热量 g_ghp 等于其热转换效率 k_ghp_g 和耗电量 p_ghp 的乘积",
        "设备运行约束：各时段地源热泵产冷量 q_ghp 等于其冷转换效率 k_ghp_q 和耗电量 p_ghp 的乘积",
        "设备运行约束：各时段地源热泵耗电量 p_ghp 不得大于其装机容量 p_ghp_installed",
        "设备运行约束：各时段地源热泵从所有地热井取热量 num_gtw_installed * g_gtw 不得小于",
        "设备运行约束：系统中只有氢燃料电池和电锅炉可以灌热，因此各时段地源热泵向地热井灌热量 g_ghp_inject 不得大于氢燃料电池产热量 g_fc、电锅炉产热量 g_eb 的和",
        "设备运行约束：各时段储氢罐储氢变化量 h_delta_hstorage 等于 下一时刻储氢罐储氢量 h_hstorage_next 减去当前时刻储氢罐储氢量 h_hstorage",
        "设备运行约束：i+1 时刻应满足 h_hstorage_next[i] 等于 h_hstorage[i+1]，而调度周期结束时，储氢罐储氢量 h_hstorage_next[-1] 等于初始时刻储氢罐储氢量 h_hstorage[0]",
        "设备运行约束：各时段储氢罐储氢量 h_hstorage 不得大于其装机容量 h_hstorage_installed",
        "设备运行约束：各时段蓄水箱供热量 g_tank 等于蓄水箱储能变化量 g_delta_tank 和其热损失量 g_tank_loss 之和的负值",
        "设备运行约束：各时段蓄水箱储能变化量 g_delta_tank 等于水箱中水的质量 m_tank_installed、水的比热 c_water 和水箱中水温变化量（下一时刻水箱温度 t_tank_next 减去当前时刻水箱水温 t_tank）的乘积",
        "设备运行约束：各时段蓄水箱热损失量 g_tank_loss 等于热损失系数 k_tank_loss 和水箱中水的质量 m_tank_installed、水的比热 c_water 和当前时刻水箱水温 t_tank 与环境温度 t_amb 的差值的乘积",
        "设备运行约束：i+1 时刻应满足 t_tank_next[i] 等于 t_tank[i+1]，而调度周期结束时，蓄水箱中水温 t_tank_next[-1] 等于初始时刻水温 t_tank[0]",
        "能量平衡约束：各时段系统的电力供应（包括从电网购电 p_pur、光伏产电 p_pv 和燃料电池产电 p_fc）减去向电网售电量 p_sell 应等于电力需求（包括电负载 p_load、电解槽耗电量 p_el、电锅炉耗电量 p_eb、热泵耗电量 p_hp 和地源热泵耗电量 p_ghp）",
        "能量平衡约束：各时段系统的热负荷 g_load 等于管网供热量 g_tube 和地源热泵供热 g_ghp 的和",
        "能量平衡约束：各时段管网供热量 g_tube 等于太阳能集热器产热量 g_sc、氢燃料电池产热量 g_fc、电锅炉产热量 g_eb、热泵产热量 g_hp 和蓄水箱供热量 g_tank 的和减去地源热泵向地热井灌热量 g_ghp_inject",
        "能量平衡约束：各时段储氢罐储氢变化量 h_delta_hstorage 等于从氢气市场购氢量 h_pur 和电解槽产氢量 h_el 的和减去氢燃料电池耗氢量 h_fc"
    ],
    "目标函数": "最小化所有设备年化投资费用和系统运行费用之和，其中各设备的年化投资费用由设备单价、设备容量和设备寿命计算，系统运行费用包括买电费用和买氢费用减去向电网卖电收入",
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
            "类别": "device-sc",
            "内容": "太阳能集热器装机上限、太阳能集热器装机下限、太阳能集热器单价、太阳能集热器寿命、太阳能集热器效率",
            "符号": "g_max, g_min, cost, life, k_sc"
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
        },
        {
            "类别": "device-gtw",
            "内容": "地热井最大数量、地热井单价、地热井寿命、单个地热井的功率",
            "符号": "number_max, cost, life, g_gtw"
        },
        {
            "类别": "device-hst",
            "内容": "储氢罐最大容量、储氢罐最小容量、储氢罐单价、储氢罐寿命",
            "符号": "h_max, h_min, cost, life"
        },
        {
            "类别": "device-ht",
            "内容": "热水箱最大容量、热水箱最小容量、热水箱单价、热水箱寿命、热水箱最高温度、热水箱最低温度、热水箱损失系数",
            "符号": "m_max, h=m_min, cost, life, g_ht"
        },
        {
            "类别": "carbon",
            "内容": "氢气、电、天然气的碳排放因子"
        }
    ],
    "变量": [
        {
            "符号": "h_pur",
            "定义": "从氢气市场购氢量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "p_pur",
            "定义": "从电网购电量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "p_sell",
            "定义": "向电网卖电量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "p_pv_installed",
            "定义": "光伏板装机容量",
            "形状": []
        },
        {
            "符号": "g_sc_installed",
            "定义": "太阳能集热器装机容量",
            "形状": []
        },
        {
            "符号": "p_fc_installed",
            "定义": "氢燃料电池装机容量",
            "形状": []
        },
        {
            "符号": "p_el_installed",
            "定义": "电解槽装机容量",
            "形状": []
        },
        {
            "符号": "p_eb_installed",
            "定义": "电锅炉装机容量",
            "形状": []
        },
        {
            "符号": "p_hp_installed",
            "定义": "热泵装机容量",
            "形状": []
        },
        {
            "符号": "p_ghp_installed",
            "定义": "地源热泵装机容量",
            "形状": []
        },
        {
            "符号": "num_gtw_installed",
            "定义": "地热井装机数量",
            "形状": []
        },
        {
            "符号": "h_hstorage_installed",
            "定义": "储氢罐装机容量",
            "形状": []
        },
        {
            "符号": "m_tank_installed",
            "定义": "蓄水箱装机容量",
            "形状": []
        },
        {
            "符号": "p_pv",
            "定义": "光伏板产电量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "g_sc",
            "定义": "太阳能集热器产热量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "p_fc",
            "定义": "氢燃料电池产电量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "g_fc",
            "定义": "氢燃料电池产热量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "h_fc",
            "定义": "氢燃料电池耗氢量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "h_el",
            "定义": "电解槽产氢量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "p_el",
            "定义": "电解槽耗电量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "g_eb",
            "定义": "电锅炉产热量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "p_eb",
            "定义": "电锅炉耗电量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "g_hp",
            "定义": "热泵产热量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "q_hp",
            "定义": "热泵产冷量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "p_hp",
            "定义": "热泵耗电量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "g_ghp",
            "定义": "地源热泵产热量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "q_ghp",
            "定义": "地源热泵产冷量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "p_ghp",
            "定义": "地源热泵耗电量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "g_ghp_inject",
            "定义": "地源热泵向地热井灌热量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "h_delta_hstorage",
            "定义": "储氢罐储氢变化量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "h_hstorage",
            "定义": "储氢罐储氢量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "h_hstorage_next",
            "定义": "储氢罐下一时刻储氢量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "g_tank",
            "定义": "蓄水箱供热量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "g_delta_tank",
            "定义": "蓄水箱储能变化量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "g_tank_loss",
            "定义": "蓄水箱热损失量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "t_tank",
            "定义": "蓄水箱水温",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "t_tank_next",
            "定义": "蓄水箱下一时刻水温",
            "形状": [
                "period"
            ]
        }
    ]
}

example_para_input = {
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
example_output = r"""
def planning_problem(period_data, input_param):
    # ------ Create model ------
    model = gp.Model("OptModel")

    # ------ Parameters input ------
    # --- 参数输入，时序数据包括电、热、冷、光照强度；单一数据包括碳排放因子、能源价格、设备价格、设备效率等 ---
    # --- 各时段数据 ---
    p_load = period_data["p_load"]*input_param["load"]["p_area"]  # 电负荷乘以面积
    g_load = period_data["g_load"]*input_param["load"]["g_area"]  # 热负荷乘以面积
    q_load = period_data["q_load"]*input_param["load"]["q_area"]  # 冷负荷乘以面积
    r_solar = period_data["r_solar"]  # 光照强度

    period = len(p_load)  # 总时段数

    # 展示负荷信息
    print("热负荷总量{}，冷负荷总量：{}，电负荷总量：{}".format(sum(g_load), sum(q_load), sum(p_load)))
    print("热负荷峰值{}，冷负荷峰值：{}，电负荷峰值：{}".format(max(g_load), max(q_load), max(p_load)))
    print("-" * 10 + "g, q, e_load" + "-" * 10)
    p_load, g_load, q_load, r_solar = np.array(p_load), np.array(g_load), np.array(q_load), np.array(r_solar)
    r_solar = r_solar * 4000 # 单位转化
    # --- 碳排放因子 ---
    alpha_e = input_param["carbon"]["alpha_e"]  # 电网排放因子 kg/kWh
    # --- 能源价格 ---
    p_price = input_param["price"]["TOU_power"] * 365  # 分时电价
    p_sel_price = input_param["price"]["p_sel_price"]  # 卖电价格
    h_price = input_param["price"]["h_price"]  # 买氢价格

    c = 4.2 / 3600  # 水的比热容
    M = 1e7  # 大 M
    # --- 各种设备的价格 ---
    cost_pv = input_param["device"]["pv"]["cost"]
    cost_sc = input_param["device"]["sc"]["cost"]
    cost_fc = input_param["device"]["fc"]["cost"]
    cost_el = input_param["device"]["el"]["cost"]
    cost_eb = input_param["device"]["eb"]["cost"]
    cost_hp = input_param["device"]["hp"]["cost"]
    cost_ghp = input_param["device"]["ghp"]["cost"]
    cost_gtw = input_param["device"]["gtw"]["cost"]
    cost_hst = input_param["device"]["hst"]["cost"]
    cost_ht = input_param["device"]["ht"]["cost"]  # yuan/kwh

    # --- 各种设备的效率系数，包括产热、制冷、发电、热转换等 ---
    k_pv = input_param["device"]["pv"]["k_pv"]
    k_sc = input_param["device"]["sc"]["k_sc"]
    k_fc_p = input_param["device"]["fc"]["k_fc_p"]
    k_fc_g = input_param["device"]["fc"]["k_fc_g"]
    eta_ex = 0.95
    k_el = input_param["device"]["el"]["k_el"]
    k_eb = input_param["device"]["eb"]["k_eb"]
    k_hp_g = input_param["device"]["hp"]["k_hp_g"]
    k_hp_q = input_param["device"]["hp"]["k_hp_q"]
    k_ghp_g = input_param["device"]["ghp"]["k_ghp_g"]
    k_ghp_q = input_param["device"]["ghp"]["k_ghp_q"]
    g_gtw = input_param["device"]["gtw"]["g_gtw"]

    g_gtw = input_param["device"]["gtw"]["g_gtw"]
    mu_ht_loss = 0.001

    # ------ Variables ------
    h_pur = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_pur{t}") for t in range(period)]  # hydrogen purchase
    p_pur = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_pur{t}") for t in range(period)]  # power purchase
    p_sel = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_sel{t}") for t in range(period)]  # power sold

    p_pv_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["pv"]["p_max"], name=f"s_pv_inst")  # ub=13340,
    p_pv = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_pv{t}") for t in range(period)]

    g_sc_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["sc"]["g_max"], name=f"s_sc_inst")
    g_sc = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_sc{t}") for t in range(period)]

    p_fc_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["fc"]["p_max"], name=f"p_fc_inst")
    h_fc = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_fc{t}") for t in range(period)]  # 燃料电池耗氢量
    p_fc = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_fc{t}") for t in range(period)]  # 燃料电池产电量
    g_fc = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_fc{t}") for t in range(period)]  # 燃料电池产热量

    p_el_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["el"]["p_max"], name="p_el_inst")  # rated heat power of fuel cells
    h_el = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_el{t}") for t in range(period)]  # 电解槽制氢量
    p_el = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_el{t}") for t in range(period)]  # 电解槽耗电量

    p_eb_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["eb"]["p_max"], name=f"p_eb_inst")
    p_eb = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_eb{t}") for t in range(period)]  # 电锅炉耗电
    g_eb = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_eb{t}") for t in range(period)]  # 电锅炉产热

    p_hp_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["hp"]["p_max"], name=f"p_hp_inst")
    p_hp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_hp{t}") for t in range(period)]  # 热泵产热的耗电 
    g_hp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_hp{t}") for t in range(period)]  # 热泵产热
    q_hp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"q_hp{t}") for t in range(period)]  # 热泵产冷

    p_ghp_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["ghp"]["p_max"], name=f"p_ghp_inst")
    p_ghp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_ghp{t}") for t in range(period)]  # 热泵产热耗电 
    g_ghp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_ghp{t}") for t in range(period)]  # 热泵产热
    g_ghp_gr = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_ghp_gr{t}") for t in range(period)]  # 热泵灌热
    q_ghp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"q_ghp{t}") for t in range(period)]  # 热泵产热

    num_gtw_inst = model.addVar(vtype=GRB.INTEGER, lb=0, name="num_gtw_inst")  # 地热井

    h_hst_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["hst"]["h_max"], name=f"h_hst_inst")
    h_hst = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_hst{t}") for t in range(period)]  # 储氢罐储氢量

    m_ht_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["ht"]["m_max"], name=f"m_ht_inst")
    t_ht = [model.addVar(vtype=GRB.CONTINUOUS, lb=input_param["device"]["ht"]["t_min"], ub=input_param["device"]["ht"]["t_max"], name=f"t_ht{t}") for t in range(period)]  # temperature of heat storage tank
    g_ht = [model.addVar(vtype=GRB.CONTINUOUS, lb=-M, name=f"g_ht{t}") for t in range(period)]

    m_ct_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["ct"]["m_max"], name=f"m_ct_inst")
    t_ct = [model.addVar(vtype=GRB.CONTINUOUS, lb=input_param["device"]["ct"]["t_min"], ub=input_param["device"]["ct"]["t_max"], name=f"t_ct{t}") for t in range(period)]  # temperature of cold water tank
    q_ct = [model.addVar(vtype=GRB.CONTINUOUS, lb=-M, name=f"q_ct{t}") for t in range(period)]

    g_tube = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_tube{t}") for t in range(period)]
    model.update()

    # ------ Constraints ------
    # --- 设备运行约束 ---
    for i in range(period):
        # 光伏板
        model.addConstr(p_pv[i] <= k_pv * p_pv_inst * r_solar[i])  # 光伏板发电约束
        # 太阳能集热器
        model.addConstr(g_sc[i] <= k_sc * g_sc_inst * r_solar[i])  # 太阳能集热器产热约束
        # 燃料电池
        model.addConstr(p_fc[i] == k_fc_p * h_fc[i])  # 燃料电池产电约束
        model.addConstr(g_fc[i] == eta_ex * k_fc_g * h_fc[i])  # 燃料电池产热约束

        model.addConstr(p_fc[i] <= p_fc_inst)  # 燃料电池功率约束
        # 电解槽
        model.addConstr(h_el[i] <= k_el * p_el[i])  # 电解槽产氢约束
        model.addConstr(p_el[i] <= p_el_inst)  # 电解槽功率约束

        # 电锅炉
        model.addConstr(g_eb[i] == k_eb * p_eb[i])  # 电锅炉产热约束
        model.addConstr(p_eb[i] <= p_eb_inst)  # 电锅炉功率约束

        # 热泵
        model.addConstr(g_hp[i] <= k_hp_g * p_hp[i])  # 热泵产热约束
        model.addConstr(q_hp[i] <= k_hp_q * p_hp[i])  # 热泵产冷约束
        model.addConstr(p_hp[i] <= p_hp_inst)  # 热泵产热功率约束

        # 地源热泵
        model.addConstr(g_ghp[i] <= p_ghp[i] * k_ghp_g)  # 地源热泵产热约束
        model.addConstr(q_ghp[i] <= p_ghp[i] * k_ghp_q)  # 地源热泵产冷约束
        model.addConstr(p_ghp[i] <= p_ghp_inst)  # 地源热泵产热功率约束

        # 储氢罐
        model.addConstr(h_hst[i] <= h_hst_inst)

    model.addConstr(num_gtw_inst * g_gtw >= p_ghp_inst * k_ghp_g)  # 井和热泵有关联，制热量-电功率=取热量
    
    # --- 能量平衡约束 ---
    # 电平衡约束
    model.addConstrs(p_load[i] == p_pur[i] + p_pv[i] + p_fc[i]
                     - p_sel[i] - p_el[i] - p_eb[i] - p_hp[i] - p_ghp[i]
                     for i in range(period))
    for i in range(period - 1):
        # 热平衡约束
        model.addConstr(g_ht[i] == (-c * m_ht_inst * (t_ht[i + 1] - t_ht[i])
                                    - mu_ht_loss * c * m_ht_inst * (t_ht[i] - input_param["device"]["ht"]["t_min"])))  # 热水箱供热量
        model.addConstr(g_tube[i] == (g_fc[i] + g_eb[i] + g_sc[i] + g_hp[i] + g_ht[i]
                                     - g_ghp_gr[i]))  # 管网供热量
        model.addConstr(g_load[i] == g_tube[i] + g_ghp[i])  # 热负荷平衡约束
        # 冷平衡约束
        model.addConstr(q_ct[i] == c * m_ht_inst * (t_ct[i + 1] - t_ct[i]))  # 冷水箱供冷量
        model.addConstr(q_load[i] == q_hp[i] + q_ghp[i] + q_ct[i])  # 冷负荷平衡约束

        # 储氢平衡约束
        model.addConstr(h_hst[i + 1] - h_hst[i] == h_pur[i] + h_el[i] - h_fc[i])  # 储氢罐约束
    # 末时刻热平衡约束，需保证调度周期始末热水箱温度一致
    model.addConstr(g_ht[-1] == (-c * m_ht_inst * (t_ht[0] - t_ht[-1])
                                 - mu_ht_loss * c * m_ht_inst * (t_ht[i] - input_param["device"]["ht"]["t_min"])))  # 热水箱供热量
    model.addConstr(g_tube[-1] == (g_fc[-1] + g_eb[-1] + g_sc[-1] + g_hp[-1] + g_ht[-1]
                                   - g_ghp_gr[-1]))  # 管网供热量
    model.addConstr(g_load[-1] == g_tube[-1] + g_ghp[-1])  # 热负荷平衡约束
    # 末时刻冷平衡约束，需保证调度周期始末冷水箱温度一致
    model.addConstr(q_ct[-1] == c * m_ht_inst * (t_ct[0] - t_ct[-1]))  # 冷水箱供冷量
    model.addConstr(g_load[-1] == q_hp[-1] + q_ghp[-1] + q_ct[-1])  # 冷负荷平衡约束
    # 储氢平衡约束
    model.addConstr(h_hst[0] - h_hst[-1] == h_pur[-1] + h_el[-1] - h_fc[-1])  # 储氢罐约束

    # ------ Objective ------
    capex = ( cost_pv * p_pv_inst / input_param["device"]["pv"]["life"]
                 + p_fc_inst * cost_fc / input_param["device"]["fc"]["life"]
                 + p_el_inst * cost_el / input_param["device"]["el"]["life"]
                 + p_eb_inst * cost_eb / input_param["device"]["eb"]["life"]
                 + g_sc_inst * cost_sc / input_param["device"]["sc"]["life"]
                 + p_hp_inst * cost_hp / input_param["device"]["hp"]["life"]
                 + p_ghp_inst * cost_ghp / input_param["device"]["ghp"]["life"]
                 + num_gtw_inst * cost_gtw / input_param["device"]["gtw"]["life"]
                 + h_hst_inst * cost_hst / input_param["device"]["hst"]["life"]
                 + m_ht_inst * cost_ht / input_param["device"]["ht"]["life"]) # 年化投资费用
    opex = (gp.quicksum([p_pur[i] * p_price[i] for i in range(period)])
            - gp.quicksum([p_sel[i] for i in range(period)]) * p_sel_price
            + gp.quicksum([h_pur[i] for i in range(period)]) * h_price) # 运行费用

    model.setObjective(
        (capex + opex),
        GRB.MINIMIZE
    )
"""
describe_input = {
    "问题描述": "重要！！！",
    "背景知识": "构建能源系统规划问题，在满足设备运行约束、能量平衡约束的前提下，构建经济最优目标函数，计算得到设备容量和全年运行数据",
    "约束条件": [
        "设备容量约束：光伏板装机容量 p_pv_installed 不得大于 2000kW",
        "设备容量约束：氢燃料电池装机容量 p_fc_installed 不得小于 500kW",
        "设备容量约束：氢燃料电池装机容量 p_fc_installed 等于电解槽装机容量 p_el_installed",
        "设备容量约束：各时段光伏板装机容量 p_pv_installed 不得大于其最大装机容量 p_pv_max",
        "设备容量约束：各时段太阳能集热器装机容量 g_sc_installed 不得大于其最大装机容量 g_sc_max",
        "设备容量约束：各时段氢燃料电池装机容量 p_fc_installed 不得大于其最大装机容量 p_fc_max",
        "设备容量约束：各时段电解槽装机容量 p_el_installed 不得大于其最大装机容量 p_el_max",
        "设备容量约束：各时段电锅炉装机容量 p_eb_installed 不得大于其最大装机容量 p_eb_max",
        "设备容量约束：各时段热泵装机容量 p_hp_installed 不得大于其最大装机容量 p_hp_max",
        "设备容量约束：各时段地源热泵装机容量 p_ghp_installed 不得大于其最大装机容量 p_ghp_max",
        "设备容量约束：各时段储氢罐装机容量 h_hstorage_installed 不得大于其最大装机容量 h_hstorage_max",
        "设备容量约束：各时段蓄水箱装机容量 m_tank_installed 不得大于其最大装机容量 m_tank_max",
        "设备运行约束：各时段光伏板产电量 p_pv 不得大于其转换效率 k_pv、装机容量 p_pv_installed 和当前太阳辐射强度 r_solar 的乘积",
        "设备运行约束：各时段太阳能集热器产热量 g_sc 不得大于其转换效率 k_sc、装机容量 g_sc_installed 和当前太阳辐射强度 r_solar 的乘积",
        "设备运行约束：各时段氢燃料电池产电量 p_fc 等于其电转换效率 k_fc_p 和耗氢量 h_fc 的乘积",
        "设备运行约束：各时段氢燃料电池产热量 g_fc 等于其热交换效率 eta_fc、热转换效率 k_fc_g 和耗氢量 h_fc 的乘积",
        "设备运行约束：各时段氢燃料电池发电量 p_fc 不得大于其装机容量 p_fc_installed",
        "设备运行约束：各时段电解槽产氢量 h_el 不得大于其转换效率 k_el 和电解槽耗电量 p_el 的乘积",
        "设备运行约束：各时段电解槽耗电量 p_el 不得大于其装机容量 p_el_installed",
        "设备运行约束：各时段电锅炉产热量 g_eb 等于其转换效率 k_eb 和耗电量 p_eb 的乘积",
        "设备运行约束：各时段电锅炉耗电量 p_eb 不得大于其装机容量 p_eb_installed",
        "设备运行约束：各时段热泵产热量 g_hp 等于其热转换效率 k_hp_g 和耗电量 p_hp 的乘积",
        "设备运行约束：各时段热泵产冷量 q_hp 等于其冷转换效率 k_hp_q 和耗电量 p_hp 的乘积",
        "设备运行约束：各时段热泵耗电量 p_hp 不得大于其装机容量 p_hp_installed",
        "设备运行约束：各时段地源热泵产热量 g_ghp 等于其热转换效率 k_ghp_g 和耗电量 p_ghp 的乘积",
        "设备运行约束：各时段地源热泵产冷量 q_ghp 等于其冷转换效率 k_ghp_q 和耗电量 p_ghp 的乘积",
        "设备运行约束：各时段地源热泵耗电量 p_ghp 不得大于其装机容量 p_ghp_installed",
        "设备运行约束：各时段地源热泵从所有地热井取热量 num_gtw_installed * g_gtw 不得小于",
        "设备运行约束：系统中只有氢燃料电池和电锅炉可以灌热，因此各时段地源热泵向地热井灌热量 g_ghp_inject 不得大于氢燃料电池产热量 g_fc、电锅炉产热量 g_eb 的和",
        "设备运行约束：各时段储氢罐储氢变化量 h_delta_hstorage 等于 下一时刻储氢罐储氢量 h_hstorage_next 减去当前时刻储氢罐储氢量 h_hstorage",
        "设备运行约束：i+1 时刻应满足 h_hstorage_next[i] 等于 h_hstorage[i+1]，而调度周期结束时，储氢罐储氢量 h_hstorage_next[-1] 等于初始时刻储氢罐储氢量 h_hstorage[0]",
        "设备运行约束：各时段储氢罐储氢量 h_hstorage 不得大于其装机容量 h_hstorage_installed",
        "设备运行约束：各时段蓄水箱供热量 g_tank 等于蓄水箱储能变化量 g_delta_tank 和其热损失量 g_tank_loss 之和的负值",
        "设备运行约束：各时段蓄水箱储能变化量 g_delta_tank 等于水箱中水的质量 m_tank_installed、水的比热 c_water 和水箱中水温变化量（下一时刻水箱温度 t_tank_next 减去当前时刻水箱水温 t_tank）的乘积",
        "设备运行约束：各时段蓄水箱热损失量 g_tank_loss 等于热损失系数 k_tank_loss 和水箱中水的质量 m_tank_installed、水的比热 c_water 和当前时刻水箱水温 t_tank 与环境温度 t_amb 的差值的乘积",
        "设备运行约束：i+1 时刻应满足 t_tank_next[i] 等于 t_tank[i+1]，而调度周期结束时，蓄水箱中水温 t_tank_next[-1] 等于初始时刻水温 t_tank[0]",
        "能量平衡约束：各时段系统的电力供应（包括从电网购电 p_pur、光伏产电 p_pv 和燃料电池产电 p_fc）减去向电网售电量 p_sell 应等于电力需求（包括电负载 p_load、电解槽耗电量 p_el、电锅炉耗电量 p_eb、热泵耗电量 p_hp 和地源热泵耗电量 p_ghp）",
        "能量平衡约束：各时段系统的热负荷 g_load 等于管网供热量 g_tube 和地源热泵供热 g_ghp 的和",
        "能量平衡约束：各时段管网供热量 g_tube 等于太阳能集热器产热量 g_sc、氢燃料电池产热量 g_fc、电锅炉产热量 g_eb、热泵产热量 g_hp 和蓄水箱供热量 g_tank 的和减去地源热泵向地热井灌热量 g_ghp_inject",
        "能量平衡约束：各时段储氢罐储氢变化量 h_delta_hstorage 等于从氢气市场购氢量 h_pur 和电解槽产氢量 h_el 的和减去氢燃料电池耗氢量 h_fc"
    ],
    "目标函数": "最小化所有设备年化投资费用和系统运行费用之和，其中各设备的年化投资费用由设备单价、设备容量和设备寿命计算，系统运行费用包括买电费用和买氢费用减去向电网卖电收入",
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
            "类别": "device-sc",
            "内容": "太阳能集热器装机上限、太阳能集热器装机下限、太阳能集热器单价、太阳能集热器寿命、太阳能集热器效率",
            "符号": "g_max, g_min, cost, life, k_sc"
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
        },
        {
            "类别": "device-gtw",
            "内容": "地热井最大数量、地热井单价、地热井寿命、单个地热井的功率",
            "符号": "number_max, cost, life, g_gtw"
        },
        {
            "类别": "device-hst",
            "内容": "储氢罐最大容量、储氢罐最小容量、储氢罐单价、储氢罐寿命",
            "符号": "h_max, h_min, cost, life"
        },
        {
            "类别": "device-ht",
            "内容": "热水箱最大容量、热水箱最小容量、热水箱单价、热水箱寿命、热水箱最高温度、热水箱最低温度、热水箱损失系数",
            "符号": "m_max, h=m_min, cost, life, g_ht"
        },
        {
            "类别": "carbon",
            "内容": "氢气、电、天然气的碳排放因子"
        }
    ],
    "变量": [
        {
            "符号": "h_pur",
            "定义": "从氢气市场购氢量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "p_pur",
            "定义": "从电网购电量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "p_sell",
            "定义": "向电网卖电量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "p_pv_installed",
            "定义": "光伏板装机容量",
            "形状": []
        },
        {
            "符号": "g_sc_installed",
            "定义": "太阳能集热器装机容量",
            "形状": []
        },
        {
            "符号": "p_fc_installed",
            "定义": "氢燃料电池装机容量",
            "形状": []
        },
        {
            "符号": "p_el_installed",
            "定义": "电解槽装机容量",
            "形状": []
        },
        {
            "符号": "p_eb_installed",
            "定义": "电锅炉装机容量",
            "形状": []
        },
        {
            "符号": "p_hp_installed",
            "定义": "热泵装机容量",
            "形状": []
        },
        {
            "符号": "p_ghp_installed",
            "定义": "地源热泵装机容量",
            "形状": []
        },
        {
            "符号": "num_gtw_installed",
            "定义": "地热井装机数量",
            "形状": []
        },
        {
            "符号": "h_hstorage_installed",
            "定义": "储氢罐装机容量",
            "形状": []
        },
        {
            "符号": "m_tank_installed",
            "定义": "蓄水箱装机容量",
            "形状": []
        },
        {
            "符号": "p_pv",
            "定义": "光伏板产电量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "g_sc",
            "定义": "太阳能集热器产热量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "p_fc",
            "定义": "氢燃料电池产电量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "g_fc",
            "定义": "氢燃料电池产热量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "h_fc",
            "定义": "氢燃料电池耗氢量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "h_el",
            "定义": "电解槽产氢量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "p_el",
            "定义": "电解槽耗电量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "g_eb",
            "定义": "电锅炉产热量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "p_eb",
            "定义": "电锅炉耗电量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "g_hp",
            "定义": "热泵产热量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "q_hp",
            "定义": "热泵产冷量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "p_hp",
            "定义": "热泵耗电量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "g_ghp",
            "定义": "地源热泵产热量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "q_ghp",
            "定义": "地源热泵产冷量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "p_ghp",
            "定义": "地源热泵耗电量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "g_ghp_inject",
            "定义": "地源热泵向地热井灌热量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "h_delta_hstorage",
            "定义": "储氢罐储氢变化量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "h_hstorage",
            "定义": "储氢罐储氢量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "h_hstorage_next",
            "定义": "储氢罐下一时刻储氢量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "g_tank",
            "定义": "蓄水箱供热量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "g_delta_tank",
            "定义": "蓄水箱储能变化量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "g_tank_loss",
            "定义": "蓄水箱热损失量",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "t_tank",
            "定义": "蓄水箱水温",
            "形状": [
                "period"
            ]
        },
        {
            "符号": "t_tank_next",
            "定义": "蓄水箱下一时刻水温",
            "形状": [
                "period"
            ]
        }
    ]
}

para_input = {
    "load": {
        "building_type": "Mixed Use",
        "p_max": 500,
        "g_max": 1200,
        "q_max": 300,
        "g_month": [11, 12, 1, 2, 3],
        "q_month": [6, 7, 8],
        "p_area": 120000.0,
        "g_area": 120000.0,
        "q_area": 120000.0
    },
    "price": {
        "TOU_power": [0.515, 0.515, 0.515, 0.515, 0.515, 0.515, 0.515, 0.515, 0.515, 0.515, 0.515, 0.515, 0.515, 0.515, 0.515, 0.515, 0.515, 0.515, 0.515, 0.515, 0.515, 0.515, 0.515, 0.515],
        "p_sel_price": 0,
        "g_price": 5.4,
        "q_price": 9.5,
        "h_price": 17.92
    },
    "device": {
        "pv": {
            "_comment": "photovoltaic, 光伏板",
            "description": "",
            "p_max": 2000,
            "p_min": 0,
            "cost": 700,
            "life": 20,
            "k_pv": 0.21
        },
        "fc": {
            "_comment": "fuel cell, 燃料电池",
            "description": "",
            "p_max": 1000,
            "p_min": 500,
            "cost": 8000,
            "life": 10,
            "k_fc_p": 15,
            "k_fc_g": 22
        },
        "el": {
            "_comment": "electrolyzer, 电解槽",
            "description": "",
            "p_max": 1000,
            "p_min": 500,
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
        }
    },
    "carbon": {
        "alpha_h2": 1.74,
        "alpha_e": 0.5839,
        "alpha_EO": 0.8922,
        "alpha_gas": 1.535
    }
}

prompt = prompt_template_json3.format(
    solver=solver,
    example_describe_input = json.dumps(example_describe_input, ensure_ascii=False),
    example_para_input = json.dumps(example_para_input, ensure_ascii=False),
    example_output= example_output,
    describe_input = json.dumps(describe_input, ensure_ascii=False),
    para_input = json.dumps(para_input, ensure_ascii=False)
)

print(prompt)
