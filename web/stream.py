import streamlit as st
from web.constant import MODEL
from module.utils import call_openai_stream, count_tokens, get_last_tokens


def llm_out_st(client, system_prompt, user_prompt, text_content):
    last_messages = None
    last_response = None
    last_finish_reason = None
    full_response = ""
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
                max_response_tokens=16384,
                temperature=0.6
            )
            last_response = ""
            last_reasoning_response = ""
            output = ""
            for chunk in completion:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    content = delta.content if delta.content else ""
                    if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                        last_reasoning_response += delta.reasoning_content
                    else:
                        last_response += content
                        output = full_response + last_response
                        st.write(output)
                    if chunk.choices[0].finish_reason is not None:
                        last_finish_reason = chunk.choices[0].finish_reason
                if chunk.usage:
                    usage_info = chunk.usage

            if MODEL == "deepseek-reasoner":
                # 若使用 DeepSeek-R1, 由于第三方服务可能将思考部分包围在 <think> 和 </think> 中, 只保留后续部分
                if "</think>" in last_response:
                    last_response = last_response.split("</think>")[1].strip()
                # 此外，DeepSeek-R1 会在思考部分结束后返回一个"\n\n"，需要去掉
                if last_response.startswith("\n\n"):
                    last_response = last_response[2:]
            full_response += last_response

            if last_finish_reason == "length":
                system_prompt = None
                user_prompt = None
                last_messages = messages
            else:
                break

        st.write("生成完成")
        # 删除开头的```json和结尾的```，以及两端的换行符
        if "```json" in full_response:
            full_response = full_response.split("```json")[1].split("```")[0].strip()
        # 删除开头的```python和结尾的```，以及两端的换行符
        if "```python" in full_response:
            full_response = full_response.split("```python")[1].split("```")[0].strip()

        return full_response
