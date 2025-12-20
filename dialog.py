#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对话框模块

封装了可爱的自定义对话框功能，用于桌面宠物的交互反馈。
"""

import wx
import math


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
        
        # 动画相关变量
        self.animation_timer = None
        self.animation_step = 0
        self.animation_max_steps = 24  # 动画总步数
        self.start_position = wx.Point(0, 0)  # 动画起始位置
        self.end_position = wx.Point(0, 0)    # 动画结束位置
        self.bounce_amplitude = 15  # 回弹幅度
    
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
    
    def show_with_animation(self, start_pos, end_pos):
        """显示对话框并执行上升和回弹动画
        
        Args:
            start_pos: 动画起始位置 (wx.Point)
            end_pos: 动画结束位置 (wx.Point)
        """
        # 保存起始和结束位置
        self.start_position = start_pos
        self.end_position = end_pos
        
        # 从起始位置开始显示对话框
        self.SetPosition(self.start_position)
        self.Show()
        
        # 初始化动画变量
        self.animation_step = 0
        
        # 创建动画定时器
        if self.animation_timer:
            self.animation_timer.Stop()
            self.animation_timer = None
        
        self.animation_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_animation_timer, self.animation_timer)
        self.animation_timer.Start(16)  # 约60fps
    
    def on_animation_timer(self, event):
        """动画定时器事件"""
        if self.animation_step >= self.animation_max_steps:
            # 动画结束，停止定时器
            self.animation_timer.Stop()
            self.animation_timer = None
            return
        
        # 计算动画进度（0-1）
        progress = self.animation_step / self.animation_max_steps
        
        # 使用正弦函数实现平滑的上升和回弹效果
        # 第一阶段：上升（0-0.5）
        if progress <= 0.5:
            # 使用二次函数加速上升
            t = progress * 2  # 转换为0-1
            # 应用缓动函数使动画更自然
            t = t * t * (3 - 2 * t)  # 缓动函数：三次贝塞尔
            y_offset = (1 - t) * self.start_position.y + t * (self.end_position.y - self.bounce_amplitude)
        else:
            # 第二阶段：回弹（0.5-1）
            t = (progress - 0.5) * 2  # 转换为0-1
            # 使用正弦函数实现回弹效果
            bounce_factor = math.sin(t * math.pi)
            y_offset = self.end_position.y + (self.bounce_amplitude * bounce_factor)
        
        # 保持水平位置不变
        new_x = self.end_position.x
        
        # 更新对话框位置
        self.SetPosition(wx.Point(new_x, int(y_offset)))
        
        # 更新透明度（可选：从半透明到完全透明）
        alpha = int(200 + 40 * progress)  # 从200到240的透明度变化
        self.SetTransparent(alpha)
        
        # 更新动画步骤
        self.animation_step += 1
    
    def hide_with_animation(self):
        """显示对话框消失动画（嗖一下收起来的效果）"""
        print("执行对话框消失动画")
        # 初始化消失动画变量
        self.animation_step = 0
        self.animation_max_steps = 12  # 消失动画总步数，较快的动画
        self.start_position = self.GetPosition()
        self.start_size = self.GetSize()
        self.end_size = (0, 0)  # 最终尺寸
        
        # 创建动画定时器
        if self.animation_timer:
            print("停止并销毁已有动画定时器")
            self.animation_timer.Stop()
            self.animation_timer = None
        
        self.animation_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_hide_animation_timer, self.animation_timer)
        self.animation_timer.Start(16)  # 约60fps
        print("消失动画定时器已启动")

    def on_hide_animation_timer(self, event):
        """消失动画定时器事件"""
        print(f"消失动画步骤: {self.animation_step}/{self.animation_max_steps}")
        if self.animation_step >= self.animation_max_steps:
            # 动画结束，关闭对话框
            print("消失动画结束，关闭对话框")
            self.animation_timer.Stop()
            self.animation_timer = None
            self.Hide()
            self.Destroy()  # 动画结束后彻底销毁对话框
            return
        
        # 计算动画进度（0-1）
        progress = self.animation_step / self.animation_max_steps
        
        # 使用缓动函数实现快速消失效果
        # 使用二次函数使动画加速消失
        t = progress * progress
        
        # 计算新的尺寸（缩放）
        new_width = int(self.start_size.width * (1 - t))
        new_height = int(self.start_size.height * (1 - t))
        
        # 计算新的位置（保持中心）
        center_x = self.start_position.x + self.start_size.width // 2
        center_y = self.start_position.y + self.start_size.height // 2
        new_x = center_x - new_width // 2
        new_y = center_y - new_height // 2
        
        # 计算新的透明度（淡出）
        alpha = int(240 * (1 - t))  # 从240到0的透明度变化
        
        # 更新对话框属性
        self.SetSize((new_width, new_height))
        self.SetPosition(wx.Point(new_x, new_y))
        self.SetTransparent(alpha)
        
        # 更新动画步骤
        self.animation_step += 1