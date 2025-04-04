@echo off
where streamlit >nul 2>&1
if %errorlevel% neq 0 (
    echo Streamlit未安装, 请安装环境依赖
    pause
    exit /b 1
)

start "" streamlit run .\web\app.py