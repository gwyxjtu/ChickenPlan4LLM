'''
Author: guo_MateBookPro 867718012@qq.com
Date: 2025-01-03 11:27:48
LastEditTime: 2025-02-27 15:07:35
LastEditors: guo_MateBookPro 867718012@qq.com
FilePath: /ChickenPlan4LLM/module/LLM/__init__.py
Description: 雪花掩盖着哽咽叹息这离别
'''
from pathlib import Path
import json
from module.LLM.prompt_template import (
    info_prompt_template,
    param_prompt_template,
    code_prompt_template,
    code_prompt_cot_template,
)
from module.LLM.example4prompts import (
    example_user_input,
    example_info_output,
    example_info_input,
    example_param_output,
    example_param_input,
    example_code_output,
)

base_path = Path(__file__).parent
with open(base_path / "user_input.json", "r", encoding="utf-8") as f:
    user_input_json = json.load(f)
with open(base_path / "user_input_detail.json", "r", encoding="utf-8") as f:
    user_input_detail_json = json.load(f)

__all__ = [
    "info_prompt_template",
    "param_prompt_template",
    "code_prompt_template",
    "example_user_input",
    "example_info_output",
    "example_info_input",
    "example_param_output",
    "example_param_input",
    "example_code_output",
    "user_input_json",
    "user_input_detail_json",
]
