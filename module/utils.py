from pathlib import Path
import json
from typing import Optional
import copy
import xlwt
import openai
import tiktoken
import transformers

PROJECT_PATH = str(Path(__file__).resolve().parents[1]).replace("\\", "/")

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
        model: str = "ep-20250215204507-wgzht",
        max_response_tokens: int = 16383,
        max_tokens: int = 16383,
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
        system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None,
        model: str = "Pro/deepseek-ai/DeepSeek-R1",
        last_messages: Optional[list] = None,
        last_response: Optional[str] = None,
        max_response_tokens: int = 16383,
        temperature: float = 0.5
):
    """调用 OpenAI API 并以流式输出的方式返回结果

    Args:
        client (OpenAI): OpenAI 客户端.
        system_prompt (str): 系统提示词. 首次请求时必传; 续写时可传 None.
        user_prompt (str): 用户提示词. 首次请求时必传; 续写时可传 None.
        model (str): 模型名称 (如 "gpt-4-turbo" 或 "o1-preview" 等).
        last_messages (list, optional): 上一次的消息. 续写时必传.
        last_response (str, optional): 上一次的回答. 续写时必传.
        max_response_tokens (int, optional): 最大响应 token 数. 传统模型对应 max_tokens, 而 o1 系列模型
            对应 max_completion_tokens. Defaults to 16383.
        temperature (float, optional): 温度. Defaults to 0.5.

    Returns:
        tuple: (completion, messages)
            completion: 流式返回的生成器
            messages: 当前对话上下文消息列表 (可用于后续续写)
    """
    # 判断 last_messages 是否为空
    if not last_messages:
        if system_prompt is None or user_prompt is None:
            raise ValueError("首次请求时必须提供 system_prompt 和 user_prompt.")
        if model == "deepseek-reasoner":
            # DeepSeek-R1 avoids adding a system prompt; all instructions should be contained within the user prompt
            messages = [{"role": "user", "content": system_prompt + user_prompt}]
        else:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
    else:
        # 续写时: 保留已有消息, 并追加上一次的回答和续写指令
        messages = copy.deepcopy(last_messages)
        messages.extend([
            {"role": "assistant", "content": last_response},
            # {"role": "user", "content": "请继续刚才的回答。注意：- 不要重复已生成的内容；- 直接进行内容续写，用'（接上文）'作为开头。"}
            # {"role": "user", "content": "请继续刚才的回答。注意，不要重复已生成的内容，直接进行内容续写，不得生成其他多余文字。"}
            {"role": "user", "content": "请继续刚才的回答。注意，不要重复已生成的内容，直接进行内容续写，不得生成其他多余文字，用'（接上文）'作为开头。"}
        ])

    # 根据 model 类型设置 max_completion_tokens 或 max_tokens
    extra_args = {}
    if "o1" in model.lower() or "o3" in model.lower():
        extra_args["max_completion_tokens"] = max_response_tokens
    else:
        extra_args["max_tokens"] = max_response_tokens

    # 写一个流式输出的 client
    # breakpoint()
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        stream=True,
        stream_options={"include_usage": True},
        **extra_args
    )
    # breakpoint()
    return completion, messages


def count_tokens(text: str, model: str = "gpt-4-turbo") -> int:
    if model == "deepseek-reasoner":
        # DeepSeek-R1 模型计算 token 数需指定编码方案
        chat_tokenizer_dir = PROJECT_PATH + "/module/deepseek_v3_tokenizer/"
        encoding = transformers.AutoTokenizer.from_pretrained(
            chat_tokenizer_dir,
            trust_remote_code=True
        )
    else:
        encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    return len(tokens)


def get_last_tokens(text: str, model: str = "gpt-4-turbo", num_tokens: int = 128) -> str:
    """
    获取输入文本中最后 num_tokens 个 token 对应的文本.

    Args:
        text (str): 原始文本.
        model (str): 模型名称, 用于选择合适的编码器. Default to "gpt-4-turbo".
        num_tokens (int): 要截取的 token 数量. Default to 128.

    Returns:
        str: 最后 num_tokens 个 token 解码后的文本.
    """
    if model == "deepseek-reasoner":
        # DeepSeek-R1 模型计算 token 数需指定编码方案
        chat_tokenizer_dir = PROJECT_PATH + "/module/deepseek_v3_tokenizer/"
        encoding = transformers.AutoTokenizer.from_pretrained(
            chat_tokenizer_dir,
            trust_remote_code=True
        )
    else:
        encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    # 截取最后 num_tokens 个 token
    last_tokens = tokens[-num_tokens:]
    # 解码回文本
    if isinstance(encoding, transformers.models.llama.tokenization_llama_fast.LlamaTokenizerFast):
        return encoding.decode(last_tokens, skip_special_tokens=True)
    else:
        return encoding.decode(last_tokens)
