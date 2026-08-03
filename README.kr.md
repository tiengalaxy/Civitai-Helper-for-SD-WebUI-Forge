### 언어
[English](README.md) | [中文](README.cn.md) | [日本語](README.jp.md)

# SD WebUI Forge Neo Classic - Civitai Helper

<p align="center">
  <strong><code>Stable Diffusion WebUI Forge</code> 전용 강화된 Civitai Helper 확장 기능</strong><br>
  원본 <a href="https://github.com/butaixianran/Stable-Diffusion-Webui-Civitai-Helper">Civitai Helper</a>에서 포크<br>
  <a href="https://github.com/willmiao/ComfyUI-Lora-Manager">ComfyUI LoRA Manager</a>에서 영감을 받은 기능 업그레이드
</p>

## ✨ 새로운 기능 (원본 대비)

| 기능 | 설명 |
|------|------|
| ⚡ **원클릭 LoRA 적용** | ⚡ 버튼 클릭 한 번으로 트리거 단어 + `<lora:name:strength>` 태그를 프롬프트에 추가. 강도는 슬라이더로 조절 가능 |
| 🔑 **트리거 단어 툴팁** | 모델 카드에 마우스를 올리면 트리거 단어가 즉시 표시 — 클릭 불필요 |
| 📦 **파일 크기 표시** | 모델 카드에 파일 크기 배지 표시 (예: `144.2 MB`) |
| 📝 **모델 메모** | 모든 모델에 개인 메모 추가 가능, `.ch_note` 파일로 모델과 함께 저장 |
| 🔍 **스마트 스캔 건너뛰기** | 이미 정보와 미리보기가 있는 모델은 자동으로 건너뛰어 스캔 시간 대폭 단축 |
| 📊 **실시간 스캔 진행률** | 퍼센트, 현재 모델 이름, 단계별 상태(SHA256 / API / 미리보기 / 건너뜀)를 실시간 표시 |
| 🔄 **새 버전 일괄 다운로드** | 감지된 모든 새 버전을 한 번에 다운로드 |
| 🗑 **확장 기능 제거 버튼** | Forge의 확장 페이지에서 직접 제거 — 폴더 수동 삭제 불필요 |
| 🔄 **강제 업데이트 버튼** | `git reset --hard` + `git pull`로 확장 기능 강제 업데이트 — force push로 인한 업데이트 감지 문제 해결 |
| 🎯 **더 많은 모델 유형** | 기존 LoRA/TI/Hypernetwork/Checkpoint 외에 **ControlNet**, **VAE**, **Upscaler** 지원 |
| 🚀 **성능 최적화** | 배치 API 요청, 프론트엔드 캐싱, 요청 잠금 — 대규모 모델 컬렉션에서도 프리즈 없음 |

## 📋 핵심 기능 (원본에서 계승)

- 모든 모델을 스캔하여 Civitai에서 모델 정보 및 미리보기 이미지 다운로드
- Civitai 모델 페이지 URL로 로컬 모델 연결
- Civitai URL로 모델(정보 + 미리보기 포함)을 하위 폴더에 다운로드
- 중단 지점에서 다운로드 재개 지원
- 로컬 모델의 Civitai 새 버전 일괄 확인
- 새 버전을 모델 폴더에 직접 다운로드
- 모델 카드 버튼:
  - 🌐 Civitai 페이지 열기
  - 💡 트리거 단어를 프롬프트에 추가
  - 🏷 미리보기 이미지의 프롬프트 사용
  - ⚡ LoRA 적용 (강도 포함, LoRA만 해당)
  - 📝 모델 메모 편집
  - ❌ 모델 제거

## 🔧 설치

### 방법 1: URL에서 설치 (권장)
1. Forge의 **Extensions** 탭 → **Install from URL**로 이동
2. 붙여넣기: `https://github.com/tiengalaxy/Civitai-Helper-for-SD-WebUI-Forge`
3. **Install** 클릭 후 Forge **재시작** (UI 다시 로드만으로는 불충분)

### 방법 2: 수동 설치
1. 이 저장소를 ZIP으로 다운로드
2. `Forge 폴더/extensions/`에 압축 해제
3. Forge 재시작

## 📖 사용 방법

### 모델 스캔
1. **Civitai Helper** 탭으로 이동
2. 스캔할 모델 유형 선택 (LoRA, Checkpoint, ControlNet, VAE, Upscaler 등)
3. **Scan** 클릭 — 이미 정보와 미리보기가 있는 모델은 자동 건너뛰기
4. 실시간 진행률 확인: 퍼센트, 현재 모델명, 단계 상태

### 모델 카드 버튼
스캔 완료 후 Extra Networks에서 모델 카드에 마우스를 올리면:
- 🔑 **트리거 단어 툴팁** — 호버 시 자동 표시
- 📦 **파일 크기 배지** — 모델명 옆에 표시
- 버튼 클릭: 🌐 💡 🏷 ⚡ 📝 ❌

### LoRA 빠른 적용
1. **LoRA Quick Apply** 섹션에서 기본 강도 설정
2. LoRA 카드의 ⚡ 버튼 클릭 — 트리거 단어 + `<lora:name:strength>`가 프롬프트에 자동 추가

