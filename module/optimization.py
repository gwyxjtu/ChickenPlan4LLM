import sys
import os
import numpy as np
import gurobipy as gp
from gurobipy import GRB

# from branch_and_bound_class import *
from module.utils import to_xls


def planning_problem(period_data, input_param):
    """规划问题求解

    Args:
        period_data (dict): 各时段数据，包括光照强度、电负荷、热负荷、冷负荷
        input_param (dict): 输入参数，包括碳排放因子、能源价格、设备价格、设备效率等

    Returns:

    """
    # ------ Create model ------
    model = gp.Model("OptModel")

    # ------ Parameters input ------
    # --- 参数输入，时序数据包括电、热、冷、光照强度；单一数据包括碳排放因子、能源价格、设备价格、设备效率等 ---
    # --- 各时段数据 ---
    p_load = period_data["p_load"]*input_param["load"]["p_area"]  # 电负荷乘以面积
    g_load = period_data["g_load"]*input_param["load"]["g_area"]  # 热负荷乘以面积
    q_load = period_data["q_load"]*input_param["load"]["q_area"]  # 冷负荷乘以面积
    r_solar = period_data["r_solar"]  # 光照强度

    period = len(p_load)  # 总时段数

    # 展示负荷信息
    print("热负荷总量{}，冷负荷总量：{}，电负荷总量：{}".format(sum(g_load), sum(q_load), sum(p_load)))
    print("热负荷峰值{}，冷负荷峰值：{}，电负荷峰值：{}".format(max(g_load), max(q_load), max(p_load)))
    print("-" * 10 + "g, q, e_load" + "-" * 10)
    p_load, g_load, q_load, r_solar = np.array(p_load), np.array(g_load), np.array(q_load), np.array(r_solar)
    r_solar = r_solar * 4000 # 单位转化
    # --- 碳排放因子 ---
    alpha_e = input_param["carbon"]["alpha_e"]  # 电网排放因子 kg/kWh
    # --- 能源价格 ---
    p_price = input_param["price"]["TOU_power"] * 365  # 分时电价
    p_sel_price = input_param["price"]["p_sel_price"]  # 卖电价格
    h_price = input_param["price"]["h_price"]  # 买氢价格

    c = 4.2 / 3600  # 水的比热容
    M = 1e7  # 大 M
    # --- 各种设备的价格 ---
    cost_pv = input_param["device"]["pv"]["cost"]
    cost_sc = input_param["device"]["sc"]["cost"]
    cost_fc = input_param["device"]["fc"]["cost"]
    cost_el = input_param["device"]["el"]["cost"]
    cost_eb = input_param["device"]["eb"]["cost"]
    cost_hp = input_param["device"]["hp"]["cost"]
    cost_ghp = input_param["device"]["ghp"]["cost"]
    cost_gtw = input_param["device"]["gtw"]["cost"]
    cost_hst = input_param["device"]["hst"]["cost"]
    cost_ht = input_param["device"]["ht"]["cost"]  # yuan/kwh

    # --- 各种设备的效率系数，包括产热、制冷、发电、热转换等 ---
    k_pv = input_param["device"]["pv"]["k_pv"]
    k_sc = input_param["device"]["sc"]["k_sc"]
    k_fc_p = input_param["device"]["fc"]["k_fc_p"]
    k_fc_g = input_param["device"]["fc"]["k_fc_g"]
    eta_ex = 0.95
    k_el = input_param["device"]["el"]["k_el"]
    k_eb = input_param["device"]["eb"]["k_eb"]
    k_hp_g = input_param["device"]["hp"]["k_hp_g"]
    k_hp_q = input_param["device"]["hp"]["k_hp_q"]
    k_ghp_g = input_param["device"]["ghp"]["k_ghp_g"]
    k_ghp_q = input_param["device"]["ghp"]["k_ghp_q"]
    g_gtw = input_param["device"]["gtw"]["g_gtw"]

    g_gtw = input_param["device"]["gtw"]["g_gtw"]
    mu_ht_loss = 0.001

    # ------ Variables ------
    h_pur = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_pur{t}") for t in range(period)]  # hydrogen purchase
    p_pur = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_pur{t}") for t in range(period)]  # power purchase
    p_sel = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_sel{t}") for t in range(period)]  # power sold

    p_pv_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["pv"]["p_max"], name=f"s_pv_inst")  # ub=13340,
    p_pv = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_pv{t}") for t in range(period)]

    g_sc_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["sc"]["g_max"], name=f"s_sc_inst")
    g_sc = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_sc{t}") for t in range(period)]

    p_fc_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["fc"]["p_max"], name=f"p_fc_inst")
    h_fc = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_fc{t}") for t in range(period)]  # 燃料电池耗氢量
    p_fc = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_fc{t}") for t in range(period)]  # 燃料电池产电量
    g_fc = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_fc{t}") for t in range(period)]  # 燃料电池产热量

    p_el_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["el"]["p_max"], name="p_el_inst")  # rated heat power of fuel cells
    h_el = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_el{t}") for t in range(period)]  # 电解槽制氢量
    p_el = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_el{t}") for t in range(period)]  # 电解槽耗电量

    p_eb_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["eb"]["p_max"], name=f"p_eb_inst")
    p_eb = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_eb{t}") for t in range(period)]  # 电锅炉耗电
    g_eb = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_eb{t}") for t in range(period)]  # 电锅炉产热

    p_hp_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["hp"]["p_max"], name=f"p_hp_inst")
    p_hp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_hp{t}") for t in range(period)]  # 热泵产热的耗电 
    g_hp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_hp{t}") for t in range(period)]  # 热泵产热
    q_hp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"q_hp{t}") for t in range(period)]  # 热泵产冷

    p_ghp_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["ghp"]["p_max"], name=f"p_ghp_inst")
    p_ghp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_ghp{t}") for t in range(period)]  # 热泵产热耗电 
    g_ghp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_ghp{t}") for t in range(period)]  # 热泵产热
    g_ghp_gr = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_ghp_gr{t}") for t in range(period)]  # 热泵灌热
    q_ghp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"q_ghp{t}") for t in range(period)]  # 热泵产热

    num_gtw_inst = model.addVar(vtype=GRB.INTEGER, lb=0, name="num_gtw_inst")  # 地热井

    h_hst_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["hst"]["h_max"], name=f"h_hst_inst")
    h_hst = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_hst{t}") for t in range(period)]  # 储氢罐储氢量

    m_ht_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["ht"]["m_max"], name=f"m_ht_inst")
    t_ht = [model.addVar(vtype=GRB.CONTINUOUS, lb=input_param["device"]["ht"]["t_min"], ub=input_param["device"]["ht"]["t_max"], name=f"t_ht{t}") for t in range(period)]  # temperature of heat storage tank
    g_ht = [model.addVar(vtype=GRB.CONTINUOUS, lb=-M, name=f"g_ht{t}") for t in range(period)]

    m_ct_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["ct"]["m_max"], name=f"m_ct_inst")
    t_ct = [model.addVar(vtype=GRB.CONTINUOUS, lb=input_param["device"]["ct"]["t_min"], ub=input_param["device"]["ct"]["t_max"], name=f"t_ct{t}") for t in range(period)]  # temperature of cold water tank
    q_ct = [model.addVar(vtype=GRB.CONTINUOUS, lb=-M, name=f"q_ct{t}") for t in range(period)]

    g_tube = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_tube{t}") for t in range(period)]
    model.update()

    # ------ Constraints ------
    # --- 设备运行约束 ---
    for i in range(period):
        # 光伏板
        model.addConstr(p_pv[i] <= k_pv * p_pv_inst * r_solar[i])  # 光伏板发电约束
        # 太阳能集热器
        model.addConstr(g_sc[i] <= k_sc * g_sc_inst * r_solar[i])  # 太阳能集热器产热约束
        # 燃料电池
        model.addConstr(p_fc[i] == k_fc_p * h_fc[i])  # 燃料电池产电约束
        model.addConstr(g_fc[i] == eta_ex * k_fc_g * h_fc[i])  # 燃料电池产热约束

        model.addConstr(p_fc[i] <= p_fc_inst)  # 燃料电池功率约束
        # 电解槽
        model.addConstr(h_el[i] <= k_el * p_el[i])  # 电解槽产氢约束
        model.addConstr(p_el[i] <= p_el_inst)  # 电解槽功率约束

        # 电锅炉
        model.addConstr(g_eb[i] == k_eb * p_eb[i])  # 电锅炉产热约束
        model.addConstr(p_eb[i] <= p_eb_inst)  # 电锅炉功率约束

        # 热泵
        model.addConstr(g_hp[i] <= k_hp_g * p_hp[i])  # 热泵产热约束
        model.addConstr(q_hp[i] <= k_hp_q * p_hp[i])  # 热泵产冷约束
        model.addConstr(p_hp[i] <= p_hp_inst)  # 热泵产热功率约束

        # 地源热泵
        model.addConstr(g_ghp[i] <= p_ghp[i] * k_ghp_g)  # 地源热泵产热约束
        model.addConstr(q_ghp[i] <= p_ghp[i] * k_ghp_q)  # 地源热泵产冷约束
        model.addConstr(p_ghp[i] <= p_ghp_inst)  # 地源热泵产热功率约束

        # 储氢罐
        model.addConstr(h_hst[i] <= h_hst_inst)

    model.addConstr(num_gtw_inst * g_gtw >= p_ghp_inst * k_ghp_g)  # 井和热泵有关联
    
    # --- 能量平衡约束 ---
    # 电平衡约束
    model.addConstrs(p_load[i] == p_pur[i] + p_pv[i] + p_fc[i]
                     - p_sel[i] - p_el[i] - p_eb[i] - p_hp[i] - p_ghp[i]
                     for i in range(period))
    for i in range(period - 1):
        # 热平衡约束
        model.addConstr(g_ht[i] == (-c * m_ht_inst * (t_ht[i + 1] - t_ht[i])
                                    - mu_ht_loss * c * m_ht_inst * (t_ht[i] - input_param["device"]["ht"]["t_min"])))  # 热水箱供热量
        model.addConstr(g_tube[i] == (g_fc[i] + g_eb[i] + g_sc[i] + g_hp[i] + g_ht[i]
                                     - g_ghp_gr[i]))  # 管网供热量
        model.addConstr(g_load[i] == g_tube[i] + g_ghp[i])  # 热负荷平衡约束
        # 冷平衡约束
        model.addConstr(q_ct[i] == c * m_ht_inst * (t_ct[i + 1] - t_ct[i]))  # 冷水箱供冷量
        model.addConstr(q_load[i] == q_hp[i] + q_ghp[i] + q_ct[i])  # 冷负荷平衡约束

        # 储氢平衡约束
        model.addConstr(h_hst[i + 1] - h_hst[i] == h_pur[i] + h_el[i] - h_fc[i])  # 储氢罐约束
    # 末时刻热平衡约束，需保证调度周期始末热水箱温度一致
    model.addConstr(g_ht[-1] == (-c * m_ht_inst * (t_ht[0] - t_ht[-1])
                                 - mu_ht_loss * c * m_ht_inst * (t_ht[i] - input_param["device"]["ht"]["t_min"])))  # 热水箱供热量
    model.addConstr(g_tube[-1] == (g_fc[-1] + g_eb[-1] + g_sc[-1] + g_hp[-1] + g_ht[-1]
                                   - g_ghp_gr[-1]))  # 管网供热量
    model.addConstr(g_load[-1] == g_tube[-1] + g_ghp[-1])  # 热负荷平衡约束
    # 末时刻冷平衡约束，需保证调度周期始末冷水箱温度一致
    model.addConstr(q_ct[-1] == c * m_ht_inst * (t_ct[0] - t_ct[-1]))  # 冷水箱供冷量
    model.addConstr(g_load[-1] == q_hp[-1] + q_ghp[-1] + q_ct[-1])  # 冷负荷平衡约束
    # 储氢平衡约束
    model.addConstr(h_hst[0] - h_hst[-1] == h_pur[-1] + h_el[-1] - h_fc[-1])  # 储氢罐约束

    # ------ Objective ------
    capex = ( cost_pv * p_pv_inst / input_param["device"]["pv"]["life"]
                 + p_fc_inst * cost_fc / input_param["device"]["fc"]["life"]
                 + p_el_inst * cost_el / input_param["device"]["el"]["life"]
                 + p_eb_inst * cost_eb / input_param["device"]["eb"]["life"]
                 + g_sc_inst * cost_sc / input_param["device"]["sc"]["life"]
                 + p_hp_inst * cost_hp / input_param["device"]["hp"]["life"]
                 + p_ghp_inst * cost_ghp / input_param["device"]["ghp"]["life"]
                 + num_gtw_inst * cost_gtw / input_param["device"]["gtw"]["life"]
                 + h_hst_inst * cost_hst / input_param["device"]["hst"]["life"]
                 + m_ht_inst * cost_ht / input_param["device"]["ht"]["life"]) # 年化投资费用
    opex = (gp.quicksum([p_pur[i] * p_price[i] for i in range(period)])
            - gp.quicksum([p_sel[i] for i in range(period)]) * p_sel_price
            + gp.quicksum([h_pur[i] for i in range(period)]) * h_price) # 运行费用

    model.setObjective(
        (capex + opex),
        GRB.MINIMIZE
    )
    # ------ Optimize ------
    model.params.NonConvex = 2
    model.Params.LogFile = "log/mip.log"
    model.params.MIPGap = 0.01
    try:
        model.optimize()
    except gp.GurobiError:
        print("Optimize failed due to non-convexity")
    if model.status == GRB.INFEASIBLE or model.status == 4:
        print("Model is infeasible")
        model.computeIIS()
        model.write("log/model.ilp")
        print("Irreducible inconsistent subsystem is written to file 'model.ilp'")

    revenue_s = sum([p_sel[i].x * p_sel_price for i in range(period)])
    revenue_p = sum([p_load[i] * p_price[i] for i in range(period)])
    revenue_g = input_param["load"]["g_area"] * input_param["price"]["g_price"] * len(
                                input_param["load"]["g_month"])
    revenue_q = input_param["load"]["q_area"] * input_param["price"]["q_price"] * len(
                                input_param["load"]["q_month"] )
    cap_sum = p_fc_inst.x * cost_fc + p_pv_inst.x * cost_pv + p_hp_inst.x * cost_hp + p_ghp_inst.x * cost_ghp + \
              g_sc_inst.x * cost_sc + p_eb_inst.x * cost_eb + p_el_inst.x * cost_el + num_gtw_inst.x * cost_gtw + \
              h_hst_inst.x * cost_hst + m_ht_inst.x * cost_ht
    opex = sum([p_pur[i].x * p_price[i] for i in range(period)]) + sum([h_pur[i].x for i in range(period)]) * h_price
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
        "m_ht_inst": format(m_ht_inst.X, ".1f"),  # 储热罐/kg
        "m_ct_inst": format(m_ct_inst.X, ".1f"),  # 冷水罐/kg
        "P_pv": format(p_pv_inst.X, ".1f"),  # 光伏面积/m2
        "G_sc": format(g_sc_inst.X, ".1f"),  # 集热器面积/m2

        "cap_fc": cost_fc * p_fc_inst.X,
        "cap_ghp": cost_ghp * p_ghp_inst.X,
        "cap_gtw": cost_gtw * num_gtw_inst.X,
        "cap_hp": cost_hp * p_hp_inst.X,
        "cap_eb": cost_eb * p_eb_inst.X,
        "cap_hst": cost_hst * h_hst_inst.X,
        "cap_ht": cost_ht * m_ht_inst.X,
        "cap_pv": p_pv_inst.X * cost_pv,
        "cap_sc": cost_sc * g_sc_inst.X,
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
        "m_ht_inst": m_ht_inst.X,  # 储热罐/kg
        "m_ct_inst": m_ct_inst.X,  # 冷水罐/kg
        "p_pv": p_pv_inst.X,  # 光伏/kW
        "g_sc": g_sc_inst.X,  # 集热器/kW
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
            "m_ht_inst": format(m_ht_inst.X, ".1f"),  # 储热罐/kg
            "m_ct_inst": format(m_ct_inst.X, ".1f"),  # 冷水罐/kg
            "P_pv": format(p_pv_inst.X, ".1f"),  # 光伏面积/m2
            "G_sc": format(g_sc_inst.X, ".1f"),  # 集热器面积/m2
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
                        "p_pur_cost": format(sum([p_pur[i].X * p_price[i] for i in range(period)]), ".2f"),
                        "h_pur_cost": format(h_price * sum([h_pur[i].X for i in range(period)]), ".2f")
                    },
                "net_revenue": format((revenue_g + revenue_q + revenue_s + revenue_p - opex) / 10000, ".2f"),
                "ele_statistics":
                    {
                        "sum_pv": format(sum(p_pv[i].X for i in range(period)), ".2f"),
                        "sum_fc": format(sum(p_fc[i].X for i in range(period)), ".2f"),
                        "sum_p_pur": format(sum(p_pur[i].X for i in range(period)), ".2f"),
                        "sum_p_sol": format(sum(p_sel[i].X for i in range(period)), ".2f")
                    }
            },
        "co2": format(sum(p_pur[i].X for i in range(period))*alpha_e / 1000, ".1f"),  # 总碳排/t
        "cer_rate": format((co2_ele_only - sum(p_pur[i].X for i in range(period))) / co2_ele_only * 100, ".1f"),  # 与电系统相比的碳减排率
        "cer_perm2": format((co2_ele_only - sum(p_pur[i].X for i in range(period))) / input_param["load"]["p_area"] / 1000, ".1f"),  # 电系统每平米的碳减排量/t
        "cer": format((co2_ele_only - sum(p_pur[i].X for i in range(period))) / 1000, ".2f"),
    }
    return output_json, operation_output_json, device_cap


if __name__ == "__main__":
    sys_path = sys.path
    print("Sys path:")
    for i in sys_path:
        print(i)
    project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print("-" * 20)
    print("Project path:", project_path, sep="\n")
    if project_path not in sys.path:
        print("Project path not in sys path, add it.")
        sys.path.append(project_path)
    else:
        print("Project path already in sys path.")
    print("Start")
