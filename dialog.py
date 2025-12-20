#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对话框模块

封装了可爱的自定义对话框功能，用于桌面宠物的交互反馈。
"""

import wx


class CuteDialog(wx.Dialog):
    """可爱的自定义对话框"""
    
    def __init__(self, parent, text="你好！", color=(255, 150, 150, 230), text_color=(255, 255, 255)):
        """初始化对话框
        
        Args:
            parent: 父窗口
            text: 对话框显示的文本
            color: 对话框背景颜色，格式为(r, g, b, alpha)
            text_color: 文本颜色，格式为(r, g, b)
        """
        # 计算合适的对话框尺寸
        dc = wx.ScreenDC()
        dc.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        text_width, text_height = dc.GetTextExtent(text)
        
        # 添加边距和装饰
        padding = 20
        width = text_width + padding * 2
        height = text_height + padding * 2
        
        # 设置最小尺寸
        width = max(width, 120)
        height = max(height, 80)
        
        # 创建对话框（无边框、透明背景）
        style = wx.DIALOG_NO_PARENT | wx.STAY_ON_TOP
        super(CuteDialog, self).__init__(parent, wx.ID_ANY, "", style=style, size=(width, height))
        
        # 配置属性
        self.background_color = color
        self.text_color = text_color
        
        # 设置窗口样式
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetTransparent(240)  # 半透明
        
        # 创建文本控件
        self.text_ctrl = wx.StaticText(self, wx.ID_ANY, text, style=wx.ALIGN_CENTER)
        self.text_ctrl.SetForegroundColour(wx.Colour(*text_color))
        self.text_ctrl.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        # 设置布局
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.text_ctrl, 1, wx.EXPAND | wx.ALL, 15)
        self.SetSizer(sizer)
        self.Layout()
        
        # 绑定绘制事件
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)  # 防止闪烁
        
        # 自动调整尺寸
        self.Fit()
        
    def on_paint(self, event):
        """绘制可爱的对话框背景"""
        dc = wx.AutoBufferedPaintDC(self)
        
        # 获取对话框尺寸
        width, height = self.GetSize()
        
        # 使用正确的方式创建GraphicsContext和路径
        gc = wx.GraphicsContext.Create(dc)
        if gc:
            # 创建圆角矩形路径
            corner_radius = 20
            path = gc.CreatePath()
            
            # 绘制圆角矩形路径
            path.MoveToPoint(corner_radius, 0)
            path.AddLineToPoint(width - corner_radius, 0)
            path.AddArcToPoint(width, 0, width, corner_radius, corner_radius)
            path.AddLineToPoint(width, height - corner_radius)
            path.AddArcToPoint(width, height, width - corner_radius, height, corner_radius)
            path.AddLineToPoint(corner_radius, height)
            path.AddArcToPoint(0, height, 0, height - corner_radius, corner_radius)
            path.AddLineToPoint(0, corner_radius)
            path.AddArcToPoint(0, 0, corner_radius, 0, corner_radius)
            path.CloseSubpath()
            
            # 填充颜色
            gc.SetBrush(wx.Brush(wx.Colour(*self.background_color)))
            gc.FillPath(path)
            
            # 绘制边框
            gc.SetPen(wx.Pen(wx.Colour(self.background_color[0]-50, self.background_color[1]-50, self.background_color[2]-50), 2))
            gc.StrokePath(path)
            
            # 绘制小尾巴（对话框指向宠物的箭头）
            tail_x = width // 2
            tail_y = height
            tail_points = [
                (tail_x - 10, tail_y),
                (tail_x, tail_y + 15),
                (tail_x + 10, tail_y)
            ]
            
            # 创建并填充三角形路径
            tail_path = gc.CreatePath()
            tail_path.MoveToPoint(tail_points[0][0], tail_points[0][1])
            tail_path.AddLineToPoint(tail_points[1][0], tail_points[1][1])
            tail_path.AddLineToPoint(tail_points[2][0], tail_points[2][1])
            tail_path.CloseSubpath()
            
            gc.SetBrush(wx.Brush(wx.Colour(*self.background_color)))
            gc.FillPath(tail_path)
