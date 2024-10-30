# info_prompt的示例输入和输出
example_user_input = {
    "项目描述": "本项目为榆林科创新城零碳分布式智慧能源中心示范项目，为运动员村进行供冷、供热以及供电服务。运动员村项目包括酒店、运动 员餐厅、办公、教育、住宅、公寓、体育等建筑。项目建设用地面积93347.47 m2，总建筑面积20.6万m2，地上建筑面积14万m2，其中住宅5.6万m2，办公4.9 万m2，酒店及运动员餐厅2.1万m2，健身中心0.5万m2，配套0.9万m2。由于DK1-13#楼酒店及运动员餐厅仅大堂地暖需能源站供应，实际供能面积约为12万m2。",
    "项目地理位置": "陕西省榆林市",
    "土地使用情况": "供能面积约为12万m2",
    "项目供能对象描述": "为运动员村进行供冷、供热以及供电服务",
    "项目预期描述": "最大化系统经济型，实现零碳供应能量，设备包括光伏板（pv）、太阳能集热器（sc）、氢燃料电池（fc）、电解槽（el）、电锅炉（eb）、热泵（hp）、地源热泵（ghp）、地热井（gtw）、储氢罐（hst）、蓄水箱（tank）以及其他必要装置设备。"
}
example_info_output = {
    "背景知识": "构建能源系统规划问题，在满足设备运行约束、能量平衡约束和其他附加约束的前提下，构建经济最优目标函数，计算得到设备容量和全年运行数据",
    "约束条件": [
        "设备容量约束：光伏板装机容量\\var{s_pv_inst}不得大于其装机上限\\param{s_pv_max}",
        "设备容量约束：太阳能集热器装机容量\\var{s_sc_inst}不得大于其装机上限\\param{s_sc_max}",
        "设备容量约束：氢燃料电池装机容量\\var{p_fc_inst}不得大于其装机上限\\param{p_fc_max}",
        "设备容量约束：电解槽装机容量\\var{p_el_inst}不得大于其装机上限\\param{p_el_max}",
        "设备容量约束：电锅炉装机容量\\var{p_eb_inst}不得大于其装机上限\\param{p_eb_max}",
        "设备容量约束：热泵装机容量\\var{p_hp_inst}不得大于其装机上限\\param{p_hp_max}",
        "设备容量约束：地源热泵装机容量\\var{p_ghp_inst}不得大于其装机上限\\param{p_ghp_max}",
        "设备容量约束：储氢罐装机容量\\var{h_hst_inst}不得大于其装机上限\\param{h_hst_max}",
        "设备容量约束：蓄水箱装机容量\\var{m_tank_inst}不得大于其装机上限\\param{m_tank_max}",
        "设备运行约束：调度周期\\param{period}内各时段光伏板产电量\\var{p_pv[t]}不得大于其产电效率\\param{k_pv}、太阳辐射强度\\param{r_solar[t]}和其装机容量\\var{s_pv_inst}的乘积",
        "设备运行约束：调度周期\\param{period}内各时段太阳能集热器产热量\\var{g_sc[t]}不得大于其产热效率\\param{k_sc}、太阳辐射强度\\param{r_solar[t]}和其装机容量\\var{s_sc_inst}的乘积",
        "设备运行约束：调度周期\\param{period}内各时段氢燃料电池产电量\\var{p_fc[t]}等于其产电效率\\param{k_fc_p}和其耗氢量\\var{h_fc[t]}的乘积",
        "设备运行约束：调度周期\\param{period}内各时段氢燃料电池产热量\\var{g_fc[t]}等于其热交换效率\\param{eta_ex}、其产热效率\\param{k_fc_g}和其耗氢量\\var{h_fc[t]}的乘积",
        "设备运行约束：调度周期\\param{period}内各时段氢燃料电池产电量\\var{p_fc[t]}不得大于其装机容量\\var{p_fc_inst}",
        "设备运行约束：调度周期\\param{period}内各时段电解槽产氢量\\var{h_el[t]}不得大于其产氢效率\\param{k_el}和其耗电量\\var{p_el[t]}的乘积",
        "设备运行约束：调度周期\\param{period}内各时段电解槽耗电量\\var{p_el[t]}不得大于其装机容量\\var{p_el_inst}",
        "设备运行约束：调度周期\\param{period}内各时段电锅炉产热量\\var{g_eb[t]}等于其产热效率\\param{k_eb}和其耗电量\\var{p_eb[t]}的乘积",
        "设备运行约束：调度周期\\param{period}内各时段电锅炉耗电量\\var{p_eb[t]}不得大于其装机容量\\var{p_eb_inst}",
        "设备运行约束：调度周期\\param{period}内各时段热泵产热量\\var{g_hp[t]}不得大于其产热效率\\param{k_hp_g}和其耗电量\\var{p_hp[t]}的乘积",
        "设备运行约束：调度周期\\param{period}内各时段热泵产冷量\\var{q_hp[t]}不得大于其产冷效率\\param{k_hp_q}和其耗电量\\var{p_hp[t]}的乘积",
        "设备运行约束：调度周期\\param{period}内各时段热泵耗电量\\var{p_hp[t]}不得大于其装机容量\\var{p_hp_inst}",
        "设备运行约束：调度周期\\param{period}内各时段地源热泵产热量\\var{g_ghp[t]}不得大于其产热效率\\param{k_ghp_g}和其耗电量\\var{p_ghp[t]}的乘积",
        "设备运行约束：调度周期\\param{period}内各时段地源热泵产冷量\\var{q_ghp[t]}不得大于其产冷效率\\param{k_ghp_q}和其耗电量\\var{p_ghp[t]}的乘积",
        "设备运行约束：调度周期\\param{period}内各时段地源热泵耗电量\\var{p_ghp[t]}不得大于其装机容量\\var{p_ghp_inst}",
        "设备运行约束：地缘热泵可以从所有地热井中取得的热量最大值（地热井装机数量\\var{num_gtw_inst} * 地热井可产热量\\param{g_gtw}）不得小于地源热泵最大产热量（地源热泵装机容量\\var{p_ghp_inst} * 其产热效率\\param{k_ghp_g}）",
        "设备运行约束：调度周期\\param{period}内各时段储氢罐储氢量\\var{h_hst[t]}不得大于其装机容量\\var{h_hst_inst}",
        "设备运行约束：调度周期\\param{period}内各时段热水箱（蓄水箱储热时）供热量\\var{g_ht[t]}等于热水箱储热变化量\\var{delta_g_ht[t]}的负值减去其热损失量\\var{g_ht_loss[t]}",
        "设备运行约束：调度周期\\param{period}内各时段热水箱热损失量\\var{g_ht_loss[t]}等于热损失系数\\param{mu_tank_loss}、水的比热 c_water、水箱中水的质量\\var{m_tank_inst}和当前时刻水箱水温\\var{t_ht[t]}与环境温度（最低水温）\\param{t_ht_min}的差值的乘积",
        "设备运行约束：调度周期\\param{period}内各时段冷水箱（蓄水箱储冷时）供冷量\\var{q_ct[t]}等于冷水箱储冷变化量\\var{delta_q_ct[t]}的负值，其冷损失量忽略不计",
        "设备运行约束：调度周期\\param{period}内各时段管网供热量\\var{g_tube[t]}等于太阳能集热器产热量\\var{g_sc[t]}、氢燃料电池产热量\\var{g_fc[t]}、电锅炉产热量\\var{g_eb[t]}、热泵产热量\\var{g_hp[t]}和热水箱（蓄水箱储热时）供热量\\var{g_ht[t]}的和减去地源热泵向地热井灌热量\\var{g_ghp_inj[t]}",
        "设备运行约束：除最后一个时段外，调度周期\\param{period}内各时段储氢罐储氢变化量\\var{delta_h_hst[t]}等于下一时刻储氢罐储氢量\\var{h_hst[t+1]}减去当前时刻储氢罐储氢量\\var{h_hst[t]}",
        "设备运行约束：除最后一个时段外，调度周期\\param{period}内各时段热水箱储热变化量\\var{delta_g_ht[t]}等于水的比热 c_water、水箱中水的质量\\var{m_tank_inst}和水箱中水温变化量（下一时刻水温\\var{t_ht[t+1]减去当前时刻水温\\var{t_ht[t]}）的乘积",
        "设备运行约束：除最后一个时段外，调度周期\\param{period}内各时段冷水箱储冷变化量\\var{delta_q_ct[t]}等于水的比热 c_water、水箱中水的质量\\var{m_tank_inst}和水箱中水温变化量（下一时刻水温\\var{t_ct[t+1]减去当前时刻水温\\var{t_ct[t]}）的乘积的负值",
        "设备运行约束：最后一个时段储氢罐储氢变化量\\var{delta_h_hst[-1]}等于初始时刻储氢罐储氢量\\var{h_hst[0]}减去当前时刻储氢罐储氢量\\var{h_hst[-1]}，以保证调度周期结束时储氢罐储氢量与初始时刻储氢量一致",
        "设备运行约束：最后一个时段热水箱储热变化量\\var{delta_g_ht[-1]}等于水的比热 c_water、水箱中水的质量\\var{m_tank_inst}和水箱中水温变化量（初始时刻水温\\var{t_ht[0]减去当前时刻水温\\var{t_ht[-1]}）的乘积，以保证调度周期结束时热水箱储热量与初始时刻储热量一致",
        "设备运行约束：最后一个时段冷水箱储冷变化量\\var{delta_q_ct[-1]}等于水的比热 c_water、水箱中水的质量\\var{m_tank_inst}和水箱中水温变化量（初始时刻水温\\var{t_ct[0]减去当前时刻水温\\var{t_ct[-1]}）的乘积的负值，以保证调度周期结束时冷水箱储冷量与初始时刻储冷量一致",
        "能量平衡约束：调度周期\\param{period}内各时段系统的电力供应（包括从电网购电量\\var{p_pur[t]}、光伏产电量\\var{p_pv[t]}和氢燃料电池产电量\\var{p_fc[t]}）减去向电网卖电量\\var{p_sell[t]}应等于电力需求（包括电负载\\param{p_load[t]}、电解槽耗电量\\var{p_el[t]}、电锅炉耗电量\\var{p_eb[t]}、热泵耗电量\\var{p_hp[t]}和地源热泵耗电量\\var{p_ghp[t]}）",
        "能量平衡约束：调度周期\\param{period}内各时段系统的热负荷\\param{g_load[t]}等于管网供热量\\var{g_tube[t]}和地源热泵供热量\\var{g_ghp[t]}的和",
        "能量平衡约束：调度周期\\param{period}内各时段系统的冷负荷\\param{q_load[t]}等于热泵产冷量\\var{q_hp[t]}、地源热泵产冷量\\var{q_ghp[t]}与冷水箱（蓄水箱储冷时）供冷量\\var{q_ct[t]}的和",
        "能量平衡约束：调度周期\\param{period}内各时段储氢罐储氢变化量\\var{delta_h_hst[t]}等于从氢气市场购氢量\\var{h_pur[t]}与电解槽产氢量\\var{h_el[t]}的和减去氢燃料电池耗氢量\\var{h_fc[t]}",
        "其他约束："
    ],
    "目标函数": "最小化所有设备年化投资费用和系统运行费用之和，其中各设备的年化投资费用由设备单价、设备容量和设备寿命计算，系统运行费用包括买电费用和买氢费用减去向电网卖电收入",
    "参数": [
        {
            "参数集信息": "负荷信息",
            "具体内容": "包括建筑类型、电负荷峰值、热负荷峰值、冷负荷峰值、供热月份、供冷月份、供电面积、供热面积、供冷面积、电负荷、热负荷、冷负荷等",
            "符号": ["building_type", "p_max", "g_max", "q_max", "g_month", "q_month", "p_area", "g_area", "q_area", "p_load", "g_load", "q_load"]
        },
        {
            "参数集信息": "太阳辐射信息",
            "具体内容": "包括太阳辐射强度",
            "符号": ["r_solar"]
        },
        {
            "参数集信息": "能源价格信息",
            "具体内容": "包括分时电价、向电网卖电价格、氢气价格",
            "符号": ["p_price", "p_sell_price", "h_price"]
        },
        {
            "参数集信息": "光伏板信息",
            "具体内容": "包括光伏板装机上限、光伏板装机下限、光伏板单价、光伏板寿命、光伏板产电效率",
            "符号": ["s_pv_max", "s_pv_min", "cost_pv", "life_pv", "k_pv"]
        },
        {
            "参数集信息": "太阳能集热器信息",
            "具体内容": "包括太阳能集热器装机上限、太阳能集热器装机下限、太阳能集热器单价、太阳能集热器寿命、太阳能集热器产热效率",
            "符号": ["s_sc_max", "s_sc_min", "cost_sc", "life_sc", "k_sc"]
        },
        {
            "参数集信息": "氢燃料电池信息",
            "具体内容": "包括氢燃料电池装机上限、氢燃料电池装机下限、氢燃料电池单价、氢燃料电池寿命、氢燃料电池产电效率、氢燃料电池产热效率、热交换效率",
            "符号": ["p_fc_max", "p_fc_min", "cost_fc", "life_fc", "k_fc_p", "k_fc_g", "eta_ex"]
        },
        {
            "参数集信息": "电解槽信息",
            "具体内容": "包括电解槽装机上限、电解槽装机下限、电解槽单价、电解槽寿命、电解槽产氢效率",
            "符号": ["p_el_max", "p_el_min", "cost_el", "life_el", "k_el"]
        },
        {
            "参数集信息": "电锅炉信息",
            "具体内容": "包括电锅炉装机上限、电锅炉装机下限、电锅炉单价、电锅炉寿命、电锅炉产热效率",
            "符号": ["p_eb_max", "p_eb_min", "cost_eb", "life_eb", "k_eb"]
        },
        {
            "参数集信息": "热泵信息",
            "具体内容": "包括热泵装机上限、热泵装机下限、热泵单价、热泵寿命、热泵产热效率、热泵产冷效率",
            "符号": ["p_hp_max", "p_hp_min", "cost_hp", "life_hp", "k_hp_g", "k_hp_q"]
        },
        {
            "参数集信息": "地源热泵信息",
            "具体内容": "包括地源热泵装机上限、地源热泵装机下限、地源热泵单价、地源热泵寿命、地源热泵产热效率、地源热泵产冷效率",
            "符号": ["p_ghp_max", "p_ghp_min", "cost_ghp", "life_ghp", "k_ghp_g", "k_ghp_q"]
        },
        {
            "参数集信息": "地热井信息",
            "具体内容": "包括地热井装机数量上限、地热井装机数量下限、地热井单价、地热井寿命、地热井可产热量",
            "符号": ["num_gtw_max", "num_gtw_min", "cost_gtw", "life_gtw", "g_gtw"]
        },
        {
            "参数集信息": "储氢罐信息",
            "具体内容": "包括储氢罐装机上限、储氢罐装机下限、储氢罐单价、储氢罐寿命",
            "符号": ["h_hst_max", "h_hst_min", "cost_hst", "life_hst"]
        },
        {
            "参数集信息": "蓄水箱信息",
            "具体内容": "包括蓄水箱装机上限、蓄水箱装机下限、蓄水箱单价、蓄水箱寿命、热水箱水温上限、热水箱水温下限、冷水箱水温上限、冷水箱水温下限、蓄水箱热损失系数",
            "符号": ["m_tank_max", "m_tank_min", "cost_tank", "life_tank", "t_ht_max", "t_ht_min", "t_ct_max", "t_ct_min", "mu_tank_loss"]
        },
        {
            "参数集信息": "其他信息",
            "具体内容": "包括调度周期、电网排放因子",
            "符号": ["period", "alpha_e"]
        }
    ],
    "变量": [
        {
            "变量集信息": "系统运行费用变量",
            "具体内容": "包括买电费用、买氢费用、向电网卖电收入",
            "符号": ["p_pur", "h_pur", "p_sell"]
        },
        {
            "变量集信息": "光伏板规划与运行变量",
            "具体内容": "包括光伏板装机容量、光伏板产电量",
            "符号": ["s_pv_inst", "p_pv"]
        },
        {
            "变量集信息": "太阳能集热器规划与运行变量",
            "具体内容": "包括太阳能集热器装机容量、太阳能集热器产热量",
            "符号": ["s_sc_inst", "g_sc"]
        },
        {
            "变量集信息": "氢燃料电池规划与运行变量",
            "具体内容": "包括氢燃料电池装机容量、氢燃料电池耗氢量、氢燃料电池产电量、氢燃料电池产热量",
            "符号": ["p_fc_inst", "h_fc", "p_fc", "g_fc"]
        },
        {
            "变量集信息": "电解槽规划与运行变量",
            "具体内容": "包括电解槽装机容量、电解槽产氢量、电解槽耗电量",
            "符号": ["p_el_inst", "h_el", "p_el"]
        },
        {
            "变量集信息": "电锅炉规划与运行变量",
            "具体内容": "包括电锅炉装机容量、电锅炉产热量、电锅炉耗电量",
            "符号": ["p_eb_inst", "g_eb", "p_eb"]
        },
        {
            "变量集信息": "热泵规划与运行变量",
            "具体内容": "包括热泵装机容量、热泵产热量、热泵产冷量、热泵耗电量",
            "符号": ["p_hp_inst", "g_hp", "q_hp", "p_hp"]
        },
        {
            "变量集信息": "地源热泵规划与运行变量",
            "具体内容": "包括地源热泵装机容量、地源热泵产热量、地源热泵产冷量、地源热泵耗电量、地源热泵向地热井灌热量",
            "符号": ["p_ghp_inst", "g_ghp", "q_ghp", "p_ghp", "g_ghp_inj"]
        },
        {
            "变量集信息": "地热井规划与运行变量",
            "具体内容": "包括地热井装机数量",
            "符号": ["num_gtw_inst"]
        },
        {
            "变量集信息": "储氢罐规划与运行变量",
            "具体内容": "包括储氢罐装机容量、储氢罐储氢量、储氢罐储氢变化量",
            "符号": ["h_hst_inst", "h_hst", "delta_h_hst"]
        },
        {
            "变量集信息": "蓄水箱规划与运行变量",
            "具体内容": "包括蓄水箱装机容量、热水箱水温、热水箱储热量、热水箱储热变化量、热水箱热损失量、冷水箱水温、冷水箱储冷量、冷水箱储冷变化量",
            "符号": ["m_tank_inst", "t_ht", "g_ht", "delta_g_ht", "g_ht_loss", "t_ct", "q_ct", "delta_q_ct"]
        },
        {
            "变量集信息": "管网规划与运行变量",
            "具体内容": "包括管网供热量",
            "符号": ["g_tube"]
        }
    ]
}

