# GitHub 到电脑双击使用（小白版）

> 目标：不在你电脑安装 Python，不敲命令，直接下载成品 exe。

## 第 1 步：在 GitHub 里生成成品
1. 打开仓库 `cnc-machining-website`。
2. 点击上方菜单 **Actions**。
3. 选择工作流 **Build Windows EXE**。
4. 点击 **Run workflow**（选择 `main` 分支）并确认运行。
5. 等待任务完成（通常 2~6 分钟）。

## 第 2 步：下载成品包
1. 点开刚才完成的那条 workflow 记录。
2. 页面最下方找到 **Artifacts**。
3. 下载 `ChatHelper-Windows`。
4. 下载下来一般是 zip，解压后会看到：
   - `ChatHelper.exe`
   - `QuickStart.txt`
   - `README.md`

## 第 3 步：双击运行
1. 双击 `ChatHelper.exe`。
2. 第一次打开：
   - 点击“设置”
   - 填入 `OpenAI API Key`
   - 点击保存
3. 按 `Ctrl + Shift + Space` 呼出窗口使用。

## 第 4 步：最常用操作
1. 点“开始说话”
2. 说中文
3. 点“停止录音”
4. 点“一键复制英文”
5. 粘贴到 WhatsApp/Facebook/邮箱

## 常见问题
- 如果快捷键无效：以管理员身份运行 `ChatHelper.exe`。
- 如果录音失败：检查 Windows 麦克风权限。
- 如果翻译失败：先检查网络，再点“重新翻译”。

---

## 你最关心的三个答案
- **下载哪个文件？** `ChatHelper-Windows` artifact（zip）。
- **双击哪个文件？** `ChatHelper.exe`。
- **第一次要做什么？** 在设置里填 OpenAI API Key。
