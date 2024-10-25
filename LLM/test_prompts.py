import json

prompt_template = """
你是一个优化专家团队中的专业程序员。团队的目标是解决一个优化问题。您的责任是编写{solver}代码。\
请您根据由```分隔的示例，学习如何通过输入设备参数、约束条件，编写{solver}代码，以完成对输入设备的建模，包括创建变量和添加约束条件。

```
**输入**：
{example_input}

**输出**：
=====
{example_output}
=====
```

由---分隔的是输入的设备信息，包括背景知识、设备描述、约束条件、参数和变量。您需要根据这些信息，编写{solver}代码，完成对设备的建模。
---
{device_input}
---

请注意：
- 只生成代码和"====="行，不要生成其他文本。
- 假定参数和变量已经定义，并且已经导入了gurobipy作为gp。现在根据此生成代码，并将其放在"====="行之间。

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
            "符号": "period",
            "定义": "设备运行时长"
        },
        {
            "符号": "p_max_fc",
            "定义": "氢燃料电池产电量上限"
        },
        {
            "符号": "k_p_fc",
            "定义": "氢燃料电池产电量与氢燃料电池耗氢量的比例"
        },
        {
            "符号": "k_g_fc",
            "定义": "氢燃料电池产热量与氢燃料电池耗氢量的比例"
        },
    ],
    "变量": [
        {
            "设备": "燃料电池 fc",
            "描述": "燃料电池产热量,燃料电池发电量,燃料电池用氢量,燃料电池额定功率",
            "符号":"g_fc,p_fc,h_fc,p_fc_inst"
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

prompt = prompt_template.format(
    solver=solver,
    example_input=json.dumps(example_input, indent=4, ensure_ascii=False),
    example_output=example_output,
    device_input=json.dumps(device_input, indent=4, ensure_ascii=False),
)

print(prompt)
