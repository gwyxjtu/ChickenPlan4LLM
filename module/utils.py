import json
import xlwt
import openai

res_dict = "./doc/"


def to_xls(res, filename):
    """将规划结果保存为 csv 文件

    Args:
        res (dict): 规划结果
        filename (str): 保存的文件名
    """
    items = list(res.keys())
    wb = xlwt.Workbook()
    new_sheet = wb.add_sheet("sheet1")
    for i in range(len(items)):
        new_sheet.write(0, i, items[i])
        if type(res[items[i]]) is list:
            column_sum = 0
            print(items[i])
            for j in range(len(res[items[i]])):
                new_sheet.write(j + 2, i, (res[items[i]])[j])
                # column_sum += (res[items[i]])[j]
            # new_sheet.write(1, i, column_sum)
        else:
            print(items[i])
            new_sheet.write(1, i, res[items[i]])

    # filename = 'res/chicken_plan_2_load_1' + '.xls'
    wb.save(res_dict + filename)


def get_openai_client(config_path):
    """获取 OpenAI 客户端

    Args:
        config_path (str): OpenAI 配置文件路径

    Returns:
        OpenAI: OpenAI 客户端
    """
    with open(config_path) as f:
        config = json.load(f)
    if len(config["openai_api_key"]) < 10:
        raise ValueError("Please provide a valid OpenAI API key in openai_config.json")

    client = openai.Client(
        api_key=config["openai_api_key"],
        organization=config["openai_org_id"],
        base_url=config["openai_base_url"],
    )

    return client


def call_openai(
        client: openai.Client,
        system_prompt: str,
        user_prompt: str,
        model: str = "gpt-4-turbo",
        max_response_tokens: int = 4096,
        max_tokens: int = 128000,
        temperature: float = 0.5
) -> str:
    """调用 OpenAI API

    Args:
        client (OpenAI): OpenAI 客户端
        system_prompt (str): 系统提示词
        user_prompt (str): 用户提示词
        model (str): 模型名称. Defaults to "gpt-4-turbo".
        max_response_tokens (int, optional): 最大响应 token 数. Defaults to 4096.
        max_tokens (int, optional): 最大 token 数. Defaults to 128000.
        temperature (float, optional): 温度. Defaults to 0.5.

    Returns:
        str: OpenAI API 返回的结果
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    full_response = ""

    while True:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            max_completion_tokens=max_response_tokens,
            max_tokens=max_tokens,
            temperature=temperature
        )
        content = completion.choices[0].message.content

        if "```json" in content:
            # 删除开头的```json和结尾的```，以及两端的换行符
            response = content.split("```json")[1].split("```")[0].strip()
        elif "```python" in content:
            # 删除开头的```python和结尾的```，以及两端的换行符
            response = content.split("```python")[1].split("```")[0].strip()
        else:
            response = content
        full_response += response
        print("-" * 50)
        print(f"Completion tokens: {completion.usage.completion_tokens}")
        print("Current response:")
        print(content)

        # 检查是否达到 max_tokens 限制
        if completion.usage.total_tokens >= max_tokens:
            print("Response exceeds max tokens.")
            break
        elif completion.usage.completion_tokens < max_response_tokens:
            print("Response complete.")
            break
        else:
            print("Response incomplete. Continuing...")
            messages.extend([{"role": "assistant", "content": content},
                             {"role": "user", "content": "请继续。"}])

    return full_response
def call_openai_stream(
        client: openai.Client,
        system_prompt: str,
        user_prompt: str,
        model: str = "gpt-4-turbo",
        max_response_tokens: int = 4096,
        max_tokens: int = 128000,
        temperature: float = 0.5
):
    """调用 OpenAI API

    Args:
        client (OpenAI): OpenAI 客户端
        system_prompt (str): 系统提示词
        user_prompt (str): 用户提示词
        model (str): 模型名称. Defaults to "gpt-4-turbo".
        max_response_tokens (int, optional): 最大响应 token 数. Defaults to 4096.
        max_tokens (int, optional): 最大 token 数. Defaults to 128000.
        temperature (float, optional): 温度. Defaults to 0.5.

    Returns:    
        str: OpenAI API 返回的结果
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    full_response = ""

    # 写一个流式输出的clinet
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        max_completion_tokens=max_response_tokens,
        max_tokens=max_tokens,
        stream=True,
        temperature=temperature
    )
    return completion
