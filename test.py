# ----------------------------------------------------------------------------------------------------------------------
# 测试 gurobi
# ----------------------------------------------------------------------------------------------------------------------
# from easydict import EasyDict as Edict
import gurobipy as gp

# 创建模型
model = gp.Model()

# 创建变量
x1 = model.addVar(vtype=gp.GRB.INTEGER, name='x1')
x2 = model.addVar(ub=3, vtype=gp.GRB.INTEGER, name='x2')
x1_ = model.addVars(range(1, 3), vtype=gp.GRB.INTEGER, name='x1_')
x2_ = model.addVars(range(1, 6), vtype=gp.GRB.INTEGER, name='x2_')
# x3 = model.addVar(vtype=gp.GRB.INTEGER, name='x4')
# x3 = model.addVars(range(0, 6), vtype=gp.GRB.INTEGER, name='x3')

# 更新变量环境
model.update()

# 创建目标函数
model.setObjective(100 * x1 + 40 * x2, sense=gp.GRB.MINIMIZE)

# 创建约束条件
left_1 = x1 + x2_[1]
left_2 = x1 + x2_[1] + x2_[2]
model.addConstr(left_1 >= 4, name='9:00-10:00')
model.addConstr(left_2 >= 3, name='10:00-11:00')
model.addConstr(x1 + x2_[1] + x2_[2] + x2_[3] >= 4, name='11:00-12:00')
model.addConstr(x1_[1] + x2_[1] + x2_[2] + x2_[3] + x2_[4] >= 6, name='12:00-13:00')
model.addConstr(x1_[2] + x2_[2] + x2_[3] + x2_[4] + x2_[5] >= 5, name='13:00-14:00')
model.addConstr(x1 + x2_[3] + x2_[4] + x2_[5] >= 6, name='14:00-15:00')
model.addConstr(x1 + x2_[4] + x2_[5] >= 8, name='15:00-16:00')
model.addConstr(x1 + x2_[5] >= 8, name='16:00-17:00')

# 此处, sum(x1_) 和 x1_.sum() 结果不同, 因为 sum(x1_) 对字典进行键相加
# 更标准的写法是使用 gp.quicksum(x1_) 和 gp.quicksum(x2_)
model.addConstr(x1_.sum() == x1, name='x1')
model.addConstr(x2_.sum() == x2, name='x2')

# 执行最优化
model.optimize()

# 打印所有变量名称及其索引
variables = model.getVars()
values = [model.getVars()[i].x for i in range(len(model.getVars()))]
print("\n已创建的变量列表: variables")
print(variables)
print()

print("x1:", x1, "variables[0]:", variables[0])
if variables[0] is x1:
    print("Yes, variables[0] is x1")
    print("variables[0] id:", id(variables[0]), type(id(variables[0])))
    print("x1 id:", id(x1), type(id(x1)))
    print(id(x1) == id(variables[0]))
else:
    print("No")

test_0 = gp.quicksum(variables[i] for i, j in enumerate(variables))
test_1 = gp.quicksum(variables)
test_2 = gp.quicksum(x2_)
test_3 = gp.quicksum(x2_[i] for i in x2_)
test_t = gp.LinExpr()
test_t = test_t + test_2
print(test_0, "\tvalue: ", test_0.getValue(), sep="")
print(test_1, "\tvalue: ", test_1.getValue(), sep="")
print(test_2, "\tvalue: ", test_2.getValue(), sep="")
print(test_3, "\tvalue: ", test_3.getValue(), sep="")
print(test_t, "\tvalue: ", test_t.getValue(), sep="")

# # 获取 variables 字典
# var_set = {}
# for var in variables:
#     index = var.varName.find("[")
#     # vars
#     if index != -1:
#         var_name = var.varName.split("[")[0]
#         var_i = int(var.varName.split("[")[1].split("]")[0])
#         if var_name in var_set:
#             var_set[var_name][var_i] = var
#         else:
#             var_set[var_name] = {}
#             var_set[var_name][var_i] = var
#         print("Variable name:", var_name, "[{}]".format(var_i), end="\t")
#         # print("Index:", var.index)
#         print("Index:", var.index, end="\t")
#         print("Value:", var.x)
#     # var
#     else:
#         var_name = var.varName
#         var_set[var_name] = var
#         print("Variable name:", var_name, end="\t")
#         # print("Index:", var.index)
#         print("Index:", var.index, end="\t")
#         print("Value:", var.x)
#
# test_4 = gp.quicksum(var_set["x1_"][i] for i in var_set["x1_"])
# test_5 = x1 + x2
# print(test_4)
# print(test_5)
# for i in var_set["x1_"]:
#     print(i, type(i))
# for i in var_set:
#     print(i, type(i))
# print("length:", len(var_set))
# print(var_set["x2_"][1])
