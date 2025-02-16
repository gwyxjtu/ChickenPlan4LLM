import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

print(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
import json
import streamlit as st
from streamlit_ace import st_ace
from constant import CODE_EDITOR_HEIGHT, MODEL

from module.LLM import (
    code_prompt_template,
    code_prompt_cot_template,
    example_info_input,
    example_param_input,
    example_code_output
)
from module import call_openai_stream
from module import code_template
import traceback

import os
import sys

def exec_opt(client):
    project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    project_path = project_path.replace("\\", "/")

    # Initialize retry count if not exists
    if 'retry_count' not in st.session_state:
        st.session_state.retry_count = 0
    
    # Initialize run history if not exists
    if 'run_history' not in st.session_state:
        st.session_state.run_history = []

    # Initialize run results if not exists
    if 'run_results' not in st.session_state:
        st.session_state.run_results = []

    local_env = {"project_path": project_path}
    solver_code = st.session_state.code
    code_to_execute = code_template.format(solver_code=solver_code)

    # Create a placeholder for streaming output
    # output_placeholder = st.empty()
    # with output_placeholder.container():
    st.write("Execution output:")
    output_area = st.empty()
    current_output = ""

    # print("=" * 80)
    # print("Code to execute:")
    # print("=" * 80)
    # print(code_to_execute)
    # current_output += code_to_execute + "\n"
    # output_area.code(current_output)

    with open("tmp.py", "w", encoding="utf-8") as f:
        f.write(code_to_execute)

    try:
        exec(code_to_execute, local_env, local_env)
        print("Execution successful.")
        current_output += "\nExecution successful.\n"
        print(local_env["device_cap"])
        # print("+++")
        # output_area.code(local_env["device_cap"])
        
        st.session_state.run_results.append(local_env["device_cap"])
        st.session_state.run_history.append({"attempt": st.session_state.retry_count + 1, "status": "success"})
        st.session_state.retry_count = 0  # Reset retry count on success
        
    except Exception as e:
        error_msg = str(e)
        print("An error occurred during execution:")
        print(traceback.format_exc())
        current_output += f"\nAn error occurred during execution:\n{traceback.format_exc()}\n"
        output_area.code(current_output)
        
        st.session_state.run_history.append({"attempt": st.session_state.retry_count + 1, "status": "error", "error": error_msg})
        output_area.code(st.session_state.run_history[-1])

        if st.session_state.retry_count < 2:  # Allow up to 2 retries
            st.session_state.retry_count += 1
            
            # Generate new code using the alternative template
            code_sys_prompt = code_prompt_cot_template[0]
            code_user_prompt = code_prompt_cot_template[1].format(
                solver="gurobipy",
                example_info_input=json.dumps(example_info_input, ensure_ascii=False),
                example_param_input=json.dumps(example_param_input, ensure_ascii=False),
                example_output=example_code_output,
                info_input=json.dumps(st.session_state.json_description, ensure_ascii=False),
                param_input=json.dumps(st.session_state.parameters, ensure_ascii=False),
                know_input=json.dumps({
                    "device_knowledge": st.session_state.filtered_device_knowledge
                }, ensure_ascii=False),
                problem=error_msg
            )
            
            completion = call_openai_stream(
                client=client,
                system_prompt=code_sys_prompt,
                user_prompt=code_user_prompt,
                model=MODEL,
                max_response_tokens=8192,
                max_tokens=16384,
                temperature=0.3
            )
            
            full_response = ""
            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content is None:
                    if "```python" in full_response:
                        full_response = full_response.split("```python")[1].split("```")[0].strip()
                    st.session_state.code = full_response
                    exec_opt(client)  # Recursive retry with new code
                else:
                    full_response += content
        else:
            st.session_state.run_results.append({"error": error_msg})
            st.session_state.retry_count = 0  # Reset retry count after max retries

def page_param2code(client):
    
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
                param_input=json.dumps(param_input, ensure_ascii=False),
                know_input = json.dumps({
                    "device_knowledge": st.session_state.filtered_device_knowledge
                }, ensure_ascii=False),
            )
            # print(code_user_prompt)
            completion = call_openai_stream(
                client=client,
                system_prompt=code_sys_prompt,
                user_prompt=code_user_prompt,
                model=MODEL,
                max_response_tokens=8192,
                max_tokens=16384,
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
    col1, col2, col3, col4 = st.columns(4)
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
    with col4:
        st.text_area(
            "设备知识",
            value=st.session_state.get("filtered_device_knowledge", "无设备知识"),
            height=200,
            key="filtered_device_knowledge_display",
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
    st.button("运行代码", on_click=lambda: exec_opt(client), use_container_width=True, type="primary")

    # 下方显示运行结果
    st.subheader("运行结果")
    
    # 显示运行历史和结果
    if hasattr(st.session_state, 'run_history') and st.session_state.run_history:
        with st.empty():
            st.write("运行历史:")
            for attempt in st.session_state.run_history:
                if attempt['status'] == 'success':
                    st.write(f"第 {attempt['attempt']} 次尝试: 执行成功")
                    # Display planning results for successful attempts
                    # 展示 planning_result 规划容量
                    # print(st.session_state.run_results)
                    # print("---")
                    # st.json(st.session_state.run_results[-1])
                else:
                    st.error(f"第 {attempt['attempt']} 次尝试失败: {attempt['error']}")
                    st.write("正在尝试优化代码重新执行...")
                # st.write("正在处理...")
                # time.sleep(0.05)  # Add a small delay for visual effect
    
    # 显示最终结果
    if hasattr(st.session_state, 'run_results') and st.session_state.run_results:
        latest_result = st.session_state.run_results[-1]
        if "error" in latest_result:
            st.error("所有重试均失败，请检查问题描述或手动修改代码")
        else:
            st.success("代码执行成功!")
            # Format and display the results in a more organized way
            with st.expander("查看详细结果", expanded=True):
                st.json(latest_result)
            # Add a summary section for key metrics
            if isinstance(latest_result, dict):
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("设备装机容量")
                    if "cap_device" in latest_result:
                        for device, capacity in latest_result["cap_device"].items():
                            st.metric(label=device, value=capacity)
                with col2:
                    st.subheader("经济性指标")
                    if "revenue_p" in latest_result:
                        st.metric(label="电费收入", value=f"{latest_result['revenue_p']:.2f}元")
                    if "revenue_g" in latest_result:
                        st.metric(label="供热收入", value=f"{latest_result['revenue_g']:.2f}元")
                    if "revenue_q" in latest_result:
                        st.metric(label="供冷收入", value=f"{latest_result['revenue_q']:.2f}元")
                    if "revenue_s" in latest_result:
                        st.metric(label="售电收入", value=f"{latest_result['revenue_s']:.2f}元")
            print(st.session_state.run_results[-1])


if __name__ == "__main__":
    exec_opt()