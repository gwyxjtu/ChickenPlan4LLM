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


def crf(year):
    """将输入文件中的设备寿命转为年化收益率

    Args:
        year: 设备寿命
    """
    i = 0.08
    crf = ((1 + i) ** year) * i / ((1 + i) ** year - 1)
    return crf


def support_device(d_cost, d_se):
    """计算配套设备价格函数, 提前写个简单的以备改进

    Args:
        d_cost:
        d_se:

    Returns:

    """
    return d_cost * d_se


def planning_problem(load_data, input_param, isolate_flag=False):
    """规划问题求解

    Args:
        load_data (dict): 负荷数据, 包括光照强度, 电负荷, 热负荷, 冷负荷
        input_param (dict): 输入参数
        isolate_flag (bool):

    Returns:

    """
    # 一年中每个月的天数
    days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    # 一年中每个月的累计小时数
    hours_sum = [sum(days[:i]) * 24 for i in range(12 + 1)]
    if isolate_flag is True:
        trade_flag = {
            "p_pur": 0,
            "p_sol": 0,
            "h_pur": input_param["calc_mode"]['isloate']['h_pur_state']
        }
    else:
        trade_flag = {
            "p_pur": input_param["calc_mode"]['grid']['p_pur_state'],
            "p_sol": input_param["calc_mode"]['grid']['p_sol_state'],
            "h_pur": input_param["calc_mode"]['grid']['h_pur_state']
        }

    # 暂存负荷数据方便 debug
    to_xls(load_data, "debug_load.xls")

    if input_param["device"]['hyd']['flag'] == 1:
        water = []
        book = xlrd.open_workbook('./load/water.xls')
        data = book.sheet_by_index(0)
        for l in range(0, 8760):
            water.append(data.cell(l, 0).value)
        if input_param["device"]['hyd']['peak'] != -1:
            max_water = max(water)
            water = [water[i] * input_param["device"]['hyd']['peak'] / max_water for i in range(len(water))]

    # ------ Create model ------
    m = gp.Model("OptModel")

    # ------ Parameters ------
    alpha_e = 0.5839  # 电网排放因子 kg/kWh
    alpha_gas = 1.535  # 天然气排放因子 kg/Nm3
    alpha_H2 = 1.74  # 氢排放因子
    alpha_eo = 0.8922  # 减排项目基准排放因子
    gas_price = 1.2

    lambda_ele_in = input_param['price']['TOU_power'] * 365  # 每个小时的电价
    discount = input_param['price']['discount']

    lambda_ele_out = input_param['price']['power_sale']  # 卖电价格
    lambda_h = input_param['price']['hydrogen_price']  # 买氢价格
    cer = input_param['calc_mode']['cer']  # 碳减排率

    c = 4.2 / 3600  # 水的比热容
    M = 1000000
    epsilon = 0.0000001
    s_sum = input_param['renewable_energy']['pv_sc_max']

    # 计算各种设备的年化收益率
    crf_fc = crf(input_param['device']['fc']['crf'])
    crf_el = crf(input_param['device']['el']['crf'])
    crf_hst = crf(input_param['device']['hst']['crf'])
    crf_water = crf(input_param['device']['ht']['crf'])
    crf_pv = crf(input_param['device']['pv']['crf'])
    crf_sc = crf(input_param['device']['sc']['crf'])
    # crf_pump =  crf(input_jso['device']n['']['crf'])
    crf_eb = crf(input_param['device']['eb']['crf'])
    crf_ac = crf(input_param['device']['ac']['crf'])
    crf_hp = crf(input_param['device']['hp']['crf'])
    crf_hp1 = crf(input_param['device']['hp1']['crf'])
    crf_hp2 = crf(input_param['device']['hp2']['crf'])
    crf_hpg = crf(input_param['device']['ghp']['crf'])
    crf_gtw = crf(input_param['device']['gtw']['crf'])
    crf_co = crf(input_param['device']['co']['crf'])
    crf_hyd = crf(input_param['device']['hyd']['crf'])
    crf_xb = crf(input_param['device']['xb']['crf'])
    crf_whp = crf(input_param['device']['whp']['crf'])

    # 导入各种设备的花费
    cost_hp = input_param['device']['hp']['cost'] + support_device(input_param['device']['hp']['cost'],
                                                                   input_param['device']['hp']['se'])
    cost_ac = input_param['device']['ac']['cost'] + support_device(input_param['device']['ac']['cost'],
                                                                   input_param['device']['ac']['se'])
    cost_hp1 = input_param['device']['hp1']['cost'] + support_device(input_param['device']['hp1']['cost'],
                                                                     input_param['device']['hp1']['se'])
    cost_hp2 = input_param['device']['hp2']['cost'] + support_device(input_param['device']['hp2']['cost'],
                                                                     input_param['device']['hp2']['se'])
    cost_hpg = input_param['device']['ghp']['cost'] + support_device(input_param['device']['ghp']['cost'],
                                                                     input_param['device']['ghp']['se'])
    cost_eb = input_param['device']['eb']['cost'] + support_device(input_param['device']['eb']['cost'],
                                                                   input_param['device']['eb']['se'])
    # cost_ec = 3326.613
    cost_fc = input_param['device']['fc']['cost'] + support_device(input_param['device']['fc']['cost'],
                                                                   input_param['device']['fc']['se'])
    cost_el = input_param['device']['el']['cost'] + support_device(input_param['device']['el']['cost'],
                                                                   input_param['device']['el']['se'])
    cost_hst = input_param['device']['hst']['cost'] + support_device(input_param['device']['hst']['cost'],
                                                                     input_param['device']['hst']['se'])
    cost_ht = input_param['device']['ht']['cost'] + support_device(input_param['device']['ht']['cost'],
                                                                   input_param['device']['ht'][
                                                                      'se'])  # rmb/kg 180 # yuan/kwh
    cost_co = input_param['device']['co']['cost'] + support_device(input_param['device']['co']['cost'],
                                                                   input_param['device']['co']['se'])
    cost_pv = input_param['device']['pv']['cost'] + support_device(input_param['device']['pv']['cost'],
                                                                   input_param['device']['pv']['se'])
    # cost_pump = 730
    cost_gtw = input_param['device']['gtw']['cost'] + support_device(input_param['device']['gtw']['cost'],
                                                                     input_param['device']['gtw']['se'])
    cost_sc = input_param['device']['sc']['cost'] + support_device(input_param['device']['sc']['cost'],
                                                                   input_param['device']['sc']['se'])
    cost_hyd = input_param['device']['hyd']['cost'] + support_device(input_param['device']['hyd']['cost'],
                                                                     input_param['device']['hyd']['se'])
    cost_xb = input_param['device']['xb']['cost'] + support_device(input_param['device']['xb']['cost'],
                                                                   input_param['device']['xb']['se'])
    cost_whp = input_param['device']['whp']['cost'] + support_device(input_param['device']['whp']['cost'],
                                                                     input_param['device']['whp']['se'])

    eta_ex = 0.95
    eta_pv = input_param['device']['pv']['beta_pv']

    # 导入各种设备的效率，包括产热、制冷、发电、热转换等等
    k_co = input_param['device']['co']['beta_co']
    k_fc_p = input_param['device']['fc']['eta_fc_p']
    k_fc_g = input_param['device']['fc']['eta_ex_g']
    k_el = input_param['device']['el']['beta_el']
    k_hp_g = input_param['device']['hp']['beta_hpg']  #
    k_hp_q = input_param['device']['hp']['beta_hpq']
    k_hp1_g = input_param['device']['hp1']['beta_hpg']
    k_hp1_q = input_param['device']['hp1']['beta_hpq']
    k_hp2_g = input_param['device']['hp2']['beta_hpg']
    k_hp2_q = input_param['device']['hp2']['beta_hpq']
    k_hpg_g = input_param['device']['ghp']['beta_ghpg']  # -dict['load_sort']*0.3
    k_hpg_q = input_param['device']['ghp']['beta_ghpq']
    k_eb = input_param['device']['eb']['beta_eb']
    k_ac = input_param['device']['ac']['beta_ac']
    k_sc = input_param['device']['sc']['beta_sc']
    theta_ex = input_param['device']['sc']['theta_ex']
    p_gtw = input_param['device']['gtw']['beta_gtw']
    k_whp = input_param['device']['whp']['beta_whp']

    # k_hpg_g = k_hpg_g*365

    # 导入负荷数据，电、热、冷、光照
    ele_load = load_data['ele_load']
    g_demand = load_data['g_demand']
    q_demand = load_data['q_demand']
    r_solar = load_data['r_solar']
    r_r_solar = load_data['r_solar']
    # ele_load= [4610.758]*8760
    # q_demand=[10604.744]*8760

    z_g_demand = load_data["z_heat_mounth"]
    z_q_demand = load_data["z_cold_mounth"]
    # 增加洗煤厂热负荷
    # for i in range(8760):
    #     # 9-11点增加热负1
    #     if i%24 >= 7 and i%24 <= 23 and z_g_demand[i] == 1:
    #         g_demand[i] += 167

    # print(sum(z_g_demand))
    # exit(0)
    # z_g_demand = [1 for i in range(8760)]
    # z_q_demand = [1 for i in range(8760)]
    # ele_day = [356.06,332.77,321.13,315.31,359.52,472.41,643.9,754.74,728.19,647.6,556.43,562.26,556.43,538.97,533.15,564.49,769.55,990.85,1023.2,954.17,930.89,809.94,630.78,471.32]

    # ele_load = ele_day*365
    # kkk = 10000/max(ele_day)
    # ele_load = [kkk*ele_load[i] for i in range(8760)]

    # q_demand = [q_demand[i]*2 for i in range(len(q_demand))]
    # g_demand = [g_demand[i]*2 for i in range(len(g_demand))]
    # ele_load = [ele_load[i]*2 for i in range(len(ele_load))]
    print(sum(g_demand), sum(q_demand), sum(ele_load))
    print(max(g_demand), max(q_demand), max(ele_load))
    print("----------------g,q,e_load----------------")

    period = 8760

    # ------ Variables ------
    z_fc = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=f"z_fc{t}") for t in range(period)]

    # z_el = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=f"z_el{t}") for t in range(period)]

    # z_hpgq = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=f"z_hpgq{t}") for t in range(period)]
    # z_hpgg = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=f"z_hpgg{t}") for t in range(period)]
    # z_ele_in = [m.addVar(lb=-0.0001, ub=1.01, vtype=GRB.BINARY, name=f"z_ele_in{t}") for t in range(period)]
    # z_ele_out = [m.addVar(lb=-0.0001, ub=1.01, vtype=GRB.BINARY, name=f"z_ele_out{t}") for t in range(period)]

    op_sum = m.addVar(vtype=GRB.CONTINUOUS, lb=-10000000000, name=f"op_sum")
    res_op_sum = op_sum
    s_pv = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"s_pv")  # ub=13340,
    s_sc = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"s_sc")
    capex_sum = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"capex_sum")
    capex_crf = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"capex_crf")
    capex_fc = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"capex_fc")
    capex_el = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"capex_el")

    num_gtw = m.addVar(vtype=GRB.INTEGER, lb=0, name='num_gtw')  # 地热井
    # Create variables

    ce_h = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="ce_h")
    g_hp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_hp{t}") for t in range(period)]  # 热泵产热
    g_hp1 = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_hp1{t}") for t in range(period)]
    g_hp2 = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_hp2{t}") for t in range(period)]
    g_hpg = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_hpg{t}") for t in range(period)]  # 热泵产热
    g_hpg_gr = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_hpg_gr{t}") for t in range(period)]  # 热泵灌热
    q_hp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"q_hp{t}") for t in range(period)]  # 热泵产热
    q_hp1 = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"q_hp1{t}") for t in range(period)]
    q_hp2 = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"q_hp2{t}") for t in range(period)]
    q_hpg = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"q_hpg{t}") for t in range(period)]  # 热泵产热

    p_xb = [m.addVar(vtype=GRB.CONTINUOUS, lb=-1000000, name=f"p_xb{t}") for t in range(period)]  # 相变储热充放功率，正值充热，负值放热

    p_hp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_hp{t}") for t in range(period)]  # 热泵产热耗电 ub = 268,
    p_hp1 = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_hp1{t}") for t in range(period)]
    p_hp2 = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_hp2{t}") for t in range(period)]
    p_hp_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["hp"]["power_max"], name=f"p_hp_max")
    p_hp1_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["hp1"]["power_max"], name=f"p_hp1_max")
    p_hp2_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["hp2"]["power_max"], name=f"p_hp2_max")
    p_whp_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["whp"]["power_max"], name=f"p_whp_max")
    p_hpc = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_hpc{t}") for t in range(period)]  # 热泵产冷的耗电,ub = 202
    p_hpc1 = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_hpc1{t}") for t in range(period)]
    p_hpc2 = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_hpc2{t}") for t in range(period)]

    # p_hpc_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0,ub = input_json["device"]["hp"]["power_max"],  name=f"p_hpc_max")

    p_hpg = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_hpg{t}") for t in range(period)]  # 热泵产热耗电 ub = 268,
    p_hpg_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["ghp"]["power_max"], name=f"p_hpg_max")

    p_hpgc = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_hpgc{t}") for t in range(period)]  # 热泵产冷的耗电,ub = 202
    # p_hpgc_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0,ub = input_json["device"]["ghp"]["power_max"],  name=f"p_hpgc_max")
    p_whp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_whp{t}") for t in range(period)]  # 余热热泵,
    g_whp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_whp{t}") for t in range(period)]
    q_whp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"q_whp{t}") for t in range(period)]

    # m_hp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_hp{t}") for t in range(period)]#热泵供热换水量
    # m_hpc = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_hpc{t}") for t in range(period)]#热泵供冷换水量

    # m_eb = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_eb{t}") for t in range(period)]#电锅炉换水量

    p_eb = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_eb{t}") for t in range(period)]  # 电锅炉耗电
    g_ac = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_ac{t}") for t in range(period)]
    p_eb_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["eb"]["power_max"], name=f"p_eb_max")
    g_ac_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["ac"]["power_max"], name=f"g_ac_max")
    q_ac = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"q_ac{t}") for t in range(period)]
    g_eb = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_eb{t}") for t in range(period)]  # 电锅炉产热
    g_tube = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_tube{t}") for t in range(period)]
    p_co = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_co{t}") for t in range(period)]
    p_co_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["co"]["power_max"], name=f"p_co_max")
    p_pv = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_pv{t}") for t in range(period)]
    t_ht = [m.addVar(vtype=GRB.CONTINUOUS, lb=55, ub=input_param['device']['ht']['t_max'], name=f"t_ht{t}") for t in
            range(period)]  # temperature of hot water tank
    m_ht = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_ht")
    m_ct = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_ct")
    t_ct = [m.addVar(vtype=GRB.CONTINUOUS, lb=2, ub=input_param['device']['ct']['t_max'], name=f"t_ct{t}") for t in
            range(period)]  # temperature of cold water tank

    m_xb = m.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param['device']['xb']['s_max'], name=f"m_xb")  # 相变储能模块大小
    s_xb = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"s_xb{t}") for t in range(period)]  # 相变储能模块在t时刻的储热量

    # q_ec = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"q_ec{t}") for t in range(period)]# electric-cold unit 产冷
    # p_ec = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_ec{t}") for t in range(period)] # 耗电
    # p_ec_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_ec_max")

    g_fc = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_fc{t}") for t in
            range(period)]  # heat generated by fuel cells
    p_fc = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_fc{t}") for t in range(period)]  # 燃料电池产电
    p_fc_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_fc_max")
    # fc_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="fc_max") # rated heat power of fuel cells
    g_sc = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_sc{t}") for t in range(period)]
    # pump_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="pump_max")

    p_el_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="p_el_max")  # rated heat power of fuel cells

    # t_de = [m.addVar(vtype=GRB.CONTINUOUS, lb=0,name=f"t_de{t}") for t in range(period)] # outlet temparature of heat supply circuits

    h_fc = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_fc{t}") for t in range(period)]  # hydrogen used in fuel cells

    # m_fc = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_fc") # fuel cells water
    # m_el = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_el") # fuel cells water
    # g_el = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_el{t}") for t in range(period)] # heat generated by Electrolyzer

    h_el = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_el{t}") for t in
            range(period)]  # hydrogen generated by electrolyzer
    p_el = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_el{t}") for t in
            range(period)]  # power consumption by electrolyzer

    h_sto = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_sto{t}") for t in range(period)]  # hydrogen storage 非季节储氢

    # h_ssto = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_sto{t}") for t in range(365)] # 季节性储氢

    h_pur = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_pur{t}") for t in range(period)]  # hydrogen purchase
    p_pur = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_pur{t}") for t in range(period)]  # power purchase
    p_hyd = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_hyd{t}") for t in range(period)]
    p_sol = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_sol{t}") for t in range(period)]  # power purchase

    cost_c_ele = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"cost_c_ele")

    cost_c_heat = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"cost_c_heat")

    cost_c_cool = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"cost_c_cool")

    cost_c = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"cost_c")
    # p_pump = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_pump{t}") for t in range(period)]

    hst = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"hst")

    # ------ Update model ------
    m.update()

    # ------ Constraints ------
    # 每日水罐温度平衡，非季节储氢量平衡
    # for i in range(int(period/24)-1):
    # m.addConstr(t_ht[i*24+24] == t_ht[24*i])
    # m.addConstr(t_ct[i*24+24] == t_ct[24*i])
    # m.addConstr(h_sto[i*24+24] == h_sto[24*i])

    # m.addConstr(t_ht[-1] == t_ht[0])
    # m.addConstr(t_ct[-1] == t_ct[0])
    # m.addConstr(h_sto[-12] == h_sto[0])

    m.addConstr(num_gtw <= input_param['device']['gtw']['number_max'])
    m.addConstr(p_fc_max <= input_param['device']['fc']['power_max'])
    m.addConstr(p_fc_max >= input_param['device']['fc']['power_min'])
    m.addConstr(p_hpg_max <= input_param['device']['ghp']['power_max'])
    m.addConstr(p_hpg_max >= input_param['device']['ghp']['power_min'])
    m.addConstr(p_hp_max <= input_param['device']['hp']['power_max'])
    m.addConstr(p_hp_max >= input_param['device']['hp']['power_min'])
    m.addConstr(p_hp1_max <= input_param['device']['hp1']['power_max'])
    m.addConstr(p_hp1_max >= input_param['device']['hp1']['power_min'])
    m.addConstr(p_hp2_max <= input_param['device']['hp2']['power_max'])
    m.addConstr(p_hp2_max >= input_param['device']['hp2']['power_min'])
    m.addConstr(p_whp_max <= input_param['device']['whp']['power_max'])

    m.addConstr(g_ac_max <= input_param['device']['ac']['power_max'])
    m.addConstr(g_ac_max >= input_param['device']['ac']['power_min'])

    m.addConstr(p_eb_max <= input_param['device']['eb']['power_max'])
    m.addConstr(p_eb_max >= input_param['device']['eb']['power_min'])
    m.addConstr(p_el_max <= input_param['device']['el']['power_max'])
    m.addConstr(p_el_max <= 50 * input_param['device']['el']['nm3_max'] / 11.2)
    m.addConstr(p_el_max >= 50 * input_param['device']['el']['nm3_min'] / 11.2)
    m.addConstr(p_el_max >= input_param['device']['el']['power_min'])
    m.addConstr(hst <= input_param['device']['hst']['sto_max'])
    m.addConstr(hst >= input_param['device']['hst']['sto_min'])
    m.addConstr(m_ht <= input_param['device']['ht']['water_max'])
    m.addConstr(m_ht >= input_param['device']['ht']['water_min'])
    m.addConstr(m_ct <= input_param['device']['ct']['water_max'])
    m.addConstr(m_ct >= input_param['device']['ct']['water_min'])
    m.addConstr(s_pv <= input_param['device']['pv']['area_max'])
    m.addConstr(s_pv >= input_param['device']['pv']['area_min'])
    m.addConstr(s_sc <= input_param['device']['sc']['area_max'])
    m.addConstr(s_sc >= input_param['device']['sc']['area_min'])
    m.addConstr(p_co_max <= input_param['device']['co']['power_max'])
    m.addConstr(p_co_max >= input_param['device']['co']['power_min'])

    # m.addConstr(p_el_max == 56818)
    # #m.addConstr(hst == )
    # m.addConstr(p_fc_max == 5293)
    # m.addConstr(p_ec_max == 195)
    # m.addConstr(p_hp_max == 0)
    # m.addConstr(s_pv == 70190)
    # 储能约束
    # if i%24 == 0 and int(i/24)<364:
    # m.addConstr(m_ct * (t_ct[i] - t_ct[i+1]) + q_demand[i]/c == m_hpc[i] * (5) +m_ec[i]*(5)  - eta_loss*m_ct*(t_ct[i] - 16))
    # m.addConstr(h_sto[i+1] - h_sto[i] + h_ssto[int(i/24)+1] - h_ssto[int(i/24)] == h_pur[i] + h_el[i] - h_fc[i])
    for i in range(period - 1):
        # hot water tank and heat supply 少个whp的热约束
        m.addConstr(
            g_tube[i] == g_fc[i] + g_whp[i] + g_hp[i] + g_hp1[i] + g_hp2[i] + g_eb[i] + g_sc[i] - g_ac[i] - g_hpg_gr[
                i] - c * m_ht * (t_ht[i + 1] - t_ht[i]) - 0.001 * c * m_ht * (
                    t_ht[i] - input_param['device']['ht']['t_supply']) - p_xb[i])
        m.addConstr(g_demand[i] == g_tube[i] + g_hpg[i])  # 区分
        m.addConstr(s_xb[i + 1] == s_xb[i] + p_xb[i])  # 相变储热在t+1时刻储量为t时刻+充放
        m.addConstr(p_xb[i] >= -m_xb * input_param['device']['xb']['p_kwh'])
        # cold water tank and cold supply
        m.addConstr(
            c * m_ht * (t_ct[i] - t_ct[i + 1]) + 0.001 * c * m_ht * (input_param['device']['ct']['t_max'] - t_ct[i]) +
            q_demand[i] == q_hp[i] + q_hp1[i] + q_hp2[i] + q_ac[i] + q_hpg[i] + q_whp[i])

        # else:
        # m.addConstr(m_ct * (t_ct[i] - t_ct[i+1]) + q_demand[i]/c == m_hpc[i] * (5) +m_ec[i]*(5)  - eta_loss*m_ct*(t_ct[i] - 16))
        m.addConstr(h_sto[i + 1] - h_sto[i] == h_pur[i] + h_el[i] - h_fc[i])  # 氢气储罐在t+1时刻的储量为t时刻+买氢-燃料电池消耗
        m.addConstr(s_xb[i] <= m_xb)  # 相变储热t时刻储量不能超过模块规划大小
    m.addConstr(g_tube[-1] == g_fc[-1] + g_hp[-1] + g_hp1[-1] + g_hp2[-1] + g_eb[-1] + g_sc[-1] + g_whp[-1] - g_hpg_gr[
        -1] - c * m_ht * (t_ht[0] - t_ht[-1]) - 0.001 * c * m_ht * (t_ht[-1] - input_param['device']['ht']['t_supply']) -
                p_xb[-1])

    m.addConstr(s_xb[0] == s_xb[-1] + p_xb[-1])
    m.addConstr(g_demand[-1] == g_tube[-1] + g_hpg[-1])
    m.addConstr(
        c * m_ht * (t_ct[-1] - t_ct[0]) + q_demand[-1] == q_hp[-1] + q_hp1[-1] + q_hp2[-1] + q_ac[-1] + q_hpg[-1] +
        q_whp[-1])
    m.addConstr(h_sto[0] - h_sto[-1] == h_pur[-1] + h_el[-1] - h_fc[-1])
    m.addConstr(s_xb[-1] <= m_xb)
    m.addConstr(p_xb[-1] >= m_xb * input_param['device']['xb']['p_kwh'])
    # m.addConstr(gp.quicksum(q_hpg)+gp.quicksum(p_hpgc)+gp.quicksum(g_hpg_gr) >= gp.quicksum(g_hpg)-gp.quicksum(p_hpg))

    m.addConstr(capex_fc == cost_fc * p_fc_max)
    m.addConstr(capex_el == cost_el * p_el_max)
    # m.addConstr(s_pv*cost_pv +s_sc*cost_sc +p_hpg_max*cost_hpg +cost_gtw*num_gtw +cost_ht*m_ht+cost_ht*m_ct+cost_hst*hst+cost_eb*p_eb_max+cost_hp*p_hp_max+cost_fc*p_fc_max+cost_el*p_el_max + 10*gp.quicksum([p_pur[i]*lambda_ele_in[i] for i in range(period)])-10*gp.quicksum(p_sol)*lambda_ele_out+10*lambda_h*gp.quicksum(h_pur)+954>=0 )
    # m.addConstr(cost_hyd*input_json["device"]['hyd']['flag'] + s_pv*cost_pv +s_sc*cost_sc +p_hpg_max*cost_hpg +cost_gtw*num_gtw +cost_ht*m_ht+cost_ht*m_ct+cost_hst*hst+cost_eb*p_eb_max+cost_hp*p_hp_max+cost_fc*p_fc_max+cost_el*p_el_max <= input_json['price']['capex_max'][1-trade_flag["p_sol"]])
    for i in range(period):
        # 电网
        m.addConstr(p_pur[i] <= 1000000000 * (trade_flag["p_pur"]))  # 是否允许电网买电
        m.addConstr(p_sol[i] <= 1000000000 * (trade_flag["p_sol"]))  # 是否允许电网卖电
        m.addConstr(h_pur[i] <= 1000000000 * (trade_flag["h_pur"]))  # 是否允许购买氢气

        # m.addConstr(z_hpgq[i] <= q_demand[i])
        # m.addConstr(z_hpgg[i] <= g_demand[i])
        # 这里得假设热负荷时连续的月份

        m.addConstr(p_hpgc[i] <= z_q_demand[i] * 10000000000)
        m.addConstr(p_hpg[i] <= z_g_demand[i] * 10000000000)
        # 燃料电池
        m.addConstr(g_fc[i] <= eta_ex * k_fc_g * h_fc[i])
        m.addConstr(1000000 * z_fc[i] >= g_fc[i])
        # m.addConstr(g_fc[i] == c*m_fc[i]*(10))
        # m.addConstr(m_fc[i] <= g_fc[i]*100000)
        m.addConstr(p_fc[i] == k_fc_p * h_fc[i])

        m.addConstr(p_fc[i] <= p_fc_max)
        m.addConstr(g_hpg_gr[i] <= g_fc[i] + g_eb[i])
        # m.addConstr(z_fc[i]+g_fc[i]>=0.01)

        # 电解槽
        m.addConstr(p_el[i] <= p_el_max)
        m.addConstr(h_el[i] <= k_el * p_el[i])
        m.addConstr(h_el[i] <= hst)  # 有问题

        if input_param["device"]['hyd']['flag'] == 1:
            m.addConstr(p_hyd[i] <= water[i])
            if input_param["device"]['hyd']['supply'] == 0:
                m.addConstr(p_el[i] == p_hyd[i])
        else:
            m.addConstr(p_hyd[i] == 0)

        # heat pump
        m.addConstr(p_hp[i] * k_hp_g == g_hp[i])
        m.addConstr(p_hp[i] <= p_hp_max)

        m.addConstr(p_hpc[i] * k_hp_q == q_hp[i])
        m.addConstr(p_hpc[i] <= p_hp_max)

        m.addConstr(p_hp1[i] * k_hp1_g == g_hp1[i])
        m.addConstr(p_hp1[i] <= p_hp1_max)

        m.addConstr(p_hpc1[i] * k_hp1_q == q_hp1[i])
        m.addConstr(p_hpc1[i] <= p_hp1_max)

        m.addConstr(p_hp2[i] * k_hp2_g == g_hp2[i])
        m.addConstr(p_hp2[i] <= p_hp2_max)

        m.addConstr(p_hpc2[i] * k_hp2_q == q_hp2[i])
        m.addConstr(p_hpc2[i] <= p_hp2_max)

        # whp
        m.addConstr(p_whp[i] * k_whp == g_whp[i])
        m.addConstr(q_whp[i] == g_whp[i] * (1 - 1 / k_whp))
        m.addConstr(p_whp[i] <= p_whp_max)

        # hpg
        m.addConstr(p_hpg[i] * k_hpg_g == g_hpg[i])
        m.addConstr(p_hpg[i] <= p_hpg_max)

        m.addConstr(p_hpgc[i] * k_hpg_q == q_hpg[i])
        m.addConstr(p_hpgc[i] <= p_hpg_max)

        # compressor
        m.addConstr(p_co[i] == k_co * h_el[i])
        m.addConstr(p_co[i] <= p_co_max)

        # electric boilor
        m.addConstr(k_eb * p_eb[i] == g_eb[i])
        m.addConstr(p_eb[i] <= p_eb_max)

        # air conditioner
        m.addConstr(q_ac[i] == k_ac * g_ac[i])
        m.addConstr(g_ac[i] <= g_ac_max)

        # hydrogen sto
        m.addConstr(h_sto[i] <= hst)

        # balance
        m.addConstr(
            p_whp[i] + p_el[i] + p_sol[i] + p_hp[i] + p_hp1[i] + p_hp2[i] + p_hpc[i] + p_hpc1[i] + p_hpc2[i] + p_hpg[
                i] + p_hpgc[i] + p_eb[i] + p_co[i] + ele_load[i] == p_hyd[i] + p_pur[i] + p_fc[i] + p_pv[i])

        # pv
        m.addConstr(p_pv[i] <= eta_pv * s_pv * r_solar[i])  # 允许丢弃可再生能源
        # sc
        m.addConstr(g_sc[i] <= k_sc * theta_ex * s_sc * r_solar[i])

        # psol
        m.addConstr(p_sol[i] <= p_fc[i] + p_pv[i])  # ？
        m.addConstr(p_sol[i] <= s_pv * r_solar[i])  # ？

        # p_gtw 井和热泵有关联，取大的
        m.addConstr(num_gtw * p_gtw >= g_hpg[i] - p_hpg[i])  # 井和热泵有关联，制热量-电功率=取热量
        m.addConstr(num_gtw * p_gtw >= q_hpg[i] + p_hpgc[i])  # 井和热泵有关联，制冷量+电功率=灌热量

    # area
    m.addConstr(s_pv + s_sc <= s_sum)
    # m.addConstr(num_gtw*p_gtw==p_hpg_max)#井和热泵有关联
    m.addConstr(op_sum == gp.quicksum([p_pur[i] * lambda_ele_in[i] for i in range(period)]) + gp.quicksum(p_hyd) *
                input_param["device"]["hyd"]["power_cost"] - gp.quicksum(
        [p_sol[i] for i in range(period)]) * lambda_ele_out + lambda_h * gp.quicksum([h_pur[i] for i in range(period)]))
    m.addConstr(op_sum <= input_param['price']['op_max'][1 - trade_flag["p_sol"]])  # 魔鬼数字，允不允许卖电的成本上限
    # m.setObjective( crf_pv * cost_pv*area_pv+ crf_el*cost_el*el_max
    #     +crf_hst * hst*cost_hst +crf_water* cost_water_hot*m_ht + crf_fc *cost_fc * fc_max + lambda_h*gp.quicksum(h_pur)*365+
    #     365*gp.quicksum([p_pur[i]*lambda_ele_in[i] for i in range(24)])-365*gp.quicksum(p_sol)*lambda_ele_out , GRB.MINIMIZE)

    m.addConstr(gp.quicksum(p_pur) <= (1 - cer) * (
                sum(ele_load) + sum(g_demand) / k_eb + sum(q_demand) / k_hpg_q))  # 碳减排约束，买电量不能超过碳排放,即1-碳减排
    if input_param['calc_mode']['c_neutral'] != 0:
        m.addConstr(gp.quicksum(p_pur) <= (input_param['calc_mode']['c_neutral']) * (
                    gp.quicksum(p_pv) + gp.quicksum(p_fc)))  # 碳中和约束
    m.addConstr(cost_c_ele == sum([ele_load[i] * lambda_ele_in[i] for i in range(period)]))
    m.addConstr(cost_c_heat == sum([g_demand[i] / 0.95 * lambda_ele_in[i] for i in range(period)]))  # /(3.41))
    m.addConstr(cost_c_cool == sum([q_demand[i] / 4 * lambda_ele_in[i] for i in range(period)]))  # /3.8)
    m.addConstr(cost_c == cost_c_cool + cost_c_heat + cost_c_ele)

    m.addConstr(
        capex_crf == crf_pv * s_pv * cost_pv + crf_sc * s_sc * cost_sc + crf_hst * hst * cost_hst + crf_water * cost_ht * (
            m_ht) + crf_hp * cost_hp * p_hp_max + crf_hp1 * cost_hp1 * p_hp1_max + crf_hp2 * cost_hp2 * p_hp2_max + crf_hpg * cost_hpg * p_hpg_max + crf_gtw * cost_gtw * num_gtw
        + crf_eb * cost_eb * p_eb_max + crf_ac * cost_ac * g_ac_max + crf_fc * capex_fc + crf_el * capex_el + crf_co * p_co_max * cost_co + crf_xb * cost_xb * m_xb + crf_whp * p_whp_max * cost_whp)
    m.addConstr(capex_sum == (cost_hyd * input_param["device"]['hyd'][
        'flag'] + s_pv * cost_pv + s_sc * cost_sc + p_hpg_max * cost_hpg + cost_gtw * num_gtw + cost_ht * m_ht + cost_hst * hst + cost_eb * p_eb_max + cost_ac * g_ac_max + cost_hp * p_hp_max + cost_hp1 * p_hp1_max + cost_hp2 * p_hp2_max + capex_fc + capex_el + cost_co * p_co_max + p_whp_max * cost_whp) * (
                        1 + input_param["price"]["PSE"]))

    m.addConstr(capex_sum <= input_param['price']['capex_max'][1 - trade_flag["p_pur"]])
    m.addConstr(ce_h == gp.quicksum(p_pur) * alpha_e)  # -gp.quicksum(p_sol)*alpha_e

    # ------ Objective ------
    m.setObjective(input_param['calc_mode']['obj']['capex_sum'] * capex_sum + input_param['calc_mode']['obj'][
        'capex_crf'] * capex_crf
                   + input_param['calc_mode']['obj']['opex'] * op_sum, GRB.MINIMIZE)

    # ------ Optimize ------
    m.params.NonConvex = 2
    m.Params.LogFile = "log/mip.log"
    m.params.MIPGap = 0.01
    # print(m.status)

    tick = time.time()

    try:
        m.optimize()
    except gp.GurobiError:
        print("Optimize failed due to non-convexity")
    # print([p_eb[i].X for i in range(period)])
    if m.status == GRB.INFEASIBLE or m.status == 4:
        print('Model is infeasible')
        m.computeIIS()
        m.write('model.ilp')
        print("Irreducible inconsistent subsystem is written to file 'model.ilp'")

    op_c = sum([(ele_load[i] + g_demand[i] / k_eb + q_demand[i] / k_hpg_q) * lambda_ele_in[i] for i in range(period)])

    cap_sum = capex_sum.x
    op_sum = sum([p_hyd[i].x for i in range(period)]) * input_param["device"]["hyd"]["power_cost"] + sum(
        [p_pur[i].X * lambda_ele_in[i] for i in range(period)]) + lambda_h * sum([h_pur[i].X for i in range(period)])
    # op_sum = op_sum.x
    revenue = sum([ele_load[i] * lambda_ele_in[i] for i in range(period)]) * input_param['price']['discount'] + sum(
        [p_sol[i].X for i in range(period)]) * lambda_ele_out + input_param['load']['load_area'] * (
                      input_param['price']['heat_price'] * (sum(z_g_demand) / 30 / 24) + input_param['price'][
                      'cold_price'] * (sum(z_q_demand) / 30 / 24))
    if input_param['price']['fixed_revenue'] != 0:
        revenue = input_param['price']['fixed_revenue']

    print("revenue_ele")
    revenue_ele = sum([ele_load[i] * lambda_ele_in[i] * input_param['price']['discount'] for i in range(period)])
    # revenue_heat = sum([g_demand[i]/0.95*lambda_ele_in[i] for i in range(period)])
    # revenue_cold = sum([q_demand[i]/4*lambda_ele_in[i] for i in range(period)])
    print(revenue_ele)
    p_a_y = (sum(ele_load) + sum(g_demand) + sum(q_demand)) / input_param["load"]["load_area"]
    if p_a_y < 60 or p_a_y > 120:
        print("负荷异常")
    else:
        print("负荷无异常")
    print(format(p_a_y, '.2f'))
    print("————————————————")

    # 规划输出
    output_json = {
        'ele_load_sum': int(sum(ele_load)),  # 电负荷总量/kwh
        'g_demand_sum': int(sum(g_demand)),  # 热负荷总量/kwh
        'q_demand_sum': int(sum(q_demand)),  # 冷负荷总量/kwh
        'ele_load_max': int(max(ele_load)),  # 电负荷峰值/kwh
        'g_demand_max': int(max(g_demand)),  # 热负荷峰值/kwh
        'q_demand_max': int(max(q_demand)),  # 冷负荷峰值/kwh
        'ele_load': ele_load,  # 电负荷8760h的分时数据/kwh
        'g_demand': g_demand,  # 热负荷8760h的分时数据/kwh
        'q_demand': q_demand,  # 冷负荷8760h的分时数据/kwh
        'r_solar': r_solar,  # 光照强度8760h的分时数据/kwh
        'r_r_solar': r_r_solar,
        'num_gtw': num_gtw.X,  # 地热井数目/个
        'p_fc_max': format(p_fc_max.X, '.1f'),  # 燃料电池容量/kw
        'p_hpg_max': format(p_hpg_max.X, '.1f'),  # 地源热泵功率/kw
        'p_hp_max': format(p_hp_max.X, '.1f'),  # 空气源热泵功率/kw
        'p_hp1_max': format(p_hp1_max.X, '.1f'),
        'p_hp2_max': format(p_hp2_max.X, '.1f'),
        'p_whp_max': format(p_whp_max.X, '.1f'),  # whp/kw
        'g_ac_max': format(g_ac_max.X, '.1f'),
        'p_eb_max': format(p_eb_max.X, '.1f'),  # 电热锅炉功率/kw
        'p_el_max': format(p_el_max.X, '.1f'),  # 电解槽功率/kw
        'nm3_el_max': format(11.2 * p_el_max.X / 50, '.1f'),  # 电解槽nm3/nm3
        'hst': format(hst.X, '.1f'),  # 储氢罐容量/kg
        'm_ht': format(m_ht.X, '.1f'),  # 储热罐/kg
        'm_ct': format(m_ct.X, '.1f'),  # 冷水罐/kg
        'area_pv': format(s_pv.X, '.1f'),  # 光伏面积/m2
        'area_sc': format(s_sc.X, '.1f'),  # 集热器面积/m2
        'p_co': format(p_co_max.X, '.1f'),  # 氢压机功率/kw
        'm_xb': format(m_xb.X, '.1f'),  # 相变储热模块大小/kwh

        'cap_fc': capex_fc.X,
        'cap_hpg': cost_hpg * p_hpg_max.X,
        'cap_gtw': cost_gtw * num_gtw.X,
        'cap_hp': cost_hp * p_hp_max.X,
        'cap_hp1': cost_hp1 * p_hp1_max.X,
        'cap_hp2': cost_hp2 * p_hp2_max.X,
        # 'cap_hpc':cost_hpc*p_hpc_max.X,
        'cap_whp': cost_whp * p_whp_max.X,
        'cap_ac': cost_ac * g_ac_max.X,
        'cap_eb': cost_eb * p_eb_max.X,
        # 'cap_ec':cost_ec*p_ec_max.X,
        'cap_hst': cost_hst * hst.X,
        'cap_ht': cost_ht * m_ht.X,
        # 'cap_ct':cost_ht*m_ct,
        'cap_pv': s_pv.X * cost_pv,
        'cap_co': cost_co * p_co_max.X,
        'cap_sc': cost_sc * s_sc.X,
        'cap_el': capex_el.X,
        'cap_xb': cost_xb * m_xb.X,

        "equipment_cost": format(cap_sum / 10000, '.2f'),  # 设备总投资/万元
        "equipment_cost_perarea": format(cap_sum / input_param["load"]["load_area"], '.2f'),  # 单位面积投资 元/平米
        "receive_year": format(cap_sum / (revenue - op_sum + 0.01), '.2f'),  # 投资回报年限/年
    }
    g_hpg_gr = [g_hpg_gr[i].X for i in range(period)]
    g_hpg = [g_hpg[i].X for i in range(period)]
    q_hpg = [q_hpg[i].X for i in range(period)]
    device_cap = {
        'num_gtw': num_gtw.X,  # 地热井数目/个
        'p_fc_max': p_fc_max.X,  # 燃料电池容量/kw
        'p_hpg_max': p_hpg_max.X,  # 地源热泵功率/kw
        'p_hp_max': p_hp_max.X,  # 空气源热泵功率/kw
        'p_hp1_max': p_hp1_max.X,
        'p_hp2_max': p_hp2_max.X,
        'p_whp_max': p_whp_max.X,  # whp/kw
        'g_ac_max': g_ac_max.X,
        'p_eb_max': p_eb_max.X,  # 电热锅炉功率/kw
        'p_el_max': p_el_max.X,  # 电解槽功率/kw
        'hst': hst.X,  # 储氢罐容量/kg
        'm_ht': m_ht.X,  # 储热罐/kg
        'm_ct': m_ct.X,  # 冷水罐/kg
        'm_xb': m_xb.X,  # 相变储热模块大小/kwh
        'area_pv': s_pv.X,  # 光伏面积/m2
        'area_sc': s_sc.X,  # 集热器面积/m2
        'p_co': p_co_max.X,  # 氢压机功率/kw
        'nm3_el_max': format(11.2 * p_el_max.X / 50, '.1f'),  # 电解槽nm3/nm3

        # 'g_hpg_gr':[-sum(g_hpg_gr[m_date[2]:m_date[5]])*7/(m_date[2] - m_date[5]), -sum(g_hpg_gr[m_date[5]:m_date[8]])*7/(m_date[5] - m_date[8]),- sum(g_hpg_gr[m_date[8]:m_date[11]])*7/(m_date[8] - m_date[11]), sum(g_hpg_gr[m_date[11]:m_date[12]]+g_hpg_gr[m_date[0]:m_date[2]])*7/(90)],
        # 'g_hpg':[-sum(g_hpg[m_date[2]:m_date[5]])*7/(m_date[2] - m_date[5]), -sum(g_hpg[m_date[5]:m_date[8]])*7/(m_date[5] - m_date[8]), -sum(g_hpg[m_date[8]:m_date[11]])*7/(m_date[8] - m_date[11]), sum(g_hpg[m_date[11]:m_date[12]]+g_hpg[m_date[0]:m_date[2]])*7/90],
        # 'q_hpg':[-sum(q_hpg[m_date[2]:m_date[5]])*7/(m_date[2] - m_date[5]), -sum(q_hpg[m_date[5]:m_date[8]])*7/(m_date[5] - m_date[8]),- sum(q_hpg[m_date[8]:m_date[11]])*7/(m_date[8] - m_date[11]), sum(q_hpg[m_date[11]:m_date[12]]+q_hpg[m_date[0]:m_date[2]])*7/90]
        "revenue_ele": sum([ele_load[i] * lambda_ele_in[i] * input_param['price']['discount'] for i in range(period)]),
        "revenue_heat": input_param['load']['load_area'] * input_param['price']['heat_price'] * sum(z_g_demand) / 30 / 24,
        "revenue_cold": input_param['load']['load_area'] * input_param['price']['cold_price'] * sum(z_q_demand) / 30 / 24,
        'g_hpg_gr': [sum(g_hpg_gr[3288:3288 + 7 * 24]), sum(g_hpg_gr[5448:5448 + 7 * 24]),
                     sum(g_hpg_gr[7656:7656 + 7 * 24]), sum(g_hpg_gr[360:360 + 7 * 24])],
        'g_hpg': [sum(g_hpg[3288:3288 + 7 * 24]), sum(g_hpg[5448:5448 + 7 * 24]), sum(g_hpg[7656:7656 + 7 * 24]),
                  sum(g_hpg[360:360 + 7 * 24])],
        'q_hpg': [sum(q_hpg[3288:3288 + 7 * 24]), sum(q_hpg[5448:5448 + 7 * 24]), sum(q_hpg[7656:7656 + 7 * 24]),
                  sum(q_hpg[360:360 + 7 * 24])],  # 调试用
        'cap_device': {
            'cap_fc': capex_fc.X,
            'cap_hpg': cost_hpg * p_hpg_max.X,
            'cap_gtw': cost_gtw * num_gtw.X,
            'cap_hp': cost_hp * p_hp_max.X,
            'cap_hp1': cost_hp1 * p_hp1_max.X,
            'cap_hp2': cost_hp2 * p_hp2_max.X,
            # 'cap_hpc':cost_hpc*p_hpc_max.X,
            'cap_whp': cost_whp * p_whp_max.X,
            'cap_ac': cost_ac * g_ac_max.X,
            'cap_eb': cost_eb * p_eb_max.X,
            # 'cap_ec':cost_ec*p_ec_max.X,
            'cap_hst': cost_hst * hst.X,
            'cap_ht': cost_ht * m_ht.X,
            # 'cap_ct':cost_ht*m_ct,
            'cap_pv': s_pv.X * cost_pv,
            'cap_co': cost_co * p_co_max.X,
            'cap_sc': cost_sc * s_sc.X,
            'cap_el': capex_el.X,
            'cap_xb': cost_xb * m_xb.X,
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

    # lambda_ele_in = input_json['price']['TOU_power']*365
    ele_sum_ele_only = np.array(ele_load) + np.array(g_demand) / k_eb + np.array(q_demand) / k_hpg_q
    gas_sum_ele_gas = (np.array(g_demand) + np.array(q_demand) / 1.35) / 7.5
    opex_ele_only = sum(np.array(lambda_ele_in) * ele_sum_ele_only)
    opex_ele_gas = sum(np.array(lambda_ele_in) * np.array(ele_load)) + sum(gas_sum_ele_gas * gas_price)
    co2_ele_only = sum(ele_sum_ele_only) * input_param['carbon']['alpha_e']
    co2_ele_gas = sum(ele_load) * input_param['carbon']['alpha_e'] + sum(gas_sum_ele_gas) * 1.535
    # print("------------")
    operation_output_json = {
        # "operation_cost_net": format((revenue-op_sum)/10000,'.1f'),  # 年化运行净收益/万元
        # "operation_cost": format(op_sum/10000,'.1f'),  # 年化运行总成本/万元
        # "revenue": format(revenue/10000,'.1f'),  # 年化运行成本/万元
        'op_cost':
            {
                'all_of_revenue':
                    {
                        'all_revenue': format(revenue / 10000, '.2f'),
                        'fixed_revenue': format(input_param['price']['fixed_revenue'] / 10000, '.2f'),
                        'p_sol_revenue': format(sum(p_sol[i].X * lambda_ele_out for i in range(period)), '.2f'),
                        "revenue_heat": format(
                            input_param['load']['load_area'] * input_param['price']['heat_price'] * sum(
                                z_g_demand) / 30 / 24, '.2f'),
                        "revenue_cold": format(
                            input_param['load']['load_area'] * input_param['price']['cold_price'] * sum(
                                z_q_demand) / 30 / 24, '.2f'),
                    },
                'all_of_op_cost':
                    {
                        'all_op_cost': format(op_sum / 10000, '.2f'),
                        'p_pur_cost': format(sum([p_pur[i].X * lambda_ele_in[i] for i in range(period)]), '.2f'),
                        'h_pur_cost': format(lambda_h * sum([h_pur[i].X for i in range(period)]), '.2f')
                    },
                'net_revenue': format((revenue - op_sum) / 10000, '.2f'),
                'ele_statistics':
                    {
                        'sum_pv': format(sum(p_pv[i].X for i in range(period)), '.2f'),
                        'sum_fc': format(sum(p_fc[i].X for i in range(period)), '.2f'),
                        'sum_p_pur': format(sum(p_pur[i].X for i in range(period)), '.2f'),
                        'sum_p_sol': format(sum(p_sol[i].X for i in range(period)), '.2f')
                    }
            },
        "operation_cost_per_month_per_square": format(op_sum / 12 / input_param['load']['load_area'], '.2f'),
        # 单位面积月均运行成本
        "cost_save_rate": format((opex_ele_only - op_sum) / opex_ele_only, '.1f'),  # 电运行成本节约比例
        "cost_save_rate_gas": format((opex_ele_gas - op_sum) / opex_ele_gas, '.1f'),  # 电气运行成本节约比例
        "co2": format(ce_h.X / 1000, '.1f'),  # 总碳排/t
        "cer_rate": format((co2_ele_only - ce_h.X) / co2_ele_only * 100, '.1f'),  # 与电系统相比的碳减排率
        "cer_gas": format((co2_ele_gas - ce_h.X) / co2_ele_gas, '.1f'),  # 与电气系统相比的碳减排率
        "cer_perm2": format((co2_ele_only - ce_h.X) / input_param['load']['load_area'] / 1000, '.1f'),  # 电系统每平米的碳减排量/t
        "cer_perm2_gas": format((co2_ele_gas - ce_h.X) / input_param['load']['load_area'] / 1000, '.1f'),
        # 电气系统每平米的碳减排量/t
        "cer": format((co2_ele_only - ce_h.X) / 1000, '.2f'),
    }
    return {'objective': m.objVal,
            'res_capex': capex_crf.X,
            'res_opex': res_op_sum.X,
            'process time': time.time() - tick,
            'cap_fc': capex_fc.X,
            'cap_ac': cost_ac * g_ac_max.X,
            'cap_hp': cost_hp * p_hp_max.X,
            'cap_hpg': cost_hpg * p_hpg_max.X,
            # 'cap_hpc':cost_hpc*p_hpc_max.X,
            'cap_eb': cost_eb * p_eb_max.X,
            # 'cap_ec':cost_ec*p_ec_max.X,
            'cap_hst': cost_hst * hst.X,
            'cap_ht': cost_ht * m_ht.X,
            # 'cap_ct':cost_ht*m_ct,
            'cap_pv': s_pv.X * cost_pv,
            'cap_el': capex_el.X,
            # s_pv.X*cost_pv
            'num_gtw': num_gtw.X,
            'p_fc_max': p_fc_max.X,
            'p_hpg_max': p_hpg_max.X,
            'p_hp_max': p_hp_max.X,
            'p_hp1_max': p_hp1_max.X,
            'p_hp2_max': p_hp2_max.X,
            'p_whp_max': p_whp_max.X,
            'p_eb_max': p_eb_max.X,
            # 'p_ec_max':p_ec_max.X,
            'p_el_max': p_el_max.X,
            'hst': hst.X,
            'm_ht': m_ht.X,
            'm_ct': m_ct.X,
            'm_xb': m_xb.X,
            'area_pv': s_pv.X,
            'area_sc': s_sc.X,
            'h_cost': lambda_h * sum([h_pur[i].X for i in range(period)]),
            'p_cost': sum([p_pur[i].X * lambda_ele_in[i] for i in range(period)]),
            'p_sol_earn': -sum([p_sol[i].X for i in range(period)]) * lambda_ele_out,
            'opex': sum([p_pur[i].X * lambda_ele_in[i] for i in range(period)]) - sum(
                [p_sol[i].X for i in range(period)]) * lambda_ele_out + lambda_h * sum(
                [h_pur[i].X for i in range(period)]),
            'hyd_pur_cost': sum([p_hyd[i].X for i in range(period)]) * input_param["device"]["hyd"]["power_cost"],
            'cap_sum': capex_sum.x,
            "operation_cost": format(op_sum / 10000, '.1f'),  # 年化运行总成本/万元
            "revenue": format(revenue / 10000, '.1f'),  # 年化运行成本/万元
            "operation_cost_per_month_per_square": format(op_sum / 12 / input_param['load']['load_area'], '.2f'),
            # 单位面积月均运行成本
            "operation_cost_net": format((revenue - op_sum) / 10000, '.1f'),  # 年化运行净收益/万元
            'cer': format((co2_ele_only - ce_h.X) / co2_ele_only, '.1f'),
            'cer_self': sum([p_sol[i].X for i in range(period)]) / co2_ele_only,
            # "load_per_area":format((sum(ele_load)+sum(g_demand)+sum(q_demand))/8760/input_json["load"]["load_area"]),
            'ele_load': ele_load,
            'g_demand': g_demand,
            'q_demand': q_demand,
            # 'm_demand':dict['m_demand'],
            'p_pur': [p_pur[i].X for i in range(period)],
            'p_sol': [p_sol[i].X for i in range(period)],
            'p_hyd': [p_hyd[i].X for i in range(period)],
            'h_pur': [h_pur[i].X for i in range(period)],
            # 'g_solar': [eta_solar*s_solar*r_solar[i] for i in range(period)],
            'p_pv': [eta_pv * s_pv.X * r_solar[i] for i in range(period)],
            'p_pv_inbalance': [p_pv[i].x for i in range(period)],
            'p_fc': [p_fc[i].X for i in range(period)],
            'g_fc': [g_fc[i].X for i in range(period)],
            'h_fc': [h_fc[i].X for i in range(period)],
            'g_ac': [g_ac[i].X for i in range(period)],
            'q_ac': [q_ac[i].X for i in range(period)],
            'p_el': [p_el[i].X for i in range(period)],
            'h_el': [h_el[i].X for i in range(period)],
            'p_hp': [p_hp[i].X for i in range(period)],
            'g_hp': [g_hp[i].X for i in range(period)],
            'p_hpc': [p_hpc[i].X for i in range(period)],
            'q_hp': [q_hp[i].X for i in range(period)],
            'p_hpg': [p_hpg[i].X for i in range(period)],
            'p_hpgc': [p_hpgc[i].X for i in range(period)],
            'q_hpg': q_hpg,
            'g_hpg': g_hpg,
            'p_whp': [p_whp[i].X for i in range(period)],
            'g_tube': [g_tube[i].X for i in range(period)],
            't_ht': [t_ht[i].X for i in range(period)],
            'h_sto': [h_sto[i].X for i in range(period)],

            'p_eb': [p_eb[i].X for i in range(period)],
            'g_eb': [g_eb[i].X for i in range(period)],
            'g_sc': [g_sc[i].X for i in range(period)],
            # 'm_eb':[m_eb[i].X for i in range(period)],
            'g_hpg_gr': g_hpg_gr,

            't_ct': [t_ct[i].X for i in range(period)]
            # 'q_ac':[pulp.value(c*m_ac*(t_cr[i] - t_ac[i])) for i in range(period)],
            # 'g_fc':[eta_ex*mu_fc_g*h_fc[i].X for i in range(period)],
            # 'g_htv':[pulp.value(c*m_ht*(t_ht[i+1] - t_ht[i])) for i in range(period)],
            # 'g_eb':[eta_eb*p_eb[i].X for i in range(period)]
            # 'g_shtv':[pulp.value(g_sht[i+1] - g_sht[i]) for i in range(period)]
            }, output_json, operation_output_json, device_cap


if __name__ == '__main__':
    sys_path = sys.path
    print("Sys path:")
    for i in sys_path:
        print(i)
    project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print('-' * 20)
    print("Project path:", project_path, sep='\n')
    if project_path not in sys.path:
        print("Project path not in sys path, add it.")
        sys.path.append(project_path)
    else:
        print("Project path already in sys path.")
    # from module.utils import to_csv
    print("Start")
