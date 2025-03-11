import streamlit as st
from web.constant import MODEL
from module import call_openai_stream, count_tokens, get_last_tokens


def llm_out_st(client, system_prompt, user_prompt, text_content):
    last_messages = None
    last_response = None
    full_response = ""
    last_finish_reason = None
    with st.empty():
        st.text(text_content)
        while True:
            completion, messages = call_openai_stream(
                client=client,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=MODEL,
                last_messages=last_messages,
                last_response=last_response,
                max_response_tokens=8192,
                temperature=0.3
            )
            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    st.write(full_response)
                if chunk.choices[0].finish_reason is not None:
                    last_finish_reason = chunk.choices[0].finish_reason
            if last_finish_reason == "length":
                system_prompt = None
                user_prompt = None
                last_messages = messages
                last_response = get_last_tokens(
                    full_response,
                    model=MODEL,
                    num_tokens=8192
                )
            else:
                break

        st.write("生成完成")
        # 若使用 DeepSeek-R1, 需将思考部分删去, 仅保留生成的内容, 思考部分由 <think> 和 </think> 包围
        if MODEL == "deepseek-reasoner":
            full_response = full_response.split("</think>")[1].strip()
        # 删除开头的```json和结尾的```，以及两端的换行符
        if "```json" in full_response:
            full_response = full_response.split("```json")[1].split("```")[0].strip()
        # 删除开头的```python和结尾的```，以及两端的换行符
        if "```python" in full_response:
            full_response = full_response.split("```python")[1].split("```")[0].strip()

        return full_response
