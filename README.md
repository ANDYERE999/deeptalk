# 🔐 非对称加/解密器

> 一个基于RSA和AES混合加密的安全通信工具，支持文本消息和文件的端到端加密。
> 一个几乎没有人工干预(除了截图、图标、初始化仓库)通过vibe coding得到的小工具

![应用界面](demo.png)

## ✨ 功能特性

- **RSA密钥对生成** - 一键生成2048位RSA密钥对
- **消息加密/解密** - 支持多接收方的文本消息加密
- **文件加密/解密** - 支持多文件打包加密，生成.epkg格式
- **混合加密** - 结合RSA和AES-256-GCM确保安全性

## 🚀 快速开始

### 方法一：使用预编译版本（推荐）

下载最新版本的 `非对称加解密器.exe`

### 方法二：从源码运行

```bash
# 克隆仓库
git clone <repository-url>
cd deeptalk

# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

## 🔨 自行构建

### 环境要求

- Python 3.7+
- Windows/macOS/Linux

### 构建步骤

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. **构建可执行文件**
   ```bash
   # 使用提供的图标
   pyinstaller --onefile --windowed --icon=asset/icon.ico --name="非对称加解密器" main.py
   
   # 不使用图标（使用默认图标）
   pyinstaller --onefile --windowed --name="非对称加解密器" main.py
   ```

3. **运行**
   ```bash
   # 可执行文件位于 dist/ 目录下
   ./dist/非对称加解密器.exe
   ```

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)

---

**⚠️ 免责声明**: 本工具仅供学习和合法用途使用。使用者需自行承担使用风险，开发者不对任何数据丢失或安全问题负责。 