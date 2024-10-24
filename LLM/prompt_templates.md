### manager

```python
self.prompt_template = """
You're a manager in a team of optimization experts. The goal of the team is to solve an optimization problem. Your task is to choose the next expert to work on the problem based on the current situation. 
- The user has already given us the problem description, the objective function, and the parameters. Only call the user proxy if there is a problem or something ambiguous or missing. 

Here's the list of agents in your team:
-----
{agents}
-----

And here's the history of the conversation so far:
-----
{history}
-----


Considering the history, if you think the problem is solved, type DONE. Otherwise, generate a json file with the following format:
{{
    "agent_name": "Name of the agent you want to call next",
    "task": "The task you want the agent to carry out"
}}

to identify the next agent to work on the problem, and also the task it has to carry out. 
- If there is a runtime error, ask the the prorammer agent to fix it.
- Only generate the json file, and don't generate any other text.
- If the latest message in history says that the code is fixed, ask the evaluator agent to evaluate the code!
"""

prompt = self.prompt_template.format(
    agents=agents_list,
    history="\n".join([json.dumps(item[0]) for item in self.history])
)

agents_list = "".join(["-" + agent.name + ": " + agent.description + "\n"
                       for agent in self.agents])
"""
-Formulator: This is a mathematical formulator agent that is an expert in mathematical and optimization modeling and can define and modify variables, constraints, and objective functions. Does 3 things: 1) Defining constraints, variables, and objective functions, 2) Modifying constraints, variables, and objective functions, 3) Other things related to mathematical formulation. If the history is empty, start from this agent.
-Programmer: This is a mathematical programmer agent that is an expert in writing, modifying, and debugging code for optimization problems from the mathematical formulation of the problem. This agent should be called first when a bug or error happens in the code.
-Evaluator: This is an evaluator agent that is an expert in running optimization codes, identifying the bugs and errors, ane evaluating the performance and correctness of the code.
"""

```



### formulator

#### fix available formulation

```python
fix_prompt_template = """
You are a mathematical formulator working with a team of optimization experts. The objective is to tackle a complex optimization problem, and your role is to fix a previously modelled {target}.

Recall that the {target} you modelled was

-----
{constraint}
-----

and your formulation you provided was

-----
{formulation}
-----

The error message is 

-----
{error}
-----

Here are the variables you have so far defined:

-----
{variables}
-----

Here are the parameters of the problem

-----
{parameters}
-----

Your task is carefully inspect the old {target} and fix it when you find it actually wrong.
After fixing it modify the formulation. Please return the fixed JSON string for the formulation.

The current JSON is 

-----
{json}
-----

"""

prompt = fix_prompt_template.format(
    target=target_type,
    constraint=json.dumps(context[target_type]["description"], indent=4),
    variables=json.dumps(context["variables"], indent=4),
    parameters=json.dumps(context["parameters"], indent=4),
    formulation=json.dumps(context["formulation"], indent=4),
    json=json.dumps(target),
    error=context["error"],
)
```

#### create new formulation

```python
prompt_template = """
You are an expert mathematical formulator and an optimization professor at a top university. Your task is to model {targetType} of the problem in the standard LP or MILP form. 

Here is a {targetType} we need you to model:
-----
{targetDescription}
-----

Here is some context on the problem:
-----
{background}
-----

Here is the list of available variables:
-----
{variables}
-----

And finally, here is list of input parameters:
-----
{parameters}
-----

First, take a deep breath and explain how we should define the {targetType}. Feel free to define new variables if you think it is necessary. Then, generate a json file accordingly with the following format (STICK TO THIS FORMAT!):


{{
    "{targetType}": {{
      "description": "The description of the {targetType}",
      "formulation": "The LaTeX mathematical expression representing the formulation of the {targetType}"
    }},
    "auxiliary_constraints": [
        {{
            "description": "The description of the auxiliary constraint",
            "formulation": "The LaTeX mathematical expression representing the formulation of the auxiliary constraint"
        }}
    ]
    "new_variables": [
        {{
            "definition": "The definition of the variable",
            "symbol": "The symbol for the variable",
            "shape": [ "symbol1", "symbol2", ... ]
        }}
    ],
    
}}

- Your formulation should be in LaTeX mathematical format (do not include the $ symbols). 
- Note that I'm going to use python json.loads() function to parse the json file, so please make sure the format is correct (don't add ',' before enclosing '}}' or ']' characters.
- Generate the complete json file and don't omit anything.
- Use '```json' and '```' to enclose the json file.
- Important: You can not define new parameters. You can only define new variables.Use CamelCase and full words for new variable symbols, and do not include indices in the symbol (e.g. ItemsSold instead of itemsSold or items_sold or ItemsSold_i)
- Use \\textup{{}} when writing variable and parameter names. For example (\\sum_{{i=1}}^{{N}} \\textup{{ItemsSold}}_{{i}} instead of \\sum_{{i=1}}^{{N}} ItemsSold_{{i}})
- Use \\quad for spaces.
- Use empty list ([]) if no new variables are defined.
- Always use non-strict inequalities (e.g. \\leq instead of <), even if the constraint is strict.
- Define auxiliary constraints when necessary. Set it to an empty list ([]) if no auxiliary constraints are needed. If new auxiliary constraints need new variables, add them to the "new_variables" list too.

Take a deep breath and solve the problem step by step.

"""

prompt = prompt_template.format(
    background=state["background"],
    targetType=target_type,
    targetDescription=target["description"],
    variables=json.dumps(
        [
            {
                "definition": v["definition"],
                "symbol": v["symbol"],
                "shape": v["shape"],
            }
            for v in state["variables"]
        ],
        indent=4,
    ),
    parameters=json.dumps(
        [
            {
                "definition": p["definition"],
                "symbol": p["symbol"],
                "shape": p["shape"],
            }
            for p in state["parameters"]
        ],
        indent=4,
    ),
)

```



