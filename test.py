# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# 测试 gurobi
# ----------------------------------------------------------------------------------------------------------------------
# # from easydict import EasyDict as Edict
# import gurobipy as gp
#
# # 创建模型
# model = gp.Model()
#
# # 创建变量
# x1 = model.addVar(vtype=gp.GRB.INTEGER, name='x1')
# x2 = model.addVar(ub=3, vtype=gp.GRB.INTEGER, name='x2')
# x1_ = model.addVars(range(1, 3), vtype=gp.GRB.INTEGER, name='x1_')
# x2_ = model.addVars(range(1, 6), vtype=gp.GRB.INTEGER, name='x2_')
# # x3 = model.addVar(vtype=gp.GRB.INTEGER, name='x4')
# # x3 = model.addVars(range(0, 6), vtype=gp.GRB.INTEGER, name='x3')
#
# # 更新变量环境
# model.update()
#
# # 创建目标函数
# model.setObjective(100 * x1 + 40 * x2, sense=gp.GRB.MINIMIZE)
#
# # 创建约束条件
# left_1 = x1 + x2_[1]
# left_2 = x1 + x2_[1] + x2_[2]
# model.addConstr(left_1 >= 4, name='9:00-10:00')
# model.addConstr(left_2 >= 3, name='10:00-11:00')
# model.addConstr(x1 + x2_[1] + x2_[2] + x2_[3] >= 4, name='11:00-12:00')
# model.addConstr(x1_[1] + x2_[1] + x2_[2] + x2_[3] + x2_[4] >= 6, name='12:00-13:00')
# model.addConstr(x1_[2] + x2_[2] + x2_[3] + x2_[4] + x2_[5] >= 5, name='13:00-14:00')
# model.addConstr(x1 + x2_[3] + x2_[4] + x2_[5] >= 6, name='14:00-15:00')
# model.addConstr(x1 + x2_[4] + x2_[5] >= 8, name='15:00-16:00')
# model.addConstr(x1 + x2_[5] >= 8, name='16:00-17:00')
#
# # 此处, sum(x1_) 和 x1_.sum() 结果不同, 因为 sum(x1_) 对字典进行键相加
# # 更标准的写法是使用 gp.quicksum(x1_) 和 gp.quicksum(x2_)
# model.addConstr(x1_.sum() == x1, name='x1')
# model.addConstr(x2_.sum() == x2, name='x2')
#
# # 执行最优化
# model.optimize()
#
# # 打印所有变量名称及其索引
# variables = model.getVars()
# values = [model.getVars()[i].x for i in range(len(model.getVars()))]
# print("\n已创建的变量列表: variables")
# print(variables)
# print()
#
# print("x1:", x1, "variables[0]:", variables[0])
# if variables[0] is x1:
#     print("Yes, variables[0] is x1")
#     print("variables[0] id:", id(variables[0]), type(id(variables[0])))
#     print("x1 id:", id(x1), type(id(x1)))
#     print(id(x1) == id(variables[0]))
# else:
#     print("No")
#
# test_0 = gp.quicksum(variables[i] for i, j in enumerate(variables))
# test_1 = gp.quicksum(variables)
# test_2 = gp.quicksum(x2_)
# test_3 = gp.quicksum(x2_[i] for i in x2_)
# test_t = gp.LinExpr()
# test_t = test_t + test_2
# print(test_0, "\tvalue: ", test_0.getValue(), sep="")
# print(test_1, "\tvalue: ", test_1.getValue(), sep="")
# print(test_2, "\tvalue: ", test_2.getValue(), sep="")
# print(test_3, "\tvalue: ", test_3.getValue(), sep="")
# print(test_t, "\tvalue: ", test_t.getValue(), sep="")
#
# # # 获取 variables 字典
# # var_set = {}
# # for var in variables:
# #     index = var.varName.find("[")
# #     # vars
# #     if index != -1:
# #         var_name = var.varName.split("[")[0]
# #         var_i = int(var.varName.split("[")[1].split("]")[0])
# #         if var_name in var_set:
# #             var_set[var_name][var_i] = var
# #         else:
# #             var_set[var_name] = {}
# #             var_set[var_name][var_i] = var
# #         print("Variable name:", var_name, "[{}]".format(var_i), end="\t")
# #         # print("Index:", var.index)
# #         print("Index:", var.index, end="\t")
# #         print("Value:", var.x)
# #     # var
# #     else:
# #         var_name = var.varName
# #         var_set[var_name] = var
# #         print("Variable name:", var_name, end="\t")
# #         # print("Index:", var.index)
# #         print("Index:", var.index, end="\t")
# #         print("Value:", var.x)
# #
# # test_4 = gp.quicksum(var_set["x1_"][i] for i in var_set["x1_"])
# # test_5 = x1 + x2
# # print(test_4)
# # print(test_5)
# # for i in var_set["x1_"]:
# #     print(i, type(i))
# # for i in var_set:
# #     print(i, type(i))
# # print("length:", len(var_set))
# # print(var_set["x2_"][1])

