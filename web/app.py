import streamlit as st
from streamlit_option_menu import option_menu
from code_editor import code_editor


# 页面标题
st.title("Energy LLM")

with st.sidebar:
    selected_tab = option_menu("Workflow", ["Description", "Parameters", "Constraints & Objective", 
        "Mathematical Formulation", "Coding", "Data Processing", "Testing"], 
        icons=['house']*7, menu_icon="cast", default_index=1)

def language2json():
    st.text_area("自然语言", "这里输入自然语言", height=200)
    json_data = """
    {
  "users": [
    {
      "id": 1,
      "name": "张三",
      "age": 28,
      "email": "zhangsan@example.com",
      "phone": "+86 138 0000 0000",
      "address": {
        "street": "长安街",
        "city": "北京",
        "postal_code": "100000"
      },
      "activities": [
        {
          "activity_id": 101,
          "activity_name": "参加会议",
          "date": "2023-10-01",
          "duration": "2小时",
          "location": "北京会议中心"
        },
        {
          "activity_id": 102,
          "activity_name": "项目演示",
          "date": "2023-10-05",
          "duration": "1.5小时",
          "location": "公司总部"
        }
      ]
    },
    {
      "id": 2,
      "name": "李四",
      "age": 32,
      "email": "lisi@example.com",
      "phone": "+86 139 0000 0000",
      "address": {
        "street": "人民路",
        "city": "上海",
        "postal_code": "200000"
      },
      "activities": [
        {
          "activity_id": 201,
          "activity_name": "团队建设",
          "date": "2023-10-10",
          "duration": "3小时",
          "location": "上海野生动物园"
        },
        {
          "activity_id": 202,
          "activity_name": "技术研讨会",
          "date": "2023-10-15",
          "duration": "4小时",
          "location": "上海科技馆"
        }
      ]
    }
  ]
}
"""
    st.text("这里是json")
    code_editor(json_data, "json")

# 主内容区域
if selected_tab:
    st.subheader(selected_tab)

    # 根据选中的标签显示对应内容
    if selected_tab == "Description":
        language2json()

    elif selected_tab == "Parameters":
        st.write("Parameters section is under construction.")

    elif selected_tab == "Constraints & Objective":
        st.write("Constraints and Objective section is under construction.")

    elif selected_tab == "Mathematical Formulation":
        st.write("Mathematical Formulation section is under construction.")

    elif selected_tab == "Coding":
        st.write("Coding section is under construction.")

    elif selected_tab == "Data Processing":
        st.write("Data Processing section is under construction.")

    elif selected_tab == "Testing":
        st.write("Testing section is under construction.")

# 底部按钮
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("Reset"):
        st.write("Resetting...")

with col2:
    if st.button("I’m feeling lucky!"):
        st.write("Feeling lucky!")

with col3:
    if st.button("Analyze"):
        st.write("Analyzing...")

# 运行指令
if __name__ == "__main__":
    st.write("Run this app with `streamlit run app.py`.")
