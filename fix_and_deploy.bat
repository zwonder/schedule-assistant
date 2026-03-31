@echo off
chcp 65001 > nul
REM 个人助理 - 问题修复和部署脚本(Windows版本)

echo ============================================================
echo   个人助理 - CloudBase数据库配置和部署工具
echo ============================================================
echo.

REM 检查Python环境
echo [检查] Python环境...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到Python,请先安装Python 3.7+
    pause
    exit /b 1
)
echo [成功] Python已安装
echo.

REM 安装依赖
echo [安装] 依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo [成功] 依赖安装成功
echo.

REM 部署数据库安全规则
echo [配置] 数据库安全规则...
echo.
echo 选择部署方式:
echo 1) 使用自动化脚本部署(需要腾讯云API密钥)
echo 2) 手动配置(通过CloudBase控制台)
echo.
set /p choice="请选择 (1/2): "

if "%choice%"=="1" (
    echo.
    echo [提示] 腾讯云API密钥获取:
    echo 访问: https://console.cloud.tencent.com/cam/capi
    echo.
    python deploy_database_rules.py
) else if "%choice%"=="2" (
    echo.
    echo [提示] 手动配置步骤:
    echo 1. 访问: https://console.cloud.tencent.com/tcb
    echo 2. 选择环境: zwonder-8gq5j7i479378123
    echo 3. 进入: 文档型数据库 -^> 选择集合 -^> 权限设置 -^> 安全规则
    echo 4. 为以下集合配置安全规则:
    echo    - pa_schedules
    echo    - pa_user_config
    echo    - pa_world_posts
    echo    - pa_blocklist
    echo.
    echo [文档] 详细配置规则请查看: CLOUDBASE_DATABASE_SETUP.md
    echo.
    pause
) else (
    echo [错误] 无效选择
    pause
    exit /b 1
)

echo.
echo ============================================================
echo [启动] 应用...
echo ============================================================
echo.
echo 访问地址: http://localhost:5001
echo.
echo [修复] 修复内容:
echo   √ 今日待办加载
echo   √ 所有日程列表
echo   √ 添加日程
echo   √ 标记任务完成
echo   √ 修改昵称
echo   √ 页面标题: 个人助理
echo.
echo ============================================================
echo.

REM 启动应用
python main.py
pause
