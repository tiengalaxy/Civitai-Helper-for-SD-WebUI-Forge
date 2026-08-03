### Language
[中文](README.cn.md) | [日本語](README.jp.md) | [한국어](README.kr.md)

# SD WebUI Forge Neo Classic - Civitai Helper

<p align="center">
  <strong>An enhanced Civitai Helper extension for <code>Stable Diffusion WebUI Forge</code></strong><br>
  Forked from the original <a href="https://github.com/butaixianran/Stable-Diffusion-Webui-Civitai-Helper">Civitai Helper</a><br>
  Inspired by <a href="https://github.com/willmiao/ComfyUI-Lora-Manager">ComfyUI LoRA Manager</a>
</p>

## ✨ What's New (vs Original)

| Feature | Description |
|---------|-------------|
| ⚡ **One-Click LoRA Apply** | Apply LoRA with trigger words + `<lora:name:strength>` tag to prompt in one click. Adjustable strength via slider. |
| 🔑 **Trigger Words Tooltip** | Hover over any model card to instantly see trigger words — no click needed. |
| 📦 **File Size Display** | Model card shows file size badge (e.g. `144.2 MB`). |
| 📝 **Model Notes** | Add personal notes to any model, saved as `.ch_note` file alongside the model. |
| 🔍 **Smart Scan Skip** | Models that already have info + preview are automatically skipped, dramatically reducing scan time. |
| 📊 **Real-Time Scan Progress** | Live progress bar with percentage, current model name, and step-by-step status (SHA256 / API / Preview / Skipped). |
| 🔄 **Batch Download New Versions** | Download all detected new versions at once. |
| 🗑 **Extension Uninstall Button** | Uninstall extensions directly from Forge's extension page — no manual folder deletion needed. |
| 🔄 **Force Update Button** | Force update any extension via `git reset --hard` + `git pull` — fixes update detection issues from force-pushed repos. |
| 🎯 **More Model Types** | Now supports **ControlNet**, **VAE**, **Upscaler** in addition to LoRA/TI/Hypernetwork/Checkpoint. |
| 🚀 **Performance Optimization** | Batch API requests, frontend caching, request locking — no more UI freezing with large model collections. |

## 📋 Core Features (from Original)

- Scan all models to download info and preview images from Civitai
- Link local model to Civitai model by URL
- Download models (with info + preview) by Civitai URL into subfolders
- Resume downloading from break-point
- Check all local models' new versions from Civitai
- Download new versions directly into model folder
- Model card buttons:
  - 🌐 Open Civitai page
  - 💡 Add trigger words to prompt
  - 🏷 Use preview image's prompt
  - ⚡ Apply LoRA with strength (LoRA only)
  - 📝 Edit model notes
  - ❌ Remove model

## 🔧 Installation

### Method 1: From URL (Recommended)
1. Go to Forge's **Extensions** tab → **Install from URL**
2. Paste: `https://github.com/tiengalaxy/Civitai-Helper-for-SD-WebUI-Forge`
3. Click **Install**, then **Restart** Forge (not just Reload UI)

### Method 2: Manual
1. Download this repo as ZIP
2. Extract to `Your Forge folder/extensions/`
3. Restart Forge

## 📖 Usage

### Scanning Models
1. Go to **Civitai Helper** tab
2. Select model types to scan (LoRA, Checkpoint, ControlNet, VAE, Upscaler, etc.)
3. Click **Scan** — models with existing info + preview are automatically skipped
4. Watch the real-time progress: percentage, current model, and step status

### Model Card Buttons
After scanning, hover over any model card in Extra Networks to see:
- 🔑 **Trigger words tooltip** — appears on hover
- 📦 **File size badge** — shown next to model name
- Click buttons: 🌐 💡 🏷 ⚡ 📝 ❌

### LoRA Quick Apply
1. Set your preferred LoRA strength in the **LoRA Quick Apply** section
2. Click ⚡ on any LoRA card — trigger words + `<lora:name:strength>` are added to your prompt