# param_prompt的示例输入和输出
# example_param_info_input = {"参数": example_info_output["参数"]}
example_info_input = example_info_output
example_param_output = {
    "load": {
        "building_type": "Hotel",
        "p_max": 300,
        "g_max": 1000,
        "q_max": 200,
        "g_month": [11, 12, 1, 2, 3],
        "q_month": [6, 7, 8],
        "p_area": 123967.0,
        "g_area": 43967.0,
        "q_area": 123967.0
    },
    "price": {
        "TOU_power": [
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515,
            0.515
        ],
        "p_sell_price": 0,
        "g_price": 5.4,
        "q_price": 9.5,
        "h_price": 17.92
    },
    "device": {
        "pv": {
            "_comment": "photovoltaic，光伏板",
            "area_max": 50000,
            "area_min": 0,
            "cost": 700,
            "life": 20,
            "k_pv": 0.21
        },
        "sc": {
            "_comment": "solar collector，太阳能集热器",
            "area_max": 0,
            "area_min": 0,
            "cost": 800,
            "life": 20,
            "k_sc": 0.72
        },
        "fc": {
            "_comment": "fuel cell，氢燃料电池",
            "p_max": 10000,
            "p_min": 0,
            "cost": 8000,
            "life": 10,
            "k_fc_p": 15,
            "k_fc_g": 22,
            "eta_ex": 0.95
        },
        "el": {
            "_comment": "electrolyzer，电解槽",
            "p_max": 1000,
            "p_min": 0,
            "cost": 2240,
            "life": 7,
            "k_el": 0.0182
        },
        "eb": {
            "_comment": "electric boiler，电锅炉",
            "p_max": 10000,
            "p_min": 0,
            "cost": 500,
            "life": 10,
            "k_eb": 0.9
        },
        "hp": {
            "_comment": "heat pump，热泵",
            "p_max": 1000,
            "p_min": 0,
            "cost": 68000,
            "life": 15,
            "k_hp_g": 4.59,
            "k_hp_q": 0
        },
        "ghp": {
            "_comment": "ground source heat pump，地源热泵",
            "p_max": 1000,
            "p_min": 0,
            "cost": 3000,
            "life": 15,
            "k_ghp_g": 3.54,
            "k_ghp_q": 4.5
        },
        "gtw": {
            "_comment": "ground thermal well，地热井",
            "number_max": 2680,
            "cost": 20000,
            "life": 30,
            "g_gtw": 7
        },
        "hst": {
            "_comment": "hydrogen storage tank，储氢罐",
            "h_max": 2000,
            "h_min": 0,
            "cost": 3000,
            "life": 15
        },
        "tank": {
            "_comment": "water tank，蓄水箱，用于储热（此时为热水箱（ht））或储冷（此时为冷水箱（ct））",
            "m_max": 10000,
            "m_min": 0,
            "cost": 0.5,
            "life": 20,
            "t_ht_max": 80,
            "t_ht_min": 20,
            "t_ct_max": 13,
            "t_ct_min": 4,
            "mu_loss": 0.001
        }
    },
    "carbon": {
        "alpha_h2": 1.74,
        "alpha_e": 0.5839,
        "alpha_EO": 0.8922,
        "alpha_gas": 1.535
    }
}

