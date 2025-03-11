import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import time
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
from module.utils import get_openai_client, call_openai, call_openai_stream

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体，确保系统已安装
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 设置项目路径
project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
project_path = project_path.replace("\\", "/")
# openai_config_path = os.path.join(project_path, "module/openai_config.json")

# 获取 OpenAI 客户端
openai_config_path = project_path + "/module/openai_config.json"
client = get_openai_client(openai_config_path)

# 页面配置
st.set_page_config(page_title="Energy LLM", page_icon=":rocket:", layout="wide")
st.markdown("""
        <style>
            .block-container {
                padding-top: 1rem;
                padding-bottom: 0rem;
            }
            .home-button-container {
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100%;
                margin-top: 200px;  /* 添加顶部间距 */
            }
            /* 首页专用按钮样式 */
            .home-page-button button {
                width: 800px;  /* 固定宽度 */
                height: 200px;  /* 增大按钮高度 */
                font-size: 24px;  /* 增大按钮字体 */
                margin: 10px auto;
            }
            .home-title {
                text-align: center;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
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

# 当前页面状态
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Home"


def page_home():
    col1, col2, _ = st.columns([7, 2.5, 1])
    with col1:
        sys_img_path = project_path+"/images/system.jpeg"
        st.markdown('<div class="home-title">大模型驱动数据中心能源系统运维管理平台</div>', unsafe_allow_html=True)
        st.image(sys_img_path, use_column_width=True)
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


def navigate_to_planning():
    st.session_state["current_page"] = "Planning"


def navigate_to_home():
    st.session_state["current_page"] = "Home"


# 页面内容
def page_language2json():

    def save_description(description):
        st.session_state.description = description
        st.info("保存成功")
    
    @st.dialog("stream")
    def generate_json():
        user_input = st.session_state.description
        # st.session_state.json_description = user_input  # test only
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
                            # 删除开头的```json和结尾的```，以及两端的换行符
                            full_response = full_response.split("```json")[1].split("```")[0].strip()
                        elif "```python" in full_response:
                            # 删除开头的```python和结尾的```，以及两端的换行符
                            full_response = full_response.split("```python")[1].split("```")[0].strip()
                        st.session_state.json_description = full_response
                    else:
                        full_response += content
                        st.write(full_response)
                        st.session_state.json_description = full_response
                    
        else:
            st.warning("请先输入问题描述")

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
            completion = call_openai_stream(
                client=client,
                system_prompt=param_sys_prompt,
                user_prompt=param_user_prompt,
                model=MODEL,
                max_response_tokens=8192,
                max_tokens=128000,
                temperature=0.3
            )
            with st.empty():
                st.text("正在生成参数")
                full_response = ""
                for i, chunk in enumerate(completion):
                    content = chunk.choices[0].delta.content
                    if content is None:
                        st.write("生成完成")
                        if "```json" in full_response:
                            # 删除开头的```json和结尾的```，以及两端的换行符
                            full_response = full_response.split("```json")[1].split("```")[0].strip()
                        elif "```python" in full_response:
                            # 删除开头的```python和结尾的```，以及两端的换行符
                            full_response = full_response.split("```python")[1].split("```")[0].strip()
                        st.session_state.parameters = full_response
                    else:
                        full_response += content
                        st.write(full_response)
                        st.session_state.parameters = full_response
        else:
            st.warning("问题描述或JSON描述缺失")

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
    
    @st.dialog("stream")
    def generate_code():
        info_input = st.session_state.json_description
        param_input = st.session_state.parameters
        # st.session_state.code = info_input + param_input  # test only
        if info_input and param_input:
            code_sys_prompt = code_prompt_template[0]
            code_user_prompt = code_prompt_template[1].format(
                solver="gurobipy",
                example_info_input=json.dumps(example_info_input, ensure_ascii=False),
                example_param_input=json.dumps(example_param_input, ensure_ascii=False),
                example_output=example_code_output,
                info_input=json.dumps(info_input, ensure_ascii=False),
                param_input=json.dumps(param_input, ensure_ascii=False)
            )
            completion = call_openai_stream(
                client=client,
                system_prompt=code_sys_prompt,
                user_prompt=code_user_prompt,
                model=MODEL,
                max_response_tokens=8192,
                max_tokens=128000,
                temperature=0.3
            )
            with st.empty():
                st.text("正在生成代码")
                full_response = ""
                for i, chunk in enumerate(completion):
                    content = chunk.choices[0].delta.content
                    if content is None:
                        st.write("代码已生成")
                        if "```json" in full_response:
                            # 删除开头的```json和结尾的```，以及两端的换行符
                            full_response = full_response.split("```json")[1].split("```")[0].strip()
                        elif "```python" in full_response:
                            # 删除开头的```python和结尾的```，以及两端的换行符
                            full_response = full_response.split("```python")[1].split("```")[0].strip()
                        st.session_state.code = full_response
                    else:
                        full_response += content
                        st.write(full_response)
                        st.session_state.code = full_response
        else:
            st.warning("JSON描述或参数缺失")

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
    # 模拟数据
    # 光照强度信息（12个月总量）
    months = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]
    solar_intensity = [300, 320, 400, 450, 500, 550, 600, 580, 450, 400, 350, 320]  # 示例数据

    # 电负荷、热负荷和冷负荷（365天每日负荷）
    days = range(1, 366)
    electric_load = np.random.uniform(50, 100, size=365)  # 示例电负荷数据
    thermal_load = np.random.uniform(30, 80, size=365)  # 示例热负荷数据
    cooling_load = np.random.uniform(20, 70, size=365)  # 示例冷负荷数据
    load_data = pd.DataFrame(
        {
            "日期": days,
            "电负荷 (MW)": electric_load,
            "热负荷 (MW)": thermal_load,
            "冷负荷 (MW)": cooling_load
        }
    )

    # 设备装机容量表
    equipment_data = {
        "设备名称": ["燃气轮机", "光伏系统", "储能系统", "锅炉", "制冷机"],
        "装机容量 (MW)": [20, 50, 10, 15, 25]
    }
    equipment_df = pd.DataFrame(equipment_data)

    # 页面布局
    col1, _, col2 = st.columns([3, 0.2, 2])  # 左侧图表，右侧表格
    with col1:
        tab1, tab2 = st.tabs(["光照强度", "负荷情况"])
        with tab1:
            fig1, ax1 = plt.subplots(figsize=(6, 3.375))
            ax1.bar(months, solar_intensity, color='skyblue')
            ax1.set_xlabel("月份")
            ax1.set_ylabel(r"光照强度 ($\mathrm{kWh/m^2}$)")
            st.pyplot(fig1)
        with tab2:
            fig2, ax2 = plt.subplots(figsize=(6, 3.375))
            sns.lineplot(x="日期", y="电负荷 (MW)", data=load_data, ax=ax2, label="电负荷", color="#2b65c8")
            sns.lineplot(x="日期", y="热负荷 (MW)", data=load_data, ax=ax2, label="热负荷", color="#fa403d")
            sns.lineplot(x="日期", y="冷负荷 (MW)", data=load_data, ax=ax2, label="冷负荷", color="#8bc7fe")
            ax2.set_xlabel("天数")
            ax2.set_ylabel("负荷 (MW)")
            ax2.legend()
            st.pyplot(fig2)

    with col2:
        # 右侧设备装机容量表格
        st.subheader("设备装机容量")
        table_html = equipment_df.to_html(index=False)
        st.markdown(
            f"""
            <div style="font-size: 20px">
                {table_html}
            </div>
            """,
            unsafe_allow_html=True
        )
    st.button("保存结果", use_container_width=True)


# 页面标题
st.title("Energy LLM")

# 判断显示首页或工作流页面
if st.session_state["current_page"] == "Home":
    page_home()
else:
    with st.sidebar:
        selected_tab = option_menu(
            menu_title="Planning",
            menu_icon="robot",
            options=["Description", "Parameters", "Coding", "Results",],
            icons=['chat', 'sliders', 'braces', 'file-earmark-bar-graph'],  # https://icons.getbootstrap.com/
            default_index=0
            )
        st.button("返回首页", on_click=navigate_to_home, use_container_width=True)

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
