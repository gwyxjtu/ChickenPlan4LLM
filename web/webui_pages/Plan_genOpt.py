import json
import streamlit as st
from streamlit_ace import st_ace
from constant import CODE_EDITOR_HEIGHT, MODEL
from module.LLM import (
    code_prompt_template,
    example_info_input,
    example_param_input,
    example_code_output
)
from module import call_openai_stream
from module import code_template
import traceback

import os
import sys

def exec_opt():
    project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    project_path = project_path.replace("\\", "/")

    local_env = {"project_path": project_path}

    solver_code = example_code_output

    code_to_execute = code_template.format(solver_code=solver_code)

    print("=" * 80)
    print("Code to execute:")
    print("=" * 80)
    print(code_to_execute)
    # save
    with open("tmp.py", "w", encoding="utf-8") as f:
        f.write(code_to_execute)
    print("=" * 80)
    print("Executing code ...")
    print("=" * 80)
    try:
        exec(code_to_execute, local_env, local_env)
        print("=" * 80)
        print("Execution successful.")
        print("=" * 80)
        print("local_env contents:")
        for key, _ in local_env.items():
            print(key)

    except Exception as e:
        # 捕获并打印详细的异常信息
        print("An error occurred during execution:")
        print(traceback.format_exc())

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
    st.button("运行代码", on_click=exec_opt, use_container_width=True, type="primary")