#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""托盘图标模块

实现宠物应用的托盘图标及菜单功能。
"""

import wx
import os
import sys


class PetTaskBarIcon:
    """宠物应用的托盘图标类（兼容模式）"""
    def __init__(self, frame):
        self.frame = frame
        self.taskbar_supported = False
        self.taskbar_icon = None
        self.status_item = None
        
        try:
            # 根据操作系统选择不同的实现方式
            if sys.platform == 'darwin':
                # 在macOS上尝试使用pyobjc
                self._init_macos_taskbar()
            else:
                # 在其他平台上使用wxPython的TaskBarIcon
                self._init_wx_taskbar()
        except Exception as e:
            print(f"初始化托盘图标失败: {e}")
            import traceback
            traceback.print_exc()
            self.taskbar_supported = False
    
    def _init_macos_taskbar(self):
        """在macOS上使用pyobjc实现托盘图标"""
        try:
            # 尝试导入pyobjc
            from AppKit import NSStatusBar, NSStatusItem, NSImage, NSMenu, NSMenuItem
            from Foundation import NSBundle, NSString
            
            # 创建状态栏项
            status_bar = NSStatusBar.systemStatusBar()
            self.status_item = status_bar.statusItemWithLength_(-1)
            
            # 设置图标
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pet.gif")
            if os.path.exists(icon_path):
                # 注意：在macOS上，NSImage不直接支持GIF，我们使用PNG或JPG
                # 这里使用默认图标作为替代
                icon = NSImage.imageNamed_("NSActionTemplate")
            else:
                icon = NSImage.imageNamed_("NSActionTemplate")
            
            self.status_item.setImage_(icon)
            self.status_item.setHighlightMode_(True)
            
            # 设置工具提示
            self.status_item.setToolTip_("可爱宠物")
            
            # 创建菜单
            menu = NSMenu.alloc().init()
            menu.setAutoenablesItems_(True)
            
            # 创建上班激励菜单项
            work_incentive_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("上班激励", "onWorkIncentive", "")
            work_incentive_item.setTarget_(self)
            work_incentive_item.setEnabled_(True)
            menu.addItem_(work_incentive_item)
            
            # 创建退出菜单项
            exit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("退出", "onExit", "")
            exit_item.setTarget_(self)
            exit_item.setEnabled_(True)
            menu.addItem_(exit_item)
            
            # 设置菜单
            self.status_item.setMenu_(menu)
            
            # 保存引用
            self._menu = menu
            self._work_incentive_item = work_incentive_item
            self._exit_item = exit_item
            
            self.taskbar_supported = True
        except ImportError:
            print("pyobjc未安装，无法在macOS上创建托盘图标")
            # 尝试安装pyobjc
            try:
                import subprocess
                subprocess.run(['pip3', 'install', 'pyobjc'], check=True)
                print("pyobjc安装成功，请重新启动程序")
            except Exception as e:
                print(f"安装pyobjc失败: {e}")
        except Exception as e:
            print(f"初始化macOS托盘图标失败: {e}")
            import traceback
            traceback.print_exc()
    
    def onWorkIncentive(self):
        """上班激励菜单项的回调方法"""
        self.on_work_incentive(None)
    
    def onExit(self):
        """退出菜单项的回调方法"""
        self.on_exit(None)
    
    def _init_wx_taskbar(self):
        """使用wxPython的TaskBarIcon实现托盘图标"""
        try:
            # 尝试导入TaskBarIcon
            taskbar_icon_class = None
            taskbar_module = None
            
            # 首先检查wx模块是否有TaskBarIcon
            if hasattr(wx, 'TaskBarIcon'):
                taskbar_icon_class = wx.TaskBarIcon
                taskbar_module = wx
            # 然后检查wx.adv模块是否有TaskBarIcon
            elif hasattr(wx, 'adv') and hasattr(wx.adv, 'TaskBarIcon'):
                taskbar_icon_class = wx.adv.TaskBarIcon
                taskbar_module = wx.adv
            
            if taskbar_icon_class:
                # 创建托盘图标实例
                self.taskbar_icon = taskbar_icon_class()
                self.taskbar_supported = True
                
                # 创建托盘图标
                icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pet.gif")
                if os.path.exists(icon_path):
                    # 从GIF文件创建图标
                    img = wx.Image(icon_path, wx.BITMAP_TYPE_GIF)
                    # 调整大小适合托盘
                    img.Rescale(16, 16, wx.IMAGE_QUALITY_HIGH)
                    icon = wx.Icon(img.ConvertToBitmap())
                else:
                    # 使用默认图标
                    icon = wx.Icon(wx.Icon.GetDefaultSize())
                
                # 设置托盘图标
                self.taskbar_icon.SetIcon(icon, "可爱宠物")
                
                # 获取事件类型
                if taskbar_module == wx:
                    evt_taskbar_left_down = wx.EVT_TASKBAR_LEFT_DOWN
                    evt_menu = wx.EVT_MENU
                else:
                    evt_taskbar_left_down = wx.adv.EVT_TASKBAR_LEFT_DOWN
                    evt_menu = wx.EVT_MENU
                
                # 绑定点击事件
                self.taskbar_icon.Bind(evt_taskbar_left_down, self.on_left_click)
                
                # 保存事件类型供后续使用
                self.evt_menu = evt_menu
        except Exception as e:
            print(f"初始化wxPython托盘图标失败: {e}")
            import traceback
            traceback.print_exc()
    
    def CreatePopupMenu(self):
        """创建托盘右键菜单（用于wxPython版本）"""
        if not self.taskbar_supported or not self.taskbar_icon:
            return None
        
        menu = wx.Menu()
        
        # 上班激励菜单项
        work_incentive_item = menu.Append(wx.ID_ANY, "上班激励")
        self.taskbar_icon.Bind(self.evt_menu, self.on_work_incentive, work_incentive_item)
        
        # 退出菜单项
        exit_item = menu.Append(wx.ID_EXIT, "退出")
        self.taskbar_icon.Bind(self.evt_menu, self.on_exit, exit_item)
        
        return menu
    
    def on_left_click(self, event):
        """托盘图标左键点击事件"""
        if not self.taskbar_supported:
            return
        
        # 左键点击显示/隐藏宠物窗口
        if self.frame.IsShown():
            self.frame.Hide()
        else:
            self.frame.Show()
    
    def on_work_incentive(self, event):
        """上班激励菜单项点击事件"""
        if not self.taskbar_supported:
            return
        
        # 调用主窗口的上班激励方法
        self.frame.on_work_incentive(event)
    
    def on_exit(self, event):
        """退出菜单项点击事件"""
        if not self.taskbar_supported:
            return
        
        # 调用主窗口的关闭方法
        self.frame.on_close(event)