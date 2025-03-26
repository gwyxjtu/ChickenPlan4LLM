'''
Author: guo_MateBookPro 867718012@qq.com
Date: 2025-03-23 13:11:09
LastEditTime: 2025-03-26 17:13:59
LastEditors: guo_MateBookPro 867718012@qq.com
FilePath: /ChickenPlan4LLM/module/code_template.py
Description: 雪花掩盖着哽咽叹息这离别
'''
code_template = """
import sys
import os
import json
import numpy as np
import pandas as pd
import gurobipy as gp
from gurobipy import GRB
from pathlib import Path

# project_path = str(Path(__file__).resolve().parents[2])

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
    
    return {{
        'p_load': p_load,
        'g_load': g_load,
        'q_load': q_load,
        'r_solar': load['Environment:Site Direct Solar Radiation Rate per Area [W/m2](Hourly)']
    }}
{solver_code}


# 读参数json
para_path = project_path + "/log/opt_test/parameters.json"
with open(para_path, "r", encoding="utf-8") as load_file:
    input_json = json.load(load_file)
    
# 读负荷csv
load = read_load(input_json["load"])

model,device_inst_list = planning_problem(load, input_json)
# ------ Optimize ------
model.params.NonConvex = 2
model.Params.LogFile = str(project_path + "/log/mip.log")
model.params.MIPGap = 0.01
try:
    model.optimize()
except gp.GurobiError:
    print("Optimize failed due to non-convexity")
if model.status == GRB.INFEASIBLE or model.status == 4:
    print("Model is infeasible")
    model.computeIIS()
    model.write(project_path + "/log/opt_test/model.ilp")
    print("Irreducible inconsistent subsystem is written to file 'model.ilp'")

device_cap = {{x: y.X for x, y in device_inst_list.items()}}


planning_result_path = project_path + "/log/opt_test/planning_result.json"
with open(planning_result_path, "w", encoding="utf-8") as f:
    json.dump(device_cap, f, ensure_ascii=False, indent=4)
print("device_cap result saved to", planning_result_path)

"""
