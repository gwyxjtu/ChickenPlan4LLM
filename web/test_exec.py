'''
Author: guo_MateBookPro 867718012@qq.com
Date: 2025-01-03 11:27:48
LastEditTime: 2025-02-08 11:23:58
LastEditors: guo_MateBookPro 867718012@qq.com
FilePath: /ChickenPlan4LLM/web/test_exec.py
Description: 雪花掩盖着哽咽叹息这离别
'''
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import traceback
from module import code_template
from module.LLM import example_code_output

from module.utils import PROJECT_PATH

local_env = {"project_path": PROJECT_PATH}

solver_code = """
def planning_problem(period_data, input_param):
    # 常数
    c_water = 4.2 / 3600  # 水的比热容
    M = 1e7  # 大 M

    # ------ Create model ------
    model = gp.Model("OptModel")

    # ------ Parameters input ------
    # 参数输入，时序数据包括电、热、冷、光照强度等；单一数据包括碳排放因子、能源价格、设备价格、设备效率等
    # --- 各时段数据 ---
    p_load = period_data["p_load"] * input_param["load"]["p_area"]  # 电负荷乘以面积
    g_load = period_data["g_load"] * input_param["load"]["g_area"]  # 热负荷乘以面积
    q_load = period_data["q_load"] * input_param["load"]["q_area"]  # 冷负荷乘以面积
    r_solar = period_data["r_solar"]  # 光照强度

    period = len(p_load)  # 总时段数

    # 展示负荷信息
    print("热负荷总量：{}，冷负荷总量：{}，电负荷总量：{}".format(sum(g_load), sum(q_load), sum(p_load)))
    print("热负荷峰值：{}，冷负荷峰值：{}，电负荷峰值：{}".format(max(g_load), max(q_load), max(p_load)))
    print("-" * 10 + "g, q, e_load" + "-" * 10)
    p_load, g_load, q_load, r_solar = np.array(p_load), np.array(g_load), np.array(q_load), np.array(r_solar)
    r_solar = r_solar * 4000  # 单位转化

    # --- 碳排放因子 ---
    alpha_e = input_param["carbon"]["alpha_e"]  # 电网排放因子 kg/kWh

    # --- 能源价格 ---
    p_price = input_param["price"]["TOU_power"] * 365  # 分时电价
    p_sell_price = input_param["price"]["p_sell_price"]  # 卖电价格
    h_price = input_param["price"]["h_price"]  # 买氢价格

    # --- 各种设备的价格 ---
    cost_pv = input_param["device"]["pv"]["cost"]  # 光伏板单价
    cost_fc = input_param["device"]["fc"]["cost"]  # 氢燃料电池单价
    cost_el = input_param["device"]["el"]["cost"]  # 电解槽单价
    cost_eb = input_param["device"]["eb"]["cost"]  # 电锅炉单价
    cost_ghp = input_param["device"]["ghp"]["cost"]  # 地源热泵单价
    cost_hp = input_param["device"]["hp"]["cost"]  # 空气源热泵单价

    # --- 各种设备的效率系数，包括产电、产热、产冷、产氢、热交换等 ---
    k_pv = input_param["device"]["pv"]["k_pv"]  # 光伏板产电效率
    k_fc_p = input_param["device"]["fc"]["k_fc_p"]  # 氢燃料电池产电效率
    k_el = input_param["device"]["el"]["k_el"]  # 电解槽产氢效率
    k_eb = input_param["device"]["eb"]["k_eb"]  # 电锅炉产热效率
    k_ghp_g = input_param["device"]["ghp"]["k_ghp_g"]  # 地源热泵产热效率
    k_hp_g = input_param["device"]["hp"]["k_hp_g"]  # 空气源热泵产热效率

    # ------ Variables ------
    p_pur = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_pur{t}") for t in range(period)]  # 从电网购电量
    p_sell = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_sell{t}") for t in range(period)]  # 向电网卖电量
    h_pur = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_pur{t}") for t in range(period)]  # 从氢气市场购氢量

    # 光伏系统
    s_pv_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["pv"]["area_max"], name="s_pv_inst")  # 光伏系统装机容量
    p_pv = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_pv{t}") for t in range(period)]  # 光伏系统产电量

    # 燃料电池
    p_fc_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["fc"]["p_max"], name="p_fc_inst")  # 燃料电池装机容量
    p_fc = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_fc{t}") for t in range(period)]  # 燃料电池产电量

    # 电解槽
    p_el_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["el"]["p_max"], name="p_el_inst")  # 电解槽装机容量
    p_el = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_el{t}") for t in range(period)]  # 电解槽耗电量

    # 电锅炉
    p_eb_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["eb"]["p_max"], name="p_eb_inst")  # 电锅炉装机容量
    g_eb = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_eb{t}") for t in range(period)]  # 电锅炉产热量

    # 地源热泵
    p_ghp_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["ghp"]["p_max"], name="p_ghp_inst")  # 地源热泵装机容量
    g_ghp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_ghp{t}") for t in range(period)]  # 地源热泵产热量

    # 空气源热泵
    p_hp_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["hp"]["p_max"], name="p_hp_inst")  # 空气源热泵装机容量
    g_hp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_hp{t}") for t in range(period)]  # 空气源热泵产热量

    # ------ Update model ------
    model.update()

    # ------ Constraints ------
    for t in range(period):
        # 设备容量约束
        model.addConstr(p_fc_inst <= input_param["device"]["fc"]["p_max"])  # 燃料电池装机容量约束
        model.addConstr(p_el_inst <= input_param["device"]["el"]["p_max"])  # 电解槽装机容量约束
        model.addConstr(s_pv_inst <= input_param["device"]["pv"]["area_max"])  # 光伏系统装机容量约束
        model.addConstr(p_eb_inst <= input_param["device"]["eb"]["p_max"])  # 电锅炉装机容量约束
        model.addConstr(p_ghp_inst <= input_param["device"]["ghp"]["p_max"])  # 地源热泵装机容量约束
        model.addConstr(p_hp_inst <= input_param["device"]["hp"]["p_max"])  # 空气源热泵装机容量约束

        # 设备运行约束
        model.addConstr(p_el[t] <= p_el_inst)  # 电解槽耗电量约束
        model.addConstr(p_fc[t] <= p_fc_inst)  # 燃料电池产电量约束
        model.addConstr(p_pv[t] <= s_pv_inst)  # 光伏系统产电量约束
        model.addConstr(g_eb[t] == input_param["device"]["eb"]["k_eb"] * p_eb[t])  # 电锅炉产热量约束
        model.addConstr(g_ghp[t] <= k_ghp_g * p_ghp[t])  # 地源热泵产热量约束
        model.addConstr(q_ct[t] <= input_param["load"]["q_max"])  # 冷水机组供冷量约束

    # 能量平衡约束
    for t in range(period):
        model.addConstr(p_pur[t] + p_pv[t] + p_fc[t] - p_sell[t] == p_load[t] + p_el[t] + g_eb[t] + g_ghp[t])  # 电平衡约束
        model.addConstr(g_ghp[t] + g_hp[t] == g_load[t])  # 热平衡约束
        model.addConstr(q_ct[t] == q_load[t])  # 冷平衡约束

    # ------ Objective ------
    capex = (cost_pv * s_pv_inst / input_param["device"]["pv"]["life"]
             + cost_fc * p_fc_inst / input_param["device"]["fc"]["life"]
             + cost_el * p_el_inst / input_param["device"]["el"]["life"]
             + cost_eb * p_eb_inst / input_param["device"]["eb"]["life"]
             + cost_ghp * p_ghp_inst / input_param["device"]["ghp"]["life"]
             + cost_hp * p_hp_inst / input_param["device"]["hp"]["life"])  # 年化投资费用
    opex = (gp.quicksum([p_pur[t] * p_price[t] for t in range(period)])
            - gp.quicksum([p_sell[t] for t in range(period)]) * p_sell_price
            + gp.quicksum([h_pur[t] for t in range(period)]) * h_price)  # 运行费用
    model.setObjective((capex + opex), GRB.MINIMIZE)
"""

code_to_execute = code_template.format(solver_code=solver_code)

print("=" * 80)
print("Code to execute:")
print("=" * 80)
print(code_to_execute)
print("=" * 80)
print("Executing code ...")
print("=" * 80)
try:
    exec(code_to_execute, local_env, local_env)
    print("=" * 80)
    print("Execution successful.")
    print("=" * 80)
    print("local_env contents:")
    for key, _ in local_env.items():
        print(key)

except Exception as e:
    # 捕获并打印详细的异常信息
    print("An error occurred during execution:")
    print(traceback.format_exc())