# ----------------------------------------------------------------------------------------------------------------------
# 测试 json
# ----------------------------------------------------------------------------------------------------------------------
import json

data1 = """
{
    "项目描述": "本项目为榆林科创新城零碳分布式智慧能源中心示范项目，为运动员村进行供冷、供热以及供电服务。运动员村项目包括酒店、运动 员餐厅、办公、教育、住宅、公寓、体育等建筑。项目建设用地面积93347.47 m2，总建筑面积20.6万m2，地上建筑面积14万m2，其中住宅5.6万m2，办公4.9 万m2，酒店及运动员餐厅2.1万m2，健身中心0.5万m2，配套0.9万m2。由于DK1-13#楼酒店及运动员餐厅仅大堂地暖需能源站供应，实际供能面积约为12万m2。",
    "项目地理位置": "陕西省榆林市",
    "土地使用情况": "供能面积约为12万m2",
    "项目供能对象描述": "为运动员村进行供冷、供热以及供电服务",
    "项目预期描述": "最大化系统经济型，实现零碳供应能量，设备包括但不限于光伏、燃料电池、地源热泵、电解槽、电锅炉、热泵、地热井、储氢罐、蓄水箱。但是燃料电池容量不低于500kW。光伏板装机不超过2000kW,燃料电池的装机容量等于电解槽的装机容量。"
}
"""
data2 = json.loads(data1)
data3 = json.dumps(data1, indent=4, ensure_ascii=False)
data4 = json.dumps(data2, indent=4, ensure_ascii=False)
print("data1 type:", type(data1))
print(data1)
print("data2 type:", type(data2))
print(data2)
print("data3 type:", type(data3))
print(data3)
print("data4 type:", type(data4))
print(data4)
with open("data3.json", "w", encoding="utf-8") as f:
    json.dump(data1, f, indent=4, ensure_ascii=False)
with open("data4.json", "w", encoding="utf-8") as f:
    json.dump(data2, f, indent=4, ensure_ascii=False)

