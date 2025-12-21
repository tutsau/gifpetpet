import json
import os
import datetime

class WorkIncentiveConfig:
    """上班激励配置管理类"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        "salary": 3000,  # 月薪，默认3000元
        "work_start_time": "09:00",  # 工作开始时间
        "work_end_time": "18:00",  # 工作结束时间
        "custom_texts": [],  # 自定义提示语列表
        "dialog_duration": 5000,  # 对话框显示时间（毫秒）
        "income_templates": ["你今天已经赚了 {money} 元"],  # 收益提示模板列表
        "remind_interval": 60,  # 提醒间隔（秒）
    }
    
    @property
    def remind_interval(self):
        """获取收益提示提醒间隔（秒）"""
        return self.config.get("remind_interval", 60)
    
    @remind_interval.setter
    def remind_interval(self, value):
        """设置收益提示提醒间隔（秒）"""
        self.config["remind_interval"] = value
    
    # 配置文件路径
    CONFIG_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "work_incentive_config.json")
    
    def __init__(self):
        """初始化配置"""
        self.load()
        # 确保income_templates是列表格式（向后兼容）
        if isinstance(self.config.get("income_templates"), str):
            self.config["income_templates"] = [self.config["income_templates"]]
        # 过滤空模板
        if "income_templates" in self.config:
            self.config["income_templates"] = [template for template in self.config["income_templates"] if template.strip()]
        # 如果没有模板，添加默认模板
        if not self.config.get("income_templates"):
            self.config["income_templates"] = ["你今天已经赚了 {money} 元"]
        # 将旧的{earned_money}占位符转换为{money}
        if "income_templates" in self.config:
            self.config["income_templates"] = [template.replace("{earned_money}", "{money}") for template in self.config["income_templates"]]
    
    def load(self):
        """从JSON文件加载配置"""
        try:
            if os.path.exists(self.CONFIG_FILE_PATH):
                with open(self.CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    # 合并加载的配置到默认配置，确保所有必要的键都存在
                    self.config.update(loaded_config)
                print("上班激励配置加载成功")
            else:
                print("上班激励配置文件不存在，使用默认配置")
        except Exception as e:
            print(f"上班激励配置加载失败: {e}")
            # 加载失败时使用默认配置
            self.config = self.DEFAULT_CONFIG.copy()
    
    def save(self):
        """保存配置到JSON文件"""
        try:
            with open(self.CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            print("上班激励配置保存成功")
        except Exception as e:
            print(f"上班激励配置保存失败: {e}")
    
    @property
    def salary(self):
        """获取月薪"""
        return self.config.get("salary", 0)
    
    @salary.setter
    def salary(self, value):
        """设置月薪"""
        self.config["salary"] = value
    
    @property
    def work_start_time(self):
        """获取上班时间"""
        return self.config.get("work_start_time", "09:00")
    
    @work_start_time.setter
    def work_start_time(self, value):
        """设置上班时间"""
        self.config["work_start_time"] = value
    
    @property
    def work_end_time(self):
        """获取下班时间"""
        return self.config.get("work_end_time", "18:00")
    
    @work_end_time.setter
    def work_end_time(self, value):
        """设置下班时间"""
        self.config["work_end_time"] = value
    
    @property
    def custom_texts(self):
        """获取自定义提示语列表"""
        return self.config.get("custom_texts", [])
    
    @custom_texts.setter
    def custom_texts(self, value):
        """设置自定义提示语列表"""
        self.config["custom_texts"] = value
    
    @property
    def dialog_duration(self):
        """获取提示消失时间（毫秒）"""
        return self.config.get("dialog_duration", 1000)
    
    @dialog_duration.setter
    def dialog_duration(self, value):
        """设置提示消失时间（毫秒）"""
        self.config["dialog_duration"] = value
    
    @property
    def income_templates(self):
        """获取收益提示模板列表"""
        # 向后兼容：如果是旧版的单个模板字符串，转换为列表
        if isinstance(self.config.get("income_template"), str):
            return [self.config.get("income_template")]
        # 向后兼容：如果是旧版的单个模板键名，转换为新键名
        if "income_template" in self.config:
            templates = [self.config.get("income_template")]
            del self.config["income_template"]
            self.config["income_templates"] = templates
            return templates
        # 返回新版的模板列表
        return self.config.get("income_templates", ["你今天已经赚了 {money} 元"])
    
    @income_templates.setter
    def income_templates(self, value):
        """设置收益提示模板列表"""
        # 确保是列表类型
        if not isinstance(value, list):
            value = [value]
        # 过滤空模板
        value = [template.strip() for template in value if template.strip()]
        self.config["income_templates"] = value
    
    @property
    def income_template(self):
        """获取收益提示模板（向后兼容，返回第一个模板）"""
        templates = self.income_templates
        return templates[0] if templates else "你今天已经赚了 {money} 元"
    
    @income_template.setter
    def income_template(self, value):
        """设置收益提示模板（向后兼容，设置为第一个模板）"""
        templates = self.income_templates
        if templates:
            templates[0] = value
        else:
            templates = [value]
        self.config["income_templates"] = templates
    
    def calculate_earned_money(self):
        """计算当前已赚取的工资"""
        if self.salary <= 0:
            return 0
            
        # 获取当前时间
        now = datetime.datetime.now()
        today = now.date()
    
        # 解析上班和下班时间
        work_start = datetime.datetime.strptime(self.work_start_time, "%H:%M").time()
        work_end = datetime.datetime.strptime(self.work_end_time, "%H:%M").time()
    
        # 计算今天的上班和下班时间点
        work_start_datetime = datetime.datetime.combine(today, work_start)
        work_end_datetime = datetime.datetime.combine(today, work_end)
    
        # 如果下班时间早于上班时间，说明跨天了
        if work_end_datetime < work_start_datetime:
            work_end_datetime += datetime.timedelta(days=1)
    
        # 计算工作时长（小时）
        work_duration_hours = (work_end_datetime - work_start_datetime).total_seconds() / 3600
    
        # 计算日薪
        daily_salary = self.salary / 21.75  # 假设每月30天
    
        # 计算每小时工资
        hourly_salary = daily_salary / work_duration_hours
    
        # 计算当前已经工作的时长
        if now < work_start_datetime:
            # 还没到上班时间
            return 0
        elif now > work_end_datetime:
            # 已经下班了
            return daily_salary
        else:
            # 正在工作中
            worked_hours = (now - work_start_datetime).total_seconds() / 3600
            return hourly_salary * worked_hours