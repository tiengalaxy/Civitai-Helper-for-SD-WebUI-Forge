### 语言
[English](README.md) | [日本語](README.jp.md) | [한국어](README.kr.md)

# SD WebUI Forge Neo Classic - Civitai Helper

<p align="center">
  <strong>专为 <code>Stable Diffusion WebUI Forge</code> 打造的增强版 Civitai Helper 插件</strong><br>
  基于原版 <a href="https://github.com/butaixianran/Stable-Diffusion-Webui-Civitai-Helper">Civitai Helper</a> 开发<br>
  参考 <a href="https://github.com/willmiao/ComfyUI-Lora-Manager">ComfyUI LoRA Manager</a> 进行功能升级
</p>

## ✨ 新增功能（对比原版）

| 功能 | 说明 |
|------|------|
| ⚡ **一键应用 LoRA** | 点击 ⚡ 按钮即可将触发词 + `<lora:名称:权重>` 标签添加到提示词，权重可通过滑块调节 |
| 🔑 **触发词悬停预览** | 鼠标悬停模型卡片即可看到触发词，无需点击 |
| 📦 **文件大小显示** | 模型卡片名称旁显示文件大小标签（如 `144.2 MB`） |
| 📝 **模型个人备注** | 为任意模型添加个人笔记，保存为 `.ch_note` 文件 |
| 🔍 **智能跳过扫描** | 已有信息和缩略图的模型自动跳过，大幅减少扫描时间 |
| 📊 **实时扫描进度** | 扫描时显示百分比进度条、当前模型名称和每一步状态（SHA256计算 / API请求 / 下载预览 / 已跳过） |
| 🔄 **批量下载新版本** | 检测到新版本后可一键批量下载 |
| 🗑 **扩展卸载按钮** | 在 Forge 扩展页面直接卸载扩展，无需手动删除文件夹 |
| 🔄 **强制更新按钮** | 通过 `git reset --hard` + `git pull` 强制更新扩展，解决因 force push 导致检测不到更新的问题 |
| 🎯 **更多模型类型** | 在原有的 LoRA/TI/Hypernetwork/Checkpoint 基础上，新增 **ControlNet**、**VAE**、**Upscaler** 支持 |
| 🚀 **性能优化** | 批量 API 请求、前端缓存、请求锁机制——大量模型时不再卡顿 |

## 📋 核心功能（继承自原版）

- 扫描所有模型，从 Civitai 下载模型信息和预览图
- 通过 Civitai 模型页面 URL 关联本地模型
- 通过 Civitai URL 下载模型（含信息和预览图）到指定子目录
- 支持断点续传下载
- 批量检查本地模型在 Civitai 上的新版本
- 直接下载新版本模型到模型目录
- 模型卡片按钮：
  - 🌐 打开 Civitai 页面
  - 💡 添加触发词到提示词
  - 🏷 使用预览图的提示词
  - ⚡ 一键应用 LoRA + 权重（仅 LoRA）
  - 📝 编辑模型备注
  - ❌ 删除模型

## 🔧 安装

### 方式一：从 URL 安装（推荐）
1. 打开 Forge 的 **扩展** 标签页 → **从 URL 安装**
2. 粘贴：`https://github.com/tiengalaxy/Civitai-Helper-for-SD-WebUI-Forge`
3. 点击 **安装**，然后**重启** Forge（不是仅重新加载 UI）

### 方式二：手动安装
1. 下载本项目 ZIP 文件
2. 解压到 `你的 Forge 目录/extensions/`
3. 重启 Forge

## 📖 使用方法

### 扫描模型
1. 进入 **Civitai Helper** 标签页
2. 选择要扫描的模型类型（LoRA、Checkpoint、ControlNet、VAE、Upscaler 等）
3. 点击 **扫描** —— 已有信息和缩略图的模型会被自动跳过
4. 观察实时进度：百分比、当前模型名称、步骤状态

### 模型卡片按钮
扫描完成后，在 Extra Networks 中悬停任意模型卡片即可看到：
- 🔑 **触发词提示** —— 鼠标悬停自动显示
- 📦 **文件大小标签** —— 显示在模型名称旁
- 点击按钮：🌐 💡 🏷 ⚡ 📝 ❌

### LoRA 快速应用
1. 在 **LoRA Quick Apply** 区域设置默认权重
2. 点击 LoRA 卡片上的 ⚡ 按钮 —— 触发词 + `<lora:名称:权重>` 自动添加到提示词

