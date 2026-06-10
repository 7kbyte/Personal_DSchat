@echo off
chcp 65001 >nul
echo ========================================
echo   DeepSeek Chat - 打包为 EXE
echo ========================================
echo.

REM 安装依赖
echo [1/4] 安装依赖...
pip install pyinstaller pywebview pillow -q

REM 清理旧的构建
echo [2/4] 清理旧构建...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM 生成图标
echo [3/4] 生成图标...
if exist "ds.png" (
    python -c "from PIL import Image; img=Image.open('ds.png'); img.save('ds.ico',format='ICO',sizes=[(256,256)])" 2>nul
)

REM 使用 spec 文件打包（包含静态资源）
echo [4/4] 开始打包...
pyinstaller DeepSeekChat.spec

echo.
echo ========================================
echo   打包完成！
echo   EXE 文件在: dist\DeepSeekChat.exe
echo ========================================
echo.
echo 提示：
echo  - 首次启动时设置 API Key
echo  - 数据保存在 %%APPDATA%%\DeepSeekChat\
echo ========================================
pause
