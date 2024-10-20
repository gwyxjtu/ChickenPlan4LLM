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
    trade_flag = {
        "p_pur": input_param["calc_mode"]["grid"]["p_pur_state"],
        "p_sol": input_param["calc_mode"]["grid"]["p_sol_state"],
        "h_pur": input_param["calc_mode"]["grid"]["h_pur_state"]
    }

    # ------ Create model ------
    model = gp.Model("OptModel")

    # ------ Parameters ------
    # --- 各时段数据 ---
    ele_load = period_data["ele_load"]  # 电负荷
    g_demand = period_data["g_demand"]  # 热负荷
    q_demand = period_data["q_demand"]  # 冷负荷
    r_solar = period_data["r_solar"]  # 光照强度
    r_r_solar = period_data["r_solar"]

    z_g_demand = period_data["z_heat_month"]
    z_q_demand = period_data["z_cold_month"]

    # period = 8760  # 总时段数
    period = len(ele_load)  # 总时段数

    # 展示负荷信息
    print("热负荷总量{}，冷负荷总量：{}，电负荷总量：{}".format(sum(g_demand), sum(q_demand), sum(ele_load)))
    print("热负荷峰值{}，冷负荷峰值：{}，电负荷峰值：{}".format(max(g_demand), max(q_demand), max(ele_load)))
    print("-" * 10 + "g, q, e_load" + "-" * 10)

    # --- 碳排放因子 ---
    alpha_e = input_param["carbon"]["alpha_e"]  # 电网排放因子 kg/kWh
    alpha_gas = input_param["carbon"]["alpha_gas"]  # 天然气排放因子 kg/Nm3
    alpha_h2 = input_param["carbon"]["alpha_h2"]  # 氢排放因子
    alpha_EO = input_param["carbon"]["alpha_EO"]  # 减排项目基准排放因子

    # --- 能源价格 ---
    ele_price = input_param["price"]["TOU_power"] * 365  # 分时电价
    discount = input_param["price"]["discount"]
    ele_sell = input_param["price"]["power_sell"]  # 卖电价格
    h_price = input_param["price"]["hydrogen_price"]  # 买氢价格
    cer = input_param["calc_mode"]["cer"]  # 碳减排率

    gas_price = 1.2

    c = 4.2 / 3600  # 水的比热容
    M = 1e7  # 大 M
    epsilon = 0.0000001

    # --- 设备规划参数 ---
    s_sum = input_param["renewable_energy"]["pv_sc_max"]

    # --- 各种设备的资本回收率 ---
    crf_pv = crf(input_param["device"]["pv"]["life"])
    crf_sc = crf(input_param["device"]["sc"]["life"])
    crf_fc = crf(input_param["device"]["fc"]["life"])
    crf_el = crf(input_param["device"]["el"]["life"])
    crf_eb = crf(input_param["device"]["eb"]["life"])
    crf_ac = crf(input_param["device"]["ac"]["life"])
    crf_hp = crf(input_param["device"]["hp"]["life"])
    crf_ghp = crf(input_param["device"]["ghp"]["life"])
    crf_gtw = crf(input_param["device"]["gtw"]["life"])
    crf_co = crf(input_param["device"]["co"]["life"])
    crf_hst = crf(input_param["device"]["hst"]["life"])
    crf_ht = crf(input_param["device"]["ht"]["life"])

    # --- 各种设备的价格 ---
    cost_pv = input_param["device"]["pv"]["cost"]
    cost_sc = input_param["device"]["sc"]["cost"]
    cost_fc = input_param["device"]["fc"]["cost"]
    cost_el = input_param["device"]["el"]["cost"]
    cost_eb = input_param["device"]["eb"]["cost"]
    cost_ac = input_param["device"]["ac"]["cost"]
    cost_hp = input_param["device"]["hp"]["cost"]
    cost_ghp = input_param["device"]["ghp"]["cost"]
    cost_gtw = input_param["device"]["gtw"]["cost"]
    cost_co = input_param["device"]["co"]["cost"]
    cost_hst = input_param["device"]["hst"]["cost"]
    cost_ht = input_param["device"]["ht"]["cost"]  # yuan/kwh

    # --- 各种设备的效率系数，包括产热、制冷、发电、热转换等 ---
    eta_pv = input_param["device"]["pv"]["beta_pv"]
    k_sc = input_param["device"]["sc"]["beta_sc"]
    theta_ex = input_param["device"]["sc"]["theta_ex"]
    k_fc_p = input_param["device"]["fc"]["eta_fc_p"]
    k_fc_g = input_param["device"]["fc"]["eta_ex_g"]
    eta_ex = 0.95
    k_el = input_param["device"]["el"]["beta_el"]
    k_eb = input_param["device"]["eb"]["beta_eb"]
    k_ac = input_param["device"]["ac"]["beta_ac"]
    k_hp_g = input_param["device"]["hp"]["beta_hpg"]
    k_hp_q = input_param["device"]["hp"]["beta_hpq"]
    k_ghp_g = input_param["device"]["ghp"]["beta_ghp_g"]
    k_ghp_q = input_param["device"]["ghp"]["beta_ghp_q"]
    p_gtw = input_param["device"]["gtw"]["beta_gtw"]
    k_co = input_param["device"]["co"]["beta_co"]
    t_ht_supply = input_param["device"]["ht"]["t_supply"]
    mu_ht_loss = 0.001

    # ------ Variables ------
    h_pur = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_pur{t}") for t in range(period)]  # hydrogen purchase
    p_pur = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_pur{t}") for t in range(period)]  # power purchase
    p_sol = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_sol{t}") for t in range(period)]  # power sold

    s_pv_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"s_pv_inst")  # ub=13340,
    p_pv = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_pv{t}") for t in range(period)]

    s_sc_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"s_sc_inst")
    g_sc = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_sc{t}") for t in range(period)]

    p_fc_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_fc_inst")
    z_fc = [model.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=f"z_fc{t}") for t in range(period)]
    h_fc = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_fc{t}") for t in range(period)]  # 燃料电池耗氢量
    p_fc = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_fc{t}") for t in range(period)]  # 燃料电池产电量
    g_fc = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_fc{t}") for t in range(period)]  # 燃料电池产热量
    # fc_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="fc_max")  # rated heat power of fuel cells
    # m_fc = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_fc") # fuel cells water

    p_el_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="p_el_inst")  # rated heat power of fuel cells
    # z_el = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=f"z_el{t}") for t in range(period)]
    h_el = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_el{t}") for t in range(period)]  # 电解槽制氢量
    p_el = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_el{t}") for t in range(period)]  # 电解槽耗电量
    # g_el = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_el{t}") for t in range(period)] # 电解槽产热量
    # m_el = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_el") # fuel cells water

    p_eb_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["eb"]["power_max"], name=f"p_eb_inst")
    p_eb = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_eb{t}") for t in range(period)]  # 电锅炉耗电
    g_eb = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_eb{t}") for t in range(period)]  # 电锅炉产热
    # m_eb = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_eb{t}") for t in range(period)]  # 电锅炉换水量

    g_ac_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["ac"]["power_max"], name=f"g_ac_inst")
    g_ac = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_ac{t}") for t in range(period)]
    q_ac = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"q_ac{t}") for t in range(period)]

    # pump_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="pump_max")
    # p_pump = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_pump{t}") for t in range(period)]

    p_hp_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["hp"]["power_max"], name=f"p_hp_inst")
    p_hp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_hp{t}") for t in range(period)]  # 热泵产热的耗电 ub=268,
    p_hpc = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_hpc{t}") for t in range(period)]  # 热泵产冷的耗电 ub=202,
    # p_hpc_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0,ub = input_json["device"]["hp"]["power_max"],  name=f"p_hpc_max")
    g_hp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_hp{t}") for t in range(period)]  # 热泵产热
    q_hp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"q_hp{t}") for t in range(period)]  # 热泵产冷
    # m_hp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_hp{t}") for t in range(period)]  # 热泵供热换水量
    # m_hpc = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_hpc{t}") for t in range(period)]  # 热泵供冷换水量

    # z_ghpq = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=f"z_ghpq{t}") for t in range(period)]
    # z_ghpg = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=f"z_ghpg{t}") for t in range(period)]
    # z_ele_in = [m.addVar(lb=-0.0001, ub=1.01, vtype=GRB.BINARY, name=f"z_ele_in{t}") for t in range(period)]
    # z_ele_out = [m.addVar(lb=-0.0001, ub=1.01, vtype=GRB.BINARY, name=f"z_ele_out{t}") for t in range(period)]

    p_ghp_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["ghp"]["power_max"], name=f"p_ghp_inst")
    p_ghp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_ghp{t}") for t in range(period)]  # 热泵产热耗电 ub=268,
    p_ghpc = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_ghpc{t}") for t in range(period)]  # 热泵产冷的耗电 ub=202,
    # p_ghpc_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0,ub = input_json["device"]["ghp"]["power_max"],  name=f"p_ghpc_max")
    g_ghp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_ghp{t}") for t in range(period)]  # 热泵产热
    g_ghp_gr = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_ghp_gr{t}") for t in range(period)]  # 热泵灌热
    q_ghp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"q_ghp{t}") for t in range(period)]  # 热泵产热

    num_gtw_inst = model.addVar(vtype=GRB.INTEGER, lb=0, name="num_gtw_inst")  # 地热井

    p_co_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["co"]["power_max"], name=f"p_co_inst")
    p_co = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_co{t}") for t in range(period)]

    h_hst_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_hst_inst")
    h_hst = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_hst{t}") for t in range(period)]  # 储氢罐储氢量

    m_ht_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_ht_inst")
    t_ht = [model.addVar(vtype=GRB.CONTINUOUS, lb=55, ub=input_param["device"]["ht"]["t_max"], name=f"t_ht{t}") for t in range(period)]  # temperature of heat storage tank
    g_ht = [model.addVar(vtype=GRB.CONTINUOUS, lb=-M, name=f"g_ht{t}") for t in range(period)]

    m_ct_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_ct_inst")
    t_ct = [model.addVar(vtype=GRB.CONTINUOUS, lb=2, ub=input_param["device"]["ct"]["t_max"], name=f"t_ct{t}") for t in range(period)]  # temperature of cold water tank
    q_ct = [model.addVar(vtype=GRB.CONTINUOUS, lb=-M, name=f"q_ct{t}") for t in range(period)]

    g_tube = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_tube{t}") for t in range(period)]

    # t_de = [m.addVar(vtype=GRB.CONTINUOUS, lb=0,name=f"t_de{t}") for t in range(period)] # outlet temparature of heat supply circuits

    cost_c_ele = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"cost_c_ele")
    cost_c_heat = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"cost_c_heat")
    cost_c_cool = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"cost_c_cool")
    cost_c = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"cost_c")

    ce_h = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="ce_h")

    # ------ Update model ------
    model.update()

    # ------ Constraints ------
    # --- 设备规划容量的取值范围 ---
    model.addConstr(s_pv_inst <= input_param["device"]["pv"]["area_max"])
    model.addConstr(s_pv_inst >= input_param["device"]["pv"]["area_min"])
    model.addConstr(s_sc_inst <= input_param["device"]["sc"]["area_max"])
    model.addConstr(s_sc_inst >= input_param["device"]["sc"]["area_min"])
    model.addConstr(s_pv_inst + s_sc_inst <= s_sum)  # 太阳能规划面积
    model.addConstr(p_fc_inst <= input_param["device"]["fc"]["power_max"])
    model.addConstr(p_fc_inst >= input_param["device"]["fc"]["power_min"])
    model.addConstr(p_el_inst <= input_param["device"]["el"]["power_max"])
    model.addConstr(p_el_inst <= 50 * input_param["device"]["el"]["nm3_max"] / 11.2)
    model.addConstr(p_el_inst >= 50 * input_param["device"]["el"]["nm3_min"] / 11.2)
    model.addConstr(p_el_inst >= input_param["device"]["el"]["power_min"])
    model.addConstr(p_eb_inst <= input_param["device"]["eb"]["power_max"])
    model.addConstr(p_eb_inst >= input_param["device"]["eb"]["power_min"])
    model.addConstr(g_ac_inst <= input_param["device"]["ac"]["power_max"])
    model.addConstr(g_ac_inst >= input_param["device"]["ac"]["power_min"])
    model.addConstr(p_hp_inst <= input_param["device"]["hp"]["power_max"])
    model.addConstr(p_hp_inst >= input_param["device"]["hp"]["power_min"])
    model.addConstr(p_ghp_inst <= input_param["device"]["ghp"]["power_max"])
    model.addConstr(p_ghp_inst >= input_param["device"]["ghp"]["power_min"])
    model.addConstr(num_gtw_inst <= input_param["device"]["gtw"]["number_max"])
    model.addConstr(p_co_inst <= input_param["device"]["co"]["power_max"])
    model.addConstr(p_co_inst >= input_param["device"]["co"]["power_min"])
    model.addConstr(h_hst_inst <= input_param["device"]["hst"]["sto_max"])
    model.addConstr(h_hst_inst >= input_param["device"]["hst"]["sto_min"])
    model.addConstr(m_ht_inst <= input_param["device"]["ht"]["water_max"])
    model.addConstr(m_ht_inst >= input_param["device"]["ht"]["water_min"])
    model.addConstr(m_ct_inst <= input_param["device"]["ct"]["water_max"])
    model.addConstr(m_ct_inst >= input_param["device"]["ct"]["water_min"])

    # --- 设备运行约束 ---
    for i in range(period):
        # 光伏板
        model.addConstr(p_pv[i] <= eta_pv * s_pv_inst * r_solar[i])  # 光伏板发电约束
        # 太阳能集热器
        model.addConstr(g_sc[i] <= k_sc * theta_ex * s_sc_inst * r_solar[i])  # 太阳能集热器产热约束
        # 燃料电池
        model.addConstr(p_fc[i] == k_fc_p * h_fc[i])  # 燃料电池产电约束
        model.addConstr(g_fc[i] == eta_ex * k_fc_g * h_fc[i] * z_fc[i])  # 燃料电池产热约束
        # model.addConstr(g_fc[i] <= eta_ex * k_fc_g * h_fc[i] * z_fc[i])  # 燃料电池产热约束
        # # 燃料电池产热约束
        # model.addConstr(g_fc[i] <= eta_ex * k_fc_g * h_fc[i])
        # model.addConstr(g_fc[i] <= z_fc[i] * M)
        model.addConstr(p_fc[i] <= p_fc_inst)  # 燃料电池功率约束，存疑？
        # 电解槽
        model.addConstr(h_el[i] <= k_el * p_el[i])  # 电解槽产氢约束
        model.addConstr(p_el[i] <= p_el_inst)  # 电解槽功率约束
        # model.addConstr(h_el[i] <= h_hst_inst)  # 有问题
        # 电锅炉
        model.addConstr(g_eb[i] == k_eb * p_eb[i])  # 电锅炉产热约束
        model.addConstr(p_eb[i] <= p_eb_inst)  # 电锅炉功率约束
        # 吸收式制冷机
        model.addConstr(q_ac[i] == k_ac * g_ac[i])  # 吸收式制冷机产冷约束
        model.addConstr(g_ac[i] <= g_ac_inst)  # 吸收式制冷机产冷功率约束
        # 热泵
        model.addConstr(g_hp[i] == k_hp_g * p_hp[i])  # 热泵产热约束
        model.addConstr(q_hp[i] == k_hp_q * p_hpc[i])  # 热泵产冷约束
        model.addConstr(p_hp[i] <= p_hp_inst)  # 热泵产热功率约束
        model.addConstr(p_hpc[i] <= p_hp_inst)  # 热泵产冷功率约束
        # 地源热泵
        model.addConstr(g_ghp[i] == p_ghp[i] * k_ghp_g)  # 地源热泵产热约束
        model.addConstr(q_ghp[i] == p_ghpc[i] * k_ghp_q)  # 地源热泵产冷约束
        model.addConstr(p_ghp[i] <= p_ghp_inst)  # 地源热泵产热功率约束
        model.addConstr(p_ghpc[i] <= p_ghp_inst)  # 地源热泵产冷功率约束
        model.addConstr(p_ghp[i] <= z_g_demand[i] * M)  # 供热月份地源热泵产热
        model.addConstr(p_ghpc[i] <= z_q_demand[i] * M)  # 供冷月份地源热泵产冷
        # 地热井
        model.addConstr(num_gtw_inst * p_gtw >= g_ghp[i] - p_ghp[i])  # 井和热泵有关联，制热量-电功率=取热量
        model.addConstr(num_gtw_inst * p_gtw >= q_ghp[i] + p_ghpc[i])  # 井和热泵有关联，制冷量+电功率=灌热量
        # 压缩机
        model.addConstr(p_co[i] == k_co * h_el[i])
        model.addConstr(p_co[i] <= p_co_inst)
        # 储氢罐
        model.addConstr(h_hst[i] <= h_hst_inst)
        # 热水罐
        pass
        # 冷水罐
        pass

    # --- 能量平衡约束 ---
    # 电平衡约束
    model.addConstrs(ele_load[i] == p_pur[i] + p_pv[i] + p_fc[i]
                     - p_sol[i] - p_el[i] - p_eb[i] - p_hp[i] - p_hpc[i] - p_ghp[i] - p_ghpc[i] - p_co[i]
                     for i in range(period))
    for i in range(period - 1):
        # 热平衡约束
        model.addConstr(g_ht[i] == (-c * m_ht_inst * (t_ht[i + 1] - t_ht[i])
                                    - mu_ht_loss * c * m_ht_inst * (t_ht[i] - t_ht_supply)))  # 热水箱供热量
        model.addConstr(g_tube[i] == (g_fc[i] + g_eb[i] + g_sc[i] + g_hp[i] + g_ht[i]
                                      - g_ac[i] - g_ghp_gr[i]))  # 管网供热量
        model.addConstr(g_demand[i] == g_tube[i] + g_ghp[i])  # 热负荷平衡约束
        # 冷平衡约束
        model.addConstr(q_ct[i] == c * m_ht_inst * (t_ct[i + 1] - t_ct[i]))  # 冷水箱供冷量
        # model.addConstr(q_ct[i] == (c * m_ht_inst * (t_ct[i + 1] - t_ct[i])
        #                             - 0.001 * c * m_ht_inst * (input_param["device"]["ct"]["t_max"] - t_ct[i])))
        model.addConstr(q_demand[i] == q_hp[i] + q_ac[i] + q_ghp[i] + q_ct[i])  # 冷负荷平衡约束
        # 储氢平衡约束
        model.addConstr(h_hst[i + 1] - h_hst[i] == h_pur[i] + h_el[i] - h_fc[i])  # 储氢罐约束
    # 末时刻热平衡约束，需保证调度周期始末热水箱温度一致
    model.addConstr(g_ht[-1] == (-c * m_ht_inst * (t_ht[0] - t_ht[-1])
                                 - mu_ht_loss * c * m_ht_inst * (t_ht[i] - t_ht_supply)))  # 热水箱供热量
    model.addConstr(g_tube[-1] == (g_fc[-1] + g_eb[-1] + g_sc[-1] + g_hp[-1] + g_ht[-1]
                                   - g_ghp_gr[-1]))  # 管网供热量
    model.addConstr(g_demand[-1] == g_tube[-1] + g_ghp[-1])  # 热负荷平衡约束
    # 末时刻冷平衡约束，需保证调度周期始末冷水箱温度一致
    model.addConstr(q_ct[-1] == c * m_ht_inst * (t_ct[0] - t_ct[-1]))  # 冷水箱供冷量
    model.addConstr(q_demand[-1] == q_hp[-1] + q_ac[-1] + q_ghp[-1] + q_ct[-1])  # 冷负荷平衡约束
    # 储氢平衡约束
    model.addConstr(h_hst[0] - h_hst[-1] == h_pur[-1] + h_el[-1] - h_fc[-1])  # 储氢罐约束

    # --- 其他约束 ---
    for i in range(period):
        # 电网
        model.addConstr(p_pur[i] <= (trade_flag["p_pur"]) * M)  # 是否允许从电网买电
        model.addConstr(p_sol[i] <= (trade_flag["p_sol"]) * M)  # 是否允许向电网卖电
        model.addConstr(h_pur[i] <= (trade_flag["h_pur"]) * M)  # 是否允许购买氢气

        # m.addConstr(z_ghpq[i] <= q_demand[i])
        # m.addConstr(z_ghpg[i] <= g_demand[i])
        # 这里得假设热负荷时连续的月份

        model.addConstr(g_ghp_gr[i] <= g_fc[i] + g_eb[i])

        # p_sol
        model.addConstr(p_sol[i] <= p_fc[i] + p_pv[i])  # ？
        model.addConstr(p_sol[i] <= s_pv_inst * r_solar[i])  # ？

    model.addConstr(gp.quicksum(p_pur) <= (1 - cer) * (sum(ele_load) + sum(g_demand) / k_eb + sum(q_demand) / k_ghp_q))  # 碳减排约束，买电量不能超过碳排放,即1-碳减排
    if input_param["calc_mode"]["c_neutral"] != 0:
        model.addConstr(gp.quicksum(p_pur) <= (input_param["calc_mode"]["c_neutral"]) * (gp.quicksum(p_pv) + gp.quicksum(p_fc)))  # 碳中和约束
    model.addConstr(cost_c_ele == sum([ele_load[i] * ele_price[i] for i in range(period)]))
    model.addConstr(cost_c_heat == sum([g_demand[i] / 0.95 * ele_price[i] for i in range(period)]))  # /(3.41))
    model.addConstr(cost_c_cool == sum([q_demand[i] / 4 * ele_price[i] for i in range(period)]))  # /3.8)
    model.addConstr(cost_c == cost_c_cool + cost_c_heat + cost_c_ele)

    model.addConstr(ce_h == gp.quicksum(p_pur) * alpha_e)  # -gp.quicksum(p_sol)*alpha_e

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
    capex = (cost_pv * s_pv_inst
             + p_fc_inst * cost_fc
             + p_el_inst * cost_el
             + p_eb_inst * cost_eb
             + s_sc_inst * cost_sc
             + g_ac_inst * cost_ac
             + p_hp_inst * cost_hp
             + p_ghp_inst * cost_ghp
             + num_gtw_inst * cost_gtw
             + p_co_inst * cost_co
             + h_hst_inst * cost_hst
             + m_ht_inst * cost_ht)
    capex_crf = (crf_pv * cost_pv * s_pv_inst
                 + crf_fc * p_fc_inst * cost_fc
                 + crf_el * p_el_inst * cost_el
                 + crf_eb * p_eb_inst * cost_eb
                 + crf_sc * s_sc_inst * cost_sc
                 + crf_ac * g_ac_inst * cost_ac
                 + crf_hp * p_hp_inst * cost_hp
                 + crf_ghp * p_ghp_inst * cost_ghp
                 + crf_gtw * num_gtw_inst * cost_gtw
                 + crf_co * p_co_inst * cost_co
                 + crf_hst * h_hst_inst * cost_hst
                 + crf_ht * m_ht_inst * cost_ht)
    opex = (gp.quicksum([p_pur[i] * ele_price[i] for i in range(period)])
            - gp.quicksum([p_sol[i] for i in range(period)]) * ele_sell
            + gp.quicksum([h_pur[i] for i in range(period)]) * h_price)

    model.setObjective(
        (input_param["calc_mode"]["obj"]["capex_sum"] * capex
         + input_param["calc_mode"]["obj"]["capex_crf"] * capex_crf
         + input_param["calc_mode"]["obj"]["opex"] * opex),
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
    # print([p_eb[i].X for i in range(period)])
    if model.status == GRB.INFEASIBLE or model.status == 4:
        print("Model is infeasible")
        model.computeIIS()
        model.write("model.ilp")
        print("Irreducible inconsistent subsystem is written to file 'model.ilp'")

    op_c = sum([(ele_load[i] + g_demand[i] / k_eb + q_demand[i] / k_ghp_q) * ele_price[i] for i in range(period)])

    cap_sum = capex_sum.x
    op_sum = sum([p_hyd[i].x for i in range(period)]) * input_param["device"]["hyd"]["power_cost"] + sum(
        [p_pur[i].X * ele_price[i] for i in range(period)]) + h_price * sum([h_pur[i].X for i in range(period)])
    # op_sum = op_sum.x
    revenue = sum([ele_load[i] * ele_price[i] for i in range(period)]) * input_param["price"]["discount"] + sum(
        [p_sol[i].X for i in range(period)]) * ele_sell + input_param["load"]["load_area"] * (
                      input_param["price"]["heat_price"] * (sum(z_g_demand) / 30 / 24) + input_param["price"][
                      "cold_price"] * (sum(z_q_demand) / 30 / 24))
    if input_param["price"]["fixed_revenue"] != 0:
        revenue = input_param["price"]["fixed_revenue"]

    print("revenue_ele")
    revenue_ele = sum([ele_load[i] * ele_price[i] * input_param["price"]["discount"] for i in range(period)])
    # revenue_heat = sum([g_demand[i]/0.95*ele_price[i] for i in range(period)])
    # revenue_cold = sum([q_demand[i]/4*ele_price[i] for i in range(period)])
    print(revenue_ele)
    p_a_y = (sum(ele_load) + sum(g_demand) + sum(q_demand)) / input_param["load"]["load_area"]
    if p_a_y < 60 or p_a_y > 120:
        print("负荷异常")
    else:
        print("负荷无异常")
    print(format(p_a_y, ".2f"))
    print("————————————————")

    # 规划输出
    output_json = {
        "ele_load_sum": int(sum(ele_load)),  # 电负荷总量/kwh
        "g_demand_sum": int(sum(g_demand)),  # 热负荷总量/kwh
        "q_demand_sum": int(sum(q_demand)),  # 冷负荷总量/kwh
        "ele_load_max": int(max(ele_load)),  # 电负荷峰值/kwh
        "g_demand_max": int(max(g_demand)),  # 热负荷峰值/kwh
        "q_demand_max": int(max(q_demand)),  # 冷负荷峰值/kwh
        "ele_load": ele_load,  # 电负荷8760h的分时数据/kwh
        "g_demand": g_demand,  # 热负荷8760h的分时数据/kwh
        "q_demand": q_demand,  # 冷负荷8760h的分时数据/kwh
        "r_solar": r_solar,  # 光照强度8760h的分时数据/kwh
        "r_r_solar": r_r_solar,
        "num_gtw_inst": num_gtw_inst.X,  # 地热井数目/个
        "p_fc_inst": format(p_fc_inst.X, ".1f"),  # 燃料电池容量/kw
        "p_ghp_inst": format(p_ghp_inst.X, ".1f"),  # 地源热泵功率/kw
        "p_hp_inst": format(p_hp_inst.X, ".1f"),  # 空气源热泵功率/kw
        "p_hp1_max": format(p_hp1_max.X, ".1f"),
        "p_hp2_max": format(p_hp2_max.X, ".1f"),
        "p_whp_max": format(p_whp_max.X, ".1f"),  # whp/kw
        "g_ac_inst": format(g_ac_inst.X, ".1f"),
        "p_eb_inst": format(p_eb_inst.X, ".1f"),  # 电热锅炉功率/kw
        "p_el_inst": format(p_el_inst.X, ".1f"),  # 电解槽功率/kw
        "nm3_el_max": format(11.2 * p_el_inst.X / 50, ".1f"),  # 电解槽nm3/nm3
        "h_hst_inst": format(h_hst_inst.X, ".1f"),  # 储氢罐容量/kg
        "m_ht_inst": format(m_ht_inst.X, ".1f"),  # 储热罐/kg
        "m_ct_inst": format(m_ct_inst.X, ".1f"),  # 冷水罐/kg
        "area_pv": format(s_pv_inst.X, ".1f"),  # 光伏面积/m2
        "area_sc": format(s_sc_inst.X, ".1f"),  # 集热器面积/m2
        "p_co": format(p_co_inst.X, ".1f"),  # 氢压机功率/kw
        "m_xb": format(m_xb.X, ".1f"),  # 相变储热模块大小/kwh

        "cap_fc": capex_fc.X,
        "cap_ghp": cost_ghp * p_ghp_inst.X,
        "cap_gtw": cost_gtw * num_gtw_inst.X,
        "cap_hp": cost_hp * p_hp_inst.X,
        "cap_hp1": cost_hp1 * p_hp1_max.X,
        "cap_hp2": cost_hp2 * p_hp2_max.X,
        # "cap_hpc":cost_hpc*p_hpc_max.X,
        "cap_whp": cost_whp * p_whp_max.X,
        "cap_ac": cost_ac * g_ac_inst.X,
        "cap_eb": cost_eb * p_eb_inst.X,
        # "cap_ec":cost_ec*p_ec_max.X,
        "cap_hst": cost_hst * h_hst_inst.X,
        "cap_ht": cost_ht * m_ht_inst.X,
        # "cap_ct":cost_ht*m_ct_inst,
        "cap_pv": s_pv_inst.X * cost_pv,
        "cap_co": cost_co * p_co_inst.X,
        "cap_sc": cost_sc * s_sc_inst.X,
        "cap_el": capex_el.X,
        "cap_xb": cost_xb * m_xb.X,

        "equipment_cost": format(cap_sum / 10000, ".2f"),  # 设备总投资/万元
        "equipment_cost_perarea": format(cap_sum / input_param["load"]["load_area"], ".2f"),  # 单位面积投资 元/平米
        "receive_year": format(cap_sum / (revenue - op_sum + 0.01), ".2f"),  # 投资回报年限/年
    }
    g_ghp_gr = [g_ghp_gr[i].X for i in range(period)]
    g_ghp = [g_ghp[i].X for i in range(period)]
    q_ghp = [q_ghp[i].X for i in range(period)]
    device_cap = {
        "num_gtw_inst": num_gtw_inst.X,  # 地热井数目/个
        "p_fc_inst": p_fc_inst.X,  # 燃料电池容量/kw
        "p_ghp_inst": p_ghp_inst.X,  # 地源热泵功率/kw
        "p_hp_inst": p_hp_inst.X,  # 空气源热泵功率/kw
        "p_hp1_max": p_hp1_max.X,
        "p_hp2_max": p_hp2_max.X,
        "p_whp_max": p_whp_max.X,  # whp/kw
        "g_ac_inst": g_ac_inst.X,
        "p_eb_inst": p_eb_inst.X,  # 电热锅炉功率/kw
        "p_el_inst": p_el_inst.X,  # 电解槽功率/kw
        "h_hst_inst": h_hst_inst.X,  # 储氢罐容量/kg
        "m_ht_inst": m_ht_inst.X,  # 储热罐/kg
        "m_ct_inst": m_ct_inst.X,  # 冷水罐/kg
        "m_xb": m_xb.X,  # 相变储热模块大小/kwh
        "area_pv": s_pv_inst.X,  # 光伏面积/m2
        "area_sc": s_sc_inst.X,  # 集热器面积/m2
        "p_co": p_co_inst.X,  # 氢压机功率/kw
        "nm3_el_max": format(11.2 * p_el_inst.X / 50, ".1f"),  # 电解槽nm3/nm3

        # "g_ghp_gr":[-sum(g_ghp_gr[m_date[2]:m_date[5]])*7/(m_date[2] - m_date[5]), -sum(g_ghp_gr[m_date[5]:m_date[8]])*7/(m_date[5] - m_date[8]),- sum(g_ghp_gr[m_date[8]:m_date[11]])*7/(m_date[8] - m_date[11]), sum(g_ghp_gr[m_date[11]:m_date[12]]+g_ghp_gr[m_date[0]:m_date[2]])*7/(90)],
        # "g_ghp":[-sum(g_ghp[m_date[2]:m_date[5]])*7/(m_date[2] - m_date[5]), -sum(g_ghp[m_date[5]:m_date[8]])*7/(m_date[5] - m_date[8]), -sum(g_ghp[m_date[8]:m_date[11]])*7/(m_date[8] - m_date[11]), sum(g_ghp[m_date[11]:m_date[12]]+g_ghp[m_date[0]:m_date[2]])*7/90],
        # "q_ghp":[-sum(q_ghp[m_date[2]:m_date[5]])*7/(m_date[2] - m_date[5]), -sum(q_ghp[m_date[5]:m_date[8]])*7/(m_date[5] - m_date[8]),- sum(q_ghp[m_date[8]:m_date[11]])*7/(m_date[8] - m_date[11]), sum(q_ghp[m_date[11]:m_date[12]]+q_ghp[m_date[0]:m_date[2]])*7/90]
        "revenue_ele": sum([ele_load[i] * ele_price[i] * input_param["price"]["discount"] for i in range(period)]),
        "revenue_heat": input_param["load"]["load_area"] * input_param["price"]["heat_price"] * sum(z_g_demand) / 30 / 24,
        "revenue_cold": input_param["load"]["load_area"] * input_param["price"]["cold_price"] * sum(z_q_demand) / 30 / 24,
        "g_ghp_gr": [sum(g_ghp_gr[3288:3288 + 7 * 24]), sum(g_ghp_gr[5448:5448 + 7 * 24]),
                     sum(g_ghp_gr[7656:7656 + 7 * 24]), sum(g_ghp_gr[360:360 + 7 * 24])],
        "g_ghp": [sum(g_ghp[3288:3288 + 7 * 24]), sum(g_ghp[5448:5448 + 7 * 24]), sum(g_ghp[7656:7656 + 7 * 24]),
                  sum(g_ghp[360:360 + 7 * 24])],
        "q_ghp": [sum(q_ghp[3288:3288 + 7 * 24]), sum(q_ghp[5448:5448 + 7 * 24]), sum(q_ghp[7656:7656 + 7 * 24]),
                  sum(q_ghp[360:360 + 7 * 24])],  # 调试用
        "cap_device": {
            "cap_fc": capex_fc.X,
            "cap_ghp": cost_ghp * p_ghp_inst.X,
            "cap_gtw": cost_gtw * num_gtw_inst.X,
            "cap_hp": cost_hp * p_hp_inst.X,
            "cap_hp1": cost_hp1 * p_hp1_max.X,
            "cap_hp2": cost_hp2 * p_hp2_max.X,
            # "cap_hpc":cost_hpc*p_hpc_max.X,
            "cap_whp": cost_whp * p_whp_max.X,
            "cap_ac": cost_ac * g_ac_inst.X,
            "cap_eb": cost_eb * p_eb_inst.X,
            # "cap_ec":cost_ec*p_ec_max.X,
            "cap_hst": cost_hst * h_hst_inst.X,
            "cap_ht": cost_ht * m_ht_inst.X,
            # "cap_ct":cost_ht*m_ct_inst,
            "cap_pv": s_pv_inst.X * cost_pv,
            "cap_co": cost_co * p_co_inst.X,
            "cap_sc": cost_sc * s_sc_inst.X,
            "cap_el": capex_el.X,
            "cap_xb": cost_xb * m_xb.X,
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
    ele_sum_ele_only = np.array(ele_load) + np.array(g_demand) / k_eb + np.array(q_demand) / k_ghp_q
    gas_sum_ele_gas = (np.array(g_demand) + np.array(q_demand) / 1.35) / 7.5
    opex_ele_only = sum(np.array(ele_price) * ele_sum_ele_only)
    opex_ele_gas = sum(np.array(ele_price) * np.array(ele_load)) + sum(gas_sum_ele_gas * gas_price)
    co2_ele_only = sum(ele_sum_ele_only) * input_param["carbon"]["alpha_e"]
    co2_ele_gas = sum(ele_load) * input_param["carbon"]["alpha_e"] + sum(gas_sum_ele_gas) * 1.535
    # print("------------")
    operation_output_json = {
        # "operation_cost_net": format((revenue-op_sum)/10000,".1f"),  # 年化运行净收益/万元
        # "operation_cost": format(op_sum/10000,".1f"),  # 年化运行总成本/万元
        # "revenue": format(revenue/10000,".1f"),  # 年化运行成本/万元
        "op_cost":
            {
                "all_of_revenue":
                    {
                        "all_revenue": format(revenue / 10000, ".2f"),
                        "fixed_revenue": format(input_param["price"]["fixed_revenue"] / 10000, ".2f"),
                        "p_sol_revenue": format(sum(p_sol[i].X * ele_sell for i in range(period)), ".2f"),
                        "revenue_heat": format(
                            input_param["load"]["load_area"] * input_param["price"]["heat_price"] * sum(
                                z_g_demand) / 30 / 24, ".2f"),
                        "revenue_cold": format(
                            input_param["load"]["load_area"] * input_param["price"]["cold_price"] * sum(
                                z_q_demand) / 30 / 24, ".2f"),
                    },
                "all_of_op_cost":
                    {
                        "all_op_cost": format(op_sum / 10000, ".2f"),
                        "p_pur_cost": format(sum([p_pur[i].X * ele_price[i] for i in range(period)]), ".2f"),
                        "h_pur_cost": format(h_price * sum([h_pur[i].X for i in range(period)]), ".2f")
                    },
                "net_revenue": format((revenue - op_sum) / 10000, ".2f"),
                "ele_statistics":
                    {
                        "sum_pv": format(sum(p_pv[i].X for i in range(period)), ".2f"),
                        "sum_fc": format(sum(p_fc[i].X for i in range(period)), ".2f"),
                        "sum_p_pur": format(sum(p_pur[i].X for i in range(period)), ".2f"),
                        "sum_p_sol": format(sum(p_sol[i].X for i in range(period)), ".2f")
                    }
            },
        "operation_cost_per_month_per_square": format(op_sum / 12 / input_param["load"]["load_area"], ".2f"),
        # 单位面积月均运行成本
        "cost_save_rate": format((opex_ele_only - op_sum) / opex_ele_only, ".1f"),  # 电运行成本节约比例
        "cost_save_rate_gas": format((opex_ele_gas - op_sum) / opex_ele_gas, ".1f"),  # 电气运行成本节约比例
        "co2": format(ce_h.X / 1000, ".1f"),  # 总碳排/t
        "cer_rate": format((co2_ele_only - ce_h.X) / co2_ele_only * 100, ".1f"),  # 与电系统相比的碳减排率
        "cer_gas": format((co2_ele_gas - ce_h.X) / co2_ele_gas, ".1f"),  # 与电气系统相比的碳减排率
        "cer_perm2": format((co2_ele_only - ce_h.X) / input_param["load"]["load_area"] / 1000, ".1f"),  # 电系统每平米的碳减排量/t
        "cer_perm2_gas": format((co2_ele_gas - ce_h.X) / input_param["load"]["load_area"] / 1000, ".1f"),
        # 电气系统每平米的碳减排量/t
        "cer": format((co2_ele_only - ce_h.X) / 1000, ".2f"),
    }
    return {"objective": model.objVal,
            "res_capex": capex_crf.X,
            "res_opex": res_op_sum.X,
            "process time": time.time() - tick,
            "cap_fc": capex_fc.X,
            "cap_ac": cost_ac * g_ac_inst.X,
            "cap_hp": cost_hp * p_hp_inst.X,
            "cap_ghp": cost_ghp * p_ghp_inst.X,
            # "cap_hpc":cost_hpc*p_hpc_max.X,
            "cap_eb": cost_eb * p_eb_inst.X,
            # "cap_ec":cost_ec*p_ec_max.X,
            "cap_hst": cost_hst * h_hst_inst.X,
            "cap_ht": cost_ht * m_ht_inst.X,
            # "cap_ct":cost_ht*m_ct_inst,
            "cap_pv": s_pv_inst.X * cost_pv,
            "cap_el": capex_el.X,
            # s_pv_inst.X*cost_pv
            "num_gtw_inst": num_gtw_inst.X,
            "p_fc_inst": p_fc_inst.X,
            "p_ghp_inst": p_ghp_inst.X,
            "p_hp_inst": p_hp_inst.X,
            "p_hp1_max": p_hp1_max.X,
            "p_hp2_max": p_hp2_max.X,
            "p_whp_max": p_whp_max.X,
            "p_eb_inst": p_eb_inst.X,
            # "p_ec_max":p_ec_max.X,
            "p_el_inst": p_el_inst.X,
            "h_hst_inst": h_hst_inst.X,
            "m_ht_inst": m_ht_inst.X,
            "m_ct_inst": m_ct_inst.X,
            "m_xb": m_xb.X,
            "area_pv": s_pv_inst.X,
            "area_sc": s_sc_inst.X,
            "h_cost": h_price * sum([h_pur[i].X for i in range(period)]),
            "p_cost": sum([p_pur[i].X * ele_price[i] for i in range(period)]),
            "p_sol_earn": -sum([p_sol[i].X for i in range(period)]) * ele_sell,
            "opex": sum([p_pur[i].X * ele_price[i] for i in range(period)]) - sum(
                [p_sol[i].X for i in range(period)]) * ele_sell + h_price * sum(
                [h_pur[i].X for i in range(period)]),
            "hyd_pur_cost": sum([p_hyd[i].X for i in range(period)]) * input_param["device"]["hyd"]["power_cost"],
            "cap_sum": capex_sum.x,
            "operation_cost": format(op_sum / 10000, ".1f"),  # 年化运行总成本/万元
            "revenue": format(revenue / 10000, ".1f"),  # 年化运行成本/万元
            "operation_cost_per_month_per_square": format(op_sum / 12 / input_param["load"]["load_area"], ".2f"),
            # 单位面积月均运行成本
            "operation_cost_net": format((revenue - op_sum) / 10000, ".1f"),  # 年化运行净收益/万元
            "cer": format((co2_ele_only - ce_h.X) / co2_ele_only, ".1f"),
            "cer_self": sum([p_sol[i].X for i in range(period)]) / co2_ele_only,
            # "load_per_area":format((sum(ele_load)+sum(g_demand)+sum(q_demand))/8760/input_json["load"]["load_area"]),
            "ele_load": ele_load,
            "g_demand": g_demand,
            "q_demand": q_demand,
            # "m_demand":dict["m_demand"],
            "p_pur": [p_pur[i].X for i in range(period)],
            "p_sol": [p_sol[i].X for i in range(period)],
            "p_hyd": [p_hyd[i].X for i in range(period)],
            "h_pur": [h_pur[i].X for i in range(period)],
            # "g_solar": [eta_solar*s_solar*r_solar[i] for i in range(period)],
            "p_pv": [eta_pv * s_pv_inst.X * r_solar[i] for i in range(period)],
            "p_pv_inbalance": [p_pv[i].x for i in range(period)],
            "p_fc": [p_fc[i].X for i in range(period)],
            "g_fc": [g_fc[i].X for i in range(period)],
            "h_fc": [h_fc[i].X for i in range(period)],
            "g_ac": [g_ac[i].X for i in range(period)],
            "q_ac": [q_ac[i].X for i in range(period)],
            "p_el": [p_el[i].X for i in range(period)],
            "h_el": [h_el[i].X for i in range(period)],
            "p_hp": [p_hp[i].X for i in range(period)],
            "g_hp": [g_hp[i].X for i in range(period)],
            "p_hpc": [p_hpc[i].X for i in range(period)],
            "q_hp": [q_hp[i].X for i in range(period)],
            "p_ghp": [p_ghp[i].X for i in range(period)],
            "p_ghpc": [p_ghpc[i].X for i in range(period)],
            "q_ghp": q_ghp,
            "g_ghp": g_ghp,
            "p_whp": [p_whp[i].X for i in range(period)],
            "g_tube": [g_tube[i].X for i in range(period)],
            "t_ht": [t_ht[i].X for i in range(period)],
            "h_hst": [h_hst[i].X for i in range(period)],

            "p_eb": [p_eb[i].X for i in range(period)],
            "g_eb": [g_eb[i].X for i in range(period)],
            "g_sc": [g_sc[i].X for i in range(period)],
            # "m_eb":[m_eb[i].X for i in range(period)],
            "g_ghp_gr": g_ghp_gr,

            "t_ct": [t_ct[i].X for i in range(period)]
            # "q_ac":[pulp.value(c*m_ac*(t_cr[i] - t_ac[i])) for i in range(period)],
            # "g_fc":[eta_ex*mu_fc_g*h_fc[i].X for i in range(period)],
            # "g_htv":[pulp.value(c*m_ht_inst*(t_ht[i+1] - t_ht[i])) for i in range(period)],
            # "g_eb":[eta_eb*p_eb[i].X for i in range(period)]
            # "g_shtv":[pulp.value(g_sht[i+1] - g_sht[i]) for i in range(period)]
            }, output_json, operation_output_json, device_cap


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
