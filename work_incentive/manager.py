import datetime
import wx
from .config import WorkIncentiveConfig
from .dialog import WorkIncentiveDialog

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
    
    def show_income_hint(self):
        """显示收益提示"""
        if self.config.salary <= 0:
            return
        
        # 计算已赚金额
        earned_money = self.config.calculate_earned_money()
        
        # 构建提示文本
        if self.config.custom_texts:
            # 如果有自定义提示语，随机选择一个
            import random
            text = random.choice(self.config.custom_texts).format(money=earned_money)
        else:
            # 使用用户自定义的收益提示模板
            text = self.config.income_template.format(earned_money=earned_money)
        
        # 创建提示对话框
        dlg = wx.Dialog(self.pet, title="上班激励", size=(300, 150))
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        text_label = wx.StaticText(dlg, label=text)
        text_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        
        main_sizer.Add(text_label, 1, wx.ALL | wx.ALIGN_CENTER, 20)
        dlg.SetSizer(main_sizer)
        dlg.Layout()
        
        # 显示对话框
        dlg.Show()
        
        # 设置自动关闭定时器
        if self.auto_close_timer:
            self.auto_close_timer.Stop()
            self.auto_close_timer.Destroy()
        
        self.auto_close_timer = wx.Timer(self.pet)
        self.pet.Bind(wx.EVT_TIMER, lambda event: self.close_hint(dlg), self.auto_close_timer)
        self.auto_close_timer.Start(self.config.dialog_duration, oneShot=True)
    
    def close_hint(self, dlg):
        """关闭提示对话框"""
        if dlg and not dlg.IsDestroyed():
            dlg.Destroy()
            
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