### 扩展管理
进入 **扩展** → **已安装** 标签页，每个扩展新增：
- 🗑 **卸载** —— 删除扩展文件夹
- 🔄 **强制更新** —— `git reset --hard` + `git pull`（解决更新检测问题）

## ⚙️ 设置

所有设置在 **设置** 标签页 → **Civitai Helper** 区域：

| 设置 | 说明 |
|------|------|
| 下载最大尺寸预览图 | 使用最高分辨率下载预览图 |
| 跳过 NSFW 预览图 | 不下载 NSFW 内容的预览图 |
| 在客户端打开链接 | 在浏览器而非服务器端打开链接 |
| 在所有文件夹中检查新版本 | 检查更新时搜索所有模型目录 |
| 代理 | Civitai API 的 HTTP/SOCKS5 代理（如 `socks5h://127.0.0.1:1080`） |
| Civitai API Key | 下载部分模型时需要 |
| Civitai 域名 | 选择 `civitai.red` 或 `civitai.com` |
| 默认 LoRA 权重 | ⚡ 按钮的默认权重（0.0 ~ 2.0） |

## 🛠 支持的模型类型

| 类型 | 目录 | 扩展名 |
|------|------|--------|
| Textual Inversion | `embeddings/` | .bin .pt .safetensors .ckpt .pth |
| Hypernetwork | `models/hypernetworks/` | .pt |
| Checkpoint | `models/Stable-diffusion/` | .safetensors .ckpt |
| LoRA | `models/Lora/` | .safetensors .bin .pt .ckpt .pth |
| ControlNet | `models/Controlnet/` | .safetensors .bin .pth |
| VAE | `models/VAE/` | .safetensors .bin .pt |
| Upscaler | `models/ESRGAN/` | .pth .safetensors |

同时支持通过命令行参数（`--lora-dir`、`--ckpt-dir`、`--controlnet-dir`、`--vae-dir` 等）指定自定义模型路径。

## ❓ 常见问题

### 卡片按钮不显示
点击 Extra Networks 工具栏中的 🔁 **Refresh Civitai Helper** 按钮。

### 检测不到扩展更新（force push 后）
使用扩展页面的 🔄 **强制更新** 按钮。

### 扫描或 API 请求失败
Civitai 可能暂时不可用或限流。稍后再试。国内用户请在设置中配置代理。

### 从 Civitai 获取到错误的模型信息
部分模型在 Civitai 数据库中的 SHA256 有误。请使用"通过 URL 获取模型信息"功能手动关联。

## 📜 更新日志

### v1.15.0 (2026-08-03)

**代码质量与可靠性提升**

- **SSL 验证恢复** — 所有下载默认启用 SSL 证书验证（之前被禁用）。代理用户仍可安全使用 HTTPS 代理。
- **网络错误自动重试** — API 调用和下载失败时自动重试最多 3 次，使用指数退避策略（2s → 4s → 8s）。
- **API 速率限制** — 集中式 `RateLimiter` 防止超出 Civitai 的速率限制，替代分散的 `time.sleep(1)` 调用。
- **批量下载修复** — `批量下载新版本` 之前是空壳函数，现已实现真正的批量下载并保存 info 文件。
- **命名元组** — 新版本检查结果改用 `NewVersion` 命名元组，替代脆弱的 `nv[3]` 下标访问。
- **死代码清理** — 删除未使用的 `setting.py` 和 `model_type_display` 字典。
- **日志改进** — 引入 `logging` 模块集成，同时保留 `printD` 以便调试。
- **下载冲突处理** — 文件名冲突改用时间戳命名，替代无限 `_2`、`_3` 循环。

### v1.14.0 (初始 Fork)

- Forge Neo 兼容性，`_resolve_ti_folder()` 自动识别 embeddings 路径
- 一键 LoRA 应用：触发词 + `<lora:名称:权重>` 标签
- 触发词悬停预览
- 模型卡片文件大小显示
- 模型个人备注（`.ch_note`）
- 智能跳过扫描（已有 info + 预览图的模型自动跳过）
- 实时扫描进度百分比和步骤状态
- 扩展卸载 / 强制更新按钮
- ControlNet、VAE、Upscaler 支持
- 批量 API 请求和前端缓存
