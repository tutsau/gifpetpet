import wx
import re

class WorkIncentiveDialog(wx.Dialog):
    """上班激励配置对话框"""
    
    def __init__(self, parent, config):
        """初始化对话框
        
        Args:
            parent: 父窗口
            config: 上班激励配置对象
        """
        super().__init__(parent, title="上班激励设置", size=(300, 250))
        
        # 保存配置引用
        self.config = config
        
        # 创建界面
        self.create_ui()
    
    def create_ui(self):
        """创建对话框界面"""
        # 创建主容器
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 月薪输入
        salary_sizer = wx.BoxSizer(wx.HORIZONTAL)
        salary_label = wx.StaticText(self, label="月薪：")
        self.salary_ctrl = wx.TextCtrl(self, value=str(self.config.salary) if self.config.salary > 0 else "")
        salary_unit = wx.StaticText(self, label="元")
        
        salary_sizer.Add(salary_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        salary_sizer.Add(self.salary_ctrl, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        salary_sizer.Add(salary_unit, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        # 上班时间输入
        start_time_sizer = wx.BoxSizer(wx.HORIZONTAL)
        start_time_label = wx.StaticText(self, label="上班时间：")
        self.start_time_ctrl = wx.TextCtrl(self, value=self.config.work_start_time)
        
        start_time_sizer.Add(start_time_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        start_time_sizer.Add(self.start_time_ctrl, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        # 下班时间输入
        end_time_sizer = wx.BoxSizer(wx.HORIZONTAL)
        end_time_label = wx.StaticText(self, label="下班时间：")
        self.end_time_ctrl = wx.TextCtrl(self, value=self.config.work_end_time)
        
        end_time_sizer.Add(end_time_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        end_time_sizer.Add(self.end_time_ctrl, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        # 自定义提示语
        custom_texts_label = wx.StaticText(self, label="自定义提示语（每行一条）：")
        self.custom_texts_ctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER, size=(350, 150))
        # 将自定义提示语列表转换为多行文本
        self.custom_texts_ctrl.SetValue("\n".join(self.config.custom_texts))
        
        # 提示消失时间
        duration_sizer = wx.BoxSizer(wx.HORIZONTAL)
        duration_label = wx.StaticText(self, label="提示消失时间：")
        self.duration_ctrl = wx.TextCtrl(self, value=str(self.config.dialog_duration // 1000))  # 显示秒数
        duration_unit = wx.StaticText(self, label="秒")
        
        duration_sizer.Add(duration_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        duration_sizer.Add(self.duration_ctrl, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        duration_sizer.Add(duration_unit, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        # 按钮区域
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_button = wx.Button(self, wx.ID_OK, "确定")
        cancel_button = wx.Button(self, wx.ID_CANCEL, "取消")
        
        button_sizer.AddStretchSpacer()
        button_sizer.Add(ok_button, 0, wx.ALL, 5)
        button_sizer.Add(cancel_button, 0, wx.ALL, 5)
        
        # 添加到主容器
        main_sizer.Add(salary_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(start_time_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(end_time_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(custom_texts_label, 0, wx.ALL, 5)
        main_sizer.Add(self.custom_texts_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(duration_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(button_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 设置主容器
        self.SetSizer(main_sizer)
        self.Layout()
        
        # 绑定事件
        self.Bind(wx.EVT_BUTTON, self.on_ok, ok_button)
        self.Bind(wx.EVT_TEXT, self.on_salary_text, self.salary_ctrl)
        self.Bind(wx.EVT_TEXT, self.on_time_text, self.start_time_ctrl)
        self.Bind(wx.EVT_TEXT, self.on_time_text, self.end_time_ctrl)
        self.Bind(wx.EVT_TEXT, self.on_duration_text, self.duration_ctrl)
    
    def on_ok(self, event):
        """确定按钮点击事件"""
        # 验证并保存输入
        try:
            # 更新配置对象
            self.config.salary = int(self.salary_ctrl.GetValue()) if self.salary_ctrl.GetValue() else 0
            
            # 简单验证时间格式
            start_time = self.start_time_ctrl.GetValue()
            end_time = self.end_time_ctrl.GetValue()
            
            if not self.is_valid_time(start_time) or not self.is_valid_time(end_time):
                wx.MessageBox("时间格式错误，请输入正确的时间（如：09:00）", "错误", wx.OK | wx.ICON_ERROR)
                return
            
            # 验证消失时间
            duration_text = self.duration_ctrl.GetValue()
            if not duration_text.isdigit() or int(duration_text) <= 0:
                wx.MessageBox("提示消失时间必须是大于0的数字", "错误", wx.OK | wx.ICON_ERROR)
                return
            
            self.config.work_start_time = start_time
            self.config.work_end_time = end_time
            
            # 保存自定义提示语（去除空行）
            self.config.custom_texts = [text.strip() for text in self.custom_texts_ctrl.GetValue().split("\n") if text.strip()]
            
            # 保存消失时间（转换为毫秒）
            self.config.dialog_duration = int(duration_text) * 1000
            
            event.Skip()
        except ValueError:
            wx.MessageBox("月薪必须是数字", "错误", wx.OK | wx.ICON_ERROR)
    
    def on_duration_text(self, event):
        """消失时间输入文本变化事件"""
        text = self.duration_ctrl.GetValue()
        # 只允许输入数字
        if text and not text.isdigit():
            self.duration_ctrl.SetValue(text[:-1])
    
    def on_salary_text(self, event):
        """月薪输入文本变化事件"""
        text = self.salary_ctrl.GetValue()
        # 只允许输入数字
        if text and not text.isdigit():
            self.salary_ctrl.SetValue(text[:-1])
    
    def on_time_text(self, event):
        """时间输入文本变化事件"""
        # 简单的时间格式控制
        ctrl = event.GetEventObject()
        text = ctrl.GetValue()
        
        # 只允许输入数字和冒号
        if len(text) > 0 and not (text[-1].isdigit() or (text[-1] == ':' and ':' not in text)):
            ctrl.SetValue(text[:-1])
    
    def is_valid_time(self, time_str):
        """验证时间格式是否正确"""
        if not time_str:
            return False
            
        # 简单验证时间格式 HH:MM
        parts = time_str.split(':')
        if len(parts) != 2:
            return False
            
        try:
            hour = int(parts[0])
            minute = int(parts[1])
            return 0 <= hour < 24 and 0 <= minute < 60
        except ValueError:
            return False
