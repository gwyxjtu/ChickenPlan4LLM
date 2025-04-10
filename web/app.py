'''
Author: guo_MateBookPro 867718012@qq.com
Date: 2025-01-07 10:10:37
LastEditTime: 2025-02-16 12:43:57
LastEditors: guo_MateBookPro 867718012@qq.com
FilePath: /ChickenPlan4LLM/web/app.py
Description: 雪花掩盖着哽咽叹息这离别
'''
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import time
from datetime import datetime
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import mpld3
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_ace import st_ace
import streamlit.components.v1 as components
from constant import (
    DEFAULT_DESCRIPTION,
    DEFAULT_JSON_DESCRIPTION,
    DEFAULT_PARAMS,
    DEFAULT_CODE,
    TEXT_AREA_HEIGHT,
    CODE_EDITOR_HEIGHT,
    MODEL
)

from module.utils import get_openai_client, call_openai, call_openai_stream
from module.utils import PROJECT_PATH, LOG_ROOT

from webui_pages.Plan_json_and_data import page_json2param
from webui_pages.Plan_userInput import page_user2json
from webui_pages.Plan_genOpt import page_param2code
from webui_pages.Plan_exec_plot import page_result

from web.logger_utils import OpenAILogger

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体，确保系统已安装
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# # 设置项目路径
# project_path = str(Path(__file__).resolve().parents[1]).replace("\\", "/")
# # openai_config_path = os.path.join(project_path, "module/openai_config.json")

# 获取 OpenAI 客户端
openai_config_path = PROJECT_PATH + "/module/openai_config.json"
client = get_openai_client(openai_config_path)

# 页面配置
st.set_page_config(page_title="Energy LLM", page_icon=":rocket:", layout="wide")
from styles import MAIN_STYLES

# Apply main styles
st.markdown(f"<style>{MAIN_STYLES}</style>", unsafe_allow_html=True)

# 初始化日志记录器
if "conversation_logger" not in st.session_state:
    st.session_state["conversation_logger"] = OpenAILogger()

if "description" not in st.session_state:
    st.session_state["description"] = DEFAULT_DESCRIPTION

if "json_description" not in st.session_state:
    st.session_state["json_description"] = DEFAULT_JSON_DESCRIPTION

if "parameters" not in st.session_state:
    st.session_state["parameters"] = DEFAULT_PARAMS

if "code" not in st.session_state:
    st.session_state["code"] = DEFAULT_CODE

# 当前页面状态
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Home"


def create_handler():
    if "session_ts" not in st.session_state:
        st.session_state["session_ts"] = datetime.now().strftime("%Y%m%d_%H%M%S")
    handler_key = f"{st.session_state['current_page']}_{st.session_state['session_ts']}"
    log_dir = f"{LOG_ROOT}/{handler_key}"
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    st.session_state.conversation_logger.add_handler(
        ui_page=st.session_state["current_page"],
        session_ts=st.session_state["session_ts"],
        log_dir=log_dir
    )


def cleanup_handler():
    if "session_ts" in st.session_state:
        st.session_state.conversation_logger.cleanup(
            ui_page=st.session_state["current_page"],
            session_ts=st.session_state["session_ts"]
        )
        del st.session_state.session_ts


def navigate_to_planning():
    cleanup_handler()  # 清理 handler
    st.session_state["current_page"] = "Planning"


def navigate_to_home():
    cleanup_handler()  # 清理 handler
    st.session_state["current_page"] = "Home"


# 写一个按钮测试api接口
def test_api(container):
    system_prompt = "You are a helpful assistant."
    user_prompt = "Say hello and introduce yourself briefly."
    completion, messages = call_openai_stream(
        client=client,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model=MODEL,
        max_response_tokens=16384,
        temperature=0.6
    )
    # breakpoint()
    # Create a container for streaming output
    # container = st.empty()
    full_response = ""
    try:
        for chunk in completion:
            if chunk.choices:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    # Update the container with the latest content
                    container.markdown(full_response)
    except Exception as e:
        container.error(f"Error during streaming: {str(e)}")
    finally:
        if full_response:
            # Keep the final response visible
            container.markdown(full_response)
            # 记录日志
            st.session_state.conversation_logger.log(
                ui_page=st.session_state["current_page"],
                task="test_api",
                messages=messages,
                full_response=full_response
            )
        else:
            container.warning("No response received")


def page_home():
    create_handler()  # 创建 handler

    col1, col2, _ = st.columns([7, 2.5, 1])
    with col1:
        sys_img_path = PROJECT_PATH + "/images/system.jpeg"
        st.markdown('<div class="home-title">大模型驱动数据中心能源系统运维管理平台</div>', unsafe_allow_html=True)
        st.image(sys_img_path, use_column_width=True)
        st.button("Test Streaming API", on_click=lambda: test_api(col1))
    with col2:
        st.markdown("<div class='home-button-container'>", unsafe_allow_html=True)
        # 使用特定的 home-page-button 类名包裹按钮
        st.markdown("<div class='home-page-button'>", unsafe_allow_html=True)
        st.button("规划设计", on_click=navigate_to_planning, key="plan_button", help="Navigate to Planning",
                  use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='home-page-button'>", unsafe_allow_html=True)
        st.button("运行调度", key="design_button", help="Design feature coming soon", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='home-page-button'>", unsafe_allow_html=True)
        st.button("评估分析", key="report_button", help="Report generation feature coming soon",
                  use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


def page_planning():
    create_handler()  # 创建 handler

    with st.sidebar:

        selected_tab = option_menu(
            menu_title="Planning",
            menu_icon="robot",
            options=["Description", "Parameters", "Coding", "Results", ],
            icons=['chat', 'sliders', 'braces', 'file-earmark-bar-graph'],  # https://icons.getbootstrap.com/
            default_index=0
        )
        st.button("返回首页", on_click=navigate_to_home, use_container_width=True)

    # 主内容区域
    if selected_tab:
        st.subheader(selected_tab)

        # 根据选中的标签显示对应内容
        if selected_tab == "Description":
            page_user2json(client)

        elif selected_tab == "Parameters":
            page_json2param(client)

        elif selected_tab == "Coding":
            page_param2code(client)

        elif selected_tab == "Results":
            page_result(client)


# 页面标题
st.title("Energy LLM")

# 判断显示首页或工作流页面
if st.session_state["current_page"] == "Home":
    page_home()
elif st.session_state["current_page"] == "Planning":
    page_planning()
elif st.session_state["current_page"] == "Design":
    pass
elif st.session_state["current_page"] == "Report":
    pass
else:
    st.error("Invalid page state")
    st.stop()
