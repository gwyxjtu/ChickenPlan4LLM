import json
from module.LLM import *

user_input = {
    "项目描述": "本项目为榆林科创新城零碳分布式智慧能源中心示范项目，为运动员村进行供冷、供热以及供电服务。运动员村项目包括酒店、运动 员餐厅、办公、教育、住宅、公寓、体育等建筑。项目建设用地面积93347.47 m2，总建筑面积20.6万m2，地上建筑面积14万m2，其中住宅5.6万m2，办公4.9 万m2，酒店及运动员餐厅2.1万m2，健身中心0.5万m2，配套0.9万m2。由于DK1-13#楼酒店及运动员餐厅仅大堂地暖需能源站供应，实际供能面积约为12万m2。",
    "项目地理位置": "陕西省榆林市",
    "土地使用情况": "供能面积约为12万m2",
    "项目供能对象描述": "为运动员村进行供冷、供热以及供电服务",
    "项目预期描述": "最大化系统经济型，实现零碳供应能量，设备包括但不限于光伏、燃料电池、地源热泵、电解槽、电锅炉、热泵、地热井、储氢罐、蓄水箱。但是燃料电池容量不低于500kW。光伏板装机不超过2000kW,燃料电池的装机容量等于电解槽的装机容量。"
}

param_info_input = {

}

if __name__ == '__main__':
    info_prompt = info_prompt_template.format(
        example_user_input=json.dumps(example_user_input, indent=4, ensure_ascii=False),
        example_output=json.dumps(example_info_output, indent=4, ensure_ascii=False),
        user_input=json.dumps(user_input, ensure_ascii=False)
    )
    print(info_prompt)

    # param_prompt = param_prompt_template.format(
    #     example_user_input=example_user_input,
    #     example_param_info_input=example_param_info_input,
    #     example_output=example_param_output,
    #     user_input=json.dumps(user_input, ensure_ascii=False),
    #     param_info_input=json.dumps(param_info_input, ensure_ascii=False)
    # )
    # print(param_prompt)
    #
    # code_prompt = code_prompt_template.format(
    #     solver="gurobipy",
    #     example_info_input=example_info_input,
    #     example_param_input=example_param_input,
    #     example_output=example_code_output,
    #     info_input=json.dumps(user_input, ensure_ascii=False),
    #     param_input=json.dumps(param_info_input, ensure_ascii=False)
    # )
    # print(code_prompt)
