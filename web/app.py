import time
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_ace import st_ace
from constant import (DEFAULT_DESCRIPTION, 
                      DEFAULT_JSON_DESCRIPTION,
                      DEFAULT_PARAMS,
                      TEXT_AREA_HEIGHT,
                      CODE_EDITOR_HEIGHT
                          )

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


# 页面内容
def page_language2json():
    
    def save_description():
        st.info("Save Success")
    
    def generate_json():
        description = st.session_state.description
        st.session_state.json_description = "{\n\"test\": 0\n}"

    def clear_json():
        st.session_state.description = ""
    
    # 主内容区域
    col1, col2 = st.columns(2)
    with col1:
        description = st.text_area("## 自然语言描述", st.session_state.description, height=TEXT_AREA_HEIGHT)
        st.session_state["description"] = description
        c1, c2, c3 = st.columns(3)
        with c1:
            st.button("保存描述", on_click=save_description)
        with c2:
            st.button("生成Json", on_click=generate_json)
        with c3:
            st.button("清空信息", on_click=clear_json)
    with col2:
        st.text("JSON描述")
        json_description=st_ace(st.session_state.json_description, language="json", height=CODE_EDITOR_HEIGHT)
        st.session_state["json_description"] = json_description

def page_json2param():
    
    def generate_params():
        description = st.session_state.description
        json_description = st.session_state.json_description
        st.session_state.parameters = "{\n\"params\": 0\n}"
    
    col1, col2 = st.columns(2)
    with col1:
        st.text("JSON描述")
        st_ace(st.session_state.json_description, language="json", height=CODE_EDITOR_HEIGHT, readonly=True)
        st.button("生成参数", on_click=generate_params)
    with col2:
        st.text("JSON参数")
        params = st_ace(st.session_state.parameters, language="json", height=CODE_EDITOR_HEIGHT)
        st.session_state["parameters"] = params
        st.button("求解")

def page_param2code():
    pass

# 页面标题
st.title("Energy LLM")

with st.sidebar:
    selected_tab = option_menu("Workflow", ["Description", "Parameters", 
                                            "Coding", "Data Processing", 
                                            "Testing"], 
        icons=['house']*5, menu_icon="cast", default_index=0)


# 主内容区域
if selected_tab:
    st.subheader(selected_tab)

    # 根据选中的标签显示对应内容
    if selected_tab == "Description":
        page_language2json()

    elif selected_tab == "Parameters":
        page_json2param()

    elif selected_tab == "Coding":
        st.write("Coding section is under construction.")

    elif selected_tab == "Data Processing":
        st.write("Data Processing section is under construction.")

    elif selected_tab == "Testing":
        st.write("Testing section is under construction.")
