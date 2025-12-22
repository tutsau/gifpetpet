#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""跨平台 GIF 桌面宠物程序

功能特性：
1. 支持自定义 GIF 动画
2. 鼠标拖拽移动
3. 鼠标悬停暂停动画并显示第一帧
4. 鼠标离开恢复动画
5. 窗口置顶显示
6. 支持透明背景
7. 跨平台兼容（Windows、Linux、macOS）
8. 点击宠物显示可爱对话框

使用方法：
1. 将你的 GIF 文件重命名为 pet.gif 并放在同一目录下
2. 运行程序：python3 main.py
3. 点击并拖拽宠物可以移动位置
4. 鼠标悬停在宠物上会暂停动画并显示第一帧
5. 鼠标离开后会恢复动画
6. 点击宠物会显示可爱的对话框

注意：在某些环境中可能需要安装依赖：
pip install pillow wxPython
"""

import wx
import sys
import os
from pet import FinalGIFDesktopPet
from taskbar import PetTaskBarIcon


def main():
    """程序主入口"""
    print(f"Python 版本: {sys.version}")
    print(f"wxPython 版本: {wx.__version__}")
    print(f"操作系统: {sys.platform}")
    
    try:
        app = wx.App(redirect=False)
        pet = FinalGIFDesktopPet()
        
        # 初始化托盘图标
        taskbar_icon = PetTaskBarIcon(pet)
        
        print("桌面宠物已启动，按 Ctrl+C 退出")
        app.MainLoop()
    except Exception as e:
        import traceback
        print(f"程序错误: {e}")
        traceback.print_exc()
        input("按回车退出...")


if __name__ == "__main__":
    main()