import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import time
import json
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_ace import st_ace
from constant import (
    DEFAULT_DESCRIPTION,
    DEFAULT_JSON_DESCRIPTION,
    DEFAULT_PARAMS,
    DEFAULT_CODE,
    TEXT_AREA_HEIGHT,
    CODE_EDITOR_HEIGHT
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
from module import get_openai_client, call_openai

# 获取 OpenAI 客户端
project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# openai_config_path = os.path.join(project_path, "module/openai_config.json")
openai_config_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + "/module/openai_config.json"
client = get_openai_client(openai_config_path)

# 页面配置
st.set_page_config(page_title="Energy LLM", page_icon=":rocket:", layout="wide")
st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                }
        </style>
        """, unsafe_allow_html=True)

if "description" not in st.session_state:
    st.session_state["description"] = DEFAULT_DESCRIPTION

if "json_description" not in st.session_state:
    st.session_state["json_description"] = DEFAULT_JSON_DESCRIPTION

if "parameters" not in st.session_state:
    st.session_state["parameters"] = DEFAULT_PARAMS

if "code" not in st.session_state:
    st.session_state["code"] = DEFAULT_CODE


# 页面内容
def page_language2json():
    def save_description(description):
        st.session_state.description = description
        st.info("保存成功")

    def generate_json():
        user_input = st.session_state.description
        st.session_state.json_description = user_input  # test only
        # if user_input:
        #     info_sys_prompt = info_prompt_template[0]
        #     info_user_prompt = info_prompt_template[1].format(
        #         example_user_input=json.dumps(example_user_input, ensure_ascii=False),
        #         example_output=json.dumps(example_info_output, ensure_ascii=False),
        #         user_input=json.dumps(user_input, ensure_ascii=False)
        #     )
        #     response = call_openai(
        #         client=client,
        #         system_prompt=info_sys_prompt,
        #         user_prompt=info_user_prompt,
        #         model="gpt-4o",
        #         max_response_tokens=8192,
        #         max_tokens=128000,
        #         temperature=0.3
        #     )
        #     st.session_state.json_description = response
        # else:
        #     st.warning("请先输入问题描述")

    def clear_json():
        st.session_state.description = ""
        st.session_state.json_description = ""
        st.info("已清空输入")

    # 主内容区域
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


def page_json2param():
    def generate_params():
        user_input = st.session_state.description
        info_input = st.session_state.json_description
        st.session_state.parameters = user_input + info_input  # test only
        # if user_input and info_input:
        #     param_sys_prompt = param_prompt_template[0]
        #     param_user_prompt = param_prompt_template[1].format(
        #         example_user_input=json.dumps(example_user_input, ensure_ascii=False),
        #         example_info_input=json.dumps(example_info_input, ensure_ascii=False),
        #         example_output=json.dumps(example_param_output, ensure_ascii=False),
        #         user_input=json.dumps(user_input, ensure_ascii=False),
        #         param_info_input=json.dumps(info_input, ensure_ascii=False)
        #     )
        #     response = call_openai(
        #         client=client,
        #         system_prompt=param_sys_prompt,
        #         user_prompt=param_user_prompt,
        #         model="gpt-4o",
        #         max_response_tokens=8192,
        #         max_tokens=128000,
        #         temperature=0.3
        #     )
        #     st.session_state.parameters = response
        # else:
        #     st.warning("问题描述或JSON描述缺失")

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


def page_param2code():
    def generate_code():
        info_input = st.session_state.json_description
        param_input = st.session_state.parameters
        st.session_state.code = info_input + param_input  # test only
        # if info_input and param_input:
        #     code_sys_prompt = code_prompt_template[0]
        #     code_user_prompt = code_prompt_template[1].format(
        #         solver="gurobipy",
        #         example_info_input=json.dumps(example_info_input, ensure_ascii=False),
        #         example_param_input=json.dumps(example_param_input, ensure_ascii=False),
        #         example_output=example_code_output,
        #         info_input=json.dumps(info_input, ensure_ascii=False),
        #         param_input=json.dumps(param_input, ensure_ascii=False)
        #     )
        #     response = call_openai(
        #         client=client,
        #         system_prompt=code_sys_prompt,
        #         user_prompt=code_user_prompt,
        #         model="gpt-4o",
        #         max_response_tokens=8192,
        #         max_tokens=128000,
        #         temperature=0.3
        #     )
        #     st.session_state.code = response
        #     st.success("代码已生成")
        # else:
        #     st.warning("JSON描述或参数缺失")

    # 上方显示历史信息
    st.subheader("历史信息")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.text_area(
            "自然语言描述",
            value=st.session_state.get("description", "无描述"),
            height=200,  # 可以自定义高度
            key="description_display",
            disabled=True  # 设置为只读
        )
    with col2:
        st.text_area(
            "问题信息",
            value=st.session_state.get("json_description", "无信息"),
            height=200,
            key="json_description_display",
            disabled=True
        )
    with col3:
        st.text_area(
            "参数信息",
            value=st.session_state.get("parameters", "无参数"),
            height=200,
            key="parameters_display",
            disabled=True
        )

    # 中间为生成代码按钮，宽度为整个页面
    st.button("生成代码", on_click=generate_code, use_container_width=True)

    # 下方显示生成的代码
    st.subheader("生成的代码")
    code = st_ace(
        st.session_state.get("code", "无代码"),
        language="python",
        height=CODE_EDITOR_HEIGHT
    )
    st.session_state.code = code

    # 运行按钮
    st.button("运行代码", use_container_width=True, type="primary")



def page_result():
    st.text("运行结果")
    st.dataframe({"a": [1, 2, 3], "b": [4, 5, 6]})
    st.line_chart({"a": [1, 2, 3, 4], "b": [4,5,6,7]})
    st.button("保存结果", use_container_width=True)


# 页面标题
st.title("Energy LLM")

with st.sidebar:
    selected_tab = option_menu(
        menu_title="Workflow",
        menu_icon="robot",
        options=["Description", "Parameters", "Coding", "Results",],
        icons=['chat', 'sliders', 'braces', 'file-earmark-bar-graph'],  # https://icons.getbootstrap.com/
        default_index=0
        )


# 主内容区域
if selected_tab:
    st.subheader(selected_tab)

    # 根据选中的标签显示对应内容
    if selected_tab == "Description":
        page_language2json()

    elif selected_tab == "Parameters":
        page_json2param()

    elif selected_tab == "Coding":
        page_param2code()

    elif selected_tab == "Results":
        page_result()
