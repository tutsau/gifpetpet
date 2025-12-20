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

使用方法：
1. 将你的 GIF 文件重命名为 pet.gif 并放在同一目录下
2. 运行程序：python3 final_petpet.py
3. 点击并拖拽宠物可以移动位置
4. 鼠标悬停在宠物上会暂停动画并显示第一帧
5. 鼠标离开后会恢复动画

注意：在某些环境中可能需要安装依赖：
pip install pillow wxPython
"""

import wx
import os
import sys
from PIL import Image

class FinalGIFDesktopPet(wx.Frame):
    """最终版 GIF 桌面宠物主类"""
    
    # 配置常量
    GIF_PATH = "oiiai_cat.gif"  # GIF 素材路径，可替换为自定义路径
    INIT_X = -100  # 初始 X 坐标（-100 表示屏幕右侧内缩 100px）
    INIT_Y = 100  # 初始 Y 坐标（顶部往下 100px）
    
    def __init__(self):
        """初始化桌面宠物"""
        # 设置窗口样式：无边框、无任务栏图标、置顶
        style = (wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.NO_BORDER)
        
        super(FinalGIFDesktopPet, self).__init__(None, wx.ID_ANY, "", 
                                               style=style, size=(100, 100))
        
        # 初始化变量
        self.is_dragging = False
        self.drag_pos = (0, 0)
        
        # GIF 动画相关变量
        self.gif_frames = []      # GIF 帧列表
        self.frame_delays = []    # 帧延迟列表
        self.current_frame = 0    # 当前播放帧
        self.animation_timer = None  # 动画定时器
        self.is_paused = False    # 动画暂停状态
        
        # 创建图像控件
        self.image_ctrl = wx.StaticBitmap(self, wx.ID_ANY)
        
        # 加载 GIF 动画
        self.load_gif()
        
        # 设置窗口透明
        self.setup_transparent_window()
        
        # 绑定事件
        self.bind_events()
        
        # 设置初始位置
        self.set_initial_position()
        
        # 显示窗口
        self.Show()
    
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
                
                # 打印帧信息（用于调试）
                print(f"帧 {i+1}/{num_frames}: 模式={frame.mode}, 尺寸={frame.size}, 延迟={delay}ms")
                
                # 创建 wx.Image
                wx_image = wx.Image(*frame.size)
                
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
        
        # 窗口事件
        self.Bind(wx.EVT_CLOSE, self.on_close)
    
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
        # 清理资源
        if self.animation_timer:
            self.animation_timer.Stop()
            self.animation_timer = None
        self.Destroy()
        wx.GetApp().ExitMainLoop()
    
    def set_initial_position(self):
        """设置窗口初始位置（屏幕右上角）"""
        # 获取屏幕尺寸
        screen_size = wx.GetDisplaySize()
        window_size = self.GetSize()
        
        # 计算初始位置（右上角）
        pos_x = screen_size.GetWidth() + self.INIT_X - window_size.GetWidth()
        pos_y = self.INIT_Y
        
        self.SetPosition((pos_x, pos_y))
        print(f"初始位置: ({pos_x}, {pos_y})")


def main():
    """程序主入口"""
    print(f"Python 版本: {sys.version}")
    print(f"wxPython 版本: {wx.__version__}")
    print(f"Pillow 版本: {Image.__version__}")
    print(f"操作系统: {sys.platform}")
    
    try:
        app = wx.App(redirect=False)
        pet = FinalGIFDesktopPet()
        print("桌面宠物已启动，按 Ctrl+C 退出")
        app.MainLoop()
    except Exception as e:
        import traceback
        print(f"程序错误: {e}")
        traceback.print_exc()
        input("按回车退出...")

if __name__ == "__main__":
    main()