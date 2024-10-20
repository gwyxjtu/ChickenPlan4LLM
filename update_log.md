## 问题

删除 isolate_flag

删除 hp1, hp2, hyd, xb, whp(余热热泵), bs 等设备

冷水箱设备建模？是否和热水箱共用？

保留 max 变量，存疑



## 设备参数

|              | 参数      |     | 含义                              |
| ------------ | --------- |-----| --------------------------------- |
| 碳排放因子   | alpha_e   |     | 电网排放因子                      |
|              | alpha_gas |     | 天然气排放因子                    |
|              | alpha_h2  |     | 氢排放因子                        |
|              | alpha_EO  |     | 减排项目基准排放                  |
| 能源价格     | ele_price |     | （分时）电价                      |
|              | discount  |     | 折扣                              |
|              | ele_sell  |     | 卖电价格                          |
|              | h_price   |     | 买氢价格                          |
|              | cer       |     | 碳减排率（ Carbon Emission Rate） |
|              | gas_price |     |                                   |
| 未知         | **s_sum** |     | pv_sc_max                         |
| 设备效率系数 | eta_pv    |     | beta_pv                           |
|              | k_fc_p    |     | eta_fc_p                          |
|              | k_fc_g    |     | eta_ex_g                          |
|              | eta_ex    |     |                                   |
|              | k_el      |     | beta_el                           |
|              | k_eb      |     | beta_eb                           |
|              | k_sc      |     | beta_sc                           |
|              | theta_ex  |     | theta_ex                          |
|              | k_ac      |     | beta_ac                           |
|              | k_hp_g    |     | beta_hpg                          |
|              | k_hp_q    |     | beta_hpq                          |
|              | k_ghp_g   |     | beta_ghp_g                        |
|              | k_ghp_q   |     | beta_ghp_q                        |
|              | p_gtw     |     | beta_gtw                          |
|              | k_co      |     | beta_co                           |



## 设备变量

| 设备    | 变量        | 变更名       | 含义              |
| ------- | ----------- | ------------ | ----------------- |
|         | h_pur       |              | hydrogen purchase |
|         | p_pur       |              | power purchase    |
|         | p_sol       |              | power sold        |
| PV      | s_pv        | s_pv_inst    |                   |
|         | p_pv        |              |                   |
| FC      | z_fc        |              |                   |
|         | h_fc        |              | 燃料电池耗氢量    |
|         | p_fc        |              | 燃料电池产电量    |
|         | p_fc_max    | p_fc_inst    |                   |
|         | g_fc        |              | 燃料电池产热量    |
| EL      | h_el        |              |                   |
|         | p_el        |              |                   |
|         | p_el_max    | p_el_inst    |                   |
| EB      | p_eb        |              |                   |
|         | p_eb_max    | p_eb_inst    |                   |
|         | g_eb        |              |                   |
| SC      | s_sc        | s_sc_inst    |                   |
|         | g_sc        |              |                   |
| AC      | g_ac        |              |                   |
|         | g_ac_max    | g_ac_inst    |                   |
|         | q_ac        |              |                   |
| HP      | p_hp        | p_hp_inst    |                   |
|         | p_hpc       |              |                   |
|         | p_hp_max    |              |                   |
|         | g_hp        |              |                   |
|         | q_hp        |              |                   |
| GHP     | p_ghp       |              |                   |
|         | p_ghp_max   | p_ghp_inst   |                   |
|         | p_ghpc      |              |                   |
|         | g_ghp       |              | 热泵产热          |
|         | g_ghp_gr    |              | 热泵灌热          |
|         | q_ghp       |              | 热泵产冷          |
| GTW     | num_gtw     | num_gtw_inst |                   |
| CO      | p_co        |              |                   |
|         | p_co_max    | p_co_inst    |                   |
| HST     | h_sto       | h_hst        |                   |
|         | hst         | h_hst_inst   |                   |
| HT      | t_ht        |              |                   |
|         | m_ht        |              |                   |
| CT      | t_ct        |              |                   |
|         | m_ct        |              |                   |
| Tube    | g_tube      |              |                   |
| unknown | cost_c_ele  |              |                   |
|         | cost_c_heat |              |                   |
|         | cost_c_cool |              |                   |
|         | cost_c      |              |                   |
|         | ce_h        |              |                   |