### 확장 기능 관리
**Extensions** → **Installed** 탭에서 각 확장 기능에 다음이 추가됨:
- 🗑 **Uninstall** — 확장 폴더 삭제
- 🔄 **Force Update** — `git reset --hard` + `git pull` (업데이트 감지 문제 해결)

## ⚙️ 설정

모든 설정은 **Settings** 탭 → **Civitai Helper** 섹션에 있습니다:

| 설정 | 설명 |
|------|------|
| Download Max Size Preview | 미리보기 이미지에 최대 해상도 사용 |
| Skip NSFW Preview | NSFW 콘텐츠 미리보기 이미지 다운로드 안 함 |
| Open URL At Client Side | 서버 대신 브라우저에서 링크 열기 |
| Check New Version In All Folders | 업데이트 확인 시 모든 모델 폴더 검색 |
| Proxy | Civitai API용 HTTP/SOCKS5 프록시 (예: `socks5h://127.0.0.1:1080`) |
| Civitai API Key | 일부 모델 다운로드에 필요 |
| Civitai Domain | `civitai.red` 또는 `civitai.com` 선택 |
| Default LoRA Strength | ⚡ 버튼의 기본 강도 (0.0 ~ 2.0) |

## 🛠 지원 모델 유형

| 유형 | 폴더 | 확장자 |
|------|------|--------|
| Textual Inversion | `embeddings/` | .bin .pt .safetensors .ckpt .pth |
| Hypernetwork | `models/hypernetworks/` | .pt |
| Checkpoint | `models/Stable-diffusion/` | .safetensors .ckpt |
| LoRA | `models/Lora/` | .safetensors .bin .pt .ckpt .pth |
| ControlNet | `models/Controlnet/` | .safetensors .bin .pth |
| VAE | `models/VAE/` | .safetensors .bin .pt |
| Upscaler | `models/ESRGAN/` | .pth .safetensors |

명령줄 인수(`--lora-dir`, `--ckpt-dir`, `--controlnet-dir`, `--vae-dir` 등)를 통한 사용자 정의 모델 경로도 지원됩니다.

## ❓ 자주 묻는 질문

### 카드 버튼이 표시되지 않음
Extra Networks 도구 모음의 🔁 **Refresh Civitai Helper** 버튼을 클릭하세요.

### 확장 업데이트가 감지되지 않음 (force push 후)
확장 페이지의 🔄 **Force Update** 버튼을 사용하세요.

### 스캔 또는 API 요청 실패
Civitai가 일시적으로 다운되었거나 속도 제한이 걸렸을 수 있습니다. 잠시 기다린 후 다시 시도하세요. 중국 내 사용자는 설정에서 프록시를 구성하세요.

### Civitai에서 잘못된 모델 정보 가져옴
일부 모델은 Civitai 데이터베이스의 SHA256이 올바르지 않습니다. "URL로 모델 정보 가져오기" 기능을 사용하여 수동으로 연결하세요.

## 📜 변경 내역

### v1.15.0 (2026-08-03)

**코드 품질 및 안정성 향상**

- **SSL 검증 복원** — 모든 다운로드가 기본적으로 SSL 인증서를 검증합니다 (이전에는 비활성화됨). 프록시 사용자는 계속 HTTPS 프록시를 안전하게 사용할 수 있습니다.
- **네트워크 오류 자동 재시도** — API 호출 및 다운로드 실패 시 지수 백오프(2s → 4s → 8s)로 최대 3회 자동 재시도합니다.
- **API 속도 제한** — 중앙 집중식 `RateLimiter`가 Civitai의 속도 제한 초과를 방지하여 분산된 `time.sleep(1)` 호출을 대체합니다.
- **일괄 다운로드 수정** — `새 버전 일괄 다운로드`가 스텁 함수였던 문제를 수정했습니다. 이제 실제로 각 버전을 다운로드하고 info 파일을 저장합니다.
- **명명된 튜플** — 새 버전 확인 결과를 `NewVersion` 명명된 튜플로 변경하여 취약한 `nv[3]` 인덱스 접근을 제거했습니다.
- **데드 코드 제거** — 사용되지 않는 `setting.py`와 `model_type_display` 딕셔너리를 정리했습니다.
- **로깅 개선** — `printD`와 공존하는 `logging` 모듈을 통합하여 디버깅을 개선했습니다.
- **다운로드 충돌 처리** — 파일 이름 충돌 시 무한 `_2`, `_3` 루프 대신 타임스탬프 기반 이름을 사용합니다.

### v1.14.0 (초기 Fork)

- Forge Neo 호환성: `_resolve_ti_folder()`로 embeddings 경로 자동 감지
- 원클릭 LoRA 적용: 트리거 단어 + `<lora:name:strength>` 태그
- 트리거 단어 툴팁 (호버 시 표시)
- 모델 카드 파일 크기 표시
- 모델 메모 (`.ch_note`)
- 스마트 스캔 건너뛰기 (info + 미리보기 있는 모델 자동 건너뜀)
- 실시간 스캔 진행률 (퍼센트, 단계 상태)
- 확장 기능 제거 / 강제 업데이트 버튼
- ControlNet, VAE, Upscaler 지원
- 배치 API 요청 및 프론트엔드 캐싱