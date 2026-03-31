# 📐 Blog Pro Max — 架構設計與執行流程

> 本文件詳細說明 blog-pro-max 的設計邏輯、模組職責、資料流與執行流程，  
> 適合想深入理解或貢獻程式碼的開發者閱讀。

---

## 目錄

1. [專案總覽](#1-專案總覽)
2. [目錄結構](#2-目錄結構)
3. [模組職責](#3-模組職責)
4. [核心設計決策](#4-核心設計決策)
5. [執行流程](#5-執行流程)
6. [資料流](#6-資料流)
7. [設定系統](#7-設定系統)
8. [風格檢查規則](#8-風格檢查規則)
9. [函式速查表](#9-函式速查表)

---

## 1. 專案總覽

**blog-pro-max** 是一個自動化 SEO 內容創作與部落格文章生成工具，核心能力包含：

- 🤖 **LLM 文章生成**：透過 OpenAI 相容 API（支援 GitHub Models 免費端點）產出文章
- 🎨 **多模板系統**：SEO 專業文章、作家 Max 個人風格、Facebook 貼文、LINE 訊息，可擴充
- ✅ **風格檢查器**：自動驗證禁用詞、標題層級、SEO 基本功、標點符號等
- 📝 **標題專家**：自動產出 4 個風格不同的標題建議（含英文 WordPress permalink slug）
- 🖼️ **封面提示詞專家**：自動產出 3 組 AI 繪圖提示詞（Midjourney / DALL-E / Stable Diffusion）
- 📄 **MD→HTML 轉換**：將 Markdown 輸出轉為 WordPress 相容 HTML
- 🔌 **18 平台 Skill 注入**：一鍵將工具安裝到 Claude、Copilot、Cursor 等 AI 助手
- 📦 **PyPI 套件發佈**：`pip install blog-pro-max` 即可全域使用

---

## 2. 目錄結構

```
blog-pro-max/
├── blog_pro_max/                    # ← Python 套件（pip install 的主體）
│   ├── __init__.py                  #    版本號定義
│   ├── _resources.py                #    雙模式資源路徑解析器
│   ├── core.py                      #    專案經理：模板註冊、環境檢查、設定管理
│   ├── blog_generator.py            #    LLM 引擎：建立 prompt、呼叫 API
│   ├── content_research.py          #    文章生成 CLI 入口
│   ├── style_checker.py             #    風格驗證引擎
│   ├── output_md2html.py            #    Markdown → HTML 轉換器
│   ├── blogpro.py                   #    CLI 工具：init / uninstall / versions / update
│   ├── copilot.json                 #    Copilot skill 設定檔
│   ├── writing-style.md             #    品牌寫作風格指南
│   └── templates/                   #    寫作模板
│       ├── blog-skill-content.md    #        SEO 專業文章模板
│       ├── max-personal-style.md    #        Max 個人風格模板
│       ├── fb-post-style.md         #        Facebook 貼文模板
│       └── line-message-style.md    #        LINE 訊息模板
│
├── scripts/                         # ← 開發模式 fallback（直接執行用）
│   ├── core.py, blog_generator.py, content_research.py, ...
│   └── output_md2html.py
│
├── templates/                       # ← 開發模式模板
├── writing-style.md                 # ← 開發模式風格指南
├── copilot.json                     # ← 開發模式設定
├── .env                             # ← API 金鑰（不進版控）
├── pyproject.toml                   # ← 套件定義、依賴、entry point
├── .github/workflows/publish.yml    # ← GitHub Actions：release 自動發佈 PyPI
└── output/                          # ← 生成的文章輸出目錄
```

### 為什麼有兩套檔案？

`blog_pro_max/`（套件）和 `scripts/`（開發用）的內容相同。  
差別在於 **import 路徑解析**：

| 執行方式 | 資源來源 | import 方式 |
|----------|----------|-------------|
| `pip install blog-pro-max` | `site-packages/blog_pro_max/` | `from blog_pro_max.core import ...` |
| `python scripts/content_research.py` | 專案根目錄 | `from core import ...` |

所有套件模組都使用 try/except 雙重 import 來支援兩種模式。

---

## 3. 模組職責

### 3.1 `_resources.py` — 資源路徑解析器

**一句話**：決定「模板、設定檔在哪裡」。

```
_is_package = (__init__.py 存在) and (templates/ 存在)
    ├─ True  → RESOURCE_ROOT = blog_pro_max/     （pip install 模式）
    └─ False → RESOURCE_ROOT = 專案根目錄/        （開發模式）
```

匯出：
- `RESOURCE_ROOT` — 所有資源的根路徑
- `get_resource_path(relative)` — 取得資源絕對路徑
- `get_templates_dir()` — 模板目錄
- `get_writing_style_path()` — 風格指南路徑

### 3.2 `core.py` — 專案經理

**一句話**：管理模板、檢查環境、組裝 prompt，是所有模組的上游依賴。

核心元件：

| 元件 | 說明 |
|------|------|
| `TEMPLATES` 字典 | 模板註冊表，定義每個模板的路徑、描述、system prompt、風格指南 |
| `ProjectConfig` | 專案設定 dataclass，從 `copilot.json` 載入 |
| `bootstrap()` | 檢查 RESOURCE_ROOT 下的目錄結構和必要檔案 |
| `build_system_prompt()` | 組裝 system prompt，自動注入風格指南 |
| `render_template()` | 載入模板並替換變數（keyword、audience、word_count 等） |
| `scan_project_status()` | 掃描整個專案狀態，產出報告 |

### 3.3 `blog_generator.py` — LLM 引擎

**一句話**：接收關鍵字和參數，呼叫 LLM API，回傳 Markdown 文章；另提供 4 類專家分析功能。

九個關鍵函式：
1. `_make_client()` — 建立 OpenAI client（優先用 GitHub Token）
2. `build_prompt()` — 呼叫 core.py 組裝 user prompt + system prompt
3. `generate_article()` — 發送 API 請求，回傳生成的文章內容
4. `generate_titles()` — 分析文章後產出 4 個標題建議（含英文 permalink slug）
5. `generate_cover_prompts()` — 分析文章後產出 3 組 AI 繪圖封面提示詞
6. `review_logic()` — 邏輯與事實專家：數據正確性、邏輯矛盾、錯別字
7. `review_structure()` — 深度與結構專家：遺漏面向、段落轉折、論述深度
8. `review_reader()` — 讀者視角專家：口吻適配、易讀性、情感共鳴
9. `review_trend()` — 時事趨勢專家：趨勢關聯、切入角度、關鍵字/Hashtag、改寫示範

**API 優先順序**：
```
GITHUB_TOKEN 存在？ → 使用 GitHub Models（免費）
    base_url = "https://models.inference.ai.azure.com"

OPENAI_API_KEY 存在？ → 使用 OpenAI 原生 API

都沒有？ → 拋出 EnvironmentError
```

**內部角色**：

| 角色 | 函式 | 說明 |
|------|------|------|
| 🔬 邏輯與事實專家 | `review_logic()` | 數據正確性、邏輯矛盾、錯別字；回傳 issue/suggest/before/after 表格 |
| 📐 深度與結構專家 | `review_structure()` | 遺漏面向、段落轉折、論述深度；回傳 issue/suggest/before/after 表格 |
| 👁️ 讀者視角專家 | `review_reader()` | 口吻適配、易讀性、情感共鳴；回傳 issue/suggest/before/after 表格 |
| 📰 時事趨勢專家 | `review_trend()` | 趨勢關聯、切入角度、關鍵字/Hashtag、改寫示範；回傳 4 個 section |
| 📝 部落格標題專家 | `generate_titles()` | 4 個標題（直述、提問、數字、情感）+ 英文 permalink slug |
| 🎨 封面提示詞專家 | `generate_cover_prompts()` | 3 組 AI 繪圖 prompt（寫實攝影、插畫、極簡設計） |

### 3.4 `content_research.py` — 文章生成 CLI

**一句話**：面向使用者的 CLI，串接整條 pipeline。

支援模式：
- `--keyword "xxx"` — 正常生成文章
- `--dry-run` — 只顯示 prompt，不呼叫 API
- `--check-only file.md` — 僅執行風格檢查
- `--status` — 顯示專案狀態
- `--list-templates` — 列出可用模板

### 3.5 `style_checker.py` — 風格驗證引擎

**一句話**：對生成的文章執行 6 項規則檢查，回傳結構化報告。

檢查項目（詳見[第 8 節](#8-風格檢查規則)）：
- 禁用詞掃描
- 標題層級驗證
- 段落長度檢查
- SEO 基本功
- 標點符號（全形/半形）
- 中英文間距

### 3.6 `output_md2html.py` — 格式轉換器

**一句話**：將 Markdown 文章轉為含 CSS 的 HTML，相容 WordPress。

流程：`讀取 .md` → `前處理（修復列表格式）` → `markdown.markdown() 解析` → `包裹 HTML 模板 + CSS` → `寫入 .html`

### 3.7 `blogpro.py` — CLI 工具（Skill 管理器）

**一句話**：管理 skill 的安裝/移除/更新/版本查詢，支援 18 個 AI 平台。

| 子命令 | 說明 |
|--------|------|
| `blogpro init --ai claude` | 將 skill 注入到指定 AI 助手 |
| `blogpro init --ai all --global` | 全域安裝到所有平台 |
| `blogpro uninstall` | 自動偵測並移除已安裝的 skill |
| `blogpro versions` | 顯示版本資訊和已安裝平台 |
| `blogpro update` | 更新所有已安裝平台到最新版本 |

---

## 4. 核心設計決策

### 4.1 RESOURCE_ROOT vs Path.cwd() 分離

這是最重要的架構決策：

| 概念 | 變數 | 用途 | 範例 |
|------|------|------|------|
| **資源位置** | `RESOURCE_ROOT` | 讀取模板、設定檔、風格指南 | `.../site-packages/blog_pro_max/` |
| **工作目錄** | `Path.cwd()` | 文章輸出、狀態掃描 | `/home/user/my-blog/` |
| **開發根目錄** | `DEV_ROOT` | 開發模式的 fallback 資源 | `.../blog-pro-max/` |

**為什麼這樣設計？**  
使用者透過 `pip install` 安裝後，可以在任意目錄執行 `blogpro`。  
模板和設定跟著套件走（不變），但輸出檔案放在使用者的工作目錄。

### 4.2 模板註冊表系統

所有模板集中定義在 `core.py` 的 `TEMPLATES` 字典：

```python
TEMPLATES = {
    "blog-skill-content": {
        "path": "templates/blog-skill-content.md",
        "description": "SEO 部落格文章（專業、結構化）",
        "style_guide": "writing-style.md",
        "system_prompt": "你是一位專業的中文 SEO 內容撰寫者...\n{style_guide}\n..."
    },
    "max-personal-style": {
        "path": "templates/max-personal-style.md",
        "description": "Max 個人風格（心情筆記、第一人稱）",
        "style_guide": None,
        "system_prompt": "你是作家 Max 的代筆 AI..."
    },
    "fb-post-style": {
        "path": "templates/fb-post-style.md",
        "description": "Facebook 貼文（口語化、▋ 標題、社群互動）",
        "style_guide": None,
        "system_prompt": "你是一位擅長經營 Facebook 的社群內容創作者..."
    },
    "line-message-style": {
        "path": "templates/line-message-style.md",
        "description": "LINE 訊息（簡短、親切、好朋友分享）",
        "style_guide": None,
        "system_prompt": "你是一位擅長用 LINE 分享好文的內容創作者..."
    }
}
```

**設計好處**：
- 新增模板只需加一個字典條目 + 模板檔案
- 風格指南注入自動處理（`{style_guide}` 佔位符）
- 模板存在性檢查統一由 `bootstrap()` 處理

### 4.3 18 平台定義

每個 AI 平台定義為 `PLATFORMS` 字典的一個條目：

```python
PLATFORMS = {
    "claude":   {"display": "Claude Code",     "root": ".claude",  "sub": "skills/blog-pro-max",  "filename": "SKILL.md"},
    "copilot":  {"display": "GitHub Copilot",  "root": ".github",  "sub": "prompts/blog-pro-max", "filename": "PROMPT.md"},
    "kiro":     {"display": "Kiro",            "root": ".kiro",    "sub": "steering/blog-pro-max", "filename": "SKILL.md"},
    "droid":    {"display": "Droid (Factory)",  "root": ".factory", "sub": "skills/blog-pro-max",  "filename": "SKILL.md"},
    "roocode":  {"display": "Roo Code",        "root": ".roo",     "sub": "skills/blog-pro-max",  "filename": "SKILL.md"},
    ...
}
```

**安裝路徑範例**：
```
Claude:    ~/.claude/skills/blog-pro-max/SKILL.md
Copilot:   ~/.github/prompts/blog-pro-max/PROMPT.md
Kiro:      ~/.kiro/steering/blog-pro-max/SKILL.md
```

### 4.4 安裝清單（Manifest）

每次 `blogpro init` 都會在 skill 目錄寫入 `.blogpro-manifest.json`：

```json
{
  "skill": "blog-pro-max",
  "version": "1.0.12",
  "platform": "claude",
  "installed_at": "2026-03-28T14:30:45.123456",
  "global": true,
  "path": "/home/user/.claude/skills/blog-pro-max"
}
```

這個清單用於：
- `blogpro versions` — 顯示每個平台的安裝版本
- `blogpro uninstall` — 自動偵測已安裝的平台
- `blogpro update` — 找出需要更新的安裝

### 4.5 SKILL.md 內容生成

`_build_skill_content()` 產生一個**自包含**的 SKILL.md 檔案，結構為：

```
---
name: blog-pro-max
version: 1.0.12
---

# 概述
[功能說明]

# 觸發方式
[斜線命令範例與解析規則]

# 參數說明
[參數表格]

# 可用模板
[模板列表]

---
## 寫作風格指南
{writing-style.md 全文內容}

---
## SEO 文章模板
{blog-skill-content.md 全文內容}

---
## Max 個人風格模板
{max-personal-style.md 全文內容}
```

**設計原則**：AI 助手讀取單一檔案即可取得所有必要上下文，無需額外讀檔。

---

## 5. 執行流程

### 5.1 文章生成（完整 Pipeline）

```
使用者輸入：
  python -m blog_pro_max.content_research --keyword "失去才懂珍惜" --template max-personal-style

    │
    ▼
┌─────────────────────────────────────────────────────┐
│  content_research.py — 解析參數                      │
│  keyword = "失去才懂珍惜"                             │
│  audience = "30-45 歲知識工作者"（預設）               │
│  template = "max-personal-style"                     │
│  model = "gpt-4o"                                    │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  core.py — 環境檢查                                  │
│  bootstrap() → 確認 templates/, writing-style.md 存在 │
│  ensure_environment() → 印出結果                      │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  blog_generator.py — 組裝 Prompt                     │
│                                                      │
│  build_prompt(keyword, audience, word_count, ...)    │
│    ├─ core.render_template() → 載入模板、替換變數      │
│    │    → user_prompt（帶有指令的完整 prompt）         │
│    │                                                  │
│    └─ core.build_system_prompt() → 組裝 system prompt │
│         → 包含模板的 system_prompt + 風格指南注入       │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  blog_generator.py — 呼叫 LLM API                    │
│                                                      │
│  _make_client()                                      │
│    → 優先 GITHUB_TOKEN（GitHub Models 免費端點）       │
│    → 備選 OPENAI_API_KEY                              │
│                                                      │
│  client.chat.completions.create(                     │
│      model = "gpt-4o",                               │
│      messages = [system_prompt, user_prompt],         │
│      temperature = 0.7,                              │
│      max_tokens = 4096                               │
│  )                                                   │
│  → 回傳 Markdown 文章                                 │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  content_research.py — 儲存文章                       │
│  Path.cwd() / "output" / "失去才懂珍惜.md"           │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  style_checker.py — 風格檢查                          │
│                                                      │
│  check_content(article, keyword)                     │
│    ├─ check_forbidden_words()    → 禁用詞掃描         │
│    ├─ check_heading_hierarchy()  → 標題層級驗證        │
│    ├─ check_paragraph_length()   → 段落長度檢查        │
│    ├─ check_seo_basics()         → SEO 基本功         │
│    ├─ check_punctuation()        → 標點符號檢查        │
│    └─ check_spacing()            → 中英間距檢查        │
│                                                      │
│  → StyleReport { issues: [...], passed: bool }       │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  blog_generator.py — 邏輯與事實專家 🔬               │
│                                                      │
│  review_logic(article, keyword, audience)            │
│    → 數據錯誤、邏輯矛盾、錯別字、AI 幻覺              │
│    → 附加 ## 🔬 邏輯與事實專家審查報告 到 .md         │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  blog_generator.py — 深度與結構專家 📐               │
│                                                      │
│  review_structure(article, keyword, audience)        │
│    → 遺漏面向、段落轉折、論述深度、結構平衡            │
│    → 附加 ## 📐 深度與結構專家審查報告 到 .md         │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  blog_generator.py — 讀者視角專家 👁️                │
│                                                      │
│  review_reader(article, keyword, audience)           │
│    → 口吻適配、易讀性、注意力留存、情感共鳴            │
│    → 附加 ## 👁️ 讀者視角專家審查報告 到 .md          │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  blog_generator.py — 時事趨勢專家 📰                 │
│                                                      │
│  review_trend(article, keyword, audience)            │
│    → trend_analysis   → 趨勢關聯分析                 │
│    → angle_suggestions → 切入角度建議                │
│    → keywords_tags    → 關鍵字與 Hashtag             │
│    → rewrite_demo     → 改寫示範                     │
│    → 附加 ## 📰 時事趨勢分析報告 到 .md              │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  blog_generator.py — 標題專家                         │
│                                                      │
│  generate_titles(article, keyword, audience)          │
│    → 4 個標題建議（直述/提問/數字/情感）                │
│    → 每個含英文 permalink slug                         │
│    → 附加到 .md 末尾                                   │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  blog_generator.py — 封面提示詞專家                    │
│                                                      │
│  generate_cover_prompts(article, keyword)             │
│    → 3 組 AI 繪圖提示詞                                │
│      ├─ 寫實攝影風格                                   │
│      ├─ 插畫風格                                       │
│      └─ 極簡設計風格                                   │
│    → 英文 prompt，可直接用於 Midjourney/DALL-E/SD      │
│    → 附加到 .md 末尾                                   │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  output_md2html.py — 格式轉換                         │
│                                                      │
│  convert_file(input.md, output.html)                 │
│    ├─ preprocess_markdown() → 修復列表格式             │
│    ├─ markdown.markdown()   → 解析為 HTML             │
│    └─ 包裹 HTML 模板 + CSS  → 寫入 .html              │
│                                                      │
│  → output/失去才懂珍惜.html                           │
└─────────────────────────────────────────────────────┘

最終產出：
  ✅ output/失去才懂珍惜.md   （原始 Markdown）
  ✅ output/失去才懂珍惜.html （HTML，WordPress 相容）
  📋 風格檢查報告（印在終端機）
  🔬 邏輯與事實審查報告（含 issue/suggest/before/after 表格）
  📐 深度與結構審查報告（含 issue/suggest/before/after 表格）
  👁️ 讀者視角審查報告（含 issue/suggest/before/after 表格）
  📰 時事趨勢分析報告（趨勢關聯、切入角度、關鍵字/Hashtag、改寫示範）
  📝 4 個推薦標題（含 WordPress permalink slug）
  🖼️ 3 組 AI 封面繪圖提示詞
```

### 5.2 Skill 注入（`blogpro init`）

```
使用者輸入：blogpro init --ai claude --global

    │
    ▼
┌─────────────────────────────────────────────────────┐
│  blogpro.py — cmd_init()                             │
│  target_root = Path.home()（--global）                │
│  platforms = ["claude"]                              │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  install_for_platform("claude", target_root)         │
│                                                      │
│  1. 建立目錄：~/.claude/skills/blog-pro-max/         │
│                                                      │
│  2. 生成 SKILL.md                                    │
│     _build_skill_content("claude", prefix)           │
│     → 讀取 writing-style.md、所有模板                 │
│     → 組裝完整的自包含 SKILL.md                       │
│                                                      │
│  3. 複製模板：templates/ → skill_dir/templates/       │
│                                                      │
│  4. 複製腳本：*.py → skill_dir/scripts/               │
│     (RESOURCE_ROOT 優先，DEV_ROOT 備選)               │
│                                                      │
│  5. 複製資源檔：writing-style.md, copilot.json        │
│                                                      │
│  6. 生成 requirements.txt（如果不存在）                │
│                                                      │
│  7. 建立 output/ 目錄                                 │
│                                                      │
│  8. 寫入 .blogpro-manifest.json                      │
│     → 版本追蹤用                                      │
└─────────────────────────────────────────────────────┘

結果：
  ~/.claude/skills/blog-pro-max/
    ├── SKILL.md
    ├── scripts/
    ├── templates/
    ├── writing-style.md
    ├── copilot.json
    ├── requirements.txt
    ├── output/
    └── .blogpro-manifest.json
```

### 5.3 斜線命令觸發（Workflow Mode）

當使用者在 AI 助手中輸入：
```
/blog-pro-max 寫一篇[失去才懂珍惜]文章,受眾[一般讀者],以作家Max風格
```

AI 助手根據 SKILL.md 中的解析規則進行拆解：

| 輸入片段 | 解析規則 | 對應參數 |
|----------|----------|----------|
| `[失去才懂珍惜]` | 第一個 `[值]` | `--keyword "失去才懂珍惜"` |
| `受眾[一般讀者]` | `受眾[值]` | `--audience "一般讀者"` |
| `作家Max風格` | 關鍵字比對 | `--template max-personal-style` |
| `字數[2000]` | `字數[N]` | `--word-count 2000` |

風格關鍵字對照表：

| 關鍵字 | 模板 |
|--------|------|
| `作家Max風格`、`Max風格`、`心情筆記` | `max-personal-style` |
| `SEO風格`、`專業風格`、`部落格風格` | `blog-skill-content` |

---

## 6. 資料流

### 6.1 模組依賴圖

```
_resources.py
    │
    │  匯出 RESOURCE_ROOT
    │
    ▼
core.py ◄──────────────────────────────────────┐
    │                                           │
    │  匯出 TEMPLATES, bootstrap(),             │
    │  build_system_prompt(), render_template()  │
    │                                           │
    ├──────────────►  blog_generator.py          │
    │                     │                     │
    │                     │  匯出 generate_article(),
    │                     │  build_prompt()      │
    │                     │                     │
    │                     ▼                     │
    │              content_research.py ──────────┘
    │                     │
    │                     ├──► style_checker.py
    │                     │       匯出 check_content()
    │                     │
    │                     └──► output_md2html.py
    │                             匯出 convert_file()
    │
    │
blogpro.py（獨立 CLI，只依賴 _resources.py）
```

### 6.2 關鍵資料結構

**ProjectConfig** — 專案設定：
```python
@dataclass
class ProjectConfig:
    name: str = "blog-pro-max"
    runtime: str = "python3"
    default_template: str = "blog-skill-content"
    default_language: str = "zh-TW"
    default_audience: str = "30-45 歲知識工作者"
    default_word_count: int = 1200
    default_model: str = "gpt-4o"
```

**StyleIssue** — 單一風格問題：
```python
@dataclass
class StyleIssue:
    rule: str           # "forbidden-word", "heading-depth", ...
    message: str
    line: int | None
    severity: str       # "warning" 或 "error"
```

**StyleReport** — 風格檢查報告：
```python
@dataclass
class StyleReport:
    issues: list[StyleIssue]

    @property
    def passed(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)
```

---

## 7. 設定系統

### 設定層級

```
┌─ pyproject.toml ──────────────────────────────────┐
│  套件元資料：名稱、版本、依賴、entry point          │
│  blogpro = "blog_pro_max.blogpro:main"            │
└───────────────────────────────────────────────────┘
          │
┌─ copilot.json ────────────────────────────────────┐
│  專案設定：name, runtime, entrypoint               │
│  由 ProjectConfig.load() 讀取                      │
└───────────────────────────────────────────────────┘
          │
┌─ .env ────────────────────────────────────────────┐
│  執行時密鑰：GITHUB_TOKEN 或 OPENAI_API_KEY        │
│  由 python-dotenv 自動載入                          │
└───────────────────────────────────────────────────┘
          │
┌─ writing-style.md ────────────────────────────────┐
│  品牌寫作規範：禁用詞、標點規則、SEO 原則            │
│  被 build_system_prompt() 注入到 system prompt      │
└───────────────────────────────────────────────────┘
          │
┌─ templates/*.md ──────────────────────────────────┐
│  寫作模板：包含變數佔位符                            │
│  由 render_template() 載入並替換                    │
└───────────────────────────────────────────────────┘
```

### 環境載入順序

```python
# 1. 嘗試套件模式 import
try:
    from blog_pro_max._resources import RESOURCE_ROOT
    from blog_pro_max.core import ...

# 2. 失敗則回退到開發模式
except ImportError:
    RESOURCE_ROOT = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(RESOURCE_ROOT / "scripts"))
    from core import ...
```

---

## 8. 風格檢查規則

| 規則 | 函式 | 嚴重度 | 說明 |
|------|------|--------|------|
| **禁用詞** | `check_forbidden_words()` | ERROR | 掃描 7 個禁用詞彙：值得注意的是、不可否認地、在這個日新月異的時代、顯而易見、毋庸置疑、筆者認為、相信讀者 |
| **標題層級** | `check_heading_hierarchy()` | ERROR | 必須恰好 1 個 H1，不可使用 H3 以下，層級正確巢狀 |
| **段落長度** | `check_paragraph_length()` | WARNING | 單一段落不超過 5 行 |
| **SEO 基本功** | `check_seo_basics()` | ERROR/WARNING | H1 包含關鍵字、關鍵字出現在前 100 字元、含內部連結佔位符 |
| **標點符號** | `check_punctuation()` | WARNING | 中文語境使用全形標點，不混用半形 |
| **中英間距** | `check_spacing()` | WARNING | 中文字元與 ASCII 字元之間需有空格 |

---

## 9. 函式速查表

### core.py（專案經理）

| 函式 | 說明 |
|------|------|
| `bootstrap()` | 檢查環境完整性，回傳 `BootstrapIssue` 列表 |
| `ensure_environment()` | 執行 bootstrap 並印出結果，回傳 bool |
| `list_templates()` | 列出所有模板及存在狀態 |
| `get_template(name)` | 取得指定模板設定，不存在則 raise KeyError |
| `load_template_content(name)` | 讀取模板檔案內容 |
| `build_system_prompt(template)` | 組裝 system prompt（含風格指南注入） |
| `render_template(template, keyword, ...)` | 載入模板並替換所有變數 |
| `format_output_path(keyword)` | 生成輸出檔案路徑 |
| `scan_project_status()` | 掃描專案現況，回傳 Markdown 報告 |

### blog_generator.py（LLM 引擎）

| 函式 | 說明 |
|------|------|
| `_make_client()` | 建立 OpenAI client（GitHub Models 優先） |
| `build_prompt(keyword, audience, ...)` | 回傳 `(user_prompt, system_prompt)` 元組 |
| `generate_article(keyword, audience, ...)` | 完整生成流程，回傳 Markdown 文章 |
| `generate_titles(content, keyword, audience)` | 產出 4 個標題建議（含英文 permalink slug），回傳 `list[dict]` |
| `generate_cover_prompts(content, keyword)` | 產出 3 組 AI 繪圖封面提示詞，回傳 `list[dict]` |
| `review_logic(content, keyword, audience)` | 邏輯與事實專家，回傳 `list[dict]`（issue/suggest/before/after）|
| `review_structure(content, keyword, audience)` | 深度與結構專家，回傳 `list[dict]`（issue/suggest/before/after）|
| `review_reader(content, keyword, audience)` | 讀者視角專家，回傳 `list[dict]`（issue/suggest/before/after）|
| `review_trend(content, keyword, audience)` | 時事趨勢專家，回傳 `dict`（trend_analysis/angle_suggestions/keywords_tags/rewrite_demo）|

### style_checker.py（風格驗證引擎）

| 函式 | 說明 |
|------|------|
| `check_forbidden_words(content)` | 掃描禁用詞 |
| `check_heading_hierarchy(content)` | 驗證標題結構 |
| `check_paragraph_length(content)` | 檢查段落長度 |
| `check_seo_basics(content, keyword)` | 檢查 SEO 基本功 |
| `check_punctuation(content)` | 檢查標點符號 |
| `check_spacing(content)` | 檢查中英間距 |
| `check_content(content, keyword)` | 執行所有檢查，回傳 `StyleReport` |
| `check_file(filepath, keyword)` | 讀取檔案後執行所有檢查 |

### blogpro.py（Skill 管理器）

| 函式 | 說明 |
|------|------|
| `install_for_platform(key, root, ...)` | 安裝 skill 到指定平台 |
| `_build_skill_content(key, prefix)` | 生成完整 SKILL.md 內容 |
| `_find_installed_platforms(root)` | 偵測已安裝的平台 |
| `cmd_init(args)` | 處理 `blogpro init` |
| `cmd_uninstall(args)` | 處理 `blogpro uninstall` |
| `cmd_versions(args)` | 處理 `blogpro versions` |
| `cmd_update(args)` | 處理 `blogpro update` |

### _resources.py（路徑解析）

| 函式 | 說明 |
|------|------|
| `get_resource_path(relative)` | 取得資源絕對路徑 |
| `get_templates_dir()` | 取得模板目錄 |
| `get_writing_style_path()` | 取得風格指南路徑 |
| `get_copilot_json_path()` | 取得 copilot.json 路徑 |

---

## 擴充指南

### 新增寫作模板

#### 快速步驟

1. 建立模板檔案：`blog_pro_max/templates/my-new-style.md`
2. 在 `core.py` 的 `TEMPLATES` 字典新增條目（目前已有 4 個模板）：

```python
"my-new-style": {
    "path": "templates/my-new-style.md",
    "description": "我的新風格",
    "style_guide": "writing-style.md",  # 或 None
    "system_prompt": "你是一位...\n{style_guide}"
}
```

3. 使用：`--template my-new-style`

---

#### 如何萃取你自己的寫作風格

如果你有自己長期維護的部落格或文章，可以讓 AI 分析你的寫作習慣，自動產出符合本系統格式的模板檔案。

**第一步：準備你的文章樣本**

收集 3–5 篇能代表你風格的文章全文。篇幅不限，建議選：
- 你覺得「最像自己」的文章
- 風格一致、不是特殊場合的例外之作
- 涵蓋不同主題更佳（生活、職場、心得等）

將所有文章貼在一起，或存成一個 `.txt` / `.md` 檔。

---

**第二步：使用以下提示詞給 AI 分析**

將你的文章樣本貼入，搭配下方提示詞，交給 ChatGPT、Claude 或 Gemini：

```
以下是我寫的 [數量] 篇文章，請仔細分析我的寫作風格，然後為我產出一份「寫作風格模板」。

--- 我的文章開始 ---
[在此貼上你的文章全文]
--- 我的文章結束 ---

請根據這些文章，產出一份 Markdown 格式的寫作風格模板，內容需包含以下區塊：

1. 模板開頭（system prompt 宣告）：
   「你是 [你的名字] 的代筆 AI。請以 [你的名字] 的寫作風格生成一篇部落格文章。」

2. 輸入變數區塊（固定格式，照抄即可）：
   - 核心關鍵字：{keyword}
   - 目標讀者：{audience}
   - 文章目標字數：{word_count}
   - 語言：{language}

3. 風格說明區塊，需包含：
   - 語氣與人稱（例：第一人稱、口語、像在和朋友說話）
   - 情緒表達方式（例：直白、帶點自嘲、不說教）
   - 常用敘事手法（例：舉例、生活插曲、反差比喻）
   - 寫作節奏（例：從事件 → 感受 → 反思 → 行動）
   - 句型偏好（例：短句多、常用破折號停頓、習慣用反問）

4. 結構要求區塊：
   標題格式、段落長度偏好、是否使用小標題、列點風格

5. 禁止事項：
   我的文章中「絕對不會出現」的用詞、句型或寫法

6. 範例句型：
   從我的文章中挑出 3–5 句最能代表我風格的句子，作為 AI 的參考錨點

輸出格式：完整的 Markdown 文件，可直接存為 .md 檔使用。
```

---

**第三步：將產出的模板存入專案**

將 AI 回傳的 Markdown 內容存為：

```
blog_pro_max/templates/my-style.md
```

（若使用 Skill 安裝模式，也要放一份到 `.claude/skills/blog-pro-max/templates/`）

---

**第四步：在 `core.py` 中註冊模板**

開啟 `blog_pro_max/core.py`，在 `TEMPLATES` 字典中新增一筆：

```python
"my-style": {
    "path": "templates/my-style.md",
    "description": "我的個人寫作風格",
    "style_guide": None,
    "system_prompt": "你是一位有溫度的部落客，請依照指定風格撰寫文章。"
}
```

> `style_guide` 可設為 `None`（風格全由模板本身定義），或指向 `writing-style.md`（套用全域規則）。

---

**第五步：測試模板**

```bash
python scripts/content_research.py --keyword "你的測試主題" --template my-style
```

確認輸出風格符合預期後，即可在日常使用中以 `--template my-style` 指定，或將其設為預設。

---

> 💡 **小技巧**：如果 AI 產出的模板一開始不夠準確，可以追加提示：「請加強 [某個面向]，我的文章中更常用 [某個特徵]」，反覆修正 2–3 次即可收斂到理想風格。

### 新增 AI 平台支援

在 `blogpro.py` 的 `PLATFORMS` 字典新增：

```python
"newai": {
    "display": "New AI",
    "root": ".newai",
    "sub": f"skills/{SKILL_NAME}",
    "filename": "SKILL.md"
}
```

即可支援 `blogpro init --ai newai`。
