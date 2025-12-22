#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""配置模块

存储应用程序的所有配置信息。
"""

import os
import json


class Config:
    """应用程序配置类"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        "GIF_PATH": "oiiai_cat.gif",  # 默认GIF文件路径
        "INIT_X": -100,  # 初始X坐标（-100表示屏幕右侧内缩100px）
        "INIT_Y": 100,   # 初始Y坐标（顶部往下100px）
        "TRANSPARENT_ALPHA": 255,  # 窗口透明度（0-255）
        "ANIMATION_PAUSE_FRAME": 0,  # 鼠标悬停时暂停的帧索引
        "DIALOG_BACKGROUND_COLOR": (255, 200, 200, 220),  # 粉色半透明背景
        "DIALOG_BORDER_COLOR": (255, 150, 150, 255),      # 粉色边框
        "DIALOG_TEXT_COLOR": (50, 50, 50, 255),           # 深灰色文本
        "DIALOG_FONT_SIZE": 14,                           # 字体大小
        "DIALOG_PADDING": 10,                             # 内边距
        "DIALOG_TAIL_HEIGHT": 10,                         # 小尾巴高度
        "DIALOG_ROUND_RADIUS": 15,                        # 圆角半径
        "DIALOG_AUTO_CLOSE_TIME": 3000,                   # 自动关闭时间（毫秒）
        "DIALOG_MAX_WIDTH": 200,                          # 对话框最大宽度
        "DRAG_THRESHOLD": 5                               # 拖拽阈值（像素），小于此值视为点击
    }
    
    # 用户配置文件路径
    @staticmethod
    def get_user_config_path():
        """获取用户配置文件的路径
        
        Returns:
            str: 用户配置文件的路径
        """
        import sys
        
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller打包后，用户配置文件放在用户目录
            return os.path.join(os.path.expanduser("~"), ".pet_config.json")
        # 未打包时，配置文件放在当前目录
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), ".pet_config.json")
    
    # 用户配置文件路径
    USER_CONFIG_PATH = get_user_config_path.__func__()
    
    # 初始化类变量
    GIF_PATH = DEFAULT_CONFIG["GIF_PATH"]
    INIT_X = DEFAULT_CONFIG["INIT_X"]
    INIT_Y = DEFAULT_CONFIG["INIT_Y"]
    TRANSPARENT_ALPHA = DEFAULT_CONFIG["TRANSPARENT_ALPHA"]
    ANIMATION_PAUSE_FRAME = DEFAULT_CONFIG["ANIMATION_PAUSE_FRAME"]
    DIALOG_BACKGROUND_COLOR = DEFAULT_CONFIG["DIALOG_BACKGROUND_COLOR"]
    DIALOG_BORDER_COLOR = DEFAULT_CONFIG["DIALOG_BORDER_COLOR"]
    DIALOG_TEXT_COLOR = DEFAULT_CONFIG["DIALOG_TEXT_COLOR"]
    DIALOG_FONT_SIZE = DEFAULT_CONFIG["DIALOG_FONT_SIZE"]
    DIALOG_PADDING = DEFAULT_CONFIG["DIALOG_PADDING"]
    DIALOG_TAIL_HEIGHT = DEFAULT_CONFIG["DIALOG_TAIL_HEIGHT"]
    DIALOG_ROUND_RADIUS = DEFAULT_CONFIG["DIALOG_ROUND_RADIUS"]
    DIALOG_AUTO_CLOSE_TIME = DEFAULT_CONFIG["DIALOG_AUTO_CLOSE_TIME"]
    DIALOG_MAX_WIDTH = DEFAULT_CONFIG["DIALOG_MAX_WIDTH"]
    DRAG_THRESHOLD = DEFAULT_CONFIG["DRAG_THRESHOLD"]
    
    # 用户配置
    user_config = DEFAULT_CONFIG.copy()
    
    @classmethod
    def load_user_config(cls):
        """加载用户配置"""
        try:
            if os.path.exists(cls.USER_CONFIG_PATH):
                with open(cls.USER_CONFIG_PATH, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    cls.user_config.update(loaded_config)
                    # 更新类变量
                    for key, value in cls.user_config.items():
                        if hasattr(cls, key):
                            setattr(cls, key, value)
                print("用户配置加载成功")
            else:
                print("用户配置文件不存在，使用默认配置")
        except Exception as e:
            print(f"用户配置加载失败: {e}")
            # 加载失败时使用默认配置
            cls.user_config = cls.DEFAULT_CONFIG.copy()
    
    @classmethod
    def save_user_config(cls):
        """保存用户配置"""
        try:
            with open(cls.USER_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(cls.user_config, f, ensure_ascii=False, indent=2)
            print("用户配置保存成功")
        except Exception as e:
            print(f"用户配置保存失败: {e}")
    
    @classmethod
    def set_gif_path(cls, gif_path):
        """设置GIF文件路径并保存配置
        
        Args:
            gif_path: GIF文件的路径
        """
        cls.GIF_PATH = gif_path
        cls.user_config["GIF_PATH"] = gif_path
        cls.save_user_config()
    
    @staticmethod
    def get_gif_path():
        """获取GIF文件的绝对路径
        
        Returns:
            str: GIF文件的绝对路径
        """
        import sys
        import os
        
        # PyInstaller打包后，资源文件会放在sys._MEIPASS目录下
        if hasattr(sys, '_MEIPASS'):
            # 如果是用户自定义的GIF路径，直接返回
            if Config.user_config.get("GIF_PATH") != Config.DEFAULT_CONFIG["GIF_PATH"]:
                return Config.GIF_PATH
            # 否则使用内置的资源文件
            return os.path.join(sys._MEIPASS, Config.GIF_PATH)
        # 未打包时，使用当前文件所在目录
        if Config.user_config.get("GIF_PATH") != Config.DEFAULT_CONFIG["GIF_PATH"]:
            return Config.GIF_PATH
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), Config.GIF_PATH)
    
    @staticmethod
    def get_dialog_texts():
        """获取对话框随机文本列表
        
        Returns:
            list: 随机文本列表
        """
        return []


# 初始化时加载用户配置
Config.load_user_config()