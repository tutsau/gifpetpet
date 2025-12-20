#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""配置模块

存储应用程序的所有配置信息。
"""

import os


class Config:
    """应用程序配置类"""
    
    # 宠物配置
    GIF_PATH = "oiiai_cat.gif"  # 默认GIF文件路径
    INIT_X = -100  # 初始X坐标（-100表示屏幕右侧内缩100px）
    INIT_Y = 100   # 初始Y坐标（顶部往下100px）
    TRANSPARENT_ALPHA = 255  # 窗口透明度（0-255）
    
    # 动画配置
    ANIMATION_PAUSE_FRAME = 0  # 鼠标悬停时暂停的帧索引
    
    # 对话框配置
    DIALOG_BACKGROUND_COLOR = (255, 200, 200, 220)  # 粉色半透明背景
    DIALOG_BORDER_COLOR = (255, 150, 150, 255)      # 粉色边框
    DIALOG_TEXT_COLOR = (50, 50, 50, 255)           # 深灰色文本
    DIALOG_FONT_SIZE = 14                           # 字体大小
    DIALOG_PADDING = 10                             # 内边距
    DIALOG_TAIL_HEIGHT = 10                         # 小尾巴高度
    DIALOG_ROUND_RADIUS = 15                        # 圆角半径
    DIALOG_AUTO_CLOSE_TIME = 3000                   # 自动关闭时间（毫秒）
    DIALOG_MAX_WIDTH = 200                          # 对话框最大宽度
    
    # 交互配置
    DRAG_THRESHOLD = 5  # 拖拽阈值（像素），小于此值视为点击
    
    @staticmethod
    def get_gif_path():
        """获取GIF文件的绝对路径
        
        Returns:
            str: GIF文件的绝对路径
        """
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), Config.GIF_PATH)
    
    @staticmethod
    def get_dialog_texts():
        """获取对话框随机文本列表
        
        Returns:
            list: 随机文本列表
        """
        return [
            "你好呀！",
            "主人，有什么事吗？",
            "今天天气真好！",
            "我是不是很可爱？",
            "需要我的帮助吗？",
            "主人，陪我玩一会儿吧～",
            "我会一直陪着你的！",
            "喵～喵～",
            "很高兴见到你！",
            "今天也要开心哦！"
        ]