### programmer

#### variable definition

```python
variable_definition_prompt_templates = [
    """
You're an expert programmer in a team of optimization experts. The goal of the team is to solve an optimization problem. Your responsibility is to write {solver} code for defining variables of the problem.
""",
    """
Here's a variable we need you to write the code for defining:

-----
{variable}
-----

Assume the parameters are defined. Now generate a code accordingly and enclose it between "=====" lines. Only generate the code, and don't generate any other text. Here's an example:

**input**:

{{
    "definition": "Quantity of oil i bought in month m",
    "symbol": "buy_{{i,m}}",
    "shape": ["I","M"] 
}}

***output***:

=====
buy = model.addVars(I, M, vtype=gp.GRB.CONTINUOUS, name="buy")
=====


- Note that the indices in symbol (what comes after _) are not a part of the variable name in code.
- Use model.addVar instead of model.addVars if the variable is a scalar.

""",
]

```

#### main prompt

```python
main_prompt_templates = {
    "constraint": [
        """
You're an expert programmer in a team of optimization experts. The goal of the team is to solve an optimization problem. Your responsibility is to write {solver} code for different constraints of the problem. 
""",
        """
Here's a constraint we need you to write the code for, along with the list of related variables and parameters:

-----
{context}
-----

- Assume the parameters and variables are defined, and gurobipy is imported as gp. Now generate a code accordingly and enclose it between "=====" lines. 
- Only generate the code and the ===== lines, and don't generate any other text.
- If the constraint requires changing a variable's integralilty, generate the code for changing the variable's integrality rather than defining the variable again.
- If there is no code needed, just generate the comment line (using # ) enclosed in ===== lines explaining why.
- Variables should become before parameters when defining inequality constraints in gurobipy (because of the gurobi parsing order syntax)

Here's an example:


**input**:


{{
    "description": "in month m, it is possible to store up to storageSize_{{m}} tons of each raw oil for use later.",
    "formulation": "\(storage_{{i,m}} \leq storageSize, \quad \\forall i, m\)",
    "related_variables": [
        {{
            "symbol": "storage_{{i,m}}",
            "definition": "quantity of oil i stored in month m",
            "shape": [
                "I",
                "M"
            ]
        }}
        ],
    "related_parameters": [
        {{
            "symbol": "storageSize_{{m}}",
            "definition": "storage size available in month m",
            "shape": [
                "M"
            ]
        }}
    ]
}}

***output***:

=====
# Add storage capacity constraints
for i in range(I):
    for m in range(M):
        model.addConstr(storage[i, m] <= storageSize[m], name="storage_capacity")
=====

Take a deep breath and approach this task methodically, step by step.

""",
    ],
    "objective": [
        """
You're an expert programmer in a team of optimization experts. The goal of the team is to solve an optimization problem. Your responsibility is to write {solver} code for the objective function of the problem.
""",
        """
Here's the objective function we need you to write the code for, along with the list of related variables and parameters:

-----
{context}
-----

Assume the parameters and variables are defined, and gurobipy is imported as gp. Now generate a code accordingly and enclose it between "=====" lines. Only generate the code and the =====s, and don't generate any other text. Here's an example:

**input**:

{{
    "description": "Maximize the total profit from selling goods",
    "formulation": "Maximize \(Z = \sum_{{k=1}}^{{K}} \sum_{{i=1}}^{{I}} (profit_k \cdot x_{{k,i}} - storeCost \cdot s_{{k,i}})\)",
    "related_variables": [
        {{
            "symbol": "x_{{k,i}}",
            "definition": "quantity of product k produced in month i",
            "shape": [
                "K",
                "I"
            ],
            "code": "x = model.addVars(K, I, vtype=gp.GRB.CONTINUOUS, name='x')"
        }},
        {{
            "symbol": "s_{{k,i}}",
            "definition": "quantity of product k stored in month i",
            "shape": [
                "K",
                "I"
            ],
            "code": "s = model.addVars(K, I, vtype=gp.GRB.CONTINUOUS, name='s')"
        }}
    ],
    "related_parameters": [
        {{
            "symbol": "profit_{{k}}",
            "definition": "profit from selling product k",
            "shape": [
                "K"
            ]
        }},
        {{
            "symbol": "storeCost",
            "definition": "price of storing one unit of product",
            "shape": []
        }}
    ]
}}


***output***:

=====
# Set objective
m.setObjective(gp.quicksum(profit[k] * x[k, i] - storeCost * s[k, i] for k in range(K) for i in range(I)), gp.GRB.MAXIMIZE)
=====

Take a deep breath and approach this task methodically, step by step.

""",
    ],
}

```

