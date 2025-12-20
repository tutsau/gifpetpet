# GIF 桌面宠物程序

基于 wxPython 开发的跨平台（macOS/Windows）、轻量稳定的 GIF 桌面宠物程序。

## 功能特性

### 窗口核心特性
- ✅ 无边框窗口：仅显示 GIF 内容，隐藏标题栏和任务栏图标
- ✅ 透明背景：完美适配 GIF 透明区域，无白边/锯齿
- ✅ 置顶显示：窗口始终在其他窗口上方
- ✅ 拖拽移动：鼠标左键按住可自由拖拽
- ✅ 尺寸适配：窗口大小自动匹配 GIF 原始尺寸
- ✅ 无焦点：不获取键盘焦点，不影响其他程序操作

### GIF 播放功能
- ✅ 原生播放：使用 wxPython 原生 `wx.Animation` 循环播放 GIF
- ✅ 悬停控制：鼠标悬停暂停，离开恢复播放
- ✅ 容错处理：GIF 文件不存在/损坏时友好提示，程序不崩溃
- ✅ 高DPI适配：在高分辨率屏幕下无模糊

### 系统托盘
- ✅ 托盘图标：自动提取 GIF 第一帧作为托盘图标
- ✅ 右键菜单：包含「显示宠物」「隐藏宠物」「退出」选项
- ✅ 左键交互：点击托盘图标切换显示/隐藏状态
- ✅ 关闭行为：点击关闭按钮时隐藏到托盘，不退出程序

### 交互体验
- ✅ 光标反馈：鼠标悬停时变为手型
- ✅ 资源清理：退出时释放所有资源，无内存泄漏
- ✅ 启动位置：默认显示在屏幕右上角

## 技术栈

- **主框架**：wxPython 4.2.1+
- **语言**：Python 3.8+
- **依赖**：仅 Python 标准库 + wxPython 核心模块

## 快速开始

### 1. 安装依赖

#### Windows
```bash
pip install wxPython
```

#### macOS
```bash
# 使用 Homebrew 安装 wxPython 依赖（推荐）
brew install wxpython

# 或者使用 pip 安装
pip install wxPython
```

### 2. 准备 GIF 素材

1. 将你喜欢的 GIF 动画文件命名为 `pet.gif`
2. 放置在与 `wx_petpet.py` 相同的目录下
3. 推荐使用透明背景的 GIF 文件，尺寸建议在 100x100 到 300x300 之间

### 3. 运行程序

```bash
python wx_petpet.py
```

## 自定义配置

你可以修改 `wx_petpet.py` 中的以下常量来定制宠物：

```python
# GIF 文件路径
GIF_PATH = "pet.gif"

# 初始位置（X 为负表示从屏幕右侧内缩的距离）
INIT_X = -100  # 初始 X 坐标
INIT_Y = 100   # 初始 Y 坐标

# 动画速度（-1 表示使用 GIF 原始速度）
ANIMATION_SPEED = -1
```

## 打包教程

使用 PyInstaller 将程序打包为可执行文件：

### Windows

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包（单文件模式）
pyinstaller --onefile --windowed --icon=pet.ico --name="GIF宠物" wx_petpet.py
```

### macOS

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包（应用程序模式）
pyinstaller --onefile --windowed --icon=pet.icns --name="GIF宠物" wx_petpet.py
```

#### 内存优化技巧

1. **剔除冗余依赖**：使用 `--exclude-module` 参数排除不需要的模块
   ```bash
   pyinstaller --onefile --windowed --exclude-module numpy --exclude-module pandas wx_petpet.py
   ```

2. **使用 UPX 压缩**：
   ```bash
   # 安装 UPX
   # Windows: 下载 https://upx.github.io/
   # macOS: brew install upx
   
   # 使用 UPX 压缩
   pyinstaller --onefile --windowed --upx-dir=/path/to/upx wx_petpet.py
   ```

3. **优化 wxPython 导入**：确保只导入必要的 wxPython 模块

## 跨平台注意事项

### Windows
- 使用 `SetTransparent` 实现透明窗口
- 托盘图标尺寸为 32x32px
- 支持 Windows 7/8/10/11

### macOS
- 使用特殊窗口样式实现透明效果
- 托盘图标尺寸为 16x16px
- 支持 macOS 10.14+（Mojave 及以上版本）
- 注意：在某些 macOS 版本中，可能需要在「系统偏好设置」→「安全性与隐私」→「辅助功能」中允许程序控制屏幕

## 问题排查

### 1. GIF 文件加载失败
- 检查文件路径是否正确
- 确保 GIF 文件格式正确，没有损坏
- 尝试使用其他 GIF 文件测试

### 2. 托盘图标不显示
- **Windows**：确保程序有创建托盘图标的权限
- **macOS**：检查系统偏好设置中的安全权限

### 3. 透明窗口有白边
- Windows：尝试调整 `SetTransparent` 的参数
- macOS：确保使用了正确的窗口样式

### 4. 高DPI屏幕下模糊
- 确保 wxPython 版本 ≥4.2.1
- 程序已自动启用高DPI支持

### 5. 程序崩溃
- 检查 Python 和 wxPython 版本是否兼容
- 查看错误信息，排查 GIF 文件问题

## 内存占用

- **Windows**：20~25MB
- **macOS**：25~30MB

## 退出程序

- 右键点击系统托盘图标，选择「退出」
- 或使用快捷键 Ctrl+C（仅在命令行运行时有效）

## 开发说明

### 项目结构

```
petpet/
├── wx_petpet.py  # 主程序文件
├── pet.gif       # GIF 素材（需自行添加）
└── README.md     # 说明文档
```

### 代码规范

- 采用面向对象设计，封装为 `WxGIFDesktopPet` 类
- 关键函数添加中文注释
- 变量命名语义化
- 捕获所有可能的异常，避免程序崩溃

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.0.0
- 初始版本发布
- 实现所有核心功能
- 支持 Windows 和 macOS 平台
