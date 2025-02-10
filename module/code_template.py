'''
Author: guo_MateBookPro 867718012@qq.com
Date: 2025-02-07 11:08:28
LastEditTime: 2025-02-10 19:57:02
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
# project_path = os.path.dirname(os.path.realpath(__file__))
# project_path = project_path.replace("\\", "/")
def read_load(building_type, file_load=""):
    if not building_type:
        raise ValueError("building_type cannot be empty")

    load_path = os.path.join(project_path, "data", "load_data")
    if not os.path.exists(load_path):
        raise FileNotFoundError(f"Load data directory not found: ")

    if not file_load:
        try:
            root, dirs, files = next(os.walk(load_path))
            matching_files = [f for f in files if building_type in f and f.endswith('.csv')]
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
    return {{
        'p_load': load['Electricity Load [J]'],
        'g_load': load['Heating Load [J]'],
        'q_load': load['Cooling Load [J]'],
        'r_solar': load['Environment:Site Direct Solar Radiation Rate per Area [W/m2](Hourly)']
    }}
{solver_code}
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
 
    device_cap = {{x: y.X for x, y in device_inst_list.items()}}
    return  device_cap


# 读参数json
with open(project_path+"/data/parameters.json", "r", encoding="utf-8") as load_file:
    input_json = json.load(load_file)
    
# 读负荷csv
load = read_load(input_json["load"]["building_type"])

device_cap = planning_problem(load, input_json)
planning_result_path = project_path + "/doc/planning_result.json"
with open(planning_result_path, "w", encoding="utf-8") as f:
    json.dump(device_cap, f, ensure_ascii=False, indent=4)
print("device_cap result saved to", planning_result_path)
"""
