DEFAULT_DESCRIPTION = """
{
    "项目描述": "本项目为榆林科创新城零碳分布式智慧能源中心示范项目，为运动员村进行供冷、供热以及供电服务。运动员村项目包括酒店、运动 员餐厅、办公、教育、住宅、公寓、体育等建筑。项目建设用地面积93347.47 m2，总建筑面积20.6万m2，地上建筑面积14万m2，其中住宅5.6万m2，办公4.9 万m2，酒店及运动员餐厅2.1万m2，健身中心0.5万m2，配套0.9万m2。由于DK1-13#楼酒店及运动员餐厅仅大堂地暖需能源站供应，实际供能面积约为12万m2。",
    "项目地理位置": "陕西省榆林市",
    "土地使用情况": "供能面积约为12万m2",
    "项目供能对象描述": "为运动员村进行供冷、供热以及供电服务",
    "项目预期描述": "最大化系统经济型，实现零碳供应能量，设备包括但不限于光伏、燃料电池、地源热泵、电解槽、电锅炉、热泵、地热井、储氢罐、蓄水箱。但是燃料电池容量不低于500kW。光伏板装机不超过2000kW,燃料电池的装机容量等于电解槽的装机容量。"
}
"""
DEFAULT_JSON_DESCRIPTION = """
{
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
"""
DEFAULT_PARAMS = ""
DEFAULT_CODE = ""

TEXT_AREA_HEIGHT = 200
CODE_EDITOR_HEIGHT = 400
