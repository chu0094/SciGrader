@echo off
chcp 65001 >nul
echo ========================================
echo   SciGrader 学生端 - 启动程序
echo ========================================
echo.

REM 检查 Python 环境
echo [1/3] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python 环境，请先安装 Python 3.8+
    pause
    exit /b 1
)
echo [✓] Python 环境正常

REM 检查并安装依赖
echo [2/3] 检查依赖包...
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装依赖包...
    pip install -r requirements.txt
) else (
    echo [✓] 依赖包已安装
)

REM 启动应用
echo [3/3] 启动 SciGrader 前端服务...
echo.
echo ========================================
echo   服务即将启动...
echo   访问地址：http://localhost:8501
echo   按 Ctrl+C 可停止服务
echo ========================================
echo.

streamlit run app.py --server.port=8501 --server.headless=true

pause
