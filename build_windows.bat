@echo off

REM Windows打包脚本

REM 确保使用正确的Python版本
set PYTHON=python

REM 安装依赖
%PYTHON% -m pip install pyinstaller wxPython pillow

REM 清理之前的构建
rmdir /s /q build dist

REM 打包应用
%PYTHON% -m PyInstaller --onefile --windowed --name="桌面宠物" --add-data="oiiai_cat.gif;." --add-data="work_incentive/work_incentive_config.json.example;work_incentive" -y main.py

echo Windows应用打包完成，可执行文件位于dist/桌面宠物.exe
pause
