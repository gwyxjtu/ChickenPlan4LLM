'''
Author: guo_MateBookPro 867718012@qq.com
Date: 2025-01-03 11:27:48
LastEditTime: 2025-01-03 14:00:45
LastEditors: guo_MateBookPro 867718012@qq.com
FilePath: /ChickenPlan4LLM/main.py
Description: 雪花掩盖着哽咽叹息这离别
'''
import time
import random

import gurobipy as gp
from gurobipy import GRB
import numpy as np
import pandas as pd
from module.optimization import planning_problem

import json
import os
import pprint


def read_load(building_type, file_load=""):
    load_path = "./data/load_data/"
    if file_load == "":
        root, dirs, files = next(os.walk("data/load_data/"))
        for file in files:
            if building_type in file:
                file_load = load_path + file
    load = pd.read_csv(file_load)
    return {'p_load': load['Electricity Load [J]'], 'g_load': load['Heating Load [J]'],
            'q_load': load['Cooling Load [J]'], 'r_solar': load['Environment:Site Direct Solar Radiation Rate per Area [W/m2](Hourly)']}



def save_json(j, name, res_dict="./doc/"):
    with open(res_dict+name+".json", 'w', encoding="utf-8") as f:
        json.dump(j, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    # 读参数json
    with open("data/parameters.json", encoding="utf-8") as load_file:
        input_json = json.load(load_file)
    # 读负荷csv
    # load = read_load(input_json["load"]["building_type"])
    load = read_load(input_json["load"]["building_type"], file_load = "./data/load_data/Shannxi_Yulin_system.csv")
    planning_json, operation_json, device_cap = planning_problem(load, input_json)
    save_json(planning_json, "planning_json")
    pprint.pprint(device_cap)


