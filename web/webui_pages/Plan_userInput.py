'''
Author: guo_MateBookPro 867718012@qq.com
Date: 2025-01-05 23:59:41
LastEditTime: 2025-01-09 16:21:47
LastEditors: guo_MateBookPro 867718012@qq.com
FilePath: /ChickenPlan4LLM/web/webui_pages/Plan_userInput.py
Description: 雪花掩盖着哽咽叹息这离别
'''
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


def plan_userInput():
    col1, col2 = st.columns(2)
    with col1:
        description = st.text_area("## 自然语言描述", value=st.session_state.get("description", ""), height=TEXT_AREA_HEIGHT)
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