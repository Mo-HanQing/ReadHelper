# ReadHelper

![ReadHelper](assets/readhelper.ico)

[中文](#中文) | [English](#english)

## 中文

ReadHelper 是一款 Windows 辅助阅读工具。它使用本地 OCR 自动识别屏幕文本行，压暗当前阅读行以外的区域，帮助你更专注地阅读网页、文档和其他屏幕内容。

### 主要功能

- OCR 自动吸附屏幕文本行
- 鼠标跟随与键盘控制两种模式
- 锁定当前阅读行，避免误触跳行
- 指定目标显示器，不影响其他屏幕
- 自定义遮罩、阅读带和 OCR 参数
- 自定义全局快捷键
- OCR 完全在本机运行，不保存截图或识别文本

### 下载与运行

1. 从 [GitHub Releases](https://github.com/Mo-HanQing/ReadHelper/releases/latest) 下载最新的 Windows 压缩包。
2. 解压完整文件夹，不要只复制 `ReadHelper.exe`。
3. 双击 `ReadHelper.exe` 启动。
4. 启动后，右键系统托盘中的 ReadHelper 图标进行设置。

ReadHelper 支持 Windows 10 和 Windows 11 64 位系统。发布包采用 one-folder 形式，完整目录约 770 MB，主要空间由本地 OCR 运行库占用。

### 使用方法

托盘菜单提供以下操作：

- 开启或关闭阅读聚焦
- 立即执行 OCR
- 锁定或解锁当前行
- 切换鼠标跟随与键盘控制模式
- 选择唯一生效的目标显示器
- 打开设置或退出程序

默认快捷键：

| 操作 | 快捷键 |
| --- | --- |
| 开启/关闭聚焦 | `Ctrl+Alt+Space` |
| 上一行/下一行 | `Alt+Up` / `Alt+Down` |
| 立即识别 | `Ctrl+Alt+R` |
| 锁定/解锁当前行 | `Ctrl+Alt+L` |
| 切换控制模式 | `Ctrl+Shift+M` |
| 减小/增大阅读带 | `Ctrl+Alt+Left` / `Ctrl+Alt+Right` |

所有快捷键都可以在“设置 > 快捷键”中修改。

### 隐私与日志

屏幕截图仅在内存中用于 OCR，不会写入磁盘；识别出的文本也不会记录到日志。

日志文件：`%LOCALAPPDATA%\ReadHelper\ReadHelper.log`

配置文件：`%LOCALAPPDATA%\ReadHelper\config.json`

## English

ReadHelper is a Windows reading aid that uses local OCR to detect text lines on screen. It dims everything outside the active reading line, helping you stay focused while reading webpages, documents, and other on-screen content.

### Features

- Automatically snaps to OCR-detected text lines
- Mouse-follow and keyboard-control modes
- Locks the current reading line to prevent accidental movement
- Targets one selected display without affecting other monitors
- Customizable dimming, focus band, and OCR settings
- Customizable global keyboard shortcuts
- Fully local OCR with no stored screenshots or recognized text

### Download and Run

1. Download the latest Windows archive from [GitHub Releases](https://github.com/Mo-HanQing/ReadHelper/releases/latest).
2. Extract the complete folder. Do not copy `ReadHelper.exe` by itself.
3. Double-click `ReadHelper.exe`.
4. Right-click the ReadHelper system tray icon to configure the app.

ReadHelper supports 64-bit Windows 10 and Windows 11. Releases use a one-folder layout. The complete folder is approximately 770 MB, mostly due to the bundled local OCR runtime.

### Usage

The tray menu lets you:

- Enable or disable reading focus
- Run OCR immediately
- Lock or unlock the current line
- Switch between mouse-follow and keyboard-control modes
- Select the only display where ReadHelper is active
- Open settings or exit the app

Default shortcuts:

| Action | Shortcut |
| --- | --- |
| Toggle reading focus | `Ctrl+Alt+Space` |
| Previous/next line | `Alt+Up` / `Alt+Down` |
| Refresh OCR | `Ctrl+Alt+R` |
| Lock/unlock current line | `Ctrl+Alt+L` |
| Switch control mode | `Ctrl+Shift+M` |
| Shrink/grow focus band | `Ctrl+Alt+Left` / `Ctrl+Alt+Right` |

All shortcuts can be changed under **Settings > Shortcuts**.

### Privacy and Logs

Screenshots are processed in memory for OCR and are never written to disk. Recognized text is not recorded in logs.

Log file: `%LOCALAPPDATA%\ReadHelper\ReadHelper.log`

Configuration file: `%LOCALAPPDATA%\ReadHelper\config.json`

## License

ReadHelper is licensed under the [MIT License](LICENSE).