# import json
#
# data = {
#   "背景知识": "构建能源系统规划问题，在满足设备运行约束、能量平衡约束和其他附加约束的前提下，构建经济最优目标函数，计算得到设备容量和全年运行数据",
#   "约束条件": [
#     "设备容量约束：光伏板装机容量\\var{s_pv_inst}不得大于其装机上限\\param{s_pv_max}",
#     "设备容量约束：太阳能集热器装机容量\\var{s_sc_inst}不得大于其装机上限\\param{s_sc_max}",
#     "设备容量约束：氢燃料电池装机容量\\var{p_fc_inst}不得小于500kW",
#     "设备容量约束：光伏板装机容量\\var{s_pv_inst}不得超过2000kW",
#     "设备容量约束：氢燃料电池装机容量\\var{p_fc_inst}等于电解槽装机容量\\var{p_el_inst}",
#     "设备容量约束：氢燃料电池装机容量\\var{p_fc_inst}不得大于其装机上限\\param{p_fc_max}",
#     "设备容量约束：电解槽装机容量\\var{p_el_inst}不得大于其装机上限\\param{p_el_max}",
#     "设备容量约束：电锅炉装机容量\\var{p_eb_inst}不得大于其装机上限\\param{p_eb_max}",
#     "设备容量约束：热泵装机容量\\var{p_hp_inst}不得大于其装机上限\\param{p_hp_max}",
#     "设备容量约束：地源热泵装机容量\\var{p_ghp_inst}不得大于其装机上限\\param{p_ghp_max}",
#     "设备容量约束：储氢罐装机容量\\var{h_hst_inst}不得大于其装机上限\\param{h_hst_max}",
#     "设备容量约束：蓄水箱装机容量\\var{m_tank_inst}不得大于其装机上限\\param{m_tank_max}",
#     "设备运行约束：调度周期\\param{period}内各时段光伏板产电量\\var{p_pv[t]}不得大于其产电效率\\param{k_pv}、太阳辐射强度\\param{r_solar[t]}和其装机容量\\var{s_pv_inst}的乘积",
#     "设备运行约束：调度周期\\param{period}内各时段太阳能集热器产热量\\var{g_sc[t]}不得大于其产热效率\\param{k_sc}、太阳辐射强度\\param{r_solar[t]}和其装机容量\\var{s_sc_inst}的乘积",
#     "设备运行约束：调度周期\\param{period}内各时段氢燃料电池产电量\\var{p_fc[t]}等于其产电效率\\param{k_fc_p}和其耗氢量\\var{h_fc[t]}的乘积",
#     "设备运行约束：调度周期\\param{period}内各时段氢燃料电池产热量\\var{g_fc[t]}等于其热交换效率\\param{eta_ex}、其产热效率\\param{k_fc_g}和其耗氢量\\var{h_fc[t]}的乘积",
#     "设备运行约束：调度周期\\param{period}内各时段氢燃料电池产电量\\var{p_fc[t]}不得大于其装机容量\\var{p_fc_inst}",
#     "设备运行约束：调度周期\\param{period}内各时段电解槽产氢量\\var{h_el[t]}不得大于其产氢效率\\param{k_el}和其耗电量\\var{p_el[t]}的乘积",
#     "设备运行约束：调度周期\\param{period}内各时段电解槽耗电量\\var{p_el[t]}不得大于其装机容量\\var{p_el_inst}",
#     "设备运行约束：调度周期\\param{period}内各时段电锅炉产热量\\var{g_eb[t]}等于其产热效率\\param{k_eb}和其耗电量\\var{p_eb[t]}的乘积",
#     "设备运行约束：调度周期\\param{period}内各时段电锅炉耗电量\\var{p_eb[t]}不得大于其装机容量\\var{p_eb_inst}",
#     "设备运行约束：调度周期\\param{period}内各时段热泵产热量\\var{g_hp[t]}不得大于其产热效率\\param{k_hp_g}和其耗电量\\var{p_hp[t]}的乘积",
#     "设备运行约束：调度周期\\param{period}内各时段热泵产冷量\\var{q_hp[t]}不得大于其产冷效率\\param{k_hp_q}和其耗电量\\var{p_hp[t]}的乘积",
#     "设备运行约束：调度周期\\param{period}内各时段热泵耗电量\\var{p_hp[t]}不得大于其装机容量\\var{p_hp_inst}",
#     "设备运行约束：调度周期\\param{period}内各时段地源热泵产热量\\var{g_ghp[t]}不得大于其产热效率\\param{k_ghp_g}和其耗电量\\var{p_ghp[t]}的乘积",
#     "设备运行约束：调度周期\\param{period}内各时段地源热泵产冷量\\var{q_ghp[t]}不得大于其产冷效率\\param{k_ghp_q}和其耗电量\\var{p_ghp[t]}的乘积",
#     "设备运行约束：调度周期\\param{period}内各时段地源热泵耗电量\\var{p_ghp[t]}不得大于其装机容量\\var{p_ghp_inst}",
#     "设备运行约束：地缘热泵可以从所有地热井中取得的热量最大值（地热井装机数量\\var{num_gtw_inst} * 地热井可产热量\\param{g_gtw}）不得小于地源热泵最大产热量（地源热泵装机容量\\var{p_ghp_inst} * 其产热效率\\param{k_ghp_g}）",
#     "设备运行约束：调度周期\\param{period}内各时段储氢罐储氢量\\var{h_hst[t]}不得大于其装机容量\\var{h_hst_inst}",
#     "设备运行约束：调度周期\\param{period}内各时段热水箱（蓄水箱储热时）供热量\\var{g_ht[t]}等于热水箱储热变化量\\var{delta_g_ht[t]}的负值减去其热损失量\\var{g_ht_loss[t]}",
#     "设备运行约束：调度周期\\param{period}内各时段热水箱热损失量\\var{g_ht_loss[t]}等于热损失系数\\param{mu_tank_loss}、水的比热 c_water、水箱中水的质量\\var{m_tank_inst}和当前时刻水箱水温\\var{t_ht[t]}与环境温度（最低水温）\\param{t_ht_min}的差值的乘积",
#     "设备运行约束：调度周期\\param{period}内各时段冷水箱（蓄水箱储冷时）供冷量\\var{q_ct[t]}等于冷水箱储冷变化量\\var{delta_q_ct[t]}的负值，其冷损失量忽略不计",
#     "设备运行约束：调度周期\\param{period}内各时段管网供热量\\var{g_tube[t]}等于太阳能集热器产热量\\var{g_sc[t]}、氢燃料电池产热量\\var{g_fc[t]}、电锅炉产热量\\var{g_eb[t]}、热泵产热量\\var{g_hp[t]}和热水箱（蓄水箱储热时）供热量\\var{g_ht[t]}的和减去地源热泵向地热井灌热量\\var{g_ghp_inj[t]}",
#     "设备运行约束：除最后一个时段外，调度周期\\param{period}内各时段储氢罐储氢变化量\\var{delta_h_hst[t]}等于下一时刻储氢罐储氢量\\var{h_hst[t+1]}减去当前时刻储氢罐储氢量\\var{h_hst[t]}",
#     "设备运行约束：除最后一个时段外，调度周期\\param{period}内各时段热水箱储热变化量\\var{delta_g_ht[t]}等于水的比热 c_water、水箱中水的质量\\var{m_tank_inst}和水箱中水温变化量（下一时刻水温\\var{t_ht[t+1]减去当前时刻水温\\var{t_ht[t]}）的乘积",
#     "设备运行约束：除最后一个时段外，调度周期\\param{period}内各时段冷水箱储冷变化量\\var{delta_q_ct[t]}等于水的比热 c_water、水箱中水的质量\\var{m_tank_inst}和水箱中水温变化量（下一时刻水温\\var{t_ct[t+1]减去当前时刻水温\\var{t_ct[t]}）的乘积的负值",
#     "设备运行约束：最后一个时段储氢罐储氢变化量\\var{delta_h_hst[-1]}等于初始时刻储氢罐储氢量\\var{h_hst[0]}减去当前时刻储氢罐储氢量\\var{h_hst[-1]}，以保证调度周期结束时储氢罐储氢量与初始时刻储氢量一致",
#     "设备运行约束：最后一个时段热水箱储热变化量\\var{delta_g_ht[-1]}等于水的比热 c_water、水箱中水的质量\\var{m_tank_inst}和水箱中水温变化量（初始时刻水温\\var{t_ht[0]减去当前时刻水温\\var{t_ht[-1]}）的乘积，以保证调度周期结束时热水箱储热量与初始时刻储热量一致",
#     "设备运行约束：最后一个时段冷水箱储冷变化量\\var{delta_q_ct[-1]}等于水的比热 c_water、水箱中水的质量\\var{m_tank_inst}和水箱中水温变化量（初始时刻水温\\var{t_ct[0]减去当前时刻水温\\var{t_ct[-1]}）的乘积的负值，以保证调度周期结束时冷水箱储冷量与初始时刻储冷量一致",
#     "能量平衡约束：调度周期\\param{period}内各时段系统的电力供应（包括从电网购电量\\var{p_pur[t]}、光伏产电量\\var{p_pv[t]}和氢燃料电池产电量\\var{p_fc[t]}）减去向电网卖电量\\var{p_sell[t]}应等于电力需求（包括电负载\\param{p_load[t]}、电解槽耗电量\\var{p_el[t]}、电锅炉耗电量\\var{p_eb[t]}、热泵耗电量\\var{p_hp[t]}和地源热泵耗电量\\var{p_ghp[t]}）",
#     "能量平衡约束：调度周期\\param{period}内各时段系统的热负荷\\param{g_load[t]}等于管网供热量\\var{g_tube[t]}和地源热泵供热量\\var{g_ghp[t]}的和",
#     "能量平衡约束：调度周期\\param{period}内各时段系统的冷负荷\\param{q_load[t]}等于热泵产冷量\\var{q_hp[t]}、地源热泵产冷量\\var{q_ghp[t]}与冷水箱（蓄水箱储冷时）供冷量\\var{q_ct[t]}的和",
#     "能量平衡约束：调度周期\\param{period}内各时段储氢罐储氢变化量\\var{delta_h_hst[t]}等于从氢气市场购氢量\\var{h_pur[t]}与电解槽产氢量\\var{h_el[t]}的和减去氢燃料电池耗氢量\\var{h_fc[t]}",
#     "其他约束："
#   ],
#   "目标函数": "最小化所有设备年化投资费用和系统运行费用之和，其中各设备的年化投资费用由设备单价、设备容量和设备寿命计算，系统运行费用包括买电费用和买氢费用减去向电网卖电收入",
#   "参数": [
#     {
#       "参数集信息": "负荷信息",
#       "具体内容": "包括建筑类型、电负荷峰值、热负荷峰值、冷负荷峰值、供热月份、供冷月份、供电面积、供热面积、供冷面积、电负荷、热负荷、冷负荷等",
#       "符号": [
#         "building_type",
#         "p_max",
#         "g_max",
#         "q_max",
#         "g_month",
#         "q_month",
#         "p_area",
#         "g_area",
#         "q_area",
#         "p_load",
#         "g_load",
#         "q_load"
#       ]
#     },
#     {
#       "参数集信息": "太阳辐射信息",
#       "具体内容": "包括太阳辐射强度",
#       "符号": [
#         "r_solar"
#       ]
#     },
#     {
#       "参数集信息": "能源价格信息",
#       "具体内容": "包括分时电价、向电网卖电价格、氢气价格",
#       "符号": [
#         "p_price",
#         "p_sell_price",
#         "h_price"
#       ]
#     },
#     {
#       "参数集信息": "光伏板信息",
#       "具体内容": "包括光伏板装机上限、光伏板装机下限、光伏板单价、光伏板寿命、光伏板产电效率",
#       "符号": [
#         "s_pv_max",
#         "s_pv_min",
#         "cost_pv",
#         "life_pv",
#         "k_pv"
#       ]
#     },
#     {
#       "参数集信息": "太阳能集热器信息",
#       "具体内容": "包括太阳能集热器装机上限、太阳能集热器装机下限、太阳能集热器单价、太阳能集热器寿命、太阳能集热器产热效率",
#       "符号": [
#         "s_sc_max",
#         "s_sc_min",
#         "cost_sc",
#         "life_sc",
#         "k_sc"
#       ]
#     },
#     {
#       "参数集信息": "氢燃料电池信息",
#       "具体内容": "包括氢燃料电池装机上限、氢燃料电池装机下限、氢燃料电池单价、氢燃料电池寿命、氢燃料电池产电效率、氢燃料电池产热效率、热交换效率",
#       "符号": [
#         "p_fc_max",
#         "p_fc_min",
#         "cost_fc",
#         "life_fc",
#         "k_fc_p",
#         "k_fc_g",
#         "eta_ex"
#       ]
#     },
#     {
#       "参数集信息": "电解槽信息",
#       "具体内容": "包括电解槽装机上限、电解槽装机下限、电解槽单价、电解槽寿命、电解槽产氢效率",
#       "符号": [
#         "p_el_max",
#         "p_el_min",
#         "cost_el",
#         "life_el",
#         "k_el"
#       ]
#     },
#     {
#       "参数集信息": "电锅炉信息",
#       "具体内容": "包括电锅炉装机上限、电锅炉装机下限、电锅炉单价、电锅炉寿命、电锅炉产热效率",
#       "符号": [
#         "p_eb_max",
#         "p_eb_min",
#         "cost_eb",
#         "life_eb",
#         "k_eb"
#       ]
#     },
#     {
#       "参数集信息": "热泵信息",
#       "具体内容": "包括热泵装机上限、热泵装机下限、热泵单价、热泵寿命、热泵产热效率、热泵产冷效率",
#       "符号": [
#         "p_hp_max",
#         "p_hp_min",
#         "cost_hp",
#         "life_hp",
#         "k_hp_g",
#         "k_hp_q"
#       ]
#     },
#     {
#       "参数集信息": "地源热泵信息",
#       "具体内容": "包括地源热泵装机上限、地源热泵装机下限、地源热泵单价、地源热泵寿命、地源热泵产热效率、地源热泵产冷效率",
#       "符号": [
#         "p_ghp_max",
#         "p_ghp_min",
#         "cost_ghp",
#         "life_ghp",
#         "k_ghp_g",
#         "k_ghp_q"
#       ]
#     },
#     {
#       "参数集信息": "地热井信息",
#       "具体内容": "包括地热井装机数量上限、地热井装机数量下限、地热井单价、地热井寿命、地热井可产热量",
#       "符号": [
#         "num_gtw_max",
#         "num_gtw_min",
#         "cost_gtw",
#         "life_gtw",
#         "g_gtw"
#       ]
#     },
#     {
#       "参数集信息": "储氢罐信息",
#       "具体内容": "包括储氢罐装机上限、储氢罐装机下限、储氢罐单价、储氢罐寿命",
#       "符号": [
#         "h_hst_max",
#         "h_hst_min",
#         "cost_hst",
#         "life_hst"
#       ]
#     },
#     {
#       "参数集信息": "蓄水箱信息",
#       "具体内容": "包括蓄水箱装机上限、蓄水箱装机下限、蓄水箱单价、蓄水箱寿命、热水箱水温上限、热水箱水温下限、冷水箱水温上限、冷水箱水温下限、蓄水箱热损失系数",
#       "符号": [
#         "m_tank_max",
#         "m_tank_min",
#         "cost_tank",
#         "life_tank",
#         "t_ht_max",
#         "t_ht_min",
#         "t_ct_max",
#         "t_ct_min",
#         "mu_tank_loss"
#       ]
#     },
#     {
#       "参数集信息": "其他信息",
#       "具体内容": "包括调度周期、电网排放因子",
#       "符号": [
#         "period",
#         "alpha_e"
#       ]
#     }
#   ],
#   "变量": [
#     {
#       "变量集信息": "系统运行费用变量",
#       "具体内容": "包括买电费用、买氢费用、向电网卖电收入",
#       "符号": [
#         "p_pur",
#         "h_pur",
#         "p_sell"
#       ]
#     },
#     {
#       "变量集信息": "光伏板规划与运行变量",
#       "具体内容": "包括光伏板装机容量、光伏板产电量",
#       "符号": [
#         "s_pv_inst",
#         "p_pv"
#       ]
#     },
#     {
#       "变量集信息": "太阳能集热器规划与运行变量",
#       "具体内容": "包括太阳能集热器装机容量、太阳能集热器产热量",
#       "符号": [
#         "s_sc_inst",
#         "g_sc"
#       ]
#     },
#     {
#       "变量集信息": "氢燃料电池规划与运行变量",
#       "具体内容": "包括氢燃料电池装机容量、氢燃料电池耗氢量、氢燃料电池产电量、氢燃料电池产热量",
#       "符号": [
#         "p_fc_inst",
#         "h_fc",
#         "p_fc",
#         "g_fc"
#       ]
#     },
#     {
#       "变量集信息": "电解槽规划与运行变量",
#       "具体内容": "包括电解槽装机容量、电解槽产氢量、电解槽耗电量",
#       "符号": [
#         "p_el_inst",
#         "h_el",
#         "p_el"
#       ]
#     },
#     {
#       "变量集信息": "电锅炉规划与运行变量",
#       "具体内容": "包括电锅炉装机容量、电锅炉产热量、电锅炉耗电量",
#       "符号": [
#         "p_eb_inst",
#         "g_eb",
#         "p_eb"
#       ]
#     },
#     {
#       "变量集信息": "热泵规划与运行变量",
#       "具体内容": "包括热泵装机容量、热泵产热量、热泵产冷量、热泵耗电量",
#       "符号": [
#         "p_hp_inst",
#         "g_hp",
#         "q_hp",
#         "p_hp"
#       ]
#     },
#     {
#       "变量集信息": "地源热泵规划与运行变量",
#       "具体内容": "包括地源热泵装机容量、地源热泵产热量、地源热泵产冷量、地源热泵耗电量、地源热泵向地热井灌热量",
#       "符号": [
#         "p_ghp_inst",
#         "g_ghp",
#         "q_ghp",
#         "p_ghp",
#         "g_ghp_inj"
#       ]
#     },
#     {
#       "变量集信息": "地热井规划与运行变量",
#       "具体内容": "包括地热井装机数量",
#       "符号": [
#         "num_gtw_inst"
#       ]
#     },
#     {
#       "变量集信息": "储氢罐规划与运行变量",
#       "具体内容": "包括储氢罐装机容量、储氢罐储氢量、储氢罐储氢变化量",
#       "符号": [
#         "h_hst_inst",
#         "h_hst",
#         "delta_h_hst"
#       ]
#     },
#     {
#       "变量集信息": "蓄水箱规划与运行变量",
#       "具体内容": "包括蓄水箱装机容量、热水箱水温、热水箱储热量、热水箱储热变化量、热水箱热损失量、冷水箱水温、冷水箱储冷量、冷水箱储冷变化量",
#       "符号": [
#         "m_tank_inst",
#         "t_ht",
#         "g_ht",
#         "delta_g_ht",
#         "g_ht_loss",
#         "t_ct",
#         "q_ct",
#         "delta_q_ct"
#       ]
#     },
#     {
#       "变量集信息": "管网规划与运行变量",
#       "具体内容": "包括管网供热量",
#       "符号": [
#         "g_tube"
#       ]
#     }
#   ]
# }
# with open("test_json.json", "w", encoding="utf-8") as f:
#     json.dump(data, f, indent=4, ensure_ascii=False)
