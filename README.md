# Antigravity 智能管理器 [中文语言包] 使用手册

> **版本**：v11.0 (Global Scan 版)  
> **适用对象**：Antigravity Agent Manager (智能体管理器)  
> **特性**：DOM 动态注入、全自动备份、一键还原、零核心破坏

---

## 📖 项目简介

本工具专为 Antigravity 设计，通过在应用层注入轻量级翻译引擎，将原本全英文的 **Agent Manager** 界面实时汉化。

### 核心亮点
- **动态扫描**：采用 MutationObserver 技术，实时监控并翻译动态加载的 UI 元素。
- **安全可靠**：不修改软件二进制文件，仅在入口 HTML 添加一行引用。
- **自动防损**：注入前自动创建 `.bak` 备份，支持随时从备份 100% 恢复。
- **校验绕过**：自动更新 `product.json` 校验树，避免软件报修。

---

## 🛠️ 环境准备

在开始汉化之前，请确保您的设备已满足以下条件：
1. **Python 环境**：已安装 Python 3.x。
2. **退出软件**：请确保 Antigravity 软件已完全关闭（由于涉及写入文件，建议检查任务管理器确保无残留进程）。

---

## 🚀 安装步骤 (一键汉化)

只需三个简单步骤，即可享受中文界面：

1. **第一步**：进入本工具目录。
2. **第二步**：双击运行 **`ZhuRu_HanHua.bat`**。
3. **第三步**：等待黑屏控制台显示 `[√] 全局路径修复与深度引擎已部署` 后，按任意键关闭。

**立即生效**：现在启动 Antigravity，打开 Agent Manager 即可看到效果！

> [!TIP]
> **软件更新后失效怎么办？**  
> 如果 Antigravity 进行了版本更新，汉化入口可能会被官方文件覆盖。此时您**只需再次运行一次 `ZhuRu_HanHua.bat`** 即可恢复。

---

## 🔄 卸载与还原 (一键恢复)

如果您需要删除汉化，回归官方原版，操作同样简单：

1. **双击运行 `QingChu_HanHua.bat`**。
2. 工具会自动通过 `.bak` 文件还原所有被修改的 HTML，并清理汉化核心脚本。
3. 还原完成后，软件将回归完全原始的状态。

---

## ⚙️ 进阶配置

### 修改安装路径
如果您的 Antigravity 安装在非默认位置（默认为 `D:\Antigravity`），请修改配置：

1. 使用记事本或 VS Code 打开 `AntigravityHanHua_GongJu.py`。
2. 找到第 9 行：`ANTIGRAVITY_AN_ZHUANG_LU_JING = r"D:\Antigravity"`。
3. 将引号内的路径修改为您实际的安装目录，保存后重新运行注入脚本即可。

---

## 📁 文件清单

| 文件名 | 作用 |
| :--- | :--- |
| `AntigravityHanHua_GongJu.py` | 核心引擎：处理备份、注入、生成 JS 及校验同步 |
| `ZhuRu_HanHua.bat` | 一键注入入口：自动杀进程并触发汉化逻辑 |
| `QingChu_HanHua.bat` | 一键还原入口：安全撤销所有修改 |
| `dicts/` | 翻译字典目录：存放各模块对应的 JSON 字典 |
| `README.md` | 您当前阅读的帮助手册 |

---

## ❓ 常见问题 (FAQ)

> [!IMPORTANT]
> **Q: 界面只有部分汉化了，有些还是英文？**  
> A: 这通常是因为字典库尚未覆盖该部分文本。您可以手动编辑 `dicts/` 目录下的 JSON 文件增加翻译规则，我们的引擎支持热加载（重启软件生效）。

> [!WARNING]
> **Q: 运行脚本提示“拒绝访问”？**  
> A: 请尝试以【管理员身份】运行批处理文件。

## 💖 致谢

本项目基于开源项目 [Cursor_chinese](https://github.com/bjrzs/Cursor_chinese) 制作，感谢原作者的无私奉献。

---
*Powered by Antigravity Assistant Team*