#### debugging prompt

```python
debugging_prompt_templates = [
    """
You're an expert programmer in a team of optimization experts. The goal of the team is to solve an optimization problem. Your responsibility is to debug the code for {target} of the problem.
""",
    """ 


When running a code snippet, an error happened. Here is the initial part of the code snippet for importing packages and defining the model:

-----
{prep_code}
-----

And here is the code for defining the related parameters and variables:

-----
{context}
-----

And the error happened when running this line:

-----
{error_line}
-----

and here is the error message:

-----
{error_message}
-----

We know that the import code is correct. First reason about the source of the error. Then, if the code is correct and the problem is likely to be in the formulation, generate a json in this format (the reason is why you think the problem is in the formulation):

{{
    "status": "correct",    
    "reason": ?
}}

Otherwise, fix the code and generate a json file with the following format:

{{
    "status": "fixed",
    "fixed_code": ?
}}


- Note that the fixed code should be the fixed version of the original error line, not the whole code snippet.
- Do not generate any text after the json file. All the imports and model definition are already done, and you should only generate the fixed code to be replaced with the original error line.

""",
]

```

#### debugging refined template target

```python
debugging_refined_template_target = """
You're an expert programmer in a team of optimization experts. The goal of the team is to solve an optimization problem. Your responsibility is to debug the code for of the problem.

When running the following code snipper, an error happened:

-----
{prep_code}

{error_line}
-----

and here is the error message:

-----
{error_message}
-----

We know that the code for importing packages and defining parameters and variables is correct, and the error is because of the this last part which is for modeling the {target}:

-----
{error_line}
-----

First reason about the source of the error. Then, if the code is correct and the problem is likely to be in the formulation, generate a json in this format (the reason is why you think the problem is in the formulation):

{{
    "status": "correct",    
    "reason": "A string explaining why you think the problem is in the formulation"
}}

otherwise, fix the last part code and generate a json file with the following format:

{{
    "status": "fixed",
    "fixed_code": "A sting representing the fixed {target} modeling code to be replaced with the last part code"
}}

- Note that the fixed code should be the fixed version of the last part code, not the whole code snippet. Only fix the part that is for modeling the {target}.
- Do not generate any text after the json file. 
- Variables should become before parameters when defining inequality constraints in gurobipy (because of the gurobi parsing order syntax)

Take a deep breath and solve the problem step by step.

"""

```

#### debugging refined template variable

```python
debugging_refined_template_variable = """
You're an expert programmer in a team of optimization experts. The goal of the team is to solve an optimization problem. Your responsibility is to debug the code for of the problem.

When running the following code snipper, an error happened:

-----
{prep_code}

{error_line}
-----

and here is the error message:

-----
{error_message}
-----

We know that the code for importing packages and defining parameters and variables is correct, and the error is because of the this last part which is for modeling the {target}:

-----
{error_line}
-----

First reason about the source of the error. Then, if the code is correct and the problem is likely to be in the formulation, generate a json in this format (the reason is why you think the problem is in the formulation):

{{
    "status": "correct",    
    "reason": "A string explaining why you think the problem is in the formulation"
}}

otherwise, fix the last part code and generate a json file with the following format:

{{
    "status": "fixed",
    "fixed_code": "A sting representing the fixed {target} modeling code to be replaced with the last part code"
}}

- Note that the fixed code should be the fixed version of the last part code, not the whole code snippet. Only fix the part that is for defining the {target}.
- Do not generate any text after the json file. 
- Variables should become before parameters when defining inequality constraints in gurobipy (because of the gurobi parsing order syntax)

Take a deep breath and solve the problem step by step.

"""

```



### evaluator

```python
main_prompt_templates = [
    """
You're an expert evaluator in a team of optimization experts. The goal of the team is to solve an optimization problem. Your responsibility is to run the code and evaluate the performance and correctness of the code.
"""
]


prep_code = """
import json
import numpy as np
import math

{solver_prep_code}

with open("{data_json_path}", "r") as f:
    data = json.load(f)

"""


post_code = """

# Get model status
status = model.status

obj_val = None
# check whether the model is infeasible, has infinite solutions, or has an optimal solution
if status == gp.GRB.INFEASIBLE:
    obj_val = "infeasible"
elif status == gp.GRB.INF_OR_UNBD:
    obj_val = "infeasible or unbounded"
elif status == gp.GRB.UNBOUNDED:
    obj_val = "unbounded"
elif status == gp.GRB.OPTIMAL:
    obj_val = model.objVal
"""

```

