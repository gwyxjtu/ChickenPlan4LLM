import xlwt

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
