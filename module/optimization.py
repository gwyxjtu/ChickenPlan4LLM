import sys
import os
import time
import random
from tkinter import E
import xlwt
import xlrd
import csv
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
    # 一年中每个月的天数
    days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    # 一年中每个月的累计小时数
    hours_sum = [sum(days[:i]) * 24 for i in range(12 + 1)]

    # 是否允许买电，卖电，买氢
    # trade_flag = {
    #     "p_pur": input_param["calc_mode"]["grid"]["p_pur_state"],
    #     "p_sel": input_param["calc_mode"]["grid"]["p_sel_state"],
    #     "h_pur": input_param["calc_mode"]["grid"]["h_pur_state"]
    # }

    # ------ Create model ------
    model = gp.Model("OptModel")

    # ------ Parameters ------
    # --- 各时段数据 ---
    p_load = period_data["p_load"]*input_param["load"]["p_area"]  # 电负荷乘以面积
    g_load = period_data["g_load"]*input_param["load"]["g_area"]  # 热负荷乘以面积
    q_load = period_data["q_load"]*input_param["load"]["q_area"]  # 冷负荷乘以面积
    r_solar = period_data["r_solar"]  # 光照强度

    # z_g_demand = period_data["z_heat_month"]
    # z_q_demand = period_data["z_cold_month"]

    # period = 8760  # 总时段数
    period = len(p_load)  # 总时段数

    # 展示负荷信息
    print("热负荷总量{}，冷负荷总量：{}，电负荷总量：{}".format(sum(g_load), sum(q_load), sum(p_load)))
    print("热负荷峰值{}，冷负荷峰值：{}，电负荷峰值：{}".format(max(g_load), max(q_load), max(p_load)))
    print("-" * 10 + "g, q, e_load" + "-" * 10)
    p_load, g_load, q_load, r_solar = np.array(p_load), np.array(g_load), np.array(q_load), np.array(r_solar)
    r_solar = r_solar * 4000 # 单位转化
    # --- 碳排放因子 ---
    alpha_e = input_param["carbon"]["alpha_e"]  # 电网排放因子 kg/kWh
    alpha_gas = input_param["carbon"]["alpha_gas"]  # 天然气排放因子 kg/Nm3
    alpha_h2 = input_param["carbon"]["alpha_h2"]  # 氢排放因子
    alpha_EO = input_param["carbon"]["alpha_EO"]  # 减排项目基准排放因子

    # --- 能源价格 ---
    p_price = input_param["price"]["TOU_power"] * 365  # 分时电价
    p_sel_price = input_param["price"]["p_sel_price"]  # 卖电价格
    h_price = input_param["price"]["h_price"]  # 买氢价格

    c = 4.2 / 3600  # 水的比热容
    M = 1e7  # 大 M
    epsilon = 0.0000001

    # --- 各种设备的价格 ---
    cost_pv = input_param["device"]["pv"]["cost"]
    cost_sc = input_param["device"]["sc"]["cost"]
    cost_fc = input_param["device"]["fc"]["cost"]
    cost_el = input_param["device"]["el"]["cost"]
    cost_eb = input_param["device"]["eb"]["cost"]
    # cost_ac = input_param["device"]["ac"]["cost"]
    cost_hp = input_param["device"]["hp"]["cost"]
    cost_ghp = input_param["device"]["ghp"]["cost"]
    cost_gtw = input_param["device"]["gtw"]["cost"]
    # cost_co = input_param["device"]["co"]["cost"]
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
    t_ht_supply = input_param["device"]["ht"]["t_supply"]

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
    z_fc = [model.addVar(vtype=GRB.BINARY, name=f"z_fc{t}") for t in range(period)]
    h_fc = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_fc{t}") for t in range(period)]  # 燃料电池耗氢量
    p_fc = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_fc{t}") for t in range(period)]  # 燃料电池产电量
    g_fc = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_fc{t}") for t in range(period)]  # 燃料电池产热量

    p_el_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["el"]["p_max"], name="p_el_inst")  # rated heat power of fuel cells
    # z_el = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=f"z_el{t}") for t in range(period)]
    h_el = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_el{t}") for t in range(period)]  # 电解槽制氢量
    p_el = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_el{t}") for t in range(period)]  # 电解槽耗电量
    # g_el = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_el{t}") for t in range(period)] # 电解槽产热量
    # m_el = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_el") # fuel cells water

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

    # ------ Update model ------
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

    model.addConstr(num_gtw_inst * g_gtw >= p_ghp_inst * k_ghp_g)  # 井和热泵有关联，制热量-电功率=取热量
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

    # --- 其他约束 ---
    model.addConstrs(g_ghp_gr[i] <= g_fc[i] + g_eb[i] for i in range(period)) # 当前系统只有燃料电池和电锅炉可以灌热
    # model.addConstr(gp.quicksum(p_pur) <= (1 - cer) * (sum(ele_load) + sum(g_demand) / k_eb + sum(q_demand) / k_ghp_q))  # 碳减排约束，买电量不能超过碳排放,即1-碳减排
    
    # if input_param["calc_mode"]["c_neutral"] != 0:
    #     model.addConstr(gp.quicksum(p_pur) <= (input_param["calc_mode"]["c_neutral"]) * (gp.quicksum(p_pv) + gp.quicksum(p_fc)))  # 碳中和约束
    # model.addConstr(cost_c_ele == sum([ele_load[i] * ele_price[i] for i in range(period)]))
    # model.addConstr(cost_c_heat == sum([g_demand[i] / 0.95 * ele_price[i] for i in range(period)]))  # /(3.41))
    # model.addConstr(cost_c_cool == sum([q_demand[i] / 4 * ele_price[i] for i in range(period)]))  # /3.8)
    # model.addConstr(cost_c == cost_c_cool + cost_c_heat + cost_c_ele)

    # model.addConstr(ce_h == gp.quicksum(p_pur) * alpha_e)  # -gp.quicksum(p_sol)*alpha_e

    # --- unused ---
    # 每日水罐温度平衡，非季节储氢量平衡
    # for i in range(int(period/24)-1):
    # m.addConstr(t_ht[i*24+24] == t_ht[24*i])
    # m.addConstr(t_ct[i*24+24] == t_ct[24*i])
    # m.addConstr(h_hst[i*24+24] == h_hst[24*i])

    # m.addConstr(p_el_max == 56818)
    # m.addConstr(p_fc_max == 5293)
    # m.addConstr(p_ec_max == 195)
    # m.addConstr(p_hp_max == 0)
    # m.addConstr(s_pv == 70190)
    # 储能约束
    # if i%24 == 0 and int(i/24)<364:
    # m.addConstr(m_ct * (t_ct[i] - t_ct[i+1]) + q_demand[i]/c == m_hpc[i] * (5) +m_ec[i]*(5)  - eta_loss*m_ct*(t_ct[i] - 16))
    # m.addConstr(h_sto[i+1] - h_sto[i] + h_ssto[int(i/24)+1] - h_ssto[int(i/24)] == h_pur[i] + h_el[i] - h_fc[i])

    # for i in range(period - 1):
    #     # cold water tank and cold supply
    #     else:
    #     m.addConstr(m_ct * (t_ct[i] - t_ct[i+1]) + q_demand[i]/c == m_hpc[i] * (5) +m_ec[i]*(5)  - eta_loss*m_ct*(t_ct[i] - 16))

    # m.addConstr(gp.quicksum(q_hpg)+gp.quicksum(p_hpgc)+gp.quicksum(g_hpg_gr) >= gp.quicksum(g_hpg)-gp.quicksum(p_hpg))
    # m.addConstr(s_pv*cost_pv +s_sc*cost_sc +p_hpg_max*cost_hpg +cost_gtw*num_gtw +cost_ht*m_ht+cost_ht*m_ct+cost_hst*hst+cost_eb*p_eb_max+cost_hp*p_hp_max+cost_fc*p_fc_max+cost_el*p_el_max + 10*gp.quicksum([p_pur[i]*lambda_ele_in[i] for i in range(period)])-10*gp.quicksum(p_sol)*lambda_ele_out+10*lambda_h*gp.quicksum(h_pur)+954>=0 )
    # m.addConstr(cost_hyd*input_json["device"]['hyd']['flag'] + s_pv*cost_pv +s_sc*cost_sc +p_hpg_max*cost_hpg +cost_gtw*num_gtw +cost_ht*m_ht+cost_ht*m_ct+cost_hst*hst+cost_eb*p_eb_max+cost_hp*p_hp_max+cost_fc*p_fc_max+cost_el*p_el_max <= input_json['price']['capex_max'][1-isloate[1]])
    # for i in range(period):
    #     m.addConstr(t_ht[-1] == t_ht[0])
    #     m.addConstr(t_ct[-1] == t_ct[0])
    #     m.addConstr(h_hst[-12] == h_hst[0])
    #
    #     m.addConstr(z_hpgq[i] <= q_demand[i])
    #     m.addConstr(z_hpgg[i] <= g_demand[i])
    #     m.addConstr(g_fc[i] == c*m_fc[i]*(10))
    #     m.addConstr(m_fc[i] <= g_fc[i]*100000)
    #     m.addConstr(z_fc[i]+g_fc[i]>=0.01)
    # m.addConstr(num_gtw_inst*p_gtw==p_ghp_inst)  # 井和热泵有关联

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
                 + m_ht_inst * cost_ht / input_param["device"]["ht"]["life"])
    opex = (gp.quicksum([p_pur[i] * p_price[i] for i in range(period)])
            - gp.quicksum([p_sel[i] for i in range(period)]) * p_sel_price
            + gp.quicksum([h_pur[i] for i in range(period)]) * h_price)

    model.setObjective(
        (capex + opex),
        GRB.MINIMIZE
    )

    # ------ Optimize ------
    model.params.NonConvex = 2
    model.Params.LogFile = "log/mip.log"
    model.params.MIPGap = 0.01
    # print(m.status)

    tick = time.time()

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
    # print(device_cap)

    # 运行后的输出
    # operation_output_json = {
    #         "operation_cost": op_sum,  # 年化运行成本/万元
    #         "cost_save_rate": (op_c-op_sum)/op_c,  #运行成本节约比例
    #         "co2":0,  #总碳排/t
    #         "cer":0,  #碳减排率
    #         "cer_perm2":200  #每平米的碳减排量/t
    # }
    # 第一步，计算 传统 电气系统 和 电系统 的 运行成本， 碳排放

    # ele_price = input_json["price"]["TOU_power"]*365
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
    # from module.utils import to_csv
    print("Start")
