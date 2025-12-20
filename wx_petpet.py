#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于 wxPython 的跨平台 GIF 桌面宠物程序
支持 macOS/Windows，轻量稳定
"""

import wx
import wx.animate
import os
import sys
from pathlib import Path


class WxGIFDesktopPet(wx.Frame):
    """GIF 桌面宠物主类"""
    
    # 配置常量
    GIF_PATH = "pet.gif"  # GIF 素材路径，可替换为自定义路径
    INIT_X = -100  # 初始 X 坐标（-100 表示屏幕右侧内缩 100px）
    INIT_Y = 100  # 初始 Y 坐标（顶部往下 100px）
    ANIMATION_SPEED = -1  # 动画速度（-1 表示使用 GIF 原始速度）
    
    def __init__(self, parent=None, id=wx.ID_ANY, title="", style=wx.DEFAULT_FRAME_STYLE):
        """初始化桌面宠物"""
        # 设置窗口样式：无边框、无任务栏图标、置顶、透明
        style = (wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.FRAME_SHAPED | 
                wx.NO_BORDER | wx.FRAME_FLOAT_ON_PARENT)
        
        super(WxGIFDesktopPet, self).__init__(parent, id, title, 
                                             pos=(0, 0), size=(100, 100), 
                                             style=style)
        
        # 初始化变量
        self.is_dragging = False
        self.drag_pos = (0, 0)
        self.is_visible = True
        
        # 高 DPI 适配
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.EnableHighDPI()
        
        # 加载 GIF 动画
        self.animation = None
        self.animation_ctrl = None
        self.load_gif()
        
        # 设置窗口属性
        self.setup_window()
        
        # 创建系统托盘
        self.tray_icon = None
        self.create_tray_icon()
        
        # 绑定事件
        self.bind_events()
        
        # 设置初始位置
        self.set_initial_position()
        
        # 显示窗口
        self.Show()
    
    def load_gif(self):
        """加载 GIF 动画文件"""
        try:
            # 检查 GIF 文件是否存在
            if not os.path.exists(self.GIF_PATH):
                raise wx.wxFileNotFoundError(f"GIF 文件不存在: {self.GIF_PATH}")
            
            # 加载 GIF 动画
            self.animation = wx.animate.Animation(self.GIF_PATH, wx.animate.ANIMATION_TYPE_GIF)
            
            # 创建动画控件
            self.animation_ctrl = wx.animate.AnimationCtrl(self, wx.ID_ANY, self.animation)
            self.animation_ctrl.SetUseBackgroundColour(True)
            self.animation_ctrl.SetInactiveBackgroundColour(wx.TRANSPARENT)
            
            # 获取 GIF 原始尺寸并调整窗口大小
            gif_width, gif_height = self.animation.GetSize()
            self.SetClientSize((gif_width, gif_height))
            self.animation_ctrl.SetClientSize((gif_width, gif_height))
            
            # 开始循环播放动画
            self.animation_ctrl.Play()
            self.animation_ctrl.SetWindowStyleFlag(wx.NO_BORDER)
            
        except Exception as e:
            # 处理异常
            error_msg = f"加载 GIF 失败: {str(e)}\n请检查文件路径或文件格式是否正确。"
            wx.MessageBox(error_msg, "错误", wx.OK | wx.ICON_ERROR)
            self.Destroy()
            sys.exit(1)
    
    def setup_window(self):
        """设置窗口属性"""
        # 设置透明背景
        if sys.platform == "win32":
            # Windows 平台：使用 SetTransparent
            self.SetTransparent(255)
        elif sys.platform == "darwin":
            # macOS 平台：使用特殊样式
            self.SetWindowStyle(self.GetWindowStyle() | wx.FRAME_TOOL_WINDOW)
        
        # 设置窗口形状为 GIF 尺寸
        self.SetShape(wx.Region(wx.Rect(0, 0, self.GetClientSize().GetWidth(), 
                                       self.GetClientSize().GetHeight())))
        
        # 禁用窗口缩放
        self.SetWindowStyleFlag(self.GetWindowStyleFlag() & ~wx.FRAME_RESIZABLE)
        
        # 设置窗口无焦点
        self.MakeTransparent(255)
        
    def create_tray_icon(self):
        """创建系统托盘图标"""
        if hasattr(wx, 'TaskBarIcon'):
            # 提取 GIF 第一帧作为托盘图标
            icon = self.create_tray_icon_from_gif()
            
            # 创建托盘图标
            self.tray_icon = wx.TaskBarIcon()
            self.tray_icon.SetIcon(icon, "GIF 桌面宠物")
            
            # 绑定托盘事件
            self.tray_icon.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_tray_left_click)
            self.tray_icon.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.on_tray_right_click)
    
    def create_tray_icon_from_gif(self):
        """从 GIF 第一帧创建托盘图标"""
        # 创建与 GIF 第一帧相同尺寸的位图
        bmp = wx.Bitmap(self.GIF_PATH, wx.BITMAP_TYPE_GIF)
        
        # 根据系统调整图标尺寸
        if sys.platform == "darwin":
            # macOS：16x16 像素
            icon_size = (16, 16)
        else:
            # Windows：32x32 像素
            icon_size = (32, 32)
        
        # 缩放位图到合适尺寸
        scaled_bmp = bmp.ConvertToImage().Scale(icon_size[0], icon_size[1]).ConvertToBitmap()
        
        # 创建图标
        icon = wx.Icon()
        icon.CopyFromBitmap(scaled_bmp)
        
        return icon
    
    def bind_events(self):
        """绑定窗口事件"""
        # 鼠标事件
        self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_mouse_left_up)
        self.Bind(wx.EVT_MOTION, self.on_mouse_motion)
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_mouse_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_mouse_leave)
        
        # 窗口事件
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        
        # 动画控件事件
        if self.animation_ctrl:
            self.animation_ctrl.Bind(wx.animate.EVT_ANIMATION_STOP, self.on_animation_stop)
    
    def on_mouse_left_down(self, event):
        """鼠标左键按下事件（开始拖拽）"""
        self.is_dragging = True
        self.drag_pos = event.GetPosition()
        self.CaptureMouse()
        event.Skip()
    
    def on_mouse_left_up(self, event):
        """鼠标左键释放事件（停止拖拽）"""
        if self.is_dragging:
            self.is_dragging = False
            if self.HasCapture():
                self.ReleaseMouse()
        event.Skip()
    
    def on_mouse_motion(self, event):
        """鼠标移动事件（处理拖拽）"""
        if self.is_dragging and self.HasCapture():
            pos = event.GetPosition()
            delta = (pos[0] - self.drag_pos[0], pos[1] - self.drag_pos[1])
            new_pos = self.ClientToScreen(delta)
            self.Move(new_pos)
        event.Skip()
    
    def on_mouse_enter(self, event):
        """鼠标进入窗口事件"""
        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        # 暂停动画
        if self.animation_ctrl:
            self.animation_ctrl.Stop()
        event.Skip()
    
    def on_mouse_leave(self, event):
        """鼠标离开窗口事件"""
        self.SetCursor(wx.Cursor(wx.CURSOR_DEFAULT))
        # 恢复动画播放
        if self.animation_ctrl:
            self.animation_ctrl.Play()
        event.Skip()
    
    def on_close(self, event):
        """窗口关闭事件（隐藏到托盘）"""
        self.Hide()
        event.Veto()  # 阻止窗口真正关闭
    
    def on_paint(self, event):
        """窗口绘制事件"""
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        event.Skip()
    
    def on_animation_stop(self, event):
        """动画停止事件（循环播放）"""
        if self.animation_ctrl:
            self.animation_ctrl.Play()
    
    def on_tray_left_click(self, event):
        """托盘图标左键点击事件（切换显示/隐藏）"""
        self.toggle_visibility()
    
    def on_tray_right_click(self, event):
        """托盘图标右键点击事件（显示菜单）"""
        menu = wx.Menu()
        
        # 显示/隐藏菜单
        if self.is_visible:
            show_hide_item = menu.Append(wx.ID_ANY, "隐藏宠物")
        else:
            show_hide_item = menu.Append(wx.ID_ANY, "显示宠物")
        
        # 退出菜单
        exit_item = menu.Append(wx.ID_EXIT, "退出")
        
        # 绑定菜单事件
        self.Bind(wx.EVT_MENU, self.toggle_visibility, show_hide_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        
        # 显示菜单
        self.tray_icon.PopupMenu(menu)
        menu.Destroy()
    
    def toggle_visibility(self, event=None):
        """切换宠物窗口的显示/隐藏状态"""
        if self.is_visible:
            self.Hide()
            self.is_visible = False
        else:
            self.Show()
            self.Raise()  # 置顶显示
            self.is_visible = True
    
    def on_exit(self, event):
        """退出程序"""
        # 销毁托盘图标
        if self.tray_icon:
            self.tray_icon.RemoveIcon()
            self.tray_icon.Destroy()
        
        # 释放动画资源
        if self.animation_ctrl:
            self.animation_ctrl.Stop()
            self.animation_ctrl.Destroy()
        
        # 退出程序
        self.Destroy()
        wx.GetApp().ExitMainLoop()
    
    def set_initial_position(self):
        """设置窗口初始位置（屏幕右上角）"""
        # 获取屏幕尺寸
        screen_size = wx.GetDisplaySize()
        
        # 计算初始位置（右上角）
        window_size = self.GetSize()
        pos_x = screen_size.GetWidth() + self.INIT_X - window_size.GetWidth()
        pos_y = self.INIT_Y
        
        # 设置位置
        self.SetPosition((pos_x, pos_y))
    
    def create_tray_icon(self):
        """创建系统托盘图标"""
        if hasattr(wx, 'TaskBarIcon'):
            try:
                # 提取 GIF 第一帧作为托盘图标
                icon = self.create_tray_icon_from_gif()
                
                # 创建托盘图标
                self.tray_icon = wx.TaskBarIcon()
                self.tray_icon.SetIcon(icon, "GIF 桌面宠物")
                
                # 绑定托盘事件
                self.tray_icon.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_tray_left_click)
                self.tray_icon.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.on_tray_right_click)
            except Exception as e:
                wx.MessageBox(f"创建系统托盘失败: {str(e)}", "警告", wx.OK | wx.ICON_WARNING)


class PetApp(wx.App):
    """应用程序主类"""
    
    def OnInit(self):
        """初始化应用程序"""
        # 高 DPI 支持
        if hasattr(self, 'SetProcessDPIAware'):
            self.SetProcessDPIAware()
        
        # 创建主窗口
        frame = WxGIFDesktopPet(None)
        frame.SetAppName("GIF 桌面宠物")
        self.SetTopWindow(frame)
        return True
    
    def OnExit(self):
        """程序退出时的清理工作"""
        return 0


def main():
    """程序主入口"""
    app = PetApp(redirect=False)
    app.MainLoop()


if __name__ == "__main__":
    main()
