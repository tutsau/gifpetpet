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
    
    # 配置文件路径
    CONFIG_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "work_incentive_config.json")
    
    def __init__(self):
        """初始化配置"""
        # 先初始化self.config为默认配置
        self.config = self.DEFAULT_CONFIG.copy()
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
                    # 合并加载的配置到当前配置，确保所有必要的键都存在
                    self.config.update(loaded_config)
                print("上班激励配置加载成功")
            else:
                print("上班激励配置文件不存在，使用默认配置")
        except Exception as e:
            print(f"上班激励配置加载失败: {e}")
            # 加载失败时重置为默认配置
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
    def remind_interval(self):
        """获取收益提示提醒间隔（秒）"""
        return self.config.get("remind_interval", 60)
    
    @remind_interval.setter
    def remind_interval(self, value):
        """设置收益提示提醒间隔（秒）"""
        self.config["remind_interval"] = value
    
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
    
    def calculate_earned_money(self):
        """计算今天已经赚了多少钱"""
        try:
            # 获取当前时间
            now = datetime.datetime.now()
            current_time = now.time()
            
            # 解析上班和下班时间
            work_start = datetime.datetime.strptime(self.work_start_time, "%H:%M").time()
            work_end = datetime.datetime.strptime(self.work_end_time, "%H:%M").time()
            
            # 如果当前时间在上班时间之前，返回0
            if current_time < work_start:
                return 0
            
            # 如果当前时间在下班时间之后，计算全天工作时间
            if current_time > work_end:
                worked_hours = (datetime.datetime.combine(now.date(), work_end) - datetime.datetime.combine(now.date(), work_start)).total_seconds() / 3600
            else:
                # 计算从上班到现在的工作时间
                worked_hours = (datetime.datetime.combine(now.date(), current_time) - datetime.datetime.combine(now.date(), work_start)).total_seconds() / 3600
            
            # 如果工作时间小于0，返回0
            if worked_hours <= 0:
                return 0
            
            # 计算每小时薪资
            hourly_salary = self.salary / (21.75 * 8)  # 21.75是平均工作日，8是每天工作小时数
            
            # 返回已赚金额
            return hourly_salary * worked_hours
        except Exception as e:
            print(f"计算已赚金额失败: {e}")
            return 0