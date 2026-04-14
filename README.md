# Antigravity 智能管理器中文语言包

> 适用对象：Antigravity Agent Manager
> 支持平台：Windows / macOS
> 方案特点：动态注入、自动备份、一键还原、尽量不碰核心二进制

---

## 项目简介

本项目用于给 Antigravity 的 **Agent Manager** 界面做中文汉化。

它的做法不是去硬改程序二进制，而是在 Antigravity 的 `resources/app/out` 目录里：
- 生成一份汉化脚本 `ag_agent_hanhua.js`
- 向工作台 HTML 注入一行 `<script>` 引用
- 自动备份原始 HTML
- 更新 `product.json` 中对应文件的校验值

这样做的好处是：
- 出问题能回滚
- 官方更新后可重新执行
- 对原始程序结构改动相对可控

---

## 功能特性

- **动态扫描翻译**：通过 `MutationObserver` 处理动态渲染内容
- **双平台支持**：Windows 和 macOS 都能直接执行
- **自动备份**：首次注入时会生成 `.bak` 备份文件
- **一键还原**：可恢复到官方原始状态
- **路径自动探测**：支持默认路径探测，也支持手动指定安装目录

---

## 使用前准备

开始前请先确认：

1. 已安装 **Python 3**
2. Antigravity 已完全退出
3. 当前账号对 Antigravity 安装目录有写权限

---

## 默认安装目录

### Windows
- `D:\Antigravity`
- 或其下的 `resources/app`

### macOS
- `/Applications/Antigravity.app`
- `/Applications/Antigravity.app/Contents/Resources/app`
- `~/Applications/Antigravity.app`
- `~/Applications/Antigravity.app/Contents/Resources/app`

---

## 安装汉化

### Windows

直接双击：

- `ZhuRu_HanHua.bat`

如果 Antigravity 不在默认目录，也可以手动执行：

```bash
python "AntigravityHanHua_GongJu.py" --install-dir "D:\Antigravity"
```

### macOS

首次使用前，先给脚本执行权限：

```bash
chmod +x "ZhuRu_HanHua.command" "QingChu_HanHua.command"
```

然后任选一种方式执行：

```bash
./ZhuRu_HanHua.command
```

或者直接双击 `ZhuRu_HanHua.command`

如果 Antigravity 不在默认目录，可手动指定路径：

```bash
python3 "AntigravityHanHua_GongJu.py" --install-dir "/Applications/Antigravity.app"
```

执行完成后，重新启动 Antigravity，打开 Agent Manager 即可查看汉化效果。

---

## 还原官方原版

### Windows

直接双击：

- `QingChu_HanHua.bat`

或手动执行：

```bash
python "AntigravityHanHua_GongJu.py" --huifu --install-dir "D:\Antigravity"
```

### macOS

执行：

```bash
./QingChu_HanHua.command
```

如果需要手动指定路径：

```bash
python3 "AntigravityHanHua_GongJu.py" --huifu --install-dir "/Applications/Antigravity.app"
```

还原时会：
- 用 `.bak` 文件恢复原始 HTML
- 删除 `ag_agent_hanhua.js`
- 同步恢复后的 checksum

---

## 手动指定路径说明

`--install-dir` 同时接受这两种形式：

1. Antigravity 应用根目录
   例如：
   - Windows：`D:\Antigravity`
   - macOS：`/Applications/Antigravity.app`

2. `resources/app` 目录
   例如：
   - Windows：`D:\Antigravity\resources\app`
   - macOS：`/Applications/Antigravity.app/Contents/Resources/app`

---

## 目录结构前提

当前脚本默认 Antigravity 安装目录中存在以下结构：

```text
resources/app/
├── product.json
└── out/
    └── vs/code/electron-browser/workbench/
        ├── workbench.html
        └── workbench-jetski-agent.html
```

如果官方后续改了目录结构，这套注入方式也得跟着调整。

---

## 文件说明

| 文件 | 说明 |
| --- | --- |
| `AntigravityHanHua_GongJu.py` | 核心逻辑：路径解析、备份、注入、还原、checksum 更新 |
| `ZhuRu_HanHua.bat` | Windows 安装入口 |
| `QingChu_HanHua.bat` | Windows 还原入口 |
| `ZhuRu_HanHua.command` | macOS 安装入口 |
| `QingChu_HanHua.command` | macOS 还原入口 |
| `dicts/` | 翻译字典 |

---

## 常见问题

### 1）提示找不到安装目录

别瞎猜，直接用 `--install-dir` 指定。

macOS 示例：

```bash
python3 "AntigravityHanHua_GongJu.py" --install-dir "/Applications/Antigravity.app"
```

### 2）提示权限不足

- Windows：尝试以管理员身份运行
- macOS：确认当前用户对应用目录有写权限

### 3）更新后汉化失效

官方更新可能覆盖了工作台 HTML，重新执行一次安装脚本即可。

### 4）只有部分文本被翻译

说明字典还没覆盖全。可在 `dicts/` 目录中继续补充 JSON 翻译条目。

---

## 致谢

本项目基于开源项目 [Cursor_chinese](https://github.com/bjrzs/Cursor_chinese) 制作，感谢原作者的无私奉献。

---

## 友情链接

感谢 **LinuxDo** 社区的支持！

[![LinuxDo](https://img.shields.io/badge/社区-LinuxDo-blue?style=for-the-badge)](https://linux.do/)
