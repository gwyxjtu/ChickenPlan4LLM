from pathlib import Path
import json
import streamlit as st
from streamlit_ace import st_ace

from web.constant import (
    DEFAULT_DESCRIPTION,
    DEFAULT_JSON_DESCRIPTION,
    DEFAULT_PARAMS,
    DEFAULT_CODE,
    TEXT_AREA_HEIGHT,
    CODE_EDITOR_HEIGHT,
    MODEL
)
from web.stream import llm_out_st
from module.LLM import (
    info_prompt_template,
    param_prompt_template,
    code_prompt_template
)
from module.LLM import (
    example_user_input,
    example_info_output,
    example_info_input,
    example_param_output,
    example_param_input,
    example_code_output
)
from module.LLM import (
    user_input_json,
    user_input_detail_json,
)
from module import get_openai_client, call_openai, call_openai_stream

project_path = Path(__file__).resolve().parents[2]

with open(project_path / "device_set/ggp_knowledge_set.json", "r", encoding="utf-8") as f:
    ggp_knowledge = json.load(f)
with open(project_path / "device_set/device_knowledge.json", "r", encoding="utf-8") as f:
    device_knowledge = json.load(f)
with open(project_path / "device_set/load_knowledge_set.json", "r", encoding="utf-8") as f:
    load_knowledge = json.load(f)

# def plan_userInput(client):
#     col1, col2 = st.columns(2)
#     with col1:
#         description = {
#             "地理位置": st.selectbox("地理位置", options=user_input_json["地理位置"]),
#             "建筑类型": st.selectbox("建筑类型", options=user_input_json["建筑类型"]),
#             # "建筑面积": st.selectbox("建筑面积", options=user_input_json["建筑面积"]),
#             "可再生能源设备需求": st.multiselect("可再生能源设备需求", options=user_input_json["可再生能源设备需求"]),
#             "供热设备需求": st.multiselect("供热设备需求", options=user_input_json["供热设备需求"]),
#             "供冷设备需求": st.multiselect("供冷设备需求", options=user_input_json["供冷设备需求"])
#         }
#         c1, c2, c3 = st.columns(3)
#         with c1:
#             st.button("保存描述", on_click=save_description, args=(description,), use_container_width=True)
#         with c2:
#             st.button("生成Json", on_click=generate_json, use_container_width=True)
#         with c3:
#             st.button("清空信息", on_click=clear_json, use_container_width=True)
#     with col2:
#         st.text("JSON描述")
#         json_description = st_ace(st.session_state.get("json_description", "无内容"), language="json", height=CODE_EDITOR_HEIGHT)
#         st.session_state.json_description = json_description


# 页面内容
def page_user2json(client):

    def save_description(description):
        st.session_state.description = description
        st.info("保存成功")
    
    @st.dialog("stream")
    def generate_json():
        user_input = st.session_state.description
        selected_devices = user_input.get("可再生能源设备需求", []) + user_input.get("供热设备需求", []) + user_input.get("供冷设备需求", [])
        filtered_device_knowledge = {k: v for k, v in device_knowledge.items() if k in selected_devices}
        # print(filtered_device_knowledge)
        st.session_state.filtered_device_knowledge = filtered_device_knowledge
        if user_input:
            info_sys_prompt = info_prompt_template[0]
            info_user_prompt = info_prompt_template[1].format(
                example_user_input=json.dumps(example_user_input, ensure_ascii=False),
                example_output=json.dumps(example_info_output, ensure_ascii=False),
                # Filter device knowledge based on user's selected equipment
                know_input=json.dumps({
                    "device_knowledge": filtered_device_knowledge,
                    "ggp_knowledge": ggp_knowledge
                }, ensure_ascii=False),
                user_input=json.dumps(user_input, ensure_ascii=False)
            )
            full_response = llm_out_st(
                client=client,
                system_prompt=info_sys_prompt,
                user_prompt=info_user_prompt,
                text_content="JSON描述"
            )
            st.session_state.json_description = full_response
        else:
            st.warning("请先输入问题描述")

    def clear_json():
        st.session_state.description = {
            "地理位置": "",
            "建筑类型": "",
            "建筑面积": "",
            "可再生能源设备需求": [],
            "供热设备需求": [],
            "供冷设备需求": []
        }
        st.session_state.json_description = ""
        st.info("已清空输入")

    # 主内容区域
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("基本信息")
        description = {
            "地理位置": st.multiselect("地理位置", options=user_input_json["地理位置"], key="geo_loc", max_selections=1),
            "建筑类型": st.multiselect("建筑类型", options=user_input_json["建筑类型"], key="build_type", max_selections=1),
            # "建筑面积": st.multiselect("建筑面积", options=user_input_json["建筑面积"], key="build_area", max_selections=1),
            "可再生能源设备需求": st.multiselect("可再生能源设备需求", options=user_input_json["可再生能源设备需求"], key="renewable"),
            "供热设备需求": st.multiselect("供热设备需求", options=user_input_json["供热设备需求"], key="heating"),
            "供冷设备需求": st.multiselect("供冷设备需求", options=user_input_json["供冷设备需求"], key="cooling")
        }
        
        st.subheader("详细参数")
        detail_description = {
            "冷负荷峰值": st.number_input("冷负荷峰值 (kW)", min_value=0, value=100000, step=1000, key="cold_peak"),
            "热负荷峰值": st.number_input("热负荷峰值 (kW)", min_value=0, value=200000, step=1000, key="heat_peak"),
            "电负荷峰值": st.number_input("电负荷峰值 (kW)", min_value=0, value=50000, step=1000, key="power_peak"),
            "建筑面积": st.number_input("建筑面积 (m²)", min_value=0, value=12000, step=1000, key="area"),
            "年总收益": st.number_input("年总收益 (元)", min_value=0, value=5000000, step=100000, key="annual_revenue"),
            "分时电价": [0.5] * 28,  # 保持原有的24小时电价格式
            "氢气价格": st.number_input("氢气价格 (元/kg)", min_value=0.0, value=20.0, step=0.1, key="h2_price"),
            "天然气价格": st.number_input("天然气价格 (元/m³)", min_value=0.0, value=50.0, step=0.1, key="gas_price")
        }
        description.update(detail_description)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.button("保存描述", on_click=save_description, args=(description,), use_container_width=True)
        with c2:
            st.button("生成Json", on_click=generate_json, use_container_width=True)
        with c3:
            st.button("清空信息", on_click=clear_json, use_container_width=True)
    with col2:
        st.text("JSON描述")
        json_description = st_ace(st.session_state.get("json_description", "无内容"), language="json", height=CODE_EDITOR_HEIGHT)
        st.session_state.json_description = json_description
