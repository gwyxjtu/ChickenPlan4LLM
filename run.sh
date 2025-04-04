#!/bin/bash
set -e

if ! command -v streamlit &> /dev/null
then
    echo "Streamlit未安装, 请安装环境依赖"
    exit 1
fi

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
APP_PATH="$SCRIPT_DIR/web/app.py"

streamlit run "$APP_PATH"