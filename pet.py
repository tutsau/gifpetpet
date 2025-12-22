#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""宠物模块

封装了桌面宠物的核心功能，包括GIF动画播放、窗口控制、交互事件等。
"""

import wx
import os
import sys
import random
import datetime
from PIL import Image
import config
from dialog import CuteDialog
from work_incentive import WorkIncentiveManager


class FinalGIFDesktopPet(wx.Frame):
    """最终版 GIF 桌面宠物主类"""
    
    def on_mouse_right_down(self, event):
        """鼠标右键点击事件（显示上下文菜单）"""
        # 创建上下文菜单
        menu = wx.Menu()
        
        # 更换形象选项
        change_image_item = menu.Append(wx.ID_ANY, "更换形象")
        self.Bind(wx.EVT_MENU, self.on_change_image, change_image_item)
        
        # 上班激励选项
        work_incentive_item = menu.Append(wx.ID_ANY, "上班激励")
        self.Bind(wx.EVT_MENU, self.on_work_incentive, work_incentive_item)
        
        # 退出选项
        exit_item = menu.Append(wx.ID_EXIT, "退出")
        self.Bind(wx.EVT_MENU, self.on_close, exit_item)
        
        # 显示菜单
        self.PopupMenu(menu)
        menu.Destroy()
        event.Skip()
    
    def on_work_incentive(self, event):
        """上班激励选项点击事件"""
        # 使用管理器显示配置对话框
        self.work_incentive_manager.show_config_dialog()
    
    def __init__(self, gif_path=config.Config.get_gif_path()):
        """初始化桌面宠物
        
        Args:
            gif_path: GIF动画文件路径
        """
        # 设置窗口样式：无边框、无任务栏图标、置顶
        style = wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.NO_BORDER
        super().__init__(parent=None, id=wx.ID_ANY, title='Cute Pet', pos=wx.DefaultPosition, size=(100, 100), style=style)
        
        # 配置属性
        self.GIF_PATH = gif_path
        self.INIT_X = -100  # 初始 X 坐标（-100 表示屏幕右侧内缩 100px）
        self.INIT_Y = 100  # 初始 Y 坐标（顶部往下 100px）
        self.TRANSPARENT_ALPHA = 255  # 窗口透明度（0-255）
        
        # 状态变量初始化
        self.is_dragging = False
        self.drag_pos = wx.Point(0, 0)
        self.click_start_pos = wx.Point(0, 0)  # 初始化点击起始位置
        
        # GIF 动画相关变量
        self.gif_frames = []      # GIF 帧列表
        self.frame_delays = []    # 帧延迟列表
        self.current_frame = 0    # 当前播放帧
        self.animation_timer = None  # 动画定时器
        self.is_paused = False    # 动画暂停状态
        
        # 对话框相关变量
        self.dialog = None  # 保存对话框引用
        self.auto_close_timer = None  # 自动关闭定时器
        
        # 弹跳效果相关变量
        self.bounce_timer = None  # 弹跳定时器
        self.bounce_offset = 0  # 当前弹跳偏移量
        self.bounce_direction = -1  # 弹跳方向 (-1: 向上, 1: 向下)
        self.bounce_amplitude = 20  # 弹跳幅度
        self.bounce_speed = 2  # 弹跳速度
        self.original_position = wx.Point(0, 0)  # 原始位置
        
        # 上班激励功能相关变量
        self.work_incentive_manager = WorkIncentiveManager(self)  # 使用新的管理器类
        
        # 收益提示定时器
        self.income_timer = None  # 每分钟弹出收益提示的定时器
        
        # 创建图像控件
        self.image_ctrl = wx.StaticBitmap(self, wx.ID_ANY)
        
        # 初始化流程
        self.load_gif()
        self.setup_transparent_window()
        self.bind_events()
        self.set_initial_position()
        # 配置已经在WorkIncentiveConfig初始化时加载
        
        # 启动收益提示定时器（每分钟弹出一次）
        self.income_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_income_timer, self.income_timer)
        self.income_timer.Start(60000)  # 60秒间隔
        
        # 显示窗口
        self.Show()
    
    def bounce(self):
        """实现史莱姆按压效果"""
        if self.bounce_timer is None:
            self.bounce_timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self.on_bounce_timer, self.bounce_timer)
            # 记录原始位置和尺寸
            self.original_position = self.GetPosition()
            self.original_size = self.GetSize()
            # 重置弹跳参数
            self.bounce_step = 0
            self.bounce_max_steps = 16  # 弹跳总步数，增加以获得更平滑的效果
            self.bounce_timer.Start(16)  # 约60fps
            return
        
        # 使用正弦函数创建更自然的弹跳效果
        import math
        
        # 计算当前弹跳进度 (0-1)
        progress = self.bounce_step / self.bounce_max_steps
        
        # 使用正弦函数计算弹跳高度，创建缓动效果
        # 前半部分(0-0.5)是按压阶段，后半部分(0.5-1)是回弹阶段
        if progress <= 0.5:
            # 按压阶段：压缩宠物
            compression_progress = progress * 2  # 0-1
            compression_factor = math.sin(compression_progress * math.pi / 2)
            
            # 计算新尺寸：垂直压缩，水平略微扩展
            new_height = int(self.original_size.height * (1 - 0.2 * compression_factor))
            new_width = int(self.original_size.width * (1 + 0.1 * compression_factor))
            
            # 更新窗口位置和尺寸
            new_pos = wx.Point(
                self.original_position.x - (new_width - self.original_size.width) // 2,
                self.original_position.y + (self.original_size.height - new_height)
            )
            self.SetPosition(new_pos)
            self.SetSize((new_width, new_height))
            self.image_ctrl.SetSize((new_width, new_height))
        else:
            # 回弹阶段：恢复原始尺寸
            rebound_progress = (progress - 0.5) * 2  # 0-1
            rebound_factor = math.sin(rebound_progress * math.pi / 2)
            
            # 计算新尺寸：逐渐恢复原始尺寸
            new_height = int(self.original_size.height * (1 - 0.2 * (1 - rebound_factor)))
            new_width = int(self.original_size.width * (1 + 0.1 * (1 - rebound_factor)))
            
            # 更新窗口位置和尺寸
            new_pos = wx.Point(
                self.original_position.x - (new_width - self.original_size.width) // 2,
                self.original_position.y + (self.original_size.height - new_height)
            )
            self.SetPosition(new_pos)
            self.SetSize((new_width, new_height))
            self.image_ctrl.SetSize((new_width, new_height))
        
        # 更新步数
        self.bounce_step += 1
        
        # 检查是否完成弹跳
        if self.bounce_step >= self.bounce_max_steps:
            # 恢复到原始位置和尺寸
            self.SetPosition(self.original_position)
            self.SetSize(self.original_size)
            self.image_ctrl.SetSize(self.original_size)
            # 清理定时器
            self.bounce_timer.Stop()
            self.bounce_timer = None
            self.bounce_step = 0
    
    def on_bounce_timer(self, event):
        """弹跳定时器事件"""
        self.bounce()
    
    def load_gif(self):
        """使用 Pillow 加载 GIF 动画"""
        try:
            if not os.path.exists(self.GIF_PATH):
                raise FileNotFoundError(f"GIF 文件不存在: {self.GIF_PATH}")
            
            # 使用 Pillow 打开 GIF 图像
            pil_image = Image.open(self.GIF_PATH)
            
            # 检查是否为动画 GIF
            if not pil_image.is_animated:
                print("警告: 这是一个静态 GIF 图像")
            
            # 获取总帧数
            num_frames = pil_image.n_frames
            print(f"GIF 总帧数: {num_frames}")
            
            # 提取所有帧
            for i in range(num_frames):
                # 定位到当前帧
                pil_image.seek(i)
                
                # 复制当前帧
                frame = pil_image.copy()
                
                # 获取帧延迟（单位：1/1000秒）
                if 'duration' in pil_image.info:
                    delay = pil_image.info['duration']
                else:
                    delay = 100  # 默认延迟 100ms
                
                if delay < 10:  # 最小延迟 10ms
                    delay = 10
                
                # 确保所有帧都转换为 RGBA 模式以处理透明度
                if frame.mode != 'RGBA':
                    frame = frame.convert('RGBA')
                
                # 将图像缩小为原来的一半
                new_size = (frame.width // 2, frame.height // 2)
                frame = frame.resize(new_size, Image.Resampling.LANCZOS)
                
                # 打印帧信息（用于调试）
                print(f"帧 {i+1}/{num_frames}: 模式={frame.mode}, 尺寸={new_size}, 延迟={delay}ms")
                
                # 创建 wx.Image
                wx_image = wx.Image(*new_size)
                
                # 设置 RGB 数据
                rgb_data = frame.convert('RGB').tobytes()
                wx_image.SetData(rgb_data)
                
                # 设置 Alpha 通道
                if frame.mode == 'RGBA':
                    alpha_data = frame.getchannel('A').tobytes()
                    wx_image.SetAlpha(alpha_data)
                else:
                    # 如果没有 Alpha 通道，创建完全不透明的通道
                    alpha_data = bytes([255] * (frame.width * frame.height))
                    wx_image.SetAlpha(alpha_data)
                
                # 转换为 wx.Bitmap
                wx_bitmap = wx_image.ConvertToBitmap()
                
                # 添加到帧列表
                self.gif_frames.append(wx_bitmap)
                self.frame_delays.append(delay)
            
            # 设置初始帧
            self.image_ctrl.SetBitmap(self.gif_frames[0])
            
            # 调整窗口大小
            size = self.gif_frames[0].GetSize()
            self.SetSize(size)
            self.image_ctrl.SetSize(size)
            
            # 启动动画
            self.start_animation()
            
            print(f"成功加载并启动 GIF 动画: {self.GIF_PATH}")
            print(f"GIF 尺寸: {size}")
            
        except Exception as e:
            print(f"加载 GIF 失败: {e}")
            import traceback
            traceback.print_exc()
            wx.MessageBox(f"加载 GIF 失败: {e}", "错误", wx.OK | wx.ICON_ERROR)
            self.Destroy()
            sys.exit(1)
    
    def start_animation(self):
        """启动 GIF 动画"""
        if self.animation_timer is None:
            self.animation_timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self.on_animation_timer, self.animation_timer)
        
        # 设置定时器间隔并启动
        self.animation_timer.Start(self.frame_delays[self.current_frame])
        print(f"动画已启动，初始延迟: {self.frame_delays[self.current_frame]}ms")
    
    def pause_animation(self, frame_index=None):
        """暂停 GIF 动画
        
        Args:
            frame_index: 可选参数，指定暂停时显示的帧索引
        """
        if self.animation_timer and self.animation_timer.IsRunning():
            self.animation_timer.Stop()
            self.is_paused = True
            
            # 如果指定了帧索引，跳转到该帧
            if frame_index is not None and 0 <= frame_index < len(self.gif_frames):
                self.current_frame = frame_index
                self.image_ctrl.SetBitmap(self.gif_frames[self.current_frame])
                print(f"动画已暂停在第 {frame_index+1} 帧")
            else:
                print("动画已暂停")
    
    def resume_animation(self):
        """恢复 GIF 动画"""
        if self.animation_timer and not self.animation_timer.IsRunning():
            self.animation_timer.Start(self.frame_delays[self.current_frame])
            self.is_paused = False
            print("动画已恢复")
    
    def on_animation_timer(self, event):
        """动画定时器事件"""
        if self.is_paused:
            return
        
        # 切换到下一帧
        self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
        
        # 更新图像
        self.image_ctrl.SetBitmap(self.gif_frames[self.current_frame])
        
        # 重新设置定时器间隔
        if self.animation_timer and self.animation_timer.IsRunning():
            self.animation_timer.Stop()
        self.animation_timer.Start(self.frame_delays[self.current_frame])
    
    def setup_transparent_window(self):
        """设置窗口透明"""
        try:
            # 根据不同系统设置透明
            if sys.platform == "win32":
                # Windows：设置透明
                self.SetTransparent(255)
            elif sys.platform == "darwin":
                # macOS：设置透明样式
                self.SetWindowStyle(self.GetWindowStyle() | wx.FRAME_TOOL_WINDOW)
                self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
            else:
                # Linux：设置透明
                self.SetTransparent(255)
            
            print("窗口透明设置完成")
        except Exception as e:
            print(f"窗口透明设置失败: {e}")
    
    def bind_events(self):
        """绑定事件"""
        # 鼠标事件
        self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_mouse_left_up)
        self.Bind(wx.EVT_MOTION, self.on_mouse_motion)
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_mouse_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_mouse_leave)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_mouse_right_down)  # 添加右键点击事件
        
        # 窗口事件
        self.Bind(wx.EVT_CLOSE, self.on_close)
    
    def on_mouse_left_down(self, event):
        """鼠标左键按下事件（开始拖拽）"""
        self.is_dragging = True
        self.drag_pos = event.GetPosition()
        self.CaptureMouse()
        # 记录按下位置用于检测点击
        self.click_start_pos = event.GetPosition()
        event.Skip()
    
    def on_mouse_left_up(self, event):
        """鼠标左键释放事件（停止拖拽）"""
        if self.is_dragging:
            self.is_dragging = False
            if self.HasCapture():
                self.ReleaseMouse()
                
            # 检测是否为点击事件（移动距离小于5像素）
            click_end_pos = event.GetPosition()
            distance = ((click_end_pos[0] - self.click_start_pos[0])**2 + 
                      (click_end_pos[1] - self.click_start_pos[1])**2)**0.5
            
            if distance < 5:
                # 执行弹跳效果
                self.bounce()
                # 显示可爱对话框
                self.show_cute_dialog()
        event.Skip()
    
    def on_mouse_motion(self, event):
        """鼠标移动事件（处理拖拽）"""
        if self.is_dragging and self.HasCapture():
            pos = event.GetPosition()
            delta = (pos[0] - self.drag_pos[0], pos[1] - self.drag_pos[1])
            new_pos = self.ClientToScreen(delta)
            self.Move(new_pos)
            
            # 更新对话框位置跟随宠物移动
            self.update_dialog_position()
        event.Skip()
    
    def on_mouse_enter(self, event):
        """鼠标进入窗口事件"""
        # 鼠标悬停时暂停动画并跳转到第一帧
        self.pause_animation(0)
        event.Skip()
    
    def on_mouse_leave(self, event):
        """鼠标离开窗口事件"""
        # 鼠标离开时恢复动画
        self.resume_animation()
        event.Skip()
    
    def on_change_image(self, event):
        """更换形象选项点击事件"""
        # 创建文件选择对话框
        file_dialog = wx.FileDialog(
            self,
            message="选择GIF动画文件",
            defaultDir="",
            defaultFile="",
            wildcard="GIF文件 (*.gif)|*.gif",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        )
        
        # 显示对话框并等待用户选择
        if file_dialog.ShowModal() == wx.ID_OK:
            # 获取用户选择的文件路径
            selected_path = file_dialog.GetPath()
            
            # 验证文件是否为GIF格式
            if selected_path.lower().endswith('.gif'):
                try:
                    # 验证GIF文件是否有效
                    from PIL import Image
                    with Image.open(selected_path) as img:
                        if img.format != 'GIF':
                            wx.MessageBox("选择的文件不是有效的GIF格式", "错误", wx.OK | wx.ICON_ERROR)
                            return
                    
                    # 更新配置并重新加载宠物形象
                    self.change_pet_image(selected_path)
                except Exception as e:
                    wx.MessageBox(f"无法加载GIF文件: {e}", "错误", wx.OK | wx.ICON_ERROR)
            else:
                wx.MessageBox("请选择GIF格式的文件", "错误", wx.OK | wx.ICON_ERROR)
        
        # 关闭对话框
        file_dialog.Destroy()
    
    def on_work_incentive(self, event):
        """上班激励选项点击事件"""
        # 使用管理器显示配置对话框
        self.work_incentive_manager.show_config_dialog()
    
    def __init__(self, gif_path=config.Config.get_gif_path()):
        """初始化桌面宠物
        
        Args:
            gif_path: GIF动画文件路径
        """
        # 设置窗口样式：无边框、无任务栏图标、置顶
        style = wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.NO_BORDER
        super().__init__(parent=None, id=wx.ID_ANY, title='Cute Pet', pos=wx.DefaultPosition, size=(100, 100), style=style)
        
        # 配置属性
        self.GIF_PATH = gif_path
        self.INIT_X = -100  # 初始 X 坐标（-100 表示屏幕右侧内缩 100px）
        self.INIT_Y = 100  # 初始 Y 坐标（顶部往下 100px）
        self.TRANSPARENT_ALPHA = 255  # 窗口透明度（0-255）
        
        # 状态变量初始化
        self.is_dragging = False
        self.drag_pos = wx.Point(0, 0)
        self.click_start_pos = wx.Point(0, 0)  # 初始化点击起始位置
        
        # GIF 动画相关变量
        self.gif_frames = []      # GIF 帧列表
        self.frame_delays = []    # 帧延迟列表
        self.current_frame = 0    # 当前播放帧
        self.animation_timer = None  # 动画定时器
        self.is_paused = False    # 动画暂停状态
        
        # 对话框相关变量
        self.dialog = None  # 保存对话框引用
        self.auto_close_timer = None  # 自动关闭定时器
        
        # 弹跳效果相关变量
        self.bounce_timer = None  # 弹跳定时器
        self.bounce_offset = 0  # 当前弹跳偏移量
        self.bounce_direction = -1  # 弹跳方向 (-1: 向上, 1: 向下)
        self.bounce_amplitude = 20  # 弹跳幅度
        self.bounce_speed = 2  # 弹跳速度
        self.original_position = wx.Point(0, 0)  # 原始位置
        
        # 上班激励功能相关变量
        self.work_incentive_manager = WorkIncentiveManager(self)  # 使用新的管理器类
        
        # 收益提示定时器
        self.income_timer = None  # 每分钟弹出收益提示的定时器
        
        # 创建图像控件
        self.image_ctrl = wx.StaticBitmap(self, wx.ID_ANY)
        
        # 初始化流程
        self.load_gif()
        self.setup_transparent_window()
        self.bind_events()
        self.set_initial_position()
        # 配置已经在WorkIncentiveConfig初始化时加载
        
        # 启动收益提示定时器（每分钟弹出一次）
        self.income_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_income_timer, self.income_timer)
        self.income_timer.Start(60000)  # 60秒间隔
        
        # 显示窗口
        self.Show()
    
    def bounce(self):
        """实现史莱姆按压效果"""
        if self.bounce_timer is None:
            self.bounce_timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self.on_bounce_timer, self.bounce_timer)
            # 记录原始位置和尺寸
            self.original_position = self.GetPosition()
            self.original_size = self.GetSize()
            # 重置弹跳参数
            self.bounce_step = 0
            self.bounce_max_steps = 16  # 弹跳总步数，增加以获得更平滑的效果
            self.bounce_timer.Start(16)  # 约60fps
            return
        
        # 使用正弦函数创建更自然的弹跳效果
        import math
        
        # 计算当前弹跳进度 (0-1)
        progress = self.bounce_step / self.bounce_max_steps
        
        # 使用正弦函数计算弹跳高度，创建缓动效果
        # 前半部分(0-0.5)是按压阶段，后半部分(0.5-1)是回弹阶段
        if progress <= 0.5:
            # 按压阶段：压缩宠物
            compression_progress = progress * 2  # 0-1
            compression_factor = math.sin(compression_progress * math.pi / 2)
            
            # 计算新尺寸：垂直压缩，水平略微扩展
            new_height = int(self.original_size.height * (1 - 0.2 * compression_factor))
            new_width = int(self.original_size.width * (1 + 0.1 * compression_factor))
            
            # 更新窗口位置和尺寸
            new_pos = wx.Point(
                self.original_position.x - (new_width - self.original_size.width) // 2,
                self.original_position.y + (self.original_size.height - new_height)
            )
            self.SetPosition(new_pos)
            self.SetSize((new_width, new_height))
            self.image_ctrl.SetSize((new_width, new_height))
        else:
            # 回弹阶段：恢复原始尺寸
            rebound_progress = (progress - 0.5) * 2  # 0-1
            rebound_factor = math.sin(rebound_progress * math.pi / 2)
            
            # 计算新尺寸：逐渐恢复原始尺寸
            new_height = int(self.original_size.height * (1 - 0.2 * (1 - rebound_factor)))
            new_width = int(self.original_size.width * (1 + 0.1 * (1 - rebound_factor)))
            
            # 更新窗口位置和尺寸
            new_pos = wx.Point(
                self.original_position.x - (new_width - self.original_size.width) // 2,
                self.original_position.y + (self.original_size.height - new_height)
            )
            self.SetPosition(new_pos)
            self.SetSize((new_width, new_height))
            self.image_ctrl.SetSize((new_width, new_height))
        
        # 更新步数
        self.bounce_step += 1
        
        # 检查是否完成弹跳
        if self.bounce_step >= self.bounce_max_steps:
            # 恢复到原始位置和尺寸
            self.SetPosition(self.original_position)
            self.SetSize(self.original_size)
            self.image_ctrl.SetSize(self.original_size)
            # 清理定时器
            self.bounce_timer.Stop()
            self.bounce_timer = None
            self.bounce_step = 0
    
    def on_bounce_timer(self, event):
        """弹跳定时器事件"""
        self.bounce()
    
    def load_gif(self):
        """使用 Pillow 加载 GIF 动画"""
        try:
            if not os.path.exists(self.GIF_PATH):
                raise FileNotFoundError(f"GIF 文件不存在: {self.GIF_PATH}")
            
            # 使用 Pillow 打开 GIF 图像
            pil_image = Image.open(self.GIF_PATH)
            
            # 检查是否为动画 GIF
            if not pil_image.is_animated:
                print("警告: 这是一个静态 GIF 图像")
            
            # 获取总帧数
            num_frames = pil_image.n_frames
            print(f"GIF 总帧数: {num_frames}")
            
            # 提取所有帧
            for i in range(num_frames):
                # 定位到当前帧
                pil_image.seek(i)
                
                # 复制当前帧
                frame = pil_image.copy()
                
                # 获取帧延迟（单位：1/1000秒）
                if 'duration' in pil_image.info:
                    delay = pil_image.info['duration']
                else:
                    delay = 100  # 默认延迟 100ms
                
                if delay < 10:  # 最小延迟 10ms
                    delay = 10
                
                # 确保所有帧都转换为 RGBA 模式以处理透明度
                if frame.mode != 'RGBA':
                    frame = frame.convert('RGBA')
                
                # 将图像缩小为原来的一半
                new_size = (frame.width // 2, frame.height // 2)
                frame = frame.resize(new_size, Image.Resampling.LANCZOS)
                
                # 打印帧信息（用于调试）
                print(f"帧 {i+1}/{num_frames}: 模式={frame.mode}, 尺寸={new_size}, 延迟={delay}ms")
                
                # 创建 wx.Image
                wx_image = wx.Image(*new_size)
                
                # 设置 RGB 数据
                rgb_data = frame.convert('RGB').tobytes()
                wx_image.SetData(rgb_data)
                
                # 设置 Alpha 通道
                if frame.mode == 'RGBA':
                    alpha_data = frame.getchannel('A').tobytes()
                    wx_image.SetAlpha(alpha_data)
                else:
                    # 如果没有 Alpha 通道，创建完全不透明的通道
                    alpha_data = bytes([255] * (frame.width * frame.height))
                    wx_image.SetAlpha(alpha_data)
                
                # 转换为 wx.Bitmap
                wx_bitmap = wx_image.ConvertToBitmap()
                
                # 添加到帧列表
                self.gif_frames.append(wx_bitmap)
                self.frame_delays.append(delay)
            
            # 设置初始帧
            self.image_ctrl.SetBitmap(self.gif_frames[0])
            
            # 调整窗口大小
            size = self.gif_frames[0].GetSize()
            self.SetSize(size)
            self.image_ctrl.SetSize(size)
            
            # 启动动画
            self.start_animation()
            
            print(f"成功加载并启动 GIF 动画: {self.GIF_PATH}")
            print(f"GIF 尺寸: {size}")
            
        except Exception as e:
            print(f"加载 GIF 失败: {e}")
            import traceback
            traceback.print_exc()
            wx.MessageBox(f"加载 GIF 失败: {e}", "错误", wx.OK | wx.ICON_ERROR)
            self.Destroy()
            sys.exit(1)
    
    def start_animation(self):
        """启动 GIF 动画"""
        if self.animation_timer is None:
            self.animation_timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self.on_animation_timer, self.animation_timer)
        
        # 设置定时器间隔并启动
        self.animation_timer.Start(self.frame_delays[self.current_frame])
        print(f"动画已启动，初始延迟: {self.frame_delays[self.current_frame]}ms")
    
    def pause_animation(self, frame_index=None):
        """暂停 GIF 动画
        
        Args:
            frame_index: 可选参数，指定暂停时显示的帧索引
        """
        if self.animation_timer and self.animation_timer.IsRunning():
            self.animation_timer.Stop()
            self.is_paused = True
            
            # 如果指定了帧索引，跳转到该帧
            if frame_index is not None and 0 <= frame_index < len(self.gif_frames):
                self.current_frame = frame_index
                self.image_ctrl.SetBitmap(self.gif_frames[self.current_frame])
                print(f"动画已暂停在第 {frame_index+1} 帧")
            else:
                print("动画已暂停")
    
    def resume_animation(self):
        """恢复 GIF 动画"""
        if self.animation_timer and not self.animation_timer.IsRunning():
            self.animation_timer.Start(self.frame_delays[self.current_frame])
            self.is_paused = False
            print("动画已恢复")
    
    def on_animation_timer(self, event):
        """动画定时器事件"""
        if self.is_paused:
            return
        
        # 切换到下一帧
        self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
        
        # 更新图像
        self.image_ctrl.SetBitmap(self.gif_frames[self.current_frame])
        
        # 重新设置定时器间隔
        if self.animation_timer and self.animation_timer.IsRunning():
            self.animation_timer.Stop()
        self.animation_timer.Start(self.frame_delays[self.current_frame])
    
    def setup_transparent_window(self):
        """设置窗口透明"""
        try:
            # 根据不同系统设置透明
            if sys.platform == "win32":
                # Windows：设置透明
                self.SetTransparent(255)
            elif sys.platform == "darwin":
                # macOS：设置透明样式
                self.SetWindowStyle(self.GetWindowStyle() | wx.FRAME_TOOL_WINDOW)
                self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
            else:
                # Linux：设置透明
                self.SetTransparent(255)
            
            print("窗口透明设置完成")
        except Exception as e:
            print(f"窗口透明设置失败: {e}")
    
    def bind_events(self):
        """绑定事件"""
        # 鼠标事件
        self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_mouse_left_up)
        self.Bind(wx.EVT_MOTION, self.on_mouse_motion)
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_mouse_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_mouse_leave)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_mouse_right_down)  # 添加右键点击事件
        
        # 窗口事件
        self.Bind(wx.EVT_CLOSE, self.on_close)
    
    def on_mouse_left_down(self, event):
        """鼠标左键按下事件（开始拖拽）"""
        self.is_dragging = True
        self.drag_pos = event.GetPosition()
        self.CaptureMouse()
        # 记录按下位置用于检测点击
        self.click_start_pos = event.GetPosition()
        event.Skip()
    
    def on_mouse_left_up(self, event):
        """鼠标左键释放事件（停止拖拽）"""
        if self.is_dragging:
            self.is_dragging = False
            if self.HasCapture():
                self.ReleaseMouse()
                
            # 检测是否为点击事件（移动距离小于5像素）
            click_end_pos = event.GetPosition()
            distance = ((click_end_pos[0] - self.click_start_pos[0])**2 + 
                      (click_end_pos[1] - self.click_start_pos[1])**2)**0.5
            
            if distance < 5:
                # 执行弹跳效果
                self.bounce()
                # 显示可爱对话框
                self.show_cute_dialog()
        event.Skip()
    
    def on_mouse_motion(self, event):
        """鼠标移动事件（处理拖拽）"""
        if self.is_dragging and self.HasCapture():
            pos = event.GetPosition()
            delta = (pos[0] - self.drag_pos[0], pos[1] - self.drag_pos[1])
            new_pos = self.ClientToScreen(delta)
            self.Move(new_pos)
            
            # 更新对话框位置跟随宠物移动
            self.update_dialog_position()
        event.Skip()
    
    def on_mouse_enter(self, event):
        """鼠标进入窗口事件"""
        # 鼠标悬停时暂停动画并跳转到第一帧
        self.pause_animation(0)
        event.Skip()
    
    def on_mouse_leave(self, event):
        """鼠标离开窗口事件"""
        # 鼠标离开时恢复动画
        self.resume_animation()
        event.Skip()
    
    def on_change_image(self, event):
        """更换形象选项点击事件"""
        # 创建文件选择对话框
        file_dialog = wx.FileDialog(
            self,
            message="选择GIF动画文件",
            defaultDir="",
            defaultFile="",
            wildcard="GIF文件 (*.gif)|*.gif",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        )
        
        # 显示对话框并等待用户选择
        if file_dialog.ShowModal() == wx.ID_OK:
            # 获取用户选择的文件路径
            selected_path = file_dialog.GetPath()
            
            # 验证文件是否为GIF格式
            if selected_path.lower().endswith('.gif'):
                try:
                    # 验证GIF文件是否有效
                    from PIL import Image
                    with Image.open(selected_path) as img:
                        if img.format != 'GIF':
                            wx.MessageBox("选择的文件不是有效的GIF格式", "错误", wx.OK | wx.ICON_ERROR)
                            return
                    
                    # 更新配置并重新加载宠物形象
                    self.change_pet_image(selected_path)
                except Exception as e:
                    wx.MessageBox(f"无法加载GIF文件: {e}", "错误", wx.OK | wx.ICON_ERROR)
            else:
                wx.MessageBox("请选择GIF格式的文件", "错误", wx.OK | wx.ICON_ERROR)
        
        # 关闭对话框
        file_dialog.Destroy()
    
    def on_work_incentive(self, event):
        """上班激励选项点击事件"""
        # 使用管理器显示配置对话框
        self.work_incentive_manager.show_config_dialog()
    
    def __init__(self, gif_path=config.Config.get_gif_path()):
        """初始化桌面宠物
        
        Args:
            gif_path: GIF动画文件路径
        """
        # 设置窗口样式：无边框、无任务栏图标、置顶
        style = wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.NO_BORDER
        super().__init__(parent=None, id=wx.ID_ANY, title='Cute Pet', pos=wx.DefaultPosition, size=(100, 100), style=style)
        
        # 配置属性
        self.GIF_PATH = gif_path
        self.INIT_X = -100  # 初始 X 坐标（-100 表示屏幕右侧内缩 100px）
        self.INIT_Y = 100  # 初始 Y 坐标（顶部往下 100px）
        self.TRANSPARENT_ALPHA = 255  # 窗口透明度（0-255）
        
        # 状态变量初始化
        self.is_dragging = False
        self.drag_pos = wx.Point(0, 0)
        self.click_start_pos = wx.Point(0, 0)  # 初始化点击起始位置
        
        # GIF 动画相关变量
        self.gif_frames = []      # GIF 帧列表
        self.frame_delays = []    # 帧延迟列表
        self.current_frame = 0    # 当前播放帧
        self.animation_timer = None  # 动画定时器
        self.is_paused = False    # 动画暂停状态
        
        # 对话框相关变量
        self.dialog = None  # 保存对话框引用
        self.auto_close_timer = None  # 自动关闭定时器
        
        # 弹跳效果相关变量
        self.bounce_timer = None  # 弹跳定时器
        self.bounce_offset = 0  # 当前弹跳偏移量
        self.bounce_direction = -1  # 弹跳方向 (-1: 向上, 1: 向下)
        self.bounce_amplitude = 20  # 弹跳幅度
        self.bounce_speed = 2  # 弹跳速度
        self.original_position = wx.Point(0, 0)  # 原始位置
        
        # 上班激励功能相关变量
        self.work_incentive_manager = WorkIncentiveManager(self)  # 使用新的管理器类
        
        # 收益提示定时器
        self.income_timer = None  # 每分钟弹出收益提示的定时器
        
        # 创建图像控件
        self.image_ctrl = wx.StaticBitmap(self, wx.ID_ANY)
        
        # 初始化流程
        self.load_gif()
        self.setup_transparent_window()
        self.bind_events()
        self.set_initial_position()
        # 配置已经在WorkIncentiveConfig初始化时加载
        
        # 启动收益提示定时器（每分钟弹出一次）
        self.income_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_income_timer, self.income_timer)
        self.income_timer.Start(60000)  # 60秒间隔
        
        # 显示窗口
        self.Show()
    
    def bounce(self):
        """实现史莱姆按压效果"""
        if self.bounce_timer is None:
            self.bounce_timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self.on_bounce_timer, self.bounce_timer)
            # 记录原始位置和尺寸
            self.original_position = self.GetPosition()
            self.original_size = self.GetSize()
            # 重置弹跳参数
            self.bounce_step = 0
            self.bounce_max_steps = 16  # 弹跳总步数，增加以获得更平滑的效果
            self.bounce_timer.Start(16)  # 约60fps
            return
        
        # 使用正弦函数创建更自然的弹跳效果
        import math
        
        # 计算当前弹跳进度 (0-1)
        progress = self.bounce_step / self.bounce_max_steps
        
        # 使用正弦函数计算弹跳高度，创建缓动效果
        # 前半部分(0-0.5)是按压阶段，后半部分(0.5-1)是回弹阶段
        if progress <= 0.5:
            # 按压阶段：压缩宠物
            compression_progress = progress * 2  # 0-1
            compression_factor = math.sin(compression_progress * math.pi / 2)
            
            # 计算新尺寸：垂直压缩，水平略微扩展
            new_height = int(self.original_size.height * (1 - 0.2 * compression_factor))
            new_width = int(self.original_size.width * (1 + 0.1 * compression_factor))
            
            # 更新窗口位置和尺寸
            new_pos = wx.Point(
                self.original_position.x - (new_width - self.original_size.width) // 2,
                self.original_position.y + (self.original_size.height - new_height)
            )
            self.SetPosition(new_pos)
            self.SetSize((new_width, new_height))
            self.image_ctrl.SetSize((new_width, new_height))
        else:
            # 回弹阶段：恢复原始尺寸
            rebound_progress = (progress - 0.5) * 2  # 0-1
            rebound_factor = math.sin(rebound_progress * math.pi / 2)
            
            # 计算新尺寸：逐渐恢复原始尺寸
            new_height = int(self.original_size.height * (1 - 0.2 * (1 - rebound_factor)))
            new_width = int(self.original_size.width * (1 + 0.1 * (1 - rebound_factor)))
            
            # 更新窗口位置和尺寸
            new_pos = wx.Point(
                self.original_position.x - (new_width - self.original_size.width) // 2,
                self.original_position.y + (self.original_size.height - new_height)
            )
            self.SetPosition(new_pos)
            self.SetSize((new_width, new_height))
            self.image_ctrl.SetSize((new_width, new_height))
        
        # 更新步数
        self.bounce_step += 1
        
        # 检查是否完成弹跳
        if self.bounce_step >= self.bounce_max_steps:
            # 恢复到原始位置和尺寸
            self.SetPosition(self.original_position)
            self.SetSize(self.original_size)
            self.image_ctrl.SetSize(self.original_size)
            # 清理定时器
            self.bounce_timer.Stop()
            self.bounce_timer = None
            self.bounce_step = 0
    
    def on_bounce_timer(self, event):
        """弹跳定时器事件"""
        self.bounce()
    
    def load_gif(self):
        """使用 Pillow 加载 GIF 动画"""
        try:
            if not os.path.exists(self.GIF_PATH):
                raise FileNotFoundError(f"GIF 文件不存在: {self.GIF_PATH}")
            
            # 使用 Pillow 打开 GIF 图像
            pil_image = Image.open(self.GIF_PATH)
            
            # 检查是否为动画 GIF
            if not pil_image.is_animated:
                print("警告: 这是一个静态 GIF 图像")
            
            # 获取总帧数
            num_frames = pil_image.n_frames
            print(f"GIF 总帧数: {num_frames}")
            
            # 提取所有帧
            for i in range(num_frames):
                # 定位到当前帧
                pil_image.seek(i)
                
                # 复制当前帧
                frame = pil_image.copy()
                
                # 获取帧延迟（单位：1/1000秒）
                if 'duration' in pil_image.info:
                    delay = pil_image.info['duration']
                else:
                    delay = 100  # 默认延迟 100ms
                
                if delay < 10:  # 最小延迟 10ms
                    delay = 10
                
                # 确保所有帧都转换为 RGBA 模式以处理透明度
                if frame.mode != 'RGBA':
                    frame = frame.convert('RGBA')
                
                # 将图像缩小为原来的一半
                new_size = (frame.width // 2, frame.height // 2)
                frame = frame.resize(new_size, Image.Resampling.LANCZOS)
                
                # 打印帧信息（用于调试）
                print(f"帧 {i+1}/{num_frames}: 模式={frame.mode}, 尺寸={new_size}, 延迟={delay}ms")
                
                # 创建 wx.Image
                wx_image = wx.Image(*new_size)
                
                # 设置 RGB 数据
                rgb_data = frame.convert('RGB').tobytes()
                wx_image.SetData(rgb_data)
                
                # 设置 Alpha 通道
                if frame.mode == 'RGBA':
                    alpha_data = frame.getchannel('A').tobytes()
                    wx_image.SetAlpha(alpha_data)
                else:
                    # 如果没有 Alpha 通道，创建完全不透明的通道
                    alpha_data = bytes([255] * (frame.width * frame.height))
                    wx_image.SetAlpha(alpha_data)
                
                # 转换为 wx.Bitmap
                wx_bitmap = wx_image.ConvertToBitmap()
                
                # 添加到帧列表
                self.gif_frames.append(wx_bitmap)
                self.frame_delays.append(delay)
            
            # 设置初始帧
            self.image_ctrl.SetBitmap(self.gif_frames[0])
            
            # 调整窗口大小
            size = self.gif_frames[0].GetSize()
            self.SetSize(size)
            self.image_ctrl.SetSize(size)
            
            # 启动动画
            self.start_animation()
            
            print(f"成功加载并启动 GIF 动画: {self.GIF_PATH}")
            print(f"GIF 尺寸: {size}")
            
        except Exception as e:
            print(f"加载 GIF 失败: {e}")
            import traceback
            traceback.print_exc()
            wx.MessageBox(f"加载 GIF 失败: {e}", "错误", wx.OK | wx.ICON_ERROR)
            self.Destroy()
            sys.exit(1)
    
    def start_animation(self):
        """启动 GIF 动画"""
        if self.animation_timer is None:
            self.animation_timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self.on_animation_timer, self.animation_timer)
        
        # 设置定时器间隔并启动
        self.animation_timer.Start(self.frame_delays[self.current_frame])
        print(f"动画已启动，初始延迟: {self.frame_delays[self.current_frame]}ms")
    
    def pause_animation(self, frame_index=None):
        """暂停 GIF 动画
        
        Args:
            frame_index: 可选参数，指定暂停时显示的帧索引
        """
        if self.animation_timer and self.animation_timer.IsRunning():
            self.animation_timer.Stop()
            self.is_paused = True
            
            # 如果指定了帧索引，跳转到该帧
            if frame_index is not None and 0 <= frame_index < len(self.gif_frames):
                self.current_frame = frame_index
                self.image_ctrl.SetBitmap(self.gif_frames[self.current_frame])
                print(f"动画已暂停在第 {frame_index+1} 帧")
            else:
                print("动画已暂停")
    
    def resume_animation(self):
        """恢复 GIF 动画"""
        if self.animation_timer and not self.animation_timer.IsRunning():
            self.animation_timer.Start(self.frame_delays[self.current_frame])
            self.is_paused = False
            print("动画已恢复")
    
    def on_animation_timer(self, event):
        """动画定时器事件"""
        if self.is_paused:
            return
        
        # 切换到下一帧
        self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
        
        # 更新图像
        self.image_ctrl.SetBitmap(self.gif_frames[self.current_frame])
        
        # 重新设置定时器间隔
        if self.animation_timer and self.animation_timer.IsRunning():
            self.animation_timer.Stop()
        self.animation_timer.Start(self.frame_delays[self.current_frame])
    
    def setup_transparent_window(self):
        """设置窗口透明"""
        try:
            # 根据不同系统设置透明
            if sys.platform == "win32":
                # Windows：设置透明
                self.SetTransparent(255)
            elif sys.platform == "darwin":
                # macOS：设置透明样式
                self.SetWindowStyle(self.GetWindowStyle() | wx.FRAME_TOOL_WINDOW)
                self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
            else:
                # Linux：设置透明
                self.SetTransparent(255)
            
            print("窗口透明设置完成")
        except Exception as e:
            print(f"窗口透明设置失败: {e}")
    
    def bind_events(self):
        """绑定事件"""
        # 鼠标事件
        self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_mouse_left_up)
        self.Bind(wx.EVT_MOTION, self.on_mouse_motion)
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_mouse_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_mouse_leave)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_mouse_right_down)  # 添加右键点击事件
        
        # 窗口事件
        self.Bind(wx.EVT_CLOSE, self.on_close)
    
    def on_mouse_left_down(self, event):
        """鼠标左键按下事件（开始拖拽）"""
        self.is_dragging = True
        self.drag_pos = event.GetPosition()
        self.CaptureMouse()
        # 记录按下位置用于检测点击
        self.click_start_pos = event.GetPosition()
        event.Skip()
    
    def on_mouse_left_up(self, event):
        """鼠标左键释放事件（停止拖拽）"""
        if self.is_dragging:
            self.is_dragging = False
            if self.HasCapture():
                self.ReleaseMouse()
                
            # 检测是否为点击事件（移动距离小于5像素）
            click_end_pos = event.GetPosition()
            distance = ((click_end_pos[0] - self.click_start_pos[0])**2 + 
                      (click_end_pos[1] - self.click_start_pos[1])**2)**0.5
            
            if distance < 5:
                # 执行弹跳效果
                self.bounce()
                # 显示可爱对话框
                self.show_cute_dialog()
        event.Skip()
    
    def on_mouse_motion(self, event):
        """鼠标移动事件（处理拖拽）"""
        if self.is_dragging and self.HasCapture():
            pos = event.GetPosition()
            delta = (pos[0] - self.drag_pos[0], pos[1] - self.drag_pos[1])
            new_pos = self.ClientToScreen(delta)
            self.Move(new_pos)
            
            # 更新对话框位置跟随宠物移动
            self.update_dialog_position()
        event.Skip()
    
    def on_mouse_enter(self, event):
        """鼠标进入窗口事件"""
        # 鼠标悬停时暂停动画并跳转到第一帧
        self.pause_animation(0)
        event.Skip()
    
    def on_mouse_leave(self, event):
        """鼠标离开窗口事件"""
        # 鼠标离开时恢复动画
        self.resume_animation()
        event.Skip()
    
    def on_close(self, event):
        """窗口关闭事件"""
        self.Hide()
        # 清理资源
        if self.animation_timer:
            self.animation_timer.Stop()
        if self.income_timer:
            self.income_timer.Stop()
        # 移除对auto_close_timer的管理，因为它由WorkIncentiveManager负责管理
        # if self.auto_close_timer:
        #     self.auto_close_timer.Stop()
        #     self.auto_close_timer.Destroy()
        if self.bounce_timer:
            self.bounce_timer.Stop()
        
        # 调用上班激励管理器的stop方法，清理其管理的资源
        if hasattr(self, 'work_incentive_manager') and self.work_incentive_manager:
            self.work_incentive_manager.stop()
        
        event.Skip()
        self.Destroy()
        wx.GetApp().ExitMainLoop()
    
    def set_initial_position(self):
        """设置窗口初始位置（屏幕右下角）"""
        # 获取屏幕尺寸
        screen_size = wx.GetDisplaySize()
        window_size = self.GetSize()
        
        # 计算初始位置（右下角，确保完全可见）
        pos_x = screen_size.GetWidth() - self.INIT_X - window_size.GetWidth()
        pos_y = screen_size.GetHeight() - self.INIT_Y - window_size.GetHeight()
        
        # 确保位置在屏幕内
        pos_x = max(0, min(pos_x, screen_size.GetWidth() - window_size.GetWidth()))
        pos_y = max(0, min(pos_y, screen_size.GetHeight() - window_size.GetHeight()))
        
        self.SetPosition((pos_x, pos_y))
        print(f"初始位置: ({pos_x}, {pos_y})")
    
    def show_cute_dialog(self):
        """显示可爱的对话框"""
        # 如果已有对话框打开，先关闭
        if self.dialog and self.dialog.IsShown():
            self.dialog.hide_with_animation()
            # 不立即设置为None，让对话框动画结束后自己销毁
        
        # 生成对话框文本
        if self.work_incentive_manager.config.show_income_bubble and self.work_incentive_manager.config.salary > 0:
            # 计算已赚金额
            earned_money = self.work_incentive_manager.config.calculate_earned_money()
            # 从收益提示模板中随机选择
            templates = self.work_incentive_manager.config.income_templates
            if templates:
                text = random.choice(templates).format(money=round(earned_money, 2))
            else:
                text = f"你今天已经赚了 {round(earned_money, 2)} 元"
        else:
            # 优先使用用户自定义的提示语
            all_texts = []
            if self.work_incentive_manager.config.custom_texts:
                all_texts.extend(self.work_incentive_manager.config.custom_texts)
            
            # 添加默认提示语
            default_texts = [
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
            all_texts.extend(default_texts)
            
            # 如果没有任何文本（理论上不会发生），使用默认文本
            if not all_texts:
                all_texts = default_texts
            
            text = random.choice(all_texts)
        
        # 创建自定义对话框
        self.dialog = CuteDialog(self, text=text)
        
        # 计算对话框位置（宠物上方居中）
        pet_pos = self.GetPosition()
        pet_size = self.GetSize()
        
        # 对话框最终位置（宠物上方居中）
        dialog_size = self.dialog.GetSize()
        end_x = pet_pos.x + (pet_size.x - dialog_size.x) // 2
        end_y = pet_pos.y - dialog_size.y - 10
        
        # 确保对话框在屏幕内
        screen_size = wx.GetDisplaySize()
        if end_x < 0:
            end_x = 0
        elif end_x + dialog_size.x > screen_size.x:
            end_x = screen_size.x - dialog_size.x
        
        end_pos = wx.Point(end_x, end_y)
        
        # 对话框起始位置（宠物头部附近）
        start_x = end_x
        start_y = pet_pos.y + pet_size.y // 4  # 宠物头部位置
        start_pos = wx.Point(start_x, start_y)
        
        # 显示对话框并执行动画
        self.dialog.show_with_animation(start_pos, end_pos)
        
        # 设置自动关闭定时器，使用用户自定义的消失时间
        if self.auto_close_timer:
            self.auto_close_timer.Stop()
            self.auto_close_timer.Destroy()
        
        self.auto_close_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_dialog_auto_close, self.auto_close_timer)
        self.auto_close_timer.Start(self.work_incentive_manager.config.dialog_duration, oneShot=True)  # 使用自定义的消失时间
    
    def on_dialog_auto_close(self, event):
        """对话框自动关闭事件处理"""
        if self.dialog and self.dialog.IsShown():
            self.dialog.hide_with_animation()
            # 不立即设置为None，让对话框动画结束后自己销毁
    
    def update_dialog_position(self):
        """更新对话框位置以跟随宠物"""
        if not self.dialog or not self.dialog.IsShown():
            return
        
        # 计算对话框位置（宠物上方居中）
        pet_pos = self.GetPosition()
        pet_size = self.GetSize()
        dialog_size = self.dialog.GetSize()
        
        dialog_pos_x = pet_pos.x + (pet_size.x - dialog_size.x) // 2
        dialog_pos_y = pet_pos.y - dialog_size.y - 10
        
        # 确保对话框在屏幕内
        screen_size = wx.GetDisplaySize()
        if dialog_pos_x < 0:
            dialog_pos_x = 0
        elif dialog_pos_x + dialog_size.x > screen_size.x:
            dialog_pos_x = screen_size.x - dialog_size.x
        
        if dialog_pos_y < 0:
            dialog_pos_y = pet_pos.y + pet_size.y + 10
        
        self.dialog.SetPosition((dialog_pos_x, dialog_pos_y))
    
    def on_income_timer(self, event):
        """收益提示定时器事件处理"""
        # 当有月薪配置时才自动弹出收益提示
        if self.work_incentive_manager.config.salary > 0:
            self.show_cute_dialog()

    def change_pet_image(self, new_gif_path):
        """更换宠物形象
        
        Args:
            new_gif_path: 新的GIF文件路径
        """
        try:
            # 保存当前位置
            current_pos = self.GetPosition()
            
            # 停止当前动画
            if self.animation_timer:
                self.animation_timer.Stop()
                self.animation_timer = None
            
            # 清空帧列表
            self.gif_frames.clear()
            self.frame_delays.clear()
            self.current_frame = 0
            
            # 更新GIF路径
            self.GIF_PATH = new_gif_path
            
            # 保存用户配置
            import config
            config.Config.set_gif_path(new_gif_path)
            
            # 重新加载GIF
            self.load_gif()
            
            # 恢复位置
            self.SetPosition(current_pos)
            
            # 显示成功消息
            # wx.MessageBox("宠物形象已成功更换！", "成功", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            print(f"更换宠物形象失败: {e}")
            wx.MessageBox(f"更换宠物形象失败: {e}", "错误", wx.OK | wx.ICON_ERROR)


