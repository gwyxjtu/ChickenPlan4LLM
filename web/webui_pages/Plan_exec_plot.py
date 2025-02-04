import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体，确保系统已安装
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

def page_result(client):
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