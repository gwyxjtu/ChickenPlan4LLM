# -*- coding: utf-8 -*-
import json
from module.LLM import *
from module import get_openai_client, call_openai


user_input = {
    "项目描述": "本项目为榆林科创新城零碳分布式智慧能源中心示范项目，为运动员村进行供冷、供热以及供电服务。运动员村项目包括酒店、运动 员餐厅、办公、教育、住宅、公寓、体育等建筑。项目建设用地面积93347.47 m2，总建筑面积20.6万m2，地上建筑面积14万m2，其中住宅5.6万m2，办公4.9 万m2，酒店及运动员餐厅2.1万m2，健身中心0.5万m2，配套0.9万m2。由于DK1-13#楼酒店及运动员餐厅仅大堂地暖需能源站供应，实际供能面积约为12万m2。",
    "项目地理位置": "陕西省榆林市",
    "土地使用情况": "供能面积约为12万m2",
    "项目供能对象描述": "为运动员村进行供冷、供热以及供电服务",
    "项目预期描述": "最大化系统经济型，实现零碳供应能量，设备包括但不限于光伏、太阳能集热器、氢燃料电池、电解槽、电锅炉、热泵、地源热泵、地热井、储氢罐、蓄水箱。但是燃料电池容量不低于500kW，光伏板的装机容量不超过2000kW，燃料电池的装机容量等于电解槽的装机容量。"
}

# param_info_input = {
#     "参数": [
#         {
#             "参数集信息": "负荷信息",
#             "具体内容": "包括建筑类型、电负荷峰值、热负荷峰值、冷负荷峰值、供热月份、供冷月份、供电面积、供热面积、供冷面积、电负荷、热负荷、冷负荷等",
#             "符号": [
#                 "building_type",
#                 "p_max",
#                 "g_max",
#                 "q_max",
#                 "g_month",
#                 "q_month",
#                 "p_area",
#                 "g_area",
#                 "q_area",
#                 "p_load",
#                 "g_load",
#                 "q_load"
#             ]
#         },
#         {
#             "参数集信息": "太阳辐射信息",
#             "具体内容": "包括太阳辐射强度",
#             "符号": [
#                 "r_solar"
#             ]
#         },
#         {
#             "参数集信息": "能源价格信息",
#             "具体内容": "包括分时电价、向电网卖电价格、氢气价格",
#             "符号": [
#                 "p_price",
#                 "p_sell_price",
#                 "h_price"
#             ]
#         },
#         {
#             "参数集信息": "光伏板信息",
#             "具体内容": "包括光伏板装机上限、光伏板装机下限、光伏板单价、光伏板寿命、光伏板产电效率",
#             "符号": [
#                 "s_pv_max",
#                 "s_pv_min",
#                 "cost_pv",
#                 "life_pv",
#                 "k_pv"
#             ]
#         },
#         {
#             "参数集信息": "太阳能集热器信息",
#             "具体内容": "包括太阳能集热器装机上限、太阳能集热器装机下限、太阳能集热器单价、太阳能集热器寿命、太阳能集热器产热效率",
#             "符号": [
#                 "s_sc_max",
#                 "s_sc_min",
#                 "cost_sc",
#                 "life_sc",
#                 "k_sc"
#             ]
#         },
#         {
#             "参数集信息": "氢燃料电池信息",
#             "具体内容": "包括氢燃料电池装机上限、氢燃料电池装机下限、氢燃料电池单价、氢燃料电池寿命、氢燃料电池产电效率、氢燃料电池产热效率、热交换效率",
#             "符号": [
#                 "p_fc_max",
#                 "p_fc_min",
#                 "cost_fc",
#                 "life_fc",
#                 "k_fc_p",
#                 "k_fc_g",
#                 "eta_ex"
#             ]
#         },
#         {
#             "参数集信息": "电解槽信息",
#             "具体内容": "包括电解槽装机上限、电解槽装机下限、电解槽单价、电解槽寿命、电解槽产氢效率",
#             "符号": [
#                 "p_el_max",
#                 "p_el_min",
#                 "cost_el",
#                 "life_el",
#                 "k_el"
#             ]
#         },
#         {
#             "参数集信息": "电锅炉信息",
#             "具体内容": "包括电锅炉装机上限、电锅炉装机下限、电锅炉单价、电锅炉寿命、电锅炉产热效率",
#             "符号": [
#                 "p_eb_max",
#                 "p_eb_min",
#                 "cost_eb",
#                 "life_eb",
#                 "k_eb"
#             ]
#         },
#         {
#             "参数集信息": "热泵信息",
#             "具体内容": "包括热泵装机上限、热泵装机下限、热泵单价、热泵寿命、热泵产热效率、热泵产冷效率",
#             "符号": [
#                 "p_hp_max",
#                 "p_hp_min",
#                 "cost_hp",
#                 "life_hp",
#                 "k_hp_g",
#                 "k_hp_q"
#             ]
#         },
#         {
#             "参数集信息": "地源热泵信息",
#             "具体内容": "包括地源热泵装机上限、地源热泵装机下限、地源热泵单价、地源热泵寿命、地源热泵产热效率、地源热泵产冷效率",
#             "符号": [
#                 "p_ghp_max",
#                 "p_ghp_min",
#                 "cost_ghp",
#                 "life_ghp",
#                 "k_ghp_g",
#                 "k_ghp_q"
#             ]
#         },
#         {
#             "参数集信息": "地热井信息",
#             "具体内容": "包括地热井装机数量上限、地热井装机数量下限、地热井单价、地热井寿命、地热井可产热量",
#             "符号": [
#                 "num_gtw_max",
#                 "num_gtw_min",
#                 "cost_gtw",
#                 "life_gtw",
#                 "g_gtw"
#             ]
#         },
#         {
#             "参数集信息": "储氢罐信息",
#             "具体内容": "包括储氢罐装机上限、储氢罐装机下限、储氢罐单价、储氢罐寿命",
#             "符号": [
#                 "h_hst_max",
#                 "h_hst_min",
#                 "cost_hst",
#                 "life_hst"
#             ]
#         },
#         {
#             "参数集信息": "蓄水箱信息",
#             "具体内容": "包括蓄水箱装机上限、蓄水箱装机下限、蓄水箱单价、蓄水箱寿命、热水箱水温上限、热水箱水温下限、冷水箱水温上限、冷水箱水温下限、蓄水箱热损失系数",
#             "符号": [
#                 "m_tank_max",
#                 "m_tank_min",
#                 "cost_tank",
#                 "life_tank",
#                 "t_ht_max",
#                 "t_ht_min",
#                 "t_ct_max",
#                 "t_ct_min",
#                 "mu_tank_loss"
#             ]
#         },
#         {
#             "参数集信息": "其他信息",
#             "具体内容": "包括调度周期、电网排放因子",
#             "符号": [
#                 "period",
#                 "alpha_e"
#             ]
#         }
#     ],
# }

