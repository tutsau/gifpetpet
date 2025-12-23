import wx
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pet import FinalGIFDesktopPet
from work_incentive.manager import WorkIncentiveManager
from work_incentive.config import WorkIncentiveConfig

# 创建应用程序实例
app = wx.App(False)

# 创建宠物实例
pet = FinalGIFDesktopPet()
pet.Show()

# 创建上班激励管理器
manager = WorkIncentiveManager(pet)

# 设置配置，确保显示提示
manager.config.salary = 10000
manager.config.remind_interval = 60  # 60秒
manager.config.dialog_duration = 5000  # 5秒

# 立即显示收益提示
manager.show_income_hint()

# 启动事件循环
app.MainLoop()
