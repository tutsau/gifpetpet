import datetime
import wx
from .config import WorkIncentiveConfig
from .dialog import WorkIncentiveDialog
from .custom_texts_dialog import CustomTextsDialog

class WorkIncentiveManager:
    """上班激励功能管理器"""
    
    def __init__(self, pet):
        """初始化上班激励管理器
        
        Args:
            pet: 宠物对象，用于显示提示和获取窗口上下文
        """
        self.pet = pet
        self.config = WorkIncentiveConfig()
        self.auto_close_timer = None
        self.income_timer = None
        
    def show_config_dialog(self):
        """显示配置对话框"""
        dlg = WorkIncentiveDialog(self.pet, self.config)
        
        # 显示对话框并等待用户操作
        if dlg.ShowModal() == wx.ID_OK:
            # 用户点击了确定按钮，保存配置
            self.config.save()
            
            # 检查是否需要重启收益提示定时器
            if self.income_timer:
                self.income_timer.Stop()
                self.income_timer.Destroy()
                self.income_timer = None
            
            # 如果设置了薪资，启动收益提示定时器
            if self.config.salary > 0:
                self.income_timer = wx.Timer(self.pet)
                self.pet.Bind(wx.EVT_TIMER, self.on_income_timer, self.income_timer)
                self.income_timer.Start(self.config.remind_interval * 1000)  # 转换为毫秒
        
        dlg.Destroy()
    
    def show_custom_texts_dialog(self):
        """显示自定义提示语设置对话框"""
        dlg = CustomTextsDialog(self.pet, self.config)
        
        # 显示对话框并等待用户操作
        if dlg.ShowModal() == wx.ID_OK:
            # 用户点击了确定按钮，保存配置
            self.config.save()
        
        dlg.Destroy()
    
    def show_income_hint(self):
        """显示收益提示"""
        if self.config.salary <= 0 or not self.config.show_income_bubble:
            return
    
        # 直接调用宠物的气泡对话框方法
        self.pet.show_cute_dialog()
    
    def close_hint(self, dlg):
        """关闭提示对话框"""
        try:
            if dlg:
                dlg.Destroy()
        except Exception as e:
            # 如果对话框已经被销毁或其他异常，忽略
            print(f"关闭对话框时发生异常: {e}")
            import traceback
            traceback.print_exc()
        
        if self.auto_close_timer:
            self.auto_close_timer.Stop()
            self.auto_close_timer.Destroy()
            self.auto_close_timer = None
    
    def stop(self):
        """停止并清理资源"""
        if self.auto_close_timer:
            self.auto_close_timer.Stop()
            self.auto_close_timer.Destroy()
            self.auto_close_timer = None
        
        if self.income_timer:
            self.income_timer.Stop()
            self.income_timer.Destroy()
            self.income_timer = None
    
    def on_income_timer(self, event):
        """收益提示定时器事件处理"""
        self.show_income_hint()