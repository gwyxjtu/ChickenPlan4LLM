
import sys
import os
import json
import numpy as np
import pandas as pd
import gurobipy as gp
from gurobipy import GRB
project_path = os.path.dirname(os.path.realpath(__file__))
project_path = project_path.replace("\\", "/")
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
    model = gp.Model("OptModel")
    period = len(period_data["p_load"])
    M = 1e7  # 大M法常数

    # ------ 参数输入 ------
    p_load = period_data["p_load"]
    g_load = period_data["g_load"]
    q_load = period_data["q_load"]
    r_solar = period_data["r_solar"]
    p_price = input_param["price"]["TOU_power"]
    p_sell_price = input_param["price"]["p_sell_price"]
    h_price = input_param["price"]["h_price"]

    # 设备参数
    pv = input_param["device"]["pv"]
    fc = input_param["device"]["fc"]
    el = input_param["device"]["el"]
    eb = input_param["device"]["eb"]
    ghp = input_param["device"]["ghp"]

    # ------ 决策变量 ------
    # 系统运行变量
    p_pur = model.addVars(period, name="p_pur", lb=0)
    h_pur = model.addVars(period, name="h_pur", lb=0)
    p_sell = model.addVars(period, name="p_sell", lb=0)
    
    # 光伏板
    p_pv_inst = model.addVar(name="p_pv_inst", ub=pv["p_pv_max"])
    p_pv = model.addVars(period, name="p_pv", lb=0)
    
    # 燃料电池
    p_fc_inst = model.addVar(name="p_fc_inst", ub=fc["p_fc_max"])
    p_fc = model.addVars(period, name="p_fc", lb=0)
    g_fc = model.addVars(period, name="g_fc", lb=0)
    h_fc = model.addVars(period, name="h_fc", lb=0)
    
    # 电解槽
    p_el_inst = model.addVar(name="p_el_inst", ub=el["p_el_max"])
    h_el = model.addVars(period, name="h_el", lb=0)
    p_el = model.addVars(period, name="p_el", lb=0)
    
    # 电锅炉
    p_eb_inst = model.addVar(name="p_eb_inst", ub=eb["p_eb_max"])
    g_eb = model.addVars(period, name="g_eb", lb=0)
    p_eb = model.addVars(period, name="p_eb", lb=0)
    
    # 地源热泵
    p_ghp_inst = model.addVar(name="p_ghp_inst", ub=ghp["p_max"])
    g_ghp = model.addVars(period, name="g_ghp", lb=0)
    q_ghp = model.addVars(period, name="q_ghp", lb=0)
    p_ghp = model.addVars(period, name="p_ghp", lb=0)

    # ------ 约束条件 ------
    # 光伏板约束
    for t in range(period):
        model.addConstr(p_pv[t] <= pv["k_pv"] * p_pv_inst * r_solar[t])
    
    # 燃料电池约束
    for t in range(period):
        model.addConstr(p_fc[t] == fc["k_fc_p"] * h_fc[t])
        model.addConstr(g_fc[t] == fc["eta_fc"] * fc["k_fc_g"] * h_fc[t])
        model.addConstr(p_fc[t] <= p_fc_inst)
    
    # 电解槽约束
    for t in range(period):
        model.addConstr(h_el[t] <= el["k_el"] * p_el[t])
        model.addConstr(p_el[t] <= p_el_inst)
    
    # 电锅炉约束
    for t in range(period):
        model.addConstr(g_eb[t] == eb["k_eb"] * p_eb[t])
        model.addConstr(p_eb[t] <= p_eb_inst)
    
    # 地源热泵约束
    for t in range(period):
        model.addConstr(g_ghp[t] <= ghp["k_ghp_g"] * p_ghp[t])
        model.addConstr(q_ghp[t
    # ------ Optimize ------
    model.params.NonConvex = 2
    model.Params.LogFile = project_path + "/log/mip.log"
    model.params.MIPGap = 0.01
    try:
        model.optimize()
    except gp.GurobiError:
        print("Optimize failed due to non-convexity")
    if model.status == GRB.INFEASIBLE or model.status == 4:
        print("Model is infeasible")
        model.computeIIS()
        model.write(project_path+"/log/model.ilp")
        print("Irreducible inconsistent subsystem is written to file 'model.ilp'")
 
    device_cap = {x: y.X for x, y in device_inst_list.items()}
    return  device_cap


# 读参数json
with open(project_path+"/web/data/parameters.json", "r", encoding="utf-8") as load_file:
    input_json = json.load(load_file)
    
# 读负荷csv
load = read_load(input_json["load"])

device_cap = planning_problem(load, input_json)
planning_result_path = project_path + "/doc/planning_result.json"
with open(planning_result_path, "w", encoding="utf-8") as f:
    json.dump(device_cap, f, ensure_ascii=False, indent=4)
print("device_cap result saved to", planning_result_path)
