#!/bin/bash

# macOS打包脚本

# 确保使用正确的Python版本
PYTHON=python3

# 安装依赖
$PYTHON -m pip install pyinstaller wxPython pillow

# 清理之前的构建
rm -rf build dist

# 打包应用
$PYTHON -m PyInstaller --onedir --windowed --name="桌面宠物" --add-data="oiiai_cat.gif:." --add-data="work_incentive/work_incentive_config.json.example:work_incentive" -y main.py

# 复制配置文件示例到dist目录
cp work_incentive/work_incentive_config.json.example dist/桌面宠物.app/Contents/Resources/work_incentive/

echo "macOS应用打包完成，可执行文件位于dist/桌面宠物.app"
