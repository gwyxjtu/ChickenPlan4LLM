
import sys
import os
import json
import numpy as np
import pandas as pd
import gurobipy as gp
from gurobipy import GRB

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

    # --- 碳排放因子 ---
    alpha_e = input_param["carbon"]["alpha_e"]  # 电网排放因子 kg/kWh

    # --- 能源价格 ---
    p_price = input_param["price"]["TOU_power"] * 365  # 分时电价
    p_sell_price = input_param["price"]["p_sell_price"]  # 卖电价格
    h_price = input_param["price"]["h_price"]  # 买氢价格

    # --- 各种设备的价格 ---
    cost_el = input_param["device"]["el"]["cost"]  # 电解槽单价
    cost_eb = input_param["device"]["eb"]["cost"]  # 电锅炉单价
    cost_ghp = input_param["device"]["ghp"]["cost"]  # 地源热泵单价

    # --- 各种设备的效率系数，包括产电、产热、产冷、产氢、热交换等 ---
    k_el = input_param["device"]["el"]["k_el"]  # 电解槽产氢效率
    k_eb = input_param["device"]["eb"]["k_eb"]  # 电锅炉产热效率
    k_ghp_g = input_param["device"]["ghp"]["k_ghp_g"]  # 地源热泵产热效率
    k_ghp_q = input_param["device"]["ghp"]["k_ghp_q"]  # 地源热泵产冷效率
    g_gtw = input_param["device"]["ghp"]["g_gtw"]  # 地热井可产热量

    # ------ Variables ------
    p_el_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="p_el_inst")  # 电解槽装机容量
    h_el = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_el{t}") for t in range(period)]  # 电解槽产氢量
    p_el = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_el{t}") for t in range(period)]  # 电解槽耗电量

    p_eb_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="p_eb_inst")  # 电锅炉装机容量
    g_eb = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_eb{t}") for t in range(period)]  # 电锅炉产热量
    p_eb = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_eb{t}") for t in range(period)]  # 电锅炉耗电量

    p_ghp_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="p_ghp_inst")  # 地源热泵装机容量
    g_ghp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_ghp{t}") for t in range(period)]  # 地源热泵产热量
    q_ghp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"q_ghp{t}") for t in range(period)]  # 地源热泵产冷量
    p_ghp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_ghp{t}") for t in range(period)]  # 地源热泵耗电量
    num_gtw_inst = model.addVar(vtype=GRB.INTEGER, lb=0, name="num_gtw_inst")  # 地热井装机数量

    # ------ Update model ------
    model.update()

    # ------ Constraints ------
    # --- 设备运行约束 ---
    for t in range(period):
        # 电解槽
        model.addConstr(p_el_inst <= input_param["device"]["el"]["p_max"])  # 电解槽装机容量约束
        model.addConstr(h_el[t] <= k_el * p_el[t])  # 电解槽产氢约束
        model.addConstr(p_el[t] <= p_el_inst)  # 电解槽耗电量约束

        # 电锅炉
        model.addConstr(p_eb_inst <= input_param["device"]["eb"]["p_max"])  # 电锅炉装机容量约束
        model.addConstr(g_eb[t] == k_eb * p_eb[t])  # 电锅炉产热约束
        model.addConstr(p_eb[t] <= p_eb_inst)  # 电锅炉耗电量约束

        # 地源热泵
        model.addConstr(p_ghp_inst <= input_param["device"]["ghp"]["p_max"])  # 地源热泵装机容量约束
        model.addConstr(g_ghp[t] <= k_ghp_g * p_ghp[t])  # 地源热泵产热约束
        model.addConstr(q_ghp[t] <= k_ghp_q * p_ghp[t])  # 地源热泵产冷约束
        model.addConstr(p_ghp[t] <= p_ghp_inst)  # 地源热泵耗电量约束

    # 地热井和地源热泵有关联，地缘热泵可以从所有地热井中取得的热量最大值不得小于地源热泵最大产热量
    model.addConstr(num_gtw_inst * g_gtw >= p_ghp_inst * k_ghp_g)

    # ------ Objective ------
    capex = (cost_el * p_el_inst / input_param["device"]["el"]["life"]
             + cost_eb * p_eb_inst / input_param["device"]["eb"]["life"]
             + cost_ghp * p_ghp_inst / input_param["device"]["ghp"]["life"])  # 年化投资费用
    opex = (gp.quicksum([p_el[t] * p_price[t] for t in range(period)])  # 运行费用
            - gp.quicksum([p_sell[t] for t in range(period)]) * p_sell_price
            + gp.quicksum([h_el[t] for t in range(period)]) * h_price)  
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

    revenue_s = sum([p_sell[t].x * p_sell_price for t in range(period)])
    revenue_p = sum([p_load[t] * p_price[t] for t in range(period)])
    revenue_g = input_param["load"]["g_area"] * input_param["price"]["g_price"] * len(
                                input_param["load"]["g_month"])
    revenue_q = input_param["load"]["q_area"] * input_param["price"]["q_price"] * len(
                                input_param["load"]["q_month"] )
    cap_sum = (cost_pv * s_pv_inst.x
               + cost_sc * s_sc_inst.x
               + cost_fc * p_fc_inst.x
               + cost_el * p_el_inst.x
               + cost_eb * p_eb_inst.x
               + cost_hp * p_hp_inst.x
               + cost_ghp * p_ghp_inst.x
               + cost_gtw * num_gtw_inst.x
               + cost_hst * h_hst_inst.x
               + cost_tank * m_tank_inst.x)
    opex = sum([p_pur[t].x * p_price[t] for t in range(period)]) + sum([h_pur[t].x for t in range(period)]) * h_price
    # 规划输出
    output_json = {
        "ele_load_sum": int(sum(p_load)),  # 电负荷总量/kwh
        "g_demand_sum": int(sum(g_load)),  # 热负荷总量/kwh
        "q_demand_sum": int(sum(q_load)),  # 冷负荷总量/kwh
        "ele_load_max": int(max(p_load)),  # 电负荷峰值/kwh
        "g_demand_max": int(max(g_load)),  # 热负荷峰值/kwh
        "q_demand_max": int(max(q_load)),  # 冷负荷峰值/kwh
        "ele_load": p_load.tolist(),  # 电负荷8760h的分时数据/kwh
        "g_demand": g_load.tolist(),  # 热负荷8760h的分时数据/kwh
        "q_demand": q_load.tolist(),  # 冷负荷8760h的分时数据/kwh
        "r_solar": r_solar.tolist(),  # 光照强度8760h的分时数据/kwh
        "num_gtw_inst": num_gtw_inst.X,  # 地热井数目/个
        "p_fc_inst": format(p_fc_inst.X, ".1f"),  # 燃料电池容量/kw
        "p_ghp_inst": format(p_ghp_inst.X, ".1f"),  # 地源热泵功率/kw
        "p_hp_inst": format(p_hp_inst.X, ".1f"),  # 空气源热泵功率/kw
        "p_eb_inst": format(p_eb_inst.X, ".1f"),  # 电热锅炉功率/kw
        "p_el_inst": format(p_el_inst.X, ".1f"),  # 电解槽功率/kw
        "h_hst_inst": format(h_hst_inst.X, ".1f"),  # 储氢罐容量/kg
        "m_tank_inst": format(m_tank_inst.X, ".1f"),  # 蓄水箱/kg
        "P_pv": format(s_pv_inst.X, ".1f"),  # 光伏面积/m2
        "G_sc": format(s_sc_inst.X, ".1f"),  # 集热器面积/m2

        "cap_fc": cost_fc * p_fc_inst.X,
        "cap_ghp": cost_ghp * p_ghp_inst.X,
        "cap_gtw": cost_gtw * num_gtw_inst.X,
        "cap_hp": cost_hp * p_hp_inst.X,
        "cap_eb": cost_eb * p_eb_inst.X,
        "cap_hst": cost_hst * h_hst_inst.X,
        "cap_tank": cost_tank * m_tank_inst.X,
        "cap_pv": cost_pv * s_pv_inst.X,
        "cap_sc": cost_sc * s_sc_inst.X,
        "cap_el": cost_el * p_el_inst.X,

        "captial": format(cap_sum / 10000, ".2f"),  # 设备总投资/万元
        "op_sum": format(opex / 10000, ".2f"),  # 设备运行总成本/万元
        "receive_year": format(cap_sum / (revenue_g + revenue_q + revenue_p + revenue_s - opex + 0.01), ".2f"),  # 投资回报年限/年
    }


    device_cap = {
        "num_gtw_inst": num_gtw_inst.X,  # 地热井数目/个
        "p_fc_inst": p_fc_inst.X,  # 燃料电池容量/kw
        "p_ghp_inst": p_ghp_inst.X,  # 地源热泵功率/kw
        "p_hp_inst": p_hp_inst.X,  # 空气源热泵功率/kw

        "p_eb_inst": p_eb_inst.X,  # 电热锅炉功率/kw
        "p_el_inst": p_el_inst.X,  # 电解槽功率/kw
        "h_hst_inst": h_hst_inst.X,  # 储氢罐容量/kg
        "m_tank_inst": m_tank_inst.X,  # 蓄水箱/kg
        "p_pv": s_pv_inst.X,  # 光伏/kW
        "g_sc": s_sc_inst.X,  # 集热器/kW
        "revenue_p": revenue_p,
        "revenue_q": revenue_q,
        "revenue_g": revenue_g,
        "revenue_s": revenue_s,

        "cap_device": {
            "num_gtw_inst": num_gtw_inst.X,  # 地热井数目/个
            "p_fc_inst": format(p_fc_inst.X, ".1f"),  # 燃料电池容量/kw
            "p_ghp_inst": format(p_ghp_inst.X, ".1f"),  # 地源热泵功率/kw
            "p_hp_inst": format(p_hp_inst.X, ".1f"),  # 空气源热泵功率/kw
            "p_eb_inst": format(p_eb_inst.X, ".1f"),  # 电热锅炉功率/kw
            "p_el_inst": format(p_el_inst.X, ".1f"),  # 电解槽功率/kw
            "h_hst_inst": format(h_hst_inst.X, ".1f"),  # 储氢罐容量/kg
            "m_tank_inst": format(m_tank_inst.X, ".1f"),  # 蓄水箱装机容量/kg
            "P_pv": format(s_pv_inst.X, ".1f"),  # 光伏面积/m2
            "G_sc": format(s_sc_inst.X, ".1f"),  # 集热器面积/m2
        },
    }
    ele_sum_ele_only = np.array(p_load) + np.array(g_load) / k_eb + np.array(q_load) / k_ghp_q
    co2_ele_only = sum(ele_sum_ele_only) * input_param["carbon"]["alpha_e"]
    operation_output_json = {
        "op_cost":
            {
                "all_of_revenue":
                    {
                        "all_revenue": format((revenue_g+revenue_q+revenue_s+revenue_p) / 10000, ".2f"),
                        "p_sol_revenue": format(revenue_s, ".2f"),
                        "revenue_heat": format(revenue_g, ".2f"),
                        "revenue_cold": format(revenue_q, ".2f"),
                    },
                "all_of_op_cost":
                    {
                        "all_op_cost": format(opex / 10000, ".2f"),
                        "p_pur_cost": format(sum([p_pur[t].X * p_price[t] for t in range(period)]), ".2f"),
                        "h_pur_cost": format(h_price * sum([h_pur[t].X for t in range(period)]), ".2f")
                    },
                "net_revenue": format((revenue_g + revenue_q + revenue_s + revenue_p - opex) / 10000, ".2f"),
                "ele_statistics":
                    {
                        "sum_pv": format(sum(p_pv[t].X for t in range(period)), ".2f"),
                        "sum_fc": format(sum(p_fc[t].X for t in range(period)), ".2f"),
                        "sum_p_pur": format(sum(p_pur[t].X for t in range(period)), ".2f"),
                        "sum_p_sell": format(sum(p_sell[t].X for t in range(period)), ".2f")
                    }
            },
        "co2": format(sum(p_pur[t].X for t in range(period))*alpha_e / 1000, ".1f"),  # 总碳排/t
        "cer_rate": format((co2_ele_only - sum(p_pur[t].X for t in range(period))) / co2_ele_only * 100, ".1f"),  # 与电系统相比的碳减排率
        "cer_perm2": format((co2_ele_only - sum(p_pur[t].X for t in range(period))) / input_param["load"]["p_area"] / 1000, ".1f"),  # 电系统每平米的碳减排量/t
        "cer": format((co2_ele_only - sum(p_pur[t].X for t in range(period))) / 1000, ".2f"),
    }
    return output_json, operation_output_json, device_cap


# 读参数json
with open(project_path+"/data/parameters.json", "r", encoding="utf-8") as load_file:
    input_json = json.load(load_file)
    
# 读负荷csv
load = read_load(input_json["load"]["building_type"])

planning_json, operation_json, device_cap = planning_problem(load, input_json)
planning_result_path = project_path + "/doc/planning_result.json"
with open(planning_result_path, "w", encoding="utf-8") as f:
    json.dump(planning_json, f, ensure_ascii=False, indent=4)
print("Planning result saved to", planning_result_path)
