
import sys
import os
import json
import numpy as np
import pandas as pd
import gurobipy as gp
from gurobipy import GRB
# project_path = os.path.dirname(os.path.realpath(__file__))
# project_path = project_path.replace("\", "/")
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
    return {
        'p_load': load['Electricity Load [J]'],
        'g_load': load['Heating Load [J]'],
        'q_load': load['Cooling Load [J]'],
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
    cost_sc = input_param["device"]["sc"]["cost"]  # 太阳能集热器单价
    cost_fc = input_param["device"]["fc"]["cost"]  # 氢燃料电池单价
    cost_el = input_param["device"]["el"]["cost"]  # 电解槽单价
    cost_eb = input_param["device"]["eb"]["cost"]  # 电锅炉单价
    cost_hp = input_param["device"]["hp"]["cost"]  # 热泵单价
    cost_ghp = input_param["device"]["ghp"]["cost"]  # 地源热泵单价
    cost_gtw = input_param["device"]["gtw"]["cost"]  # 地热井单价
    cost_hst = input_param["device"]["hst"]["cost"]  # 储氢罐单价
    cost_tank = input_param["device"]["tank"]["cost"]  # 蓄水箱单价，元/kWh

    # --- 各种设备的效率系数，包括产电、产热、产冷、产氢、热交换等 ---
    k_pv = input_param["device"]["pv"]["k_pv"]  # 光伏板产电效率
    k_sc = input_param["device"]["sc"]["k_sc"]  # 太阳能集热器产热效率
    k_fc_p = input_param["device"]["fc"]["k_fc_p"]  # 氢燃料电池产电效率
    k_fc_g = input_param["device"]["fc"]["k_fc_g"]  # 氢燃料电池产热效率
    eta_ex = input_param["device"]["fc"]["eta_ex"]  # 燃料电池热交换效率
    k_el = input_param["device"]["el"]["k_el"]  # 电解槽产氢效率
    k_eb = input_param["device"]["eb"]["k_eb"]  # 电锅炉产热效率
    k_hp_g = input_param["device"]["hp"]["k_hp_g"]  # 热泵产热效率
    k_hp_q = input_param["device"]["hp"]["k_hp_q"]  # 热泵产冷效率
    k_ghp_g = input_param["device"]["ghp"]["k_ghp_g"]  # 地源热泵产热效率
    k_ghp_q = input_param["device"]["ghp"]["k_ghp_q"]  # 地源热泵产冷效率
    mu_tank_loss = input_param["device"]["tank"]["mu_loss"]  # 蓄水箱能量损失系数

    g_gtw = input_param["device"]["gtw"]["g_gtw"]  # 地热井可产热量

    t_ht_min = input_param["device"]["tank"]["t_ht_min"]

    # ------ Variables ------
    h_pur = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_pur{t}") for t in range(period)]  # 从氢气市场购氢量
    p_pur = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_pur{t}") for t in range(period)]  # 从电网购电量
    p_sell = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_sell{t}") for t in range(period)]  # 向电网卖电量
    # 光伏板
    s_pv_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["pv"]["area_max"], name=f"s_pv_inst")  # 光伏板装机容量
    p_pv = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_pv{t}") for t in range(period)]  # 光伏板产电量
    # 太阳能集热器
    s_sc_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["sc"]["area_max"], name=f"s_sc_inst")  # 太阳能集热器装机容量
    g_sc = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_sc{t}") for t in range(period)]  # 太阳能集热器产热量
    # 氢燃料电池
    p_fc_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["fc"]["p_max"], name=f"p_fc_inst")  # 氢燃料电池装机容量
    h_fc = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_fc{t}") for t in range(period)]  # 氢燃料电池耗氢量
    p_fc = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_fc{t}") for t in range(period)]  # 氢燃料电池产电量
    g_fc = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_fc{t}") for t in range(period)]  # 氢燃料电池产热量
    # 电解槽
    p_el_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["el"]["p_max"], name="p_el_inst")  # 电解槽装机容量
    h_el = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_el{t}") for t in range(period)]  # 电解槽产氢量
    p_el = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_el{t}") for t in range(period)]  # 电解槽耗电量
    # 电锅炉
    p_eb_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["eb"]["p_max"], name=f"p_eb_inst")  # 电锅炉装机容量
    p_eb = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_eb{t}") for t in range(period)]  # 电锅炉耗电量
    g_eb = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_eb{t}") for t in range(period)]  # 电锅炉产热量
    # 空气源热泵
    p_hp_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["hp"]["p_max"], name=f"p_hp_inst")  # 空气源热泵装机容量
    p_hp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_hp{t}") for t in range(period)]  # 空气源热泵耗电量
    g_hp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_hp{t}") for t in range(period)]  # 空气源热泵产热量
    q_hp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"q_hp{t}") for t in range(period)]  # 空气源热泵产冷量
    # 地源热泵
    p_ghp_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["ghp"]["p_max"], name=f"p_ghp_inst")  # 地源热泵装机容量
    p_ghp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_ghp{t}") for t in range(period)]  # 地源热泵耗电量
    g_ghp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_ghp{t}") for t in range(period)]  # 地源热泵产热量
    q_ghp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"q_ghp{t}") for t in range(period)]  # 地源热泵产冷量
    # 地热井
    num_gtw_inst = model.addVar(vtype=GRB.INTEGER, lb=0, ub=input_param["device"]["gtw"]["number_max"], name="num_gtw_inst")  # 地热井装机数量
    # 储氢罐
    h_hst_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["hst"]["h_max"], name=f"h_hst_inst")  # 储氢罐装机容量
    h_hst = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_hst{t}") for t in range(period)]  # 储氢罐储氢量
    delta_h_hst = [model.addVar(vtype=GRB.CONTINUOUS, lb=-M, name=f"delta_h_hst{t}") for t in range(period)]  # 储氢罐储氢变化量
    # 热水箱
    m_tank_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["tank"]["m_max"], name=f"m_tank_inst")  # 蓄水箱装机容量
    t_ht = [model.addVar(vtype=GRB.CONTINUOUS, lb=input_param["device"]["tank"]["t_ht_min"], ub=input_param["device"]["tank"]["t_ht_max"], name=f"t_ht{t}") for t in range(period)]  # 热水箱水温
    g_ht = [model.addVar(vtype=GRB.CONTINUOUS, lb=-M, name=f"g_ht{t}") for t in range(period)]  # 热水箱供热量
    delta_g_ht = [model.addVar(vtype=GRB.CONTINUOUS, lb=-M, name=f"delta_g_ht{t}") for t in range(period)]  # 热水箱储热变化量
    g_ht_loss = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_ht_loss{t}") for t in range(period)]  # 热水箱热损失量
    t_ct = [model.addVar(vtype=GRB.CONTINUOUS, lb=input_param["device"]["tank"]["t_ct_min"], ub=input_param["device"]["tank"]["t_ct_max"], name=f"t_ct{t}") for t in range(period)]  # 冷水箱水温
    q_ct = [model.addVar(vtype=GRB.CONTINUOUS, lb=-M, name=f"q_ct{t}") for t in range(period)]  # 冷水箱供冷量
    delta_q_ct = [model.addVar(vtype=GRB.CONTINUOUS, lb=-M, name=f"delta_q_ct{t}") for t in range(period)]  # 冷水箱储冷变化量
    # 管网
    g_tube = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_tube{t}") for t in range(period)]  # 管网供热量
    g_ghp_inj = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_ghp_inj{t}") for t in range(period)]  # 地源热泵灌热量

    # 设备装机列表，每次必须生成，只包含上文建模出现过的设备
    device_inst_list = {
        "电解槽": p_el_inst,
        "光伏板": s_pv_inst,
        "燃料电池": p_fc_inst,
        "电锅炉": p_eb_inst,
        "空气源热泵": p_hp_inst,
        "地源热泵": p_ghp_inst,
        "地热井": num_gtw_inst,
        "储氢罐": h_hst_inst,
        "热水箱": m_tank_inst,
    }
    # ------ Update model ------
    model.update()

    # ------ Constraints ------
    # --- 设备运行约束 ---
    for t in range(period):
        # 光伏板
        model.addConstr(p_pv[t] <= k_pv * s_pv_inst * r_solar[t])  # 光伏板发电约束
        # 太阳能集热器
        model.addConstr(g_sc[t] <= k_sc * s_sc_inst * r_solar[t])  # 太阳能集热器产热约束
        # 燃料电池
        model.addConstr(p_fc[t] == k_fc_p * h_fc[t])  # 燃料电池产电约束
        model.addConstr(g_fc[t] == eta_ex * k_fc_g * h_fc[t])  # 燃料电池产热约束
        model.addConstr(p_fc[t] <= p_fc_inst)  # 燃料电池功率约束
        # 电解槽
        model.addConstr(h_el[t] <= k_el * p_el[t])  # 电解槽产氢约束
        model.addConstr(p_el[t] <= p_el_inst)  # 电解槽功率约束
        # 电锅炉
        model.addConstr(g_eb[t] == k_eb * p_eb[t])  # 电锅炉产热约束
        model.addConstr(p_eb[t] <= p_eb_inst)  # 电锅炉功率约束
        # 热泵
        model.addConstr(g_hp[t] <= k_hp_g * p_hp[t])  # 热泵产热约束
        model.addConstr(q_hp[t] <= k_hp_q * p_hp[t])  # 热泵产冷约束
        model.addConstr(p_hp[t] <= p_hp_inst)  # 热泵产热功率约束
        # 地源热泵
        model.addConstr(g_ghp[t] <= p_ghp[t] * k_ghp_g)  # 地源热泵产热约束
        model.addConstr(q_ghp[t] <= p_ghp[t] * k_ghp_q)  # 地源热泵产冷约束
        model.addConstr(p_ghp[t] <= p_ghp_inst)  # 地源热泵产热功率约束
        # 储氢罐
        model.addConstr(h_hst[t] <= h_hst_inst)  # 储氢罐储氢量约束
        # 热水箱（蓄水箱储热时）
        model.addConstr(g_ht[t] == -delta_g_ht[t] - g_ht_loss[t])  # 热水箱供热量
        model.addConstr(g_ht_loss[t] == mu_tank_loss * c_water * m_tank_inst * (t_ht[t] - t_ht_min))  # 热水箱热损失量
        # 冷水箱（蓄水箱储冷时）
        model.addConstr(q_ct[t] == -delta_q_ct[t])  # 冷水箱供冷量

    # 地热井和地源热泵有关联，地缘热泵可以从所有地热井中取得的热量最大值不得小于地源热泵最大产热量
    model.addConstr(num_gtw_inst * g_gtw >= p_ghp_inst * k_ghp_g)
    # 储能设备约束
    for t in range(period - 1):
        model.addConstr(delta_h_hst[t] == h_hst[t + 1] - h_hst[t])  # 储氢罐储氢变化量
        model.addConstr(delta_g_ht[t] == c_water * m_tank_inst * (t_ht[t + 1] - t_ht[t]))  # 热水箱储热变化量
        model.addConstr(delta_q_ct[t] == -c_water * m_tank_inst * (t_ct[t + 1] - t_ct[t]))  # 冷水箱储冷变化量
    # 调度周期结束时，须保证储氢罐储氢量与初始时刻储氢量一致，以及蓄水箱（热水箱/冷水箱）水温与初始时刻水温一致
    model.addConstr(delta_h_hst[-1] == h_hst[0] - h_hst[-1])  # 储氢罐约束
    model.addConstr(delta_g_ht[-1] == c_water * m_tank_inst * (t_ht[0] - t_ht[-1]))  # 热水箱约束
    model.addConstr(delta_q_ct[-1] == -c_water * m_tank_inst * (t_ct[0] - t_ct[-1]))  # 冷水箱约束

    # --- 能量平衡约束 ---
    for t in range(period):
        model.addConstr(p_pur[t] + p_pv[t] + p_fc[t] - p_sell[t] == p_load[t] + p_el[t] + p_eb[t] + p_hp[t] + p_ghp[t])  # 电平衡约束，只能包含已有的变量
        # g_load 为 numpy 数组，不能单独放在约束的左侧；q_load 同理
        model.addConstr(g_sc[t] + g_fc[t] + g_eb[t] + g_hp[t] + g_ht[t] + g_ghp[t] == g_load[t] + g_ghp_inj[t])  # 热平衡约束
        model.addConstr(q_hp[t] + q_ghp[t] + q_ct[t] == q_load[t])  # 冷平衡约束
        model.addConstr(h_pur[t] + h_el[t] - h_fc[t] == delta_h_hst[t])  # 氢平衡约束

    # ------ Objective ------
    # 年化投资费用，是每个设备的投资总和
    capex = (cost_pv * s_pv_inst / input_param["device"]["pv"]["life"]
             + cost_sc * s_sc_inst / input_param["device"]["sc"]["life"]
             + cost_fc * p_fc_inst / input_param["device"]["fc"]["life"]
             + cost_el * p_el_inst / input_param["device"]["el"]["life"]
             + cost_eb * p_eb_inst / input_param["device"]["eb"]["life"]
             + cost_hp * p_hp_inst / input_param["device"]["hp"]["life"]
             + cost_ghp * p_ghp_inst / input_param["device"]["ghp"]["life"]
             + cost_gtw * num_gtw_inst / input_param["device"]["gtw"]["life"]
             + cost_hst * h_hst_inst / input_param["device"]["hst"]["life"]
             + cost_tank * m_tank_inst / input_param["device"]["tank"]["life"])  
    # 运行费用
    opex = (gp.quicksum([p_pur[t] * p_price[t] for t in range(period)])
            - gp.quicksum([p_sell[t] for t in range(period)]) * p_sell_price
            + gp.quicksum([h_pur[t] for t in range(period)]) * h_price)  
    model.setObjective((capex + opex), GRB.MINIMIZE)
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
with open(project_path+"/data/parameters.json", "r", encoding="utf-8") as load_file:
    input_json = json.load(load_file)
    
# 读负荷csv
load = read_load(input_json["load"]["building_type"])

device_cap = planning_problem(load, input_json)
planning_result_path = project_path + "/doc/planning_result.json"
with open(planning_result_path, "w", encoding="utf-8") as f:
    json.dump(device_cap, f, ensure_ascii=False, indent=4)
print("device_cap result saved to", planning_result_path)
