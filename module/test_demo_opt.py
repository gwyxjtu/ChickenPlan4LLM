'''
Author: guo_MateBookPro 867718012@qq.com
Date: 2025-02-27 15:05:17
LastEditTime: 2025-03-26 15:56:25
LastEditors: guo_MateBookPro 867718012@qq.com
FilePath: /ChickenPlan4LLM/module/test_demo_opt.py
Description: 雪花掩盖着哽咽叹息这离别
'''
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from module.LLM import (
    example_code_output,
    example_param_output
)
from module import code_template
import json

# 增加主函数
def gen_tmp():
    code_gen = code_template.format(solver_code=example_code_output)
    target_path = Path(__file__).resolve().parents[1] / "log/opt_test/parameters.json"
    target_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = Path(__file__).resolve().parents[1] / "log/opt_test/tmp.py"
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(code_gen)
    # example_param_output 写入parameter.json

    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(example_param_output, f, ensure_ascii=False, indent=4)
if __name__ == "__main__":
    gen_tmp()