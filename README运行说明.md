# 桌面宠物应用 - 运行说明

## 应用简介
这是一个基于Python和wxPython开发的桌面宠物应用，使用GIF动画作为宠物形象，并具有上班激励功能。

## 运行方式

### 方法一：直接点击运行（推荐）
1. 打开 `dist` 文件夹
2. 找到 `桌面宠物.app` 文件
3. 双击即可启动应用

### 方法二：命令行运行
```bash
python3 main.py
```

## 功能说明

1. **宠物动画**：
   - 加载并显示GIF动画
   - 支持窗口透明效果
   - 可在桌面自由移动

2. **上班激励**：
   - 定时显示上班收益提示
   - 支持自定义薪资和提示模板
   - 配置文件路径：`work_incentive/work_incentive_config.json`

## 退出方式

1. **正常退出**：
   - 点击宠物窗口，然后按 `Ctrl+C` 退出
   - 或直接关闭终端窗口

2. **强制退出**：
   - 在macOS的活动监视器中结束进程

## 注意事项

1. 首次运行可能需要一些时间加载GIF资源
2. 应用程序支持macOS系统
3. 如遇到运行问题，请检查是否已安装Python 3和wxPython依赖

## 配置说明

配置文件 `work_incentive/work_incentive_config.json` 包含以下可配置项：

- `salary`：月薪金额
- `income_templates`：收益提示模板列表
- `work_start_time`：上班时间
- `work_end_time`：下班时间
- `show_income_interval`：显示收益提示的时间间隔（毫秒）

您可以根据需要修改这些配置项来自定义应用程序的行为。
