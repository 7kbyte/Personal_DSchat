@echo off
chcp 65001 >nul
echo ========================================
echo   DeepSeek Chat - 打包为 EXE
echo ========================================
echo.

REM 安装依赖
echo [1/3] 安装依赖...
pip install pyinstaller -q
pip install pywebview -q

REM 清理旧的构建
echo [2/3] 清理旧构建...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM 打包
echo [3/4] 转换图标...
python -c "from PIL import Image; img=Image.open('ds.png'); img.save('ds.ico',format='ICO',sizes=[(256,256)])" 2>nul

echo [4/4] 开始打包...
pyinstaller --onefile --noconsole --name "DeepSeekChat" --icon=ds.ico main.py

echo.
echo ========================================
echo   打包完成！
echo   EXE 文件在: dist\DeepSeekChat.exe
echo ========================================
echo.
echo 提示：
echo  - 首次启动时设置 API Key
echo  - 历史记录保存在 %%APPDATA%%\DeepSeekChat\
echo ========================================
pause
