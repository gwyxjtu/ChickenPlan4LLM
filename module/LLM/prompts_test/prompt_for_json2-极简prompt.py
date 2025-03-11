import json

# 描述性json -> 代码
prompt_template_json3 = """
你是一个优化专家团队中的专业程序员。团队的目标是解决一个能源系统设备容量规划的最优化问题。您的责任是根据用户需求和模型参数的描述json，构建一个模型参数数据json文件。\
现在给出案例，请学习如何根据新的文本生成新的json。
```
**输入**：
{example_input}

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

example_input = {
    "背景知识": "构建能源系统规划问题，在满足设备运行约束、能量平衡约束的前提下，构建经济最优目标函数，计算得到设备容量和全年运行数据",
    "设备描述": "氢燃料电池是一种消耗氢气产生电力和热能的设备",
    "约束条件": [
        "设备运行时长为`period`",
        "设备容量约束：氢燃料电池装机容量上限为`p_max_fc`",
        "设备运行约束：氢燃料电池产电量不超过氢燃料电池转换为产电量的装机容量",
        "设备运行约束：氢燃料电池产电量等于氢燃料电池耗氢量的`k_p_fc`倍",
        "设备运行约束：氢燃料电池产热量等于氢燃料电池耗氢量的`k_g_fc`倍",
    ],
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
    "变量": [
        {
            "符号": "p_fc_install",
            "定义": "氢燃料电池转换为产电量的装机容量"
        },
        {
            "符号": "p_fc",
            "定义": "氢燃料电池产电量"
        },
        {
            "符号": "h_fc",
            "定义": "氢燃料电池耗氢量"
        },
        {
            "符号": "g_fc",
            "定义": "氢燃料电池产热量"
        },
    ],
}

example_output = """
# 创建变量
p_fc_install = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_fc_inst")  # 氢燃料电池转换为产电量的装机容量
h_fc = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_fc{t}") for t in range(period)]  # 氢燃料电池耗氢量
p_fc = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_fc{t}") for t in range(period)]  # 氢燃料电池产电量
g_fc = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_fc{t}") for t in range(period)]  # 氢燃料电池产热量
# 更新模型
model.update()
# 添加约束条件
model.addConstr(p_fc_install <= p_max_fc, name="p_fc_install")  # 氢燃料电池装机容量上限
for t in range(period):
    model.addConstr(p_fc[t] <= p_fc_install)  # 氢燃料电池产电量上限
    model.addConstr(p_fc[t] == k_p_fc * h_fc[t], name=f"p_fc{t}")  # 氢燃料电池产电量约束
    model.addConstr(g_fc[t] == k_g_fc * h_fc[t], name=f"g_fc{t}")  # 氢燃料电池产热量约束
"""

device_input = {
    "背景知识": "构建能源系统规划问题，在满足设备运行约束、能量平衡约束的前提下，构建经济最优目标函数，计算得到设备容量和全年运行数据",
    "设备描述": "电解槽是一种消耗电力产生氢气的设备",
    "约束条件": [
        "设备运行时长为`period`",
        "设备容量约束：电解槽装机容量上限为`p_max_el`",
        "设备运行约束：电解槽耗电功率不超过电解槽装机容量",
        "设备运行约束：电解槽产氢量等于电解槽耗电量的`k_p_el`倍",
    ],
    "参数": [
        {
            "符号": "period",
            "定义": "设备运行时长"
        },
        {
            "符号": "p_max_el",
            "定义": "电解槽产氢量上限"
        },
        {
            "符号": "k_p_el",
            "定义": "电解槽产氢量与电解槽耗电量的比例"
        },
    ],
    "变量": [
        {
            "符号": "p_el_install",
            "定义": "电解槽装机容量"
        },
        {
            "符号": "h_el",
            "定义": "电解槽产氢量"
        },
        {
            "符号": "p_el",
            "定义": "电解槽耗电量"
        },
    ],
}

prompt = prompt_template_json3.format(
    solver=solver,
    example_input=json.dumps(example_input, indent=4, ensure_ascii=False),
    example_output=example_output,
    device_input=json.dumps(device_input, indent=4, ensure_ascii=False),
)

print(prompt)
