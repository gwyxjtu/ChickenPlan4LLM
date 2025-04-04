
import sys
import os
import json
import numpy as np
import pandas as pd
import gurobipy as gp
from gurobipy import GRB


def read_load(load_json, file_load=""):
    if not load_json["building_type"]:
        raise ValueError("building_type cannot be empty")

    load_path = os.path.join(project_path, "data", "load_data")
    if not os.path.exists(load_path):
        raise FileNotFoundError(f"Load data directory not found: ")

    if not file_load:
        try:
            root, dirs, files = next(os.walk(load_path))
            matching_files = [f for f in files if load_json["building_type"] in f and f.endswith('.csv')]
            file_load = os.path.join(load_path, matching_files[0])
        except StopIteration:
            raise FileNotFoundError(f"Failed to read directory:")

        load = pd.read_csv(file_load)
    required_columns = [
        'Electricity Load [J]',
        'Heating Load [J]',
        'Cooling Load [J]',
        'Environment:Site Direct Solar Radiation Rate per Area [W/m2](Hourly)'
    ]
    # 按照峰值等修改负荷
    # Scale loads according to peak values and areas
    p_load = load['Electricity Load [J]'] / max(load['Electricity Load [J]']) * load_json['p_max']
    g_load = load['Heating Load [J]']/ max(load['Heating Load [J]']) * load_json['g_max']
    q_load = load['Cooling Load [J]']/ max(load['Cooling Load [J]']) * load_json['q_max']
    
    return {
        'p_load': p_load,
        'g_load': g_load,
        'q_load': q_load,
        'r_solar': load['Environment:Site Direct Solar Radiation Rate per Area [W/m2](Hourly)']
    }
