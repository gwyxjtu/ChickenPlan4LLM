import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import traceback
from module import code_template
from module.LLM import example_code_output

project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
project_path = project_path.replace("\\", "/")

local_env = {"project_path": project_path}

solver_code = example_code_output

code_to_execute = code_template.format(solver_code=solver_code)

print("=" * 80)
print("Code to execute:")
print("=" * 80)
print(code_to_execute)
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
