
from constant import (
    DEFAULT_DESCRIPTION,
    DEFAULT_JSON_DESCRIPTION,
    DEFAULT_PARAMS,
    DEFAULT_CODE,
    TEXT_AREA_HEIGHT,
    CODE_EDITOR_HEIGHT,
    MODEL
)
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
import streamlit as st
from streamlit_ace import st_ace
import json


def plan_userInput(client):
    col1, col2 = st.columns(2)
    with col1:
        description = {
            "地理位置": st.selectbox("地理位置", options=user_input_json["地理位置"]),
            "建筑类型": st.selectbox("建筑类型", options=user_input_json["建筑类型"]),
            "建筑面积": st.selectbox("建筑面积", options=user_input_json["建筑面积"]),
            "可再生能源设备需求": st.multiselect("可再生能源设备需求", options=user_input_json["可再生能源设备需求"]),
            "供热设备需求": st.multiselect("供热设备需求", options=user_input_json["供热设备需求"]),
            "供冷设备需求": st.multiselect("供冷设备需求", options=user_input_json["供冷设备需求"])
        }
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

# 页面内容
def page_user2json(client):

    def save_description(description):
        st.session_state.description = description
        st.info("保存成功")
    
    @st.dialog("stream")
    def generate_json():
        user_input = st.session_state.description
        if user_input:
            info_sys_prompt = info_prompt_template[0]
            info_user_prompt = info_prompt_template[1].format(
                example_user_input=json.dumps(example_user_input, ensure_ascii=False),
                example_output=json.dumps(example_info_output, ensure_ascii=False),
                user_input=json.dumps(user_input, ensure_ascii=False)
            )
            completion = call_openai_stream(
                client=client,
                system_prompt=info_sys_prompt,
                user_prompt=info_user_prompt,
                model=MODEL,
                max_response_tokens=8192,
                max_tokens=128000,
                temperature=0.3
            )
            with st.empty():
                st.text("JSON描述")
                full_response = ""
                for i, chunk in enumerate(completion):
                    content = chunk.choices[0].delta.content
                    if content is None:
                        st.write("生成完成")
                        if "```json" in full_response:
                            full_response = full_response.split("```json")[1].split("```")[0].strip()
                        elif "```python" in full_response:
                            full_response = full_response.split("```python")[1].split("```")[0].strip()
                        st.session_state.json_description = full_response
                    else:
                        full_response += content
                        st.write(full_response)
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
        description = {
            "地理位置": st.multiselect("地理位置", options=user_input_json["地理位置"], key="geo_loc", max_selections=1),
            "建筑类型": st.multiselect("建筑类型", options=user_input_json["建筑类型"], key="build_type", max_selections=1),
            "建筑面积": st.multiselect("建筑面积", options=user_input_json["建筑面积"], key="build_area", max_selections=1),
            "可再生能源设备需求": st.multiselect("可再生能源设备需求", options=user_input_json["可再生能源设备需求"], key="renewable"),
            "供热设备需求": st.multiselect("供热设备需求", options=user_input_json["供热设备需求"], key="heating"),
            "供冷设备需求": st.multiselect("供冷设备需求", options=user_input_json["供冷设备需求"], key="cooling")
        }
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