def planning_problem(period_data, input_param):
    # 常数
    c_water = 4.2 / 3600  # 水的比热容
    M = 1e7  # 大 M

    # ------ Create model ------
    model = gp.Model("OptModel")

    # ------ Parameters input ------
    # 参数输入，时序数据包括电、热、冷、光照强度等；单一数据包括碳排放因子、能源价格、设备价格、设备效率等
    # --- 各时段数据 ---
    period = len(period_data["p_load"])
    p_load = period_data["p_load"]  
    g_load = period_data["g_load"]  
    q_load = period_data["q_load"]  
    r_solar = period_data["r_solar"]  # 光照强度

    # --- 碳排放因子 ---
    alpha_e = input_param["carbon"]["alpha_e"]  # 电网排放因子 kg/kWh

    # --- 能源价格 ---
    p_price = input_param["price"]["TOU_power"] * 365  # 分时电价，输入的只有24h，需要乘365形成全年
    p_sell_price = input_param["price"]["p_sell_price"]  # 卖电价格
    h_price = input_param["price"]["h_price"]  # 买氢价格

    # --- 各种设备的价格 ---
    cost_fc = input_param["device"]["fc"]["cost"]  # 氢燃料电池单价
    cost_tank = input_param["device"]["tank"]["cost"]  # 蓄水箱单价，元/kWh

    # --- 各种设备的效率系数，包括产电、产热、产冷、产氢、热交换等 ---
    k_fc_p = input_param["device"]["fc"]["k_fc_p"]  # 氢燃料电池产电效率
    k_fc_g = input_param["device"]["fc"]["k_fc_g"]  # 氢燃料电池产热效率
    eta_ex = input_param["device"]["fc"]["eta_ex"]  # 燃料电池热交换效率
    mu_tank_loss = input_param["device"]["tank"]["mu_loss"]  # 蓄水箱能量损失系数
    t_ht_min = input_param["device"]["tank"]["t_ht_min"]

    # ------ Variables ------
    h_pur = [model.addVar(vtype=gp.GRB.CONTINUOUS, lb=0, name=f"h_pur{t}") for t in range(period)]  # 从氢气市场购氢量
    p_pur = [model.addVar(vtype=gp.GRB.CONTINUOUS, lb=0, name=f"p_pur{t}") for t in range(period)]  # 从电网购电量
    p_sell = [model.addVar(vtype=gp.GRB.CONTINUOUS, lb=0, name=f"p_sell{t}") for t in range(period)]  # 向电网卖电量

    # 氢燃料电池
    p_fc_inst = model.addVar(vtype=gp.GRB.CONTINUOUS, lb=0, name=f"p_fc_inst")  # 氢燃料电池装机容量
    h_fc = [model.addVar(vtype=gp.GRB.CONTINUOUS, lb=0, name=f"h_fc{t}") for t in range(period)]  # 氢燃料电池耗氢量
    p_fc = [model.addVar(vtype=gp.GRB.CONTINUOUS, lb=0, name=f"p_fc{t}") for t in range(period)]  # 氢燃料电池产电量
    g_fc = [model.addVar(vtype=gp.GRB.CONTINUOUS, lb=0, name=f"g_fc{t}") for t in range(period)]  # 氢燃料电池产热量

    # 热水箱
    m_tank_inst = model.addVar(vtype=gp.GRB.CONTINUOUS, lb=0, name=f"m_tank_inst")  # 蓄水箱装机容量
    t_ht = [model.addVar(vtype=gp.GRB.CONTINUOUS, lb=t_ht_min, name=f"t_ht{t}") for t in range(period)]  # 热水箱水温
    g_ht = [model.addVar(vtype=gp.GRB.CONTINUOUS, lb=-M, name=f"g_ht{t}") for t in range(period)]  # 热水箱供热量
    delta_g_ht = [model.addVar(vtype=gp.GRB.CONTINUOUS, lb=-M, name=f"delta_g_ht{t}") for t in range(period)]  # 热水箱储热变化量
    g_ht_loss = [model.addVar(vtype=gp.GRB.CONTINUOUS, lb=0, name=f"g_ht_loss{t}") for t in range(period)]  # 热水箱热损失量

    # 地源热泵
    p_ghp_inst = model.addVar(vtype=gp.GRB.CONTINUOUS, lb=0, name=f"p_ghp_inst")  # 地源热泵装机容量
    g_ghp = [model.addVar(vtype=gp.GRB.CONTINUOUS, lb=0, name=f"g_ghp{t}") for t in range(period)]  # 地源热泵产热量
    q_ghp = [model.addVar(vtype=gp.GRB.CONTINUOUS, lb=0, name=f"q_ghp{t}") for t in range(period)]  # 地源热泵产冷量

    # 设备装机列表
    device_inst_list = {
        "氢燃料电池": p_fc_inst,
        "热水箱": m_tank_inst,
        "地源热泵": p_ghp_inst,
    }

    # ------ Update model ------
    model.update()

    # ------ Constraints ------
    # --- 设备运行约束 ---
    for t in range(period):
        # 氢燃料电池
        model.addConstr(p_fc[t] == k_fc_p * h_fc[t])  # 燃料电池产电约束
        model.addConstr(g_fc[t] == eta_ex * k_fc_g * h_fc[t])  # 燃料电池产热约束
        model.addConstr(p_fc[t] <= p_fc_inst)  # 燃料电池功率约束

        # 热水箱（蓄水箱储热时）
        model.addConstr(g_ht[t] == -delta_g_ht[t] - g_ht_loss[t])  # 热水箱供热量
        model.addConstr(g_ht_loss[t] == mu_tank_loss * c_water * m_tank_inst * (t_ht[t] - t_ht_min))  # 热水箱热损失量

    # 储能设备约束
    for t in range(period - 1):
        model.addConstr(delta_g_ht[t] == c_water * m_tank_inst * (t_ht[t + 1] - t_ht[t]))  # 热水箱储热变化量

    # --- 能量平衡约束 ---
    for t in range(period):
        model.addConstr(p_pur[t] + p_fc[t] - p_sell[t] == p_load[t])  # 电平衡约束
        model.addConstr(g_fc[t] + g_ht[t] == g_load[t])  # 热平衡约束
        model.addConstr(q_ghp[t] == q_load[t])  # 冷平衡约束

    # ------ Objective ------
    # 年化投资费用
    capex = cost_fc * p_fc_inst / input_param["device"]["fc"]["life"] + cost_tank * m_tank_inst / input_param["device"]["tank"]["life"]
    # 运行费用
    opex = (gp.quicksum([p_pur[t] * p_price[t] for t in range(period)]) - gp.quicksum([p_sell[t] for t in range(period)]) * p_sell_price)
    model.setObjective((capex + opex), gp.GRB.MINIMIZE)
    
    return model, device_inst_list


def run_model(model, device_inst_list):
    # ------ Optimize ------
    model.params.NonConvex = 2
    model.Params.LogFile = log_dir + "/mip.log"
    model.params.MIPGap = 0.01
    try:
        model.optimize()
    except gp.GurobiError:
        print("Optimize failed due to non-convexity")
    if model.status == GRB.INFEASIBLE or model.status == 4:
        print("Model is infeasible")
        model.computeIIS()
        model.write(log_dir + "/model.ilp")
        print("Irreducible inconsistent subsystem is written to file 'model.ilp'")
 
    device_cap = {x: y.X for x, y in device_inst_list.items()}
    return  device_cap


# 读参数json
with open(log_dir + "/parameters_gen.json", "r", encoding="utf-8") as load_file:
    input_json = json.load(load_file)
    
# 读负荷csv
load = read_load(input_json["load"])

model, device_inst_list = planning_problem(load, input_json)
device_cap = run_model(model, device_inst_list)
planning_result_path = project_path + "/doc/planning_result.json"
with open(planning_result_path, "w", encoding="utf-8") as f:
    json.dump(device_cap, f, ensure_ascii=False, indent=4)
print("device_cap result saved to", planning_result_path)
