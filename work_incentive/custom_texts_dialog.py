import wx

class CustomTextsDialog(wx.Dialog):
    """自定义提示语设置对话框"""
    
    def __init__(self, parent, config):
        """初始化对话框
        
        Args:
            parent: 父窗口
            config: 上班激励配置对象
        """
        super().__init__(parent, title="自定义提示语设置", size=(400, 450), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
        # 保存配置引用
        self.config = config
        
        # 创建界面
        self.create_ui()
    
    def create_ui(self):
        """创建对话框界面"""
        # 创建主容器
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 自定义提示语
        custom_texts_label = wx.StaticText(self, label="自定义提示语（每行一条）：")
        self.custom_texts_ctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER, size=(350, 300))
        # 将自定义提示语列表转换为多行文本
        self.custom_texts_ctrl.SetValue("\n".join(self.config.custom_texts))
        
        # 按钮区域
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_button = wx.Button(self, wx.ID_OK, "确定")
        cancel_button = wx.Button(self, wx.ID_CANCEL, "取消")
        
        button_sizer.AddStretchSpacer()
        button_sizer.Add(ok_button, 0, wx.ALL, 5)
        button_sizer.Add(cancel_button, 0, wx.ALL, 5)

        # 绑定事件
        self.Bind(wx.EVT_BUTTON, self.on_ok, ok_button)
        
        # 添加到主容器
        main_sizer.Add(custom_texts_label, 0, wx.ALL, 5)
        main_sizer.Add(self.custom_texts_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(button_sizer, 0, wx.EXPAND | wx.ALL, 5)
        # 设置主容器
        self.SetSizer(main_sizer)
        self.Layout()

    def on_ok(self, event):
        """确定按钮点击事件"""
        try:
            # 保存自定义提示语（去除空行）
            self.config.custom_texts = [text.strip() for text in self.custom_texts_ctrl.GetValue().split("\n") if text.strip()]
            
            event.Skip()
        except Exception as e:
            wx.MessageBox(f"保存失败: {e}", "错误", wx.OK | wx.ICON_ERROR)