if __name__ == '__main__':
    client = get_openai_client("../openai_config.json")

    print("====== Generate info ======")
    info_sys_prompt = info_prompt_template[0]
    info_user_prompt = info_prompt_template[1].format(
        example_user_input=json.dumps(example_user_input, ensure_ascii=False),
        example_output=json.dumps(example_info_output, ensure_ascii=False),
        user_input=json.dumps(user_input, ensure_ascii=False)
    )
    print("prompt:", info_user_prompt, sep="\n")

    response = call_openai(
        client,
        system_prompt=info_sys_prompt,
        user_prompt=info_user_prompt,
        model="gpt-4o",
        max_response_tokens=8192,
        max_tokens=128000,
        temperature=0.3,
    )
    print("=" * 50)
    print("response:", response, sep="\n")

    info_output = json.loads(response)

    print("====== Generate param ======")
    param_info_input = {"参数": info_output["参数"]}
    param_sys_prompt = param_prompt_template[0]
    param_user_prompt = param_prompt_template[1].format(
        example_user_input=json.dumps(example_user_input, ensure_ascii=False),
        example_info_input=json.dumps(example_info_input, ensure_ascii=False),
        example_output=json.dumps(example_param_output, ensure_ascii=False),
        user_input=json.dumps(user_input, ensure_ascii=False),
        param_info_input=json.dumps(param_info_input, ensure_ascii=False)
    )
    print("prompt:", param_user_prompt, sep="\n")

    response = call_openai(
        client,
        system_prompt=param_sys_prompt,
        user_prompt=param_user_prompt,
        model="gpt-4o",
        max_response_tokens=8192,
        max_tokens=128000,
        temperature=0.3,
    )
    print("=" * 50)
    print("response:", response, sep="\n")

    param_output = json.loads(response)

    print("====== Generate code ======")
    info_input = info_output
    param_input = param_output
    code_sys_prompt = code_prompt_template[0]
    code_user_prompt = code_prompt_template[1].format(
        solver="gurobipy",
        example_info_input=json.dumps(example_info_input, ensure_ascii=False),
        example_param_input=json.dumps(example_param_input, ensure_ascii=False),
        example_output=example_code_output,
        info_input=json.dumps(info_input, ensure_ascii=False),
        param_input=json.dumps(param_input, ensure_ascii=False)
    )
    print("prompt:", code_user_prompt, sep="\n")
    response = call_openai(
        client,
        system_prompt=code_sys_prompt,
        user_prompt=code_user_prompt,
        model="gpt-4o",
        max_response_tokens=8192,
        max_tokens=128000,
        temperature=0.3,
    )
    print("=" * 50)
    print("response:", response, sep="\n")
