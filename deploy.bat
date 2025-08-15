@echo off
:: ========================================
:: Windows 批处理脚本：部署项目到服务器
:: 自动排除 .git, .venv, __pycache__ 等文件夹
:: ========================================

:: ============= 配置区 ===============
set "LOCAL_DIR=."                 :: 本地项目路径（当前目录）
set "TEMP_DIR=./_deploy_temp"     :: 临时目录（用于排除后复制）
set "REMOTE_USER=rogerwang2008"            :: 服务器用户名
set "REMOTE_HOST=WangHai-ThinkPadX1" :: 服务器地址
set "REMOTE_PATH=~/scripts/cloudflare_ddns"  :: 服务器目标路径
set "KEY=E:\Projects\Web-WCJ\id_rsa"

:: 要排除的目录（robocopy 格式，每行一个 /XD 后面的）
set "EXCLUDE_DIRS=.git .venv __pycache__ _deploy_temp"

:: SSH 端口（可选，默认22）
set "SSH_PORT=22"
:: ============= 配置区结束 =============


echo Cleaning up temporary directory...
if exist "%TEMP_DIR%" rd /s /q "%TEMP_DIR%"

echo Copying files...
robocopy "%LOCAL_DIR%" "%TEMP_DIR%" /E /COPYALL /XD "%EXCLUDE_DIRS%"

if %ERRORLEVEL% LEQ 4 (
    echo Files copied!
) else (
    echo Error copying files: %ERRORLEVEL%
    pause
    exit /b 1
)

echo Uploading %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_PATH% ...
scp -i "%KEY%" -r -P %SSH_PORT% "%TEMP_DIR%/" "%REMOTE_USER%@%REMOTE_HOST%:%REMOTE_PATH%"

if %ERRORLEVEL% == 0 (
    echo Deployment completed.
) else (
    echo Error uploading to server.
    pause
    exit /b 1
)

echo Cleaning up...
@REM rd /s /q "%TEMP_DIR%"

echo.
echo Deployment finished.
pause