### Extension Management
Go to **Extensions** → **Installed** tab, each extension now has:
- 🗑 **Uninstall** — delete extension folder
- 🔄 **Force Update** — `git reset --hard` + `git pull` (fixes update detection issues)

## ⚙️ Settings

All settings are in **Settings** tab → **Civitai Helper** section:

| Setting | Description |
|---------|-------------|
| Download Max Size Preview | Use maximum resolution for preview images |
| Skip NSFW Preview | Don't download NSFW preview images |
| Open URL At Client Side | Open links in browser instead of server |
| Check New Version In All Folders | Search all model folders when checking for updates |
| Proxy | HTTP/SOCKS5 proxy for Civitai API (e.g. `socks5h://127.0.0.1:1080`) |
| Civitai API Key | Required for downloading some models |
| Civitai Domain | Choose between `civitai.red` and `civitai.com` |
| Default LoRA Strength | Default weight for ⚡ button (0.0 ~ 2.0) |

## 🛠 Supported Model Types

| Type | Folder | Extensions |
|------|--------|------------|
| Textual Inversion | `embeddings/` | .bin .pt .safetensors .ckpt .pth |
| Hypernetwork | `models/hypernetworks/` | .pt |
| Checkpoint | `models/Stable-diffusion/` | .safetensors .ckpt |
| LoRA | `models/Lora/` | .safetensors .bin .pt .ckpt .pth |
| ControlNet | `models/Controlnet/` | .safetensors .bin .pth |
| VAE | `models/VAE/` | .safetensors .bin .pt |
| Upscaler | `models/ESRGAN/` | .pth .safetensors |

Custom model paths via command-line arguments (`--lora-dir`, `--ckpt-dir`, `--controlnet-dir`, `--vae-dir`, etc.) are also supported.

## ❓ Common Issues

### Card buttons not showing
Click the 🔁 **Refresh Civitai Helper** button in the Extra Networks toolbar.

### Can't detect extension updates (after force push)
Use the 🔄 **Force Update** button on the Extensions page.

### Scan or API request failed
Civitai may be temporarily down or rate-limiting. Wait a moment and try again. If you're in China, configure a proxy in settings.

### Wrong model info from Civitai
Some models have incorrect SHA256 in Civitai's database. Use "Get Model Info by URL" to manually link your model.

## 📜 Changelog

### v1.15.0 (2026-08-03)

**Code Quality & Reliability**

- **SSL verification restored** — All downloads now verify SSL certificates by default (was disabled). Proxy users can still use HTTPS proxies safely.
- **Automatic retry on network errors** — API calls and downloads now retry up to 3 times with exponential backoff (2s → 4s → 8s) when Civitai is temporarily unreachable.
- **API rate limiting** — Centralized `RateLimiter` prevents exceeding Civitai's rate limits, replacing scattered `time.sleep(1)` calls.
- **Batch download fix** — `Batch Download New Versions` was a stub; now it actually downloads each version and saves info files.
- **Named tuples** — New version check results now use `NewVersion` named tuples instead of fragile `nv[3]` index access.
- **Dead code removed** — Unused `setting.py` and `model_type_display` dict cleaned up.
- **Logging improved** — Added `logging` module integration alongside existing `printD` for better debugging.
- **Download conflict handling** — File name conflicts now use timestamp-based naming instead of infinite `_2`, `_3` loops.

### v1.14.0 (Initial Fork)

- Forge Neo compatibility with `_resolve_ti_folder()` for embeddings path
- One-click LoRA apply with trigger words + `<lora:name:strength>` tag
- Trigger words tooltip on hover
- File size display on model cards
- Model notes (`.ch_note`)
- Smart scan skip (skip models with existing info + preview)
- Real-time scan progress with percentage and step status
- Extension uninstall / force update buttons
- ControlNet, VAE, Upscaler support
- Batch API requests and frontend caching
