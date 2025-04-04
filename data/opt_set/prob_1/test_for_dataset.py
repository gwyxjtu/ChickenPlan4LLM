'''
Author: guo_MateBookPro 867718012@qq.com
Date: 2025-02-27 15:05:17
LastEditTime: 2025-03-26 16:57:14
LastEditors: guo_MateBookPro 867718012@qq.com
FilePath: /ChickenPlan4LLM/data/opt_sets/test_for_dataset.py
Description: 雪花掩盖着哽咽叹息这离别
'''
prob = "prob_1"
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from module import code_template
from module.utils import PROJECT_PATH
import json


prob_path = Path(__file__).resolve().parents[0] / f"{prob}"
opt_para = json.load(open(prob_path / "opt_para.json", "r", encoding="utf-8"))
opt_code = open(prob_path / "opt_code.py", "r", encoding="utf-8").read()

# 路径修改

def gen_tmp():
    code_to_execute = code_template.format(solver_code=opt_code)
    para_path = Path(__file__).resolve().parents[2] / "log/opt_test/parameters.json"
    with open(para_path, "w", encoding="utf-8") as f:
        json.dump(opt_para, f, ensure_ascii=False, indent=4)
    tmp_path = Path(__file__).resolve().parents[2] / "log/opt_test/tmp.py"
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(code_to_execute)
    # 执行代码
    local_env = {
        "__builtins__": __builtins__,
        "project_path": PROJECT_PATH,
    }
    exec(code_to_execute, local_env)
    print(local_env["device_cap"])


if __name__ == "__main__":
    gen_tmp()
