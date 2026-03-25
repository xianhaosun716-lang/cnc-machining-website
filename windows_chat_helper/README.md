# Chinese to English Chat Helper (Windows MVP)

这是一个面向新手的 Windows 桌面小工具：
- 全局快捷键呼出窗口
- 中文语音识别
- 自动翻译成适合外贸聊天的英文
- 一键复制英文
- 本地保存历史记录

---

## 1. 为什么选这个技术方案（先给你结论）

### 最终选型
- **Python + Tkinter（桌面界面）**
- **keyboard（全局快捷键）**
- **sounddevice + soundfile（麦克风录音）**
- **OpenAI API（语音识别 + 翻译）**
- **PyInstaller（打包 exe）**

### 为什么这样选
1. **最容易做出可运行 MVP**：Tkinter 是 Python 自带 GUI，安装成本低。
2. **全局快捷键实现简单**：`keyboard` 可快速注册系统级热键。
3. **可打包成单个 exe**：PyInstaller 成熟、资料多。
4. **准确度与实现复杂度平衡**：中文语音识别和翻译直接用 API，准确率高于多数纯离线方案。
5. **后续你容易维护**：代码结构简单、文件少，注释清晰。

> 说明：这是“本地运行桌面程序 + 云端识别翻译”的模式。程序本体在本地，识别/翻译请求走网络。

---

## 2. 功能清单（MVP 已覆盖）

- [x] 全局快捷键呼出窗口（默认 `Ctrl+Shift+Space`）
- [x] 开始/停止录音
- [x] 中文语音识别
- [x] 自动翻译成英文
- [x] 显示中文与英文
- [x] 一键复制英文
- [x] 复制中英双语
- [x] 重新识别
- [x] 重新翻译
- [x] 本地历史记录（默认 20 条，可改）
- [x] 可打包成 exe

---

## 3. 项目结构

```text
windows_chat_helper/
├─ app.py                 # 主程序（UI、流程、按钮逻辑）
├─ audio_recorder.py      # 麦克风录音
├─ config.py              # 设置读取/保存
├─ history_store.py       # 历史记录管理
├─ language_service.py    # 调 OpenAI 做识别和翻译
├─ requirements.txt       # 依赖
└─ README.md              # 使用说明
```

---

## 4. 从零开始运行（Windows 新手版，详细步骤）

## 4.1 安装 Python
1. 打开 Python 官网下载安装 **Python 3.11 或 3.12**。
2. 安装时一定勾选 **Add Python to PATH**。
3. 安装完成后，打开 CMD，输入：

```bash
python --version
```

看到版本号说明成功。

## 4.2 打开项目目录
假设你的项目放在：
`D:\projects\cnc-machining-website\windows_chat_helper`

在该目录空白处 `Shift + 右键`，选择“在终端中打开”。

## 4.3 创建虚拟环境（推荐）

```bash
python -m venv .venv
.venv\Scripts\activate
```

激活后命令行前面会出现 `(.venv)`。

## 4.4 安装依赖

```bash
pip install -r requirements.txt
```

## 4.5 准备 OpenAI API Key
你需要一个 OpenAI API Key（用于语音识别和翻译）。

首次运行程序后：
1. 点击 `设置`
2. 把 API Key 填进 `OpenAI API Key`
3. 点击保存

## 4.6 启动程序

```bash
python app.py
```

---

## 5. 使用方法（最短路径）

1. 启动程序后，按全局快捷键 `Ctrl+Shift+Space` 呼出窗口。  
2. 点击 **开始说话**。  
3. 说中文（比如报价、材质、交期等内容）。  
4. 点击 **停止录音**。  
5. 程序自动识别 + 翻译。  
6. 点击 **一键复制英文**，直接粘贴到 Facebook/WhatsApp/邮箱。  

---

## 6. API、费用与方案建议

## 6.1 需要什么服务
- OpenAI API（1 个 Key 即可）
- 语音识别模型：`gpt-4o-mini-transcribe`
- 翻译模型：`gpt-4.1-mini`

## 6.2 费用大概
- 按调用量计费（语音分钟数 + 文本 token）。
- 日常聊天场景一般成本可控，建议先小规模试用。
- 具体以 OpenAI 官方定价页实时价格为准。

## 6.3 免费/低成本方案
- 可尝试免费翻译接口或离线识别模型，但通常稳定性、准确度、术语表现会下降。
- 对你这种“外贸客户即时沟通”场景，**先用当前方案做 MVP 最稳妥**。

---

## 7. 网络异常、麦克风异常、失败重试设计

程序内已经做了基础处理：
1. **网络异常/超时**：会弹窗提示失败，不会崩溃。
2. **麦克风没录到声音**：提示“未录到声音，请检查麦克风后重试”。
3. **识别失败**：可点“重新识别”。
4. **翻译失败**：可点“重新翻译”。
5. **历史记录不会丢**：成功记录写入本地 JSON。

---

## 8. 打包 exe（Windows）

你现在可以用**一键脚本**打包，不需要自己记命令：

```text
双击：build_windows.bat
```

脚本会自动完成：
1. 创建虚拟环境
2. 安装依赖
3. 运行 PyInstaller
4. 生成交付目录和 zip

最终产物：

```text
release\ChatHelper-Windows\
release\ChatHelper-Windows.zip
```

你要发给客户/同事时，直接给 `ChatHelper-Windows.zip` 即可。

如果你想手动命令打包，也可以：

```bash
pyinstaller --noconfirm ChatHelper.spec
python package_release.py
```

第一次运行建议右键“以管理员身份运行”（有些机器全局快捷键库在普通权限下受限）。

## 8.1 交付包内如何使用（给最终用户）
1. 解压 `ChatHelper-Windows.zip`
2. 双击 `ChatHelper.exe`
3. 打开“设置”填入 OpenAI API Key 并保存
4. 开始使用（录音 -> 翻译 -> 复制）

---

## 9. 常见问题

### Q1：按快捷键没反应？
- 检查是否和其他软件快捷键冲突。
- 到设置里改成别的，如 `ctrl+alt+space`。
- 尝试管理员权限运行。

### Q2：录音失败？
- 检查 Windows 麦克风权限：
  `设置 -> 隐私和安全性 -> 麦克风`。
- 确认麦克风硬件正常。

### Q3：翻译太生硬？
- 设置里把风格改成 `business` 或 `polite`。
- 说话时尽量包含关键参数（尺寸、材质、数量、交期）。

---

## 10. 后续升级方向（第二阶段）

1. **一键粘贴到当前聊天框**（模拟 Ctrl+V，支持“复制+粘贴”一键化）。
2. **术语词典增强**（CNC/注塑/挤出行业术语优先级更高）。
3. **快捷短语模板**（报价模板、交期模板、付款条款模板）。
4. **自动润色开关**（保守直译 / 商务润色两种模式）。
5. **系统托盘常驻**（开机自启后后台常驻，减少打扰）。
6. **离线兜底模式**（网络断开时用本地模型低质量应急）。

---

## 11. 维护建议（给新手）

- 只改 `app.py` 的按钮和页面逻辑，风险最低。
- 不要随意改 `requirements.txt` 大版本。
- 每次改完先运行：

```bash
python app.py
```

确认没报错再重新打包。