# code_prompt的示例输入和输出
example_param_input = example_param_output
example_code_output = """
def planning_problem(period_data, input_param):
    \"\"\"规划问题求解

    Args:
        period_data (dict): 各时段数据，包括光照强度、电负荷、热负荷、冷负荷
        input_param (dict): 输入参数，包括碳排放因子、能源价格、设备价格、设备效率等
    \"\"\"
    # 常数
    c_water = 4.2 / 3600  # 水的比热容
    M = 1e7  # 大 M

    # ------ Create model ------
    model = gp.Model("OptModel")

    # ------ Parameters input ------
    # 参数输入，时序数据包括电、热、冷、光照强度等；单一数据包括碳排放因子、能源价格、设备价格、设备效率等
    # --- 各时段数据 ---
    p_load = period_data["p_load"]*input_param["load"]["p_area"]  # 电负荷乘以面积
    g_load = period_data["g_load"]*input_param["load"]["g_area"]  # 热负荷乘以面积
    q_load = period_data["q_load"]*input_param["load"]["q_area"]  # 冷负荷乘以面积
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
    # 热泵
    p_hp_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["hp"]["p_max"], name=f"p_hp_inst")  # 热泵装机容量
    p_hp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_hp{t}") for t in range(period)]  # 热泵耗电量
    g_hp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_hp{t}") for t in range(period)]  # 热泵产热量
    q_hp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"q_hp{t}") for t in range(period)]  # 热泵产冷量
    # 地源热泵
    p_ghp_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["ghp"]["p_max"], name=f"p_ghp_inst")  # 地源热泵装机容量
    p_ghp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_ghp{t}") for t in range(period)]  # 地源热泵耗电量
    g_ghp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_ghp{t}") for t in range(period)]  # 地源热泵产热量
    g_ghp_inj = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_ghp_inj{t}") for t in range(period)]  # 地源热泵灌热量
    q_ghp = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"q_ghp{t}") for t in range(period)]  # 地源热泵产冷量
    # 地热井
    num_gtw_inst = model.addVar(vtype=GRB.INTEGER, lb=0, ub=input_param["device"]["gtw"]["number_max"], name="num_gtw_inst")  # 地热井装机数量
    # 储氢罐
    h_hst_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["hst"]["h_max"], name=f"h_hst_inst")  # 储氢罐装机容量
    h_hst = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_hst{t}") for t in range(period)]  # 储氢罐储氢量
    delta_h_hst = [model.addVar(vtype=GRB.CONTINUOUS, lb=-M, name=f"delta_h_hst{t}") for t in range(period)]  # 储氢罐储氢变化量
    # 蓄水箱
    m_tank_inst = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=input_param["device"]["tank"]["m_max"], name=f"m_tank_inst")  # 蓄水箱装机容量
    t_ht = [model.addVar(vtype=GRB.CONTINUOUS, lb=input_param["device"]["tank"]["t_ht_min"], ub=input_param["device"]["tank"]["t_ht_max"], name=f"t_ht{t}") for t in range(period)]  # 热水箱水温
    g_ht = [model.addVar(vtype=GRB.CONTINUOUS, lb=-M, name=f"g_ht{t}") for t in range(period)]  # 热水箱供热量
    delta_g_ht = [model.addVar(vtype=GRB.CONTINUOUS, lb=-M, name=f"delta_g_ht{t}") for t in range(period)]  # 热水箱储热变化量
    g_ht_loss = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_ht_loss{t}") for t in range(period)]  # 热水箱热损失量
    t_ct = [model.addVar(vtype=GRB.CONTINUOUS, lb=input_param["device"]["tank"]["t_ct_min"], ub=input_param["device"]["tank"]["t_ct_min"], name=f"t_ct{t}") for t in range(period)]  # 冷水箱水温
    q_ct = [model.addVar(vtype=GRB.CONTINUOUS, lb=-M, name=f"q_ct{t}") for t in range(period)]  # 冷水箱供冷量
    delta_q_ct = [model.addVar(vtype=GRB.CONTINUOUS, lb=-M, name=f"delta_q_ct{t}") for t in range(period)]  # 冷水箱储冷变化量
    # 管网
    g_tube = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_tube{t}") for t in range(period)]  # 管网供热量

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
        # 管网
        model.addConstr(g_tube[t] == g_sc[t] + g_fc[t] + g_eb[t] + g_hp[t] + g_ht[t] - g_ghp_inj[t])  # 管网供热量
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
        model.addConstr(p_pur[t] + p_pv[t] + p_fc[t] - p_sell[t] == p_load[t] + p_el[t] + p_eb[t] + p_hp[t] + p_ghp[t])  # 电平衡约束
        # g_load 为 numpy 数组，不能单独放在约束的左侧；q_load 同理
        model.addConstr(g_tube[t] + g_ghp[t] == g_load[t])  # 热平衡约束
        model.addConstr(q_hp[t] + q_ghp[t] + q_ct[t] == q_load[t])  # 冷平衡约束
        model.addConstr(h_pur[t] + h_el[t] - h_fc[t] == delta_h_hst[t])  # 氢平衡约束

    # ------ Objective ------
    capex = (cost_pv * s_pv_inst / input_param["device"]["pv"]["life"]
             + cost_sc * s_sc_inst / input_param["device"]["sc"]["life"]
             + cost_fc * p_fc_inst / input_param["device"]["fc"]["life"]
             + cost_el * p_el_inst / input_param["device"]["el"]["life"]
             + cost_eb * p_eb_inst / input_param["device"]["eb"]["life"]
             + cost_hp * p_hp_inst / input_param["device"]["hp"]["life"]
             + cost_ghp * p_ghp_inst / input_param["device"]["ghp"]["life"]
             + cost_gtw * num_gtw_inst / input_param["device"]["gtw"]["life"]
             + cost_hst * h_hst_inst / input_param["device"]["hst"]["life"]
             + cost_tank * m_tank_inst / input_param["device"]["tank"]["life"])  # 年化投资费用
    opex = (gp.quicksum([p_pur[t] * p_price[t] for t in range(period)])
            - gp.quicksum([p_sell[t] for t in range(period)]) * p_sell_price
            + gp.quicksum([h_pur[t] for t in range(period)]) * h_price)  # 运行费用
    model.setObjective((capex + opex), GRB.MINIMIZE)
"""

if __name__ == "__main__":
    print("=" * 50)
    print("下面是info_prompt的示例：")
    print("example_user_input:\n", example_user_input)
    print("example_info_output:\n", example_info_output)
    print("=" * 50)
    print("下面是param_prompt的示例：")
    print("example_user_input:\n", example_user_input)
    print("example_info_input:\n", example_info_input)
    print("example_param_output:\n", example_param_output)
    print("=" * 50)
    print("下面是code_prompt的示例：")
    print("example_info_input:\n", example_info_input)
    print("example_param_input:\n", example_param_input)
    print("example_code_output:\n", example_code_output)
