<div style="font-size: 14pt;">
  <a href="./README.md">中文</a> |
  <a href="./README_en.md">English</a>
</div>



# ChickenPlan4LLM

通过 LLM 赋能，提供能源系统规划、运行、设计的自动化解决方案。



## 代码说明

### 项目核心结构

```bash
key_dirs/
├── data/
│   ├── device_set/
│   ├── load/
│   ├── solar/
│   └── opt_set/
├── web/
│   ├── webui_pages/
│   ├── app.py
├── module/
│   ├── LLM/
│   ├── code_template.py
│   └── utils.py
└── log/
```

### 日志记录说明

- `log` 目录下存放日志文件
- `log/{功能}_{时间}` 目录下存放对应功能的日志文件
- 对于 `log/Planning_{时间}` 目录下的文件：
  - `conversations.log` 存放大模型对话记录
  - `parameters_gen.json` 存放生成的能源系统建模参数
  - `code_gen.py` 存放生成的能源系统规划代码
  - `opt_res` 目录下存放能源系统规划结果

### 运行说明

运行代码前，请确保安装了以下依赖：

```bash
$ pip install -r requirements.txt
```

### 快速启动

选择下列任一方式启动：

#### 通过脚本 (推荐)
```bash
# Windows
$ ./run.bat

# Linux/MacOS
$ chmod +x run.sh
```

#### 直接执行
```bash
$ streamlit run ./web/app.py
```
