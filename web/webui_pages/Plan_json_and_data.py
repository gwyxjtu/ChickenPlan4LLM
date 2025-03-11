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
    param_prompt_template,
    example_user_input,
    example_info_input,
    example_param_output
)
from module.utils import call_openai_stream
from module.utils import PROJECT_PATH


def page_json2param(client):
    
    @st.dialog("stream")
    def generate_params():
        user_input = st.session_state.description
        info_input = st.session_state.json_description
        # st.session_state.parameters = user_input + info_input  # test only
        if user_input and info_input:
            param_sys_prompt = param_prompt_template[0]
            param_user_prompt = param_prompt_template[1].format(
                example_user_input=json.dumps(example_user_input, ensure_ascii=False),
                example_info_input=json.dumps(example_info_input, ensure_ascii=False),
                example_output=json.dumps(example_param_output, ensure_ascii=False),
                user_input=json.dumps(user_input, ensure_ascii=False),
                param_info_input=json.dumps(info_input, ensure_ascii=False)
            )
            full_response = llm_out_st(
                client=client,
                system_prompt=param_sys_prompt,
                user_prompt=param_user_prompt,
                text_content="正在生成参数"
            )
            st.session_state.parameters = full_response
        else:
            st.warning("问题描述或JSON描述缺失")
        # write json
        try:
            # Parse the JSON string to ensure valid format
            json_data = json.loads(st.session_state.parameters)
            # Write the parsed JSON with standard formatting
            with open(PROJECT_PATH + "/web/data/parameters.json", "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
        except json.JSONDecodeError:
            st.error("Invalid JSON format in parameters")

    col1, col2 = st.columns(2)
    with col1:
        st.text("JSON描述")
        st_ace(st.session_state.json_description, language="json", height=CODE_EDITOR_HEIGHT, readonly=True)
        st.button("生成参数", on_click=generate_params, use_container_width=True)
    with col2:
        st.text("JSON参数")
        params = st_ace(st.session_state.parameters, language="json", height=CODE_EDITOR_HEIGHT)
        st.session_state["parameters"] = params
        # st.button("求解", use_container_width=True)
