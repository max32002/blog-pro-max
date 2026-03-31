# Scripts 參考手冊

本文件詳述 `scripts/`（以及 `blog_pro_max/`）目錄下每個檔案的用途、獨立使用情境、完整參數列表與範例。

---

## 目錄

1. [content_research.py — 文章生成主程式](#1-content_researchpy--文章生成主程式)
2. [style_checker.py — 風格驗證引擎](#2-style_checkerpy--風格驗證引擎)
3. [output_md2html.py — Markdown 轉 HTML](#3-output_md2htmlpy--markdown-轉-html)
4. [blog_generator.py — LLM 引擎（函式庫）](#4-blog_generatorpy--llm-引擎函式庫)
5. [core.py — 環境管理與模板系統](#5-corepy--環境管理與模板系統)
6. [blogpro.py — Skill 安裝管理器](#6-blogpropy--skill-安裝管理器)

---

## 1. `content_research.py` — 文章生成主程式

### 用途

整個 blog-pro-max 的主要入口。串接完整 pipeline：
```
讀取關鍵字 → 生成文章 → 風格檢查 → 標題建議 → 封面提示詞 → 輸出 HTML
```

### 獨立使用情境

- 直接在終端機生成文章，不透過 AI Assistant
- 批次處理多篇文章（搭配 shell script 或 task runner）
- 只執行風格檢查，不重新生成文章

### 執行方式

```bash
# 套件模式（推薦）
python -m blog_pro_max.content_research [參數]

# 開發模式
python scripts/content_research.py [參數]
```

### 參數列表

| 參數 | 型別 | 預設值 | 說明 |
|------|------|--------|------|
| `--keyword` | str | — | 核心關鍵字；支援 `@檔案路徑` 從檔案讀取 |
| `--keyword-file` | str | — | 從指定檔案讀取關鍵字（替代 `--keyword`） |
| `--audience` | str | `30-45 歲知識工作者` | 目標讀者描述 |
| `--word-count` | int | `1200` | 目標字數 |
| `--language` | str | `zh-TW` | 輸出語言代碼 |
| `--model` | str | `gpt-4o` | OpenAI 模型名稱 |
| `--template` | str | `blog-skill-content` | 寫作風格模板名稱 |
| `--output` | str | `output/{keyword}.md` | 自訂輸出檔案路徑 |
| `--check-only` | str | — | 僅對指定 .md 檔執行風格檢查，不生成文章 |
| `--dry-run` | flag | — | 顯示 prompt 內容但不呼叫 API |
| `--status` | flag | — | 顯示專案狀態報告後離開 |
| `--list-templates` | flag | — | 列出所有可用模板後離開 |

> **注意**：`--keyword` 和 `--keyword-file` 二擇一，至少提供一個（`--status` 和 `--list-templates` 例外）。

### 可用模板

| 模板名稱 | 說明 |
|----------|------|
| `blog-skill-content` | SEO 專業文章（預設） |
| `max-personal-style` | 作家 Max 個人風格 |
| `fb-post-style` | Facebook 貼文格式 |
| `line-message-style` | LINE 訊息格式 |

### 範例

```bash
# 基本生成
python -m blog_pro_max.content_research --keyword "遠端工作生產力"

# 指定受眾與字數
python -m blog_pro_max.content_research \
  --keyword "Python 入門" \
  --audience "程式設計初學者" \
  --word-count 800

# 使用個人風格模板
python -m blog_pro_max.content_research \
  --keyword "失去才懂珍惜" \
  --template max-personal-style

# 使用 Facebook 貼文格式
python -m blog_pro_max.content_research \
  --keyword "時間管理" \
  --template fb-post-style

# 關鍵字很長，從檔案讀取（兩種方式）
echo "如何在高壓工作環境下維持身心健康與工作生活平衡" > topic.txt
python -m blog_pro_max.content_research --keyword @topic.txt
python -m blog_pro_max.content_research --keyword-file topic.txt

# 只看 prompt，不呼叫 API
python -m blog_pro_max.content_research --keyword "AI 工具" --dry-run

# 對已有的 .md 檔執行風格檢查
python -m blog_pro_max.content_research \
  --keyword "Python" \
  --check-only output/python-入門.md

# 查看可用模板
python -m blog_pro_max.content_research --list-templates

# 查看專案狀態
python -m blog_pro_max.content_research --status
```

### 退出碼

| 代碼 | 意義 |
|------|------|
| `0` | 成功，風格檢查通過 |
| `1` | 生成失敗，或風格檢查有 ERROR |
| `2` | 參數錯誤 |

---

## 2. `style_checker.py` — 風格驗證引擎

### 用途

對 Markdown 文章執行 6 項風格與 SEO 規則檢查，回傳結構化報告。可獨立使用，也被 `content_research.py` 自動呼叫。

### 獨立使用情境

- 手動撰寫的文章，上傳前快速驗證
- CI/CD 流程中自動檢查草稿品質
- 批次檢查已存在的文章庫

### 執行方式

```bash
python scripts/style_checker.py <檔案路徑> [關鍵字]
```

### 參數列表

| 參數 | 型別 | 必填 | 說明 |
|------|------|------|------|
| `filepath` | positional | ✅ | 要檢查的 .md 檔路徑 |
| `keyword` | positional | ❌ | 核心關鍵字，用於 SEO 規則驗證 |

### 檢查規則

| 規則 | 嚴重度 | 說明 |
|------|--------|------|
| **禁用詞** | ERROR | 掃描 7 個 AI 口癖：`值得注意的是`、`不可否認地`、`在這個日新月異的時代`、`顯而易見`、`毋庸置疑`、`筆者認為`、`相信讀者` |
| **標題層級** | ERROR | 必須恰好 1 個 H1；不允許 H3 以下；層級不可跳躍 |
| **段落長度** | WARNING | 單一段落超過 5 行時提醒 |
| **SEO 基本功** | ERROR/WARNING | H1 含關鍵字（ERROR）；關鍵字出現在前 100 字（WARNING）；含內部連結佔位符（WARNING） |
| **標點符號** | WARNING | 中文語境應使用全形標點（，。！？） |
| **中英間距** | WARNING | 中文字元與英文/數字之間需有空格 |

### 範例

```bash
# 基本檢查（不指定關鍵字）
python scripts/style_checker.py output/my-article.md

# 含關鍵字的 SEO 檢查
python scripts/style_checker.py output/python-教學.md "Python 入門"

# 搭配 grep 只看錯誤
python scripts/style_checker.py output/my-article.md "關鍵字" | grep ERROR
```

### 輸出範例

```
🔍 風格檢查報告
================
❌ ERROR   [禁用詞] 第 12 行：發現禁用詞「值得注意的是」，建議改為「需要注意的是」
⚠️  WARNING [段落長度] 第 25 行：段落超過 5 行（目前 7 行）
⚠️  WARNING [中英間距] 第 34 行：「使用Python來」應改為「使用 Python 來」

結果：1 個錯誤，2 個警告
狀態：❌ 未通過
```

### 作為函式庫使用

```python
from style_checker import check_content, check_file

# 檢查字串
report = check_content(article_text, keyword="Python")
if report.passed:
    print("✅ 通過")

# 檢查檔案
report = check_file("output/article.md", keyword="Python")
print(report.summary())
print(f"錯誤數：{report.error_count}")
print(f"警告數：{report.warning_count}")
```

---

## 3. `output_md2html.py` — Markdown 轉 HTML

### 用途

將 Markdown 檔案轉換為含 CSS 樣式的完整 HTML 文件，適合貼入 WordPress 或其他 CMS。

### 獨立使用情境

- 手動撰寫的 .md 草稿，需轉換成 HTML 預覽
- 批次將文章庫的所有 .md 轉為 HTML
- 獨立於生成流程，單純做格式轉換

### 執行方式

```bash
python scripts/output_md2html.py <輸入.md> <輸出.html>
```

### 參數列表

| 參數 | 型別 | 必填 | 說明 |
|------|------|------|------|
| `input` | positional | ✅ | 輸入 Markdown 檔案路徑 |
| `output` | positional | ✅ | 輸出 HTML 檔案路徑 |

### 功能特性

- 支援 Markdown 擴充語法：表格、程式碼區塊、圍欄式程式碼
- 程式碼語法高亮（`codehilite` 擴充）
- 自動修復列表格式（`preprocess_markdown()` 前處理）
- 輸出含完整 HTML 結構（`<!DOCTYPE html>` + CSS）
- 內文寬度限制 800px，適合部落格閱讀

### 範例

```bash
# 基本轉換
python scripts/output_md2html.py output/my-article.md output/my-article.html

# 轉換到不同目錄
python scripts/output_md2html.py drafts/article.md public/article.html

# 批次轉換（bash）
for f in output/*.md; do
    python scripts/output_md2html.py "$f" "${f%.md}.html"
done
```

### 作為函式庫使用

```python
from output_md2html import convert_file

convert_file("input.md", "output.html")
```

---

## 4. `blog_generator.py` — LLM 引擎（函式庫）

### 用途

封裝對 OpenAI 相容 API 的所有呼叫。提供文章生成、標題建議、封面提示詞三個功能。**無法獨立執行**，作為函式庫被其他腳本引用。

### 獨立使用情境

- 在自己的 Python 腳本中直接呼叫，整合進自訂流程
- 測試不同 prompt 或模型的效果（搭配 Python REPL）

### 無 CLI，只能作為函式庫

```python
from blog_generator import generate_article, generate_titles, generate_cover_prompts

# 生成文章
article = generate_article(
    keyword="Python 入門",
    audience="程式設計初學者",
    word_count=1000,
    language="zh-TW",
    model="gpt-4o",
    template="blog-skill-content",
)
print(article)
```

### 函式說明

#### `generate_article()`

```python
def generate_article(
    keyword: str,
    audience: str = "30-45 歲知識工作者",
    word_count: int = 1200,
    language: str = "zh-TW",
    model: str = "gpt-4o",
    template: str = "blog-skill-content",
) -> str
```

呼叫 LLM API，回傳完整 Markdown 文章字串。

#### `generate_titles()`

```python
def generate_titles(
    article_content: str,
    keyword: str,
    audience: str = "30-45 歲知識工作者",
    language: str = "zh-TW",
    model: str = "gpt-4o",
) -> list[dict]
```

分析文章後產出 4 個標題建議，回傳格式：

```python
[
    {"title": "如何用 Python 打造自動化工作流", "slug": "python-automation-workflow"},
    {"title": "Python 新手必看：5 個入門關鍵", "slug": "python-beginners-5-keys"},
    ...
]
```

#### `generate_cover_prompts()`

```python
def generate_cover_prompts(
    article_content: str,
    keyword: str,
    audience: str = "30-45 歲知識工作者",
    model: str = "gpt-4o",
) -> list[dict]
```

產出 3 組 AI 繪圖封面提示詞，回傳格式：

```python
[
    {
        "style": "寫實攝影",
        "prompt": "A focused programmer at a modern desk, soft natural lighting...",
        "description": "適合科技、教學類文章的專業感封面"
    },
    ...
]
```

### `review_logic(content, keyword, audience, model, temperature)`

邏輯與事實專家，檢查文章的數據正確性、邏輯矛盾與錯別字。

| 參數 | 預設 | 說明 |
|------|------|------|
| `content` | — | 文章 Markdown 內容（超過 3000 字自動截斷）|
| `keyword` | — | 主題關鍵字 |
| `audience` | `"30-45 歲知識工作者"` | 目標受眾描述 |
| `model` | `"gpt-4.1"` | LLM 模型名稱 |
| `temperature` | `0.3` | 溫度（低=嚴謹）|

回傳格式：

```python
[
    {
        "issue": "第二段引用的「每天產生 2.5 quintillion bytes 數據」缺乏來源依據",
        "suggest": "加上資料來源，例如 IBM 2023 年報告，或改用有據可查的數字",
        "before": "每天全球會產生 2.5 quintillion bytes 的數據。",
        "after": "根據 IBM 研究，每天全球產生約 2.5 quintillion bytes 的數據（IBM, 2023）。"
    },
    ...
]
```

### `review_structure(content, keyword, audience, model, temperature)`

深度與結構專家，分析文章遺漏面向、段落轉折、論述深度。

| 參數 | 預設 | 說明 |
|------|------|------|
| `temperature` | `0.5` | 其餘參數同 review_logic |

回傳格式：同 review_logic（`list[dict]` with issue/suggest/before/after）

### `review_reader(content, keyword, audience, model, temperature)`

讀者視角專家，評估口吻適配性、易讀性、情感共鳴與注意力留存。

| 參數 | 預設 | 說明 |
|------|------|------|
| `temperature` | `0.5` | 其餘參數同 review_logic |

回傳格式：同 review_logic（`list[dict]` with issue/suggest/before/after）

### `review_trend(content, keyword, audience, model, temperature)`

時事趨勢專家，分析文章與當前熱議話題的關聯，提供時效性優化建議。

| 參數 | 預設 | 說明 |
|------|------|------|
| `temperature` | `0.6` | 其餘參數同 review_logic |

回傳格式：

```python
{
    "trend_analysis": "文章主題與近期「AI 工具生產力」熱潮高度相關...\n討論熱度：高",
    "angle_suggestions": "1. 結合 ChatGPT-5 發表會切入...\n2. 連結年度知識工作者趨勢報告...",
    "keywords_tags": "搜尋關鍵字：AI生產力工具, 職場效率提升...\nHashtag：#AI工具 #職場效率",
    "rewrite_demo": "原文：這個方法可以提高工作效率。\n改寫：在 ChatGPT-5 問世後的今天，這個方法已成為..."
}
```

### API 優先順序

```
GITHUB_TOKEN 存在 → GitHub Models（免費）
    endpoint: https://models.inference.ai.azure.com

OPENAI_API_KEY 存在 → OpenAI 原生 API

都沒有 → 拋出 EnvironmentError
```

### 環境變數設定

```bash
# .env 或直接設定環境變數
GITHUB_TOKEN=ghp_xxxxxxxxxxxx   # 推薦：免費
OPENAI_API_KEY=sk-xxxxxxxxxxxx  # 備選：按量計費
```

---

## 5. `core.py` — 環境管理與模板系統

### 用途

管理環境設定、模板系統、專案配置，是整個工具的核心基礎設施。也可獨立執行查看環境狀態。

### 獨立使用情境

- 安裝後確認環境是否正常
- 查看目前已安裝的模板
- 排查設定問題

### 執行方式

```bash
python scripts/core.py [子命令]
```

### 子命令

| 子命令 | 說明 |
|--------|------|
| `status` | 掃描專案狀態，輸出 Markdown 報告 |
| `check` | 驗證環境完整性（0=正常，1=有問題） |
| `templates` | 列出所有可用模板及其存在狀態 |

### 範例

```bash
# 查看專案狀態（模板、輸出目錄、環境變數）
python scripts/core.py status

# 驗證環境（適合用在 CI）
python scripts/core.py check && echo "環境正常"

# 列出模板
python scripts/core.py templates
```

### 作為函式庫使用

```python
from core import ensure_environment, list_templates, build_system_prompt, render_template

# 驗證環境
if not ensure_environment():
    sys.exit(1)

# 列出模板
templates = list_templates()
for name, info in templates.items():
    print(f"{name}: {info['description']} ({'✅' if info['exists'] else '❌'})")

# 渲染模板
user_prompt = render_template(
    template_name="blog-skill-content",
    keyword="Python 入門",
    audience="初學者",
    word_count=1000,
    language="zh-TW",
)

# 取得 system prompt
system_prompt = build_system_prompt("blog-skill-content")
```

---

## 6. `blogpro.py` — Skill 安裝管理器

### 用途

管理 blog-pro-max Skill 在各 AI 助手平台的安裝、更新與移除。安裝後，AI 助手能直接理解並執行文章生成指令。

### 執行方式

```bash
blogpro <子命令> [參數]
```

---

### 子命令：`init` — 安裝 Skill

```bash
blogpro init --ai <平台> [--global] [--target <路徑>]
```

**參數：**

| 參數 | 說明 |
|------|------|
| `--ai` | 目標平台（見下表）或 `all` 安裝全部 |
| `--global` | 安裝到全域（`~/`），適用電腦上所有專案 |
| `--target` | 自訂安裝根目錄 |

**支援的 18 個平台：**

| 參數值 | 平台名稱 | 安裝路徑 |
|--------|----------|----------|
| `claude` | Claude Code | `.claude/skills/blog-pro-max/` |
| `cursor` | Cursor | `.cursor/skills/blog-pro-max/` |
| `windsurf` | Windsurf | `.windsurf/skills/blog-pro-max/` |
| `copilot` | GitHub Copilot | `.github/skills/blog-pro-max/` |
| `antigravity` | Antigravity | `.antigravity/skills/blog-pro-max/` |
| `kiro` | Kiro | `.kiro/skills/blog-pro-max/` |
| `codex` | Codex CLI | `.codex/skills/blog-pro-max/` |
| `qoder` | Qoder | `.qoder/skills/blog-pro-max/` |
| `roo` | Roo Code | `.roo/skills/blog-pro-max/` |
| `gemini` | Gemini CLI | `.gemini/skills/blog-pro-max/` |
| `trae` | Trae | `.trae/skills/blog-pro-max/` |
| `opencode` | OpenCode | `.opencode/skills/blog-pro-max/` |
| `continue` | Continue | `.continue/skills/blog-pro-max/` |
| `codebuddy` | CodeBuddy | `.codebuddy/skills/blog-pro-max/` |
| `droid` | Droid (Factory) | `.droid/skills/blog-pro-max/` |
| `kilocode` | KiloCode | `.kilocode/skills/blog-pro-max/` |
| `warp` | Warp | `.warp/skills/blog-pro-max/` |
| `augment` | Augment | `.augment/skills/blog-pro-max/` |

**範例：**

```bash
# 安裝到單一平台（當前目錄）
blogpro init --ai claude

# 全域安裝（所有專案皆可使用）
blogpro init --ai copilot --global

# 一次安裝到全部 18 個平台
blogpro init --ai all --global

# 安裝到自訂路徑
blogpro init --ai cursor --target /workspace/my-project
```

**安裝後目錄結構：**

```
.claude/skills/blog-pro-max/
├── SKILL.md              ← AI 助手讀取的 Skill 說明（自包含）
├── scripts/              ← 所有 Python 腳本
│   ├── content_research.py
│   ├── blog_generator.py
│   ├── core.py
│   ├── style_checker.py
│   ├── output_md2html.py
│   └── blogpro.py
├── templates/            ← 寫作模板
├── writing-style.md      ← 品牌風格指南
├── copilot.json          ← 專案設定
├── requirements.txt      ← Python 依賴
├── output/               ← 文章輸出目錄
└── .blogpro-manifest.json ← 版本追蹤（用於 uninstall）
```

---

### 子命令：`uninstall` — 移除 Skill

```bash
blogpro uninstall [--ai <平台>] [--global]
```

**參數：**

| 參數 | 說明 |
|------|------|
| `--ai` | 指定移除的平台；省略則自動偵測所有已安裝平台 |
| `--global` | 從全域安裝目錄移除 |

**範例：**

```bash
# 移除特定平台
blogpro uninstall --ai claude

# 自動偵測並移除所有本地安裝
blogpro uninstall

# 移除所有全域安裝
blogpro uninstall --global

# 移除全部（本地 + 全域）
blogpro uninstall --ai all
blogpro uninstall --ai all --global
```

---

### 子命令：`versions` — 查看版本資訊

```bash
blogpro versions
```

無額外參數。輸出包含：

- 目前版本號（如 `v1.0.5`）
- 套件安裝路徑（RESOURCE_ROOT）
- 目前工作目錄
- 完整版本歷史（版本、日期、變更說明）
- 本地已安裝平台清單（含版本）
- 全域已安裝平台清單（含版本）

**範例輸出：**

```
📦 blog-pro-max
  目前版本：v1.0.5
  專案路徑：/usr/local/lib/python3.11/site-packages/blog_pro_max

📋 版本歷史：
  v1.0.5  2026-03-28  支援從檔案讀取關鍵字（@file 語法 + --keyword-file 參數）
  v1.0.4  2026-03-28  新增 FB/LINE 模板、標題專家、封面提示詞專家、完整文件更新
  ...

🔌 本地已安裝平台：
  ✅ claude    v1.0.5  .claude/skills/blog-pro-max/
  ✅ copilot   v1.0.5  .github/skills/blog-pro-max/
```

---

### 子命令：`update` — 更新所有已安裝平台

```bash
blogpro update
```

無額外參數。自動：

1. 掃描本地與全域的所有已安裝平台
2. 重新執行安裝，覆蓋舊版 SKILL.md、腳本和資源
3. 更新 `.blogpro-manifest.json` 中的版本號

**範例：**

```bash
# 升級 blog-pro-max 套件後，更新所有平台的 Skill
pip install --upgrade blog-pro-max
blogpro update
```

---

## 快速參考：各腳本功能對照表

| 腳本 | 可獨立執行 | 主要輸入 | 主要輸出 |
|------|-----------|----------|----------|
| `content_research.py` | ✅ | `--keyword` / `--keyword-file` | `.md` + `.html` 文章 |
| `style_checker.py` | ✅ | `<filepath>` | 風格檢查報告 |
| `output_md2html.py` | ✅ | `<input.md> <output.html>` | HTML 文件 |
| `blog_generator.py` | ❌（函式庫） | `keyword` + API | Markdown 文章字串 |
| `core.py` | ✅ | `status` / `check` / `templates` | 狀態報告 / 驗證結果 |
| `blogpro.py` | ✅ | `init` / `uninstall` / `update` / `versions` | Skill 檔案安裝 |

---

## Skill Mode 斜線命令參考

安裝 Skill 後，在任何支援的 AI 平台（Claude、Cursor、Gemini 等）可使用以下斜線命令：

### 文章生成

| 指令 | 說明 |
|------|------|
| `幫我寫一篇關於 <主題> 的文章` | 生成 SEO 文章（預設風格） |
| `用 Max 風格寫 <主題>` | Max 個人風格文章 |
| `寫 FB 貼文 <主題>` | Facebook 社群貼文格式 |
| `寫 LINE 貼文 <主題>` | LINE 社群貼文格式 |

### 審稿專家

| 指令 | 說明 |
|------|------|
| `全科檢查 output/article.md` | 執行邏輯、結構、讀者視角三位專家全面審查 |
| `檢查邏輯 output/article.md` | 🔬 邏輯與事實專家：數據正確性、邏輯矛盾、錯別字 |
| `檢查結構 output/article.md` | 📐 深度與結構專家：遺漏面向、段落轉折、論述深度 |
| `檢查讀者 output/article.md` | 👁️ 讀者視角專家：口吻適配、易讀性、情感共鳴 |

### 行銷優化

| 指令 | 說明 |
|------|------|
| `幫我生成標題 output/article.md` | 📝 4 個標題建議（含英文 permalink slug）|
| `幫我生成封面 output/article.md` | 🎨 3 組 AI 繪圖封面提示詞 |
| `分析趨勢 output/article.md` | 📰 時事趨勢分析（趨勢關聯、切入角度、關鍵字/Hashtag、改寫示範）|

### 風格檢查

| 指令 | 說明 |
|------|------|
| `幫我檢查風格 output/article.md` | 執行 style_checker：禁用詞、標題層級、SEO、標點符號等 |
| `轉換為 HTML output/article.md` | 將 .md 轉換為 .html 格式 |
