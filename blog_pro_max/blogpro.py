#!/usr/bin/env python3
"""
blogpro — blog-pro-max CLI 統一入口

用法：
  blogpro init --ai claude           # 注入 skill 到 Claude
  blogpro init --ai copilot --global # 全域安裝到 ~/
  blogpro uninstall --ai claude      # 移除指定平台
  blogpro uninstall                  # 自動偵測並移除
  blogpro versions                   # 顯示版本資訊
  blogpro update                     # 更新到最新版本
"""

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Ensure UTF-8 output on all platforms
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# RESOURCE_ROOT = where bundled assets (templates, scripts) live
# DEV_ROOT      = repo root (only useful when running from git clone, as fallback)
# WORKING_DIR   = Path.cwd(), where the user runs the command (for display only)
_PACKAGE_DIR = Path(__file__).resolve().parent
_is_package = (_PACKAGE_DIR / "__init__.py").is_file() and (_PACKAGE_DIR / "templates").is_dir()
if _is_package:
    RESOURCE_ROOT = _PACKAGE_DIR
else:
    RESOURCE_ROOT = _PACKAGE_DIR.parent

DEV_ROOT = _PACKAGE_DIR.parent  # fallback for dev-mode resources

SKILL_NAME = "blog-pro-max"
VERSION = "1.0.57"
VERSION_HISTORY = [
    {"version": "1.0.57", "date": "2026-09-06", "changes": "架構重構：移除指令/腳本模式雙分支，全面轉為純 LLM 模式；精簡模板並強化多維度分析報告與零樣本 Agent 流程"},
    {"version": "1.0.56", "date": "2026-09-06", "changes": "更新 pi agent 指令 — 腳本輸出 prompt 後由 LLM 生成文章"},
    {"version": "1.0.55", "date": "2026-09-06", "changes": "LLM 模式為預設生成方式，精簡提示詞以減少 token 用量"},
    {"version": "1.0.54", "date": "2026-09-06", "changes": "因應 Google 終止個人免費 Gemini CLI 並改推 Antigravity CLI，全面移除 Gemini CLI 並改用 agy CLI (--ai agy)"},
    {"version": "1.0.53", "date": "2026-09-06", "changes": "支援 Pi Agent (--ai pi) 與 Antigravity CLI (--ai agy)；生成的 SKILL.md 強化對 progressive disclosure 與各 Agent 檔案寫入工具相容性"},
    {"version": "1.0.52", "date": "2026-04-12", "changes": "風格微調, 套用在手機上閱讀舒適"},
    {"version": "1.0.46", "date": "2026-04-02", "changes": "分析流程重構：全部分析一次執行完畢，文章本文存 keyword.md，所有分析存 keyword_analysis.md；HTML 輸出自動合併文章＋分析為單一 .html；修正 Gemini CLI Skill Mode 重複寫入 bug：LLM 模式改為全部分析完畢後一次性寫檔，禁止多次 write_file；新增腳本失敗停止指令，防止靜默回退 LLM 模式造成內容重疊"},
    {"version": "1.0.38", "date": "2026-04-01", "changes": "優化存檔流程：12個區塊輸出完畢後自動儲存當前風格，再詢問是否另存其他3種"},
    {"version": "1.0.36", "date": "2026-04-01", "changes": "Max風格微調"},
    {"version": "1.0.35", "date": "2026-04-01", "changes": "增加 快速生成模式"},
    {"version": "1.0.34", "date": "2026-04-01", "changes": "format md2html output"},
    {"version": "1.0.33", "date": "2026-04-01", "changes": "Script Mode 補齊 6 個段落級專家（發散、問題、迷因、插話、插畫、唱反調），與 Skill Mode 輸出的 12 個區塊一致；移除已棄用的 Pygments 依賴（requirements.txt、pyproject.toml、Skill 安裝產生的 requirements）；刪除根目錄 scripts/ 與 templates/ 後確認三種模式（Package、Skill、Script）皆不受影響"},
    {"version": "1.0.32", "date": "2026-04-01", "changes": "output_md2html: **Prompt:** 開頭的行自動轉為 code block 格式"},
    {"version": "1.0.31", "date": "2026-04-01", "changes": "output_md2html: 移除 codehilite（避免 <pre> 輸出混亂），改用 fenced_code；max-width 改為 1024px；移除 Pygments 依賴"},
    {"version": "1.0.30", "date": "2026-04-01", "changes": "修正 CI 測試：移除不存在的 --list-templates CLI 旗標"},
    {"version": "1.0.29", "date": "2026-04-01", "changes": "修正 ruff linting 錯誤（F401 未使用 import、F541 無佔位符 f-string）"},
    {"version": "1.0.28", "date": "2026-04-01", "changes": "系統優化：擴充模板別名辨識（日記/心情/貼文/短訊等同義詞）、強化參考資料提取邏輯（長度驗證+主題確認）、加入風格衝突優先級規則、CI 功能測試+ruff linting、publish 版本驗證、FAQ 補充參考資料模式與斜線命令說明"},
    {"version": "1.0.27", "date": "2026-03-31", "changes": "重新發布 v1.0.26 的變更（修正存檔行為：確保 .md 包含全部 12 個專家區塊）"},
    {"version": "1.0.26", "date": "2026-03-31", "changes": "修正存檔指令：明確要求 .md 必須包含文章本文 + 全部 12 個專家區塊，不得只存文章本文"},
    {"version": "1.0.25", "date": "2026-03-31", "changes": "將插話專家、插畫專家、唱反調專家也加入自動觸發清單（第10-12項必須輸出），全部 12 個專家區塊皆自動輸出"},
    {"version": "1.0.24", "date": "2026-03-31", "changes": "將發散專家、問題專家、迷因專家加入 LLM 模式自動觸發清單（第7-9項必須輸出）"},
    {"version": "1.0.23", "date": "2026-03-31", "changes": "強化 LLM 模式指令：明確標注全部6個區塊為「必須輸出、不得省略」，防止 Gemini CLI 在三維度審稿後提早停止"},
    {"version": "1.0.22", "date": "2026-03-31", "changes": "修正 f-string 語法錯誤：Markdown 範本中的 {佔位符} 改為 {{佔位符}} 以防止 Python 3.10 解析錯誤"},
    {"version": "1.0.21", "date": "2026-03-31", "changes": "新增三個內部角色：發散專家（每段落延伸相關話題）、問題專家（每段落提出3-5個問題）、迷因專家（每段落提出迷因/幽默關鍵字）"},
    {"version": "1.0.20", "date": "2026-03-31", "changes": "新增三個內部角色：插話專家（每段落舉例說明）、插畫專家（每段落3組AI圖片提示詞）、唱反調專家（每段落反駁觀點）"},
    {"version": "1.0.19", "date": "2026-03-30", "changes": "三維度審稿專家改用條列格式取代 Markdown 表格，方便直接複製給 AI 進行下一輪修改"},
    {"version": "1.0.18", "date": "2026-03-30", "changes": "升版至 1.0.18"},
    {"version": "1.0.17", "date": "2026-03-30", "changes": "版本歷史清單改為時間倒序，顯示最新 3 筆"},
    {"version": "1.0.16", "date": "2026-03-30", "changes": "推薦標題選項的 WordPress Permalink 改用有意義的英文單字，不再使用中文拼音"},
    {"version": "1.0.15", "date": "2026-03-30", "changes": "修正 PyPI 跨版本相容性（openai>=2.0.0、ddgs optional、Python classifiers、CI matrix）；新增參考資料生成模式（貼入素材+指令自動生成文章並執行全科檢查、標題建議、封面提示詞）"},
    {"version": "1.0.12", "date": "2026-03-29", "changes": "修正 Gemini CLI 輸出路徑問題：SKILL.md 明確規定所有輸出須存至使用者工作目錄 output/"},
    {"version": "1.0.11", "date": "2026-03-29", "changes": "強化三位審稿專家提示詞，新增流暢性/連貫性/理解難度檢查；全面優化四個寫作模板"},
    {"version": "1.0.10", "date": "2026-03-29", "changes": "時事趨勢專家整合 DuckDuckGo Web Search，分析改以真實當前資料為依據"},
    {"version": "1.0.9", "date": "2026-03-29", "changes": "LLM-only 模式自動同時產生 .html 檔案；新增範本排版與語言難度限制；更新文件"},
    {"version": "1.0.8", "date": "2026-03-29", "changes": "新增三維度審稿專家（邏輯/結構/讀者）與時事趨勢專家；更新完整文件"},
    {"version": "1.0.7", "date": "2026-03-28", "changes": "LLM 模式存檔時詢問存單一風格或全部 4 種風格"},
    {"version": "1.0.6", "date": "2026-03-28", "changes": "修正 Skill Mode 在純 LLM 平台的輸出格式與存檔行為"},
    {"version": "1.0.5", "date": "2026-03-28", "changes": "支援從檔案讀取關鍵字（@file 語法 + --keyword-file 參數）"},
    {"version": "1.0.4", "date": "2026-03-28", "changes": "新增 FB/LINE 模板、標題專家、封面提示詞專家、完整文件更新"},
    {"version": "1.0.3", "date": "2026-03-28", "changes": "新增 GitHub Actions CI/CD publish workflow"},
    {"version": "1.0.2", "date": "2026-03-28", "changes": "修正路徑問題：分離 RESOURCE_ROOT 與工作目錄，從任意路徑執行皆正確"},
    {"version": "1.0.0", "date": "2026-03-28", "changes": "初始版本：SEO 文章生成、Max 風格、風格檢查、MD→HTML、18 平台 init"},
]

# ── AI Assistant 平台定義 ─────────────────────────────

PLATFORMS = {
    "claude": {
        "display": "Claude Code",
        "root": ".claude",
        "sub": f"skills/{SKILL_NAME}",
        "filename": "SKILL.md",
    },
    "cursor": {
        "display": "Cursor",
        "root": ".cursor",
        "sub": f"skills/{SKILL_NAME}",
        "filename": "SKILL.md",
    },
    "windsurf": {
        "display": "Windsurf",
        "root": ".windsurf",
        "sub": f"skills/{SKILL_NAME}",
        "filename": "SKILL.md",
    },
    "copilot": {
        "display": "GitHub Copilot",
        "root": ".github",
        "sub": f"prompts/{SKILL_NAME}",
        "filename": "PROMPT.md",
    },
    "antigravity": {
        "display": "Antigravity",
        "root": ".agents",
        "sub": f"skills/{SKILL_NAME}",
        "filename": "SKILL.md",
    },
    "agy": {
        "display": "Antigravity CLI (agy)",
        "root": ".agents",
        "sub": f"skills/{SKILL_NAME}",
        "filename": "SKILL.md",
    },
    "pi": {
        "display": "Pi Agent",
        "root": ".pi",
        "sub": f"skills/{SKILL_NAME}",
        "global_root": ".pi/agent",
        "filename": "SKILL.md",
    },
    "kiro": {
        "display": "Kiro",
        "root": ".kiro",
        "sub": f"steering/{SKILL_NAME}",
        "filename": "SKILL.md",
    },
    "codex": {
        "display": "Codex CLI",
        "root": ".codex",
        "sub": f"skills/{SKILL_NAME}",
        "filename": "SKILL.md",
    },
    "qoder": {
        "display": "Qoder",
        "root": ".qoder",
        "sub": f"skills/{SKILL_NAME}",
        "filename": "SKILL.md",
    },
    "roocode": {
        "display": "Roo Code",
        "root": ".roo",
        "sub": f"skills/{SKILL_NAME}",
        "filename": "SKILL.md",
    },
    "trae": {
        "display": "Trae",
        "root": ".trae",
        "sub": f"skills/{SKILL_NAME}",
        "filename": "SKILL.md",
    },
    "opencode": {
        "display": "OpenCode",
        "root": ".opencode",
        "sub": f"skills/{SKILL_NAME}",
        "filename": "SKILL.md",
    },
    "continue": {
        "display": "Continue",
        "root": ".continue",
        "sub": f"skills/{SKILL_NAME}",
        "filename": "SKILL.md",
    },
    "codebuddy": {
        "display": "CodeBuddy",
        "root": ".codebuddy",
        "sub": f"skills/{SKILL_NAME}",
        "filename": "SKILL.md",
    },
    "droid": {
        "display": "Droid (Factory)",
        "root": ".factory",
        "sub": f"skills/{SKILL_NAME}",
        "filename": "SKILL.md",
    },
    "kilocode": {
        "display": "KiloCode",
        "root": ".kilocode",
        "sub": f"skills/{SKILL_NAME}",
        "filename": "SKILL.md",
    },
    "warp": {
        "display": "Warp",
        "root": ".warp",
        "sub": f"skills/{SKILL_NAME}",
        "filename": "SKILL.md",
    },
    "augment": {
        "display": "Augment",
        "root": ".augment",
        "sub": f"skills/{SKILL_NAME}",
        "filename": "SKILL.md",
    },
}

COPY_FILES = ["writing-style.md", "copilot.json", "requirements.txt"]

# Python script files to include in skill installs
SCRIPT_FILES = [
    "core.py",
    "blog_generator.py",
    "content_research.py",
    "style_checker.py",
    "output_md2html.py",
    "blogpro.py",
    "__init__.py",
]


# ══════════════════════════════════════════════════════
#  Skill 文件生成
# ══════════════════════════════════════════════════════

def _build_frontmatter(platform_key):
    desc = (
        "自動化 SEO 內容創作與部落格文章生成工具。"
        "支援 4 種寫作風格模板（SEO 專業、Max 個人風格、Facebook 貼文、LINE 訊息），"
        "具備多維度專家審查（邏輯、深度、讀者視角、時事趨勢）、標題與封面生成及 HTML 輸出。"
    )
    if platform_key == "claude":
        desc = (
            "Blog content intelligence. "
            "自動化 SEO 內容創作與部落格文章生成。"
            "4 種寫作風格模板（SEO 專業 / Max 個人風格 / FB 貼文 / LINE 訊息）、"
            "多維度專家審查、風格檢查、MD 與 HTML 雙格式輸出。"
            "Actions: generate, check, convert, plan, write, review, "
            "optimize SEO, create blog posts, analyze style."
        )
    elif platform_key in ("antigravity", "agy", "pi"):
        desc = (
            "Blog Pro Max: 自動化 SEO 內容創作與部落格文章生成工具。"
            "當使用者需要撰寫部落格文章、SEO 內容、個人風格隨筆、Facebook 貼文、LINE 訊息、"
            "進行多維度文章審查（邏輯、深度、讀者視角、時事趨勢）、取得推薦標題、生成封面提示詞、"
            "檢查寫作風格或輸出 HTML 時使用此技能。"
            "支援自然語言對話、/blog-pro-max 及 /skill:blog-pro-max 指令。"
        )
    return "\n".join([
        "---",
        f"name: {SKILL_NAME}",
        f"version: {VERSION}",
        f'description: "{desc}"',
        "---",
    ])


def _build_skill_content(platform_key, script_prefix=""):
    fm = _build_frontmatter(platform_key)
    writing_style = (RESOURCE_ROOT / "writing-style.md").read_text(encoding="utf-8")
    max_template = (RESOURCE_ROOT / "templates" / "max-personal-style.md").read_text(encoding="utf-8")
    seo_template = (RESOURCE_ROOT / "templates" / "blog-skill-content.md").read_text(encoding="utf-8")
    fb_template = (RESOURCE_ROOT / "templates" / "fb-post-style.md").read_text(encoding="utf-8")
    line_template = (RESOURCE_ROOT / "templates" / "line-message-style.md").read_text(encoding="utf-8")

    return f"""{fm}

# Blog Pro Max — 自動化 SEO 內容創作與部落格文章生成

## 概述

blog-pro-max 支援 4 種寫作風格：

- **blog-skill-content**：SEO 專業風格（精簡、直接、關鍵字最佳化）
- **max-personal-style**：Max 個人風格（心情筆記、生活化敘事、自我反思）
- **fb-post-style**：Facebook 貼文（口語化、「▋ 」標題、社群互動）
- **line-message-style**：LINE 訊息（簡短親切、好朋友分享）

## 觸發方式

### Slash Command 與自然語言指令

```
/blog-pro-max 寫一篇[主題關鍵字]文章,受眾[目標讀者],以[風格名稱]風格
```

**範例：**

```
/blog-pro-max 寫一篇[AI創作悖論]文章,受眾[30-45 歲知識工作者],以SEO風格
/blog-pro-max 寫一篇[失去才懂珍惜]文章,受眾[一般讀者],以作家Max風格
/blog-pro-max 寫一篇[遠端工作]文章,受眾[上班族],以FB風格
/blog-pro-max 幫我取標題 output/my-article.md
/blog-pro-max 檢查風格 output/my-article.md
```

**解析規則：**

1. `[...]` 中的值 → 核心關鍵字
2. `受眾[...]` → 目標讀者（預設：`30-45 歲知識工作者`）
3. 風格關鍵字對應：
   - `作家Max風格` / `Max風格` / `心情筆記` / `日記` / `心情` / `感受` → `max-personal-style`
   - `SEO風格` / `專業風格` / `部落格` / `教學` / `技巧` → `blog-skill-content`（預設）
   - `FB風格` / `Facebook` / `臉書` / `貼文` / `社群` → `fb-post-style`
   - `LINE風格` / `LINE訊息` / `短訊` / `聊天` → `line-message-style`
   - 無法識別時預設 `blog-skill-content`，提示：「未識別風格 [xxx]，改用 SEO 預設模板。」
4. `字數[N]` → 目標字數（預設：`1200`）
5. 其他獨立指令：`幫我取標題 <路徑>` / `幫我生成封面 <路徑>` / `全科檢查 <路徑>` / `檢查邏輯` / `檢查結構` / `檢查讀者` / `分析趨勢` / `插話建議` / `段落插畫` / `唱反調` / `發散思考` / `提出問題` / `迷因建議` / `檢查風格`

### 參考資料生成模式

**觸發條件（滿足任一）：**
- 訊息包含「以下是我收集的資料」、「根據以下資料」、「這是參考資料」
- 訊息結構：[貼上的原始素材] + [生成指令]
- 使用者明確指定「參考資料模式」

**執行步驟：**
1. 提取參考資料區塊（若超過 5000 字則截斷並提示；若不足 100 字則提示補充）
2. 提取受眾與風格（未指定則使用預設值）
3. 若未指定關鍵字，自動推斷主題並向使用者確認
4. 以參考資料為核心基礎，依選定模板生成文章

---

## LLM 執行流程

收到文章生成請求後，LLM **一氣呵成執行以下 5 步驟（中間不需停下來向使用者確認）**：

### 1. 解析意圖與套用風格規範
- 提取關鍵字、目標受眾、寫作風格與字數。
- 風格規範優先級（高 → 低）：
  1. 使用者明確指令（例如「語氣再幽默一點」）
  2. 選定模板的風格指南
  3. `writing-style.md` 全域規則（禁用詞、標題層級、標點等，禁用詞規則永遠適用）

### 2. 生成文章本文
- 依照選定模板的格式與規範，專注生成完整的高品質文章。
- **此步驟只產出文章本文，嚴禁在此步驟夾帶任何分析或審查內容。**

### 3. 執行全部分析（在記憶體中累積）
文章生成後，依序執行多維度分析（所有分析累積在記憶體中，最後一次性寫入）：
1. **三維度審稿**：🔬 邏輯與事實、📐 深度與結構、👁️ 讀者視角
2. **標題建議**：部落格標題專家產出 4 組不同風格標題 + 英文 slug
3. **封面提示詞**：封面專家產出 3 組 AI 繪圖提示詞（Midjourney / DALL-E / SD）
4. **時事趨勢分析**：趨勢關聯、切入角度、關鍵字/Hashtag、內容改寫示範
5. **延伸反思與互動**：發散思考、唱反調、插話建議、段落插畫、提出問題、迷因建議

### 4. 存檔規則（嚴格遵守，防止重複）
- **存檔路徑**：所有檔案一律存到**使用者工作目錄**的 `output/` 資料夾（絕對不能存到 Skill 安裝目錄）。
- **呼叫次數限制**：
  - `output/關鍵字.md`：文章完成後**只呼叫寫檔工具一次**，寫入純文章本文。
  - `output/關鍵字_analysis.md`：所有分析完成後**只呼叫寫檔工具一次**，寫入合併後的全部分析報告。
  - `output/關鍵字.html`：合併文章與分析內容為 HTML 格式，**只呼叫寫檔工具一次**。
  - **嚴禁對同一個檔案多次重複呼叫寫入工具**。

### 5. 完成回報與多風格延伸
檔案寫入完成後輸出確認訊息：

```
✅ 文章與分析已完成
📄 文章：output/關鍵字.md
📊 分析：output/關鍵字_analysis.md
🌐 合併 HTML：output/關鍵字.html
```

> 💡 若使用者回覆 `y`，依序以其他 3 種風格模板重新生成並儲存（命名如 `output/關鍵字-max.md`、`output/關鍵字-fb.md`、`output/關鍵字-line.md`，自動跳過已生成的風格）。

---

## 分析報告格式規範（output/關鍵字_analysis.md）

分析報告應包含以下章節區塊：

```markdown
# 📊 《文章標題》多維度分析報告

## 🔬 邏輯與事實專家審查報告
**1. [問題標題]**
- **修改建議**：...
- **原文**：...
- **修改後**：...

## 📐 深度與結構專家審查報告
...

## 👁️ 讀者視角專家審查報告
...

## 📰 時事趨勢分析報告
### 🔗 趨勢關聯分析
### 🎯 切入角度建議
### 🏷️ 關鍵字與標籤優化
### ✍️ 內容改寫示範

## 📝 推薦標題選項
1. 直述型：... (slug: ...)
2. 提問型：... (slug: ...)
3. 數字型：... (slug: ...)
4. 情感型：... (slug: ...)

## 🎨 推薦封面提示詞
1. 寫實攝影風：`Prompt...` (說明: ...)
2. 插畫風格：`Prompt...` (說明: ...)
3. 極簡設計風：`Prompt...` (說明: ...)

## 🌀 發散專家建議
## 🔴 唱反調專家報告
## 💬 插話專家建議
## 🖼️ 段落插畫提示詞
## ❓ 問題專家建議 (FAQ 靈感)
## 😂 迷因專家建議
```

---

## 寫作風格指南

{writing_style}

---

## SEO 文章模板

{seo_template}

---

## Max 個人風格模板

{max_template}

---

## Facebook 貼文風格模板

{fb_template}

---

## LINE 訊息風格模板

{line_template}
"""


# ══════════════════════════════════════════════════════
#  init — 安裝 skill
# ══════════════════════════════════════════════════════

def install_for_platform(platform_key, target_root, global_install=False, offline=False):
    plat = PLATFORMS[platform_key]
    display = plat["display"]
    root_name = plat["global_root"] if (global_install and "global_root" in plat) else plat["root"]
    skill_dir = target_root / root_name / plat["sub"]
    skill_file = skill_dir / plat["filename"]

    if global_install:
        prefix = str(skill_dir).replace("\\", "/") + "/"
    else:
        prefix = root_name + "/" + plat["sub"] + "/"

    print(f"  📦 {display}...")

    try:
        skill_dir.mkdir(parents=True, exist_ok=True)

        content = _build_skill_content(platform_key, prefix)
        skill_file.write_text(content, encoding="utf-8")

        # ── Copy templates ──
        tmpl_src = RESOURCE_ROOT / "templates"
        if not tmpl_src.is_dir():
            tmpl_src = DEV_ROOT / "templates"
        tmpl_dst = skill_dir / "templates"
        if tmpl_src.is_dir():
            if tmpl_dst.exists():
                shutil.rmtree(tmpl_dst)
            shutil.copytree(tmpl_src, tmpl_dst)

        # ── Copy scripts ──
        # When installed via pip, Python files are in RESOURCE_ROOT (blog_pro_max/)
        # When in dev mode, they're in DEV_ROOT/scripts/
        scripts_dst = skill_dir / "scripts"
        scripts_dst.mkdir(exist_ok=True)

        scripts_src_pkg = RESOURCE_ROOT  # package mode
        scripts_src_dev = DEV_ROOT / "scripts"  # dev mode

        for fname in SCRIPT_FILES:
            src = scripts_src_pkg / fname
            if not src.is_file():
                src = scripts_src_dev / fname
            if src.is_file():
                shutil.copy2(src, scripts_dst / fname)

        # ── Copy resource files ──
        for file_name in COPY_FILES:
            src = RESOURCE_ROOT / file_name
            if not src.is_file():
                src = DEV_ROOT / file_name
            dst = skill_dir / file_name
            if src.is_file():
                shutil.copy2(src, dst)

        # Also generate requirements.txt if not found
        req_dst = skill_dir / "requirements.txt"
        if not req_dst.is_file():
            req_dst.write_text(
                "openai>=1.0.0\npython-dotenv>=1.0.0\nMarkdown>=3.5.0\n",
                encoding="utf-8",
            )

        (skill_dir / "output").mkdir(exist_ok=True)

        # Write install manifest for uninstall tracking
        manifest = {
            "skill": SKILL_NAME,
            "version": VERSION,
            "platform": platform_key,
            "installed_at": datetime.now().isoformat(),
            "global": global_install,
            "path": str(skill_dir),
        }
        manifest_path = skill_dir / ".blogpro-manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"     ✅ {skill_file}")
        return True

    except Exception as e:
        print(f"     ❌ 失敗：{e}")
        return False


def cmd_init(args):
    if args.target:
        target_root = Path(args.target).resolve()
    elif args.global_install:
        target_root = Path.home()
    else:
        target_root = Path.cwd()

    mode = "離線模式" if args.offline else "本地資源"
    scope = "全域" if args.global_install else "本地"
    print(f"🚀 blog-pro-max v{VERSION} skill 安裝（{scope}，{mode}）")
    print(f"📂 安裝目錄：{target_root}")
    print()

    if args.ai == "all":
        seen_paths = set()
        targets = []
        for key, plat in PLATFORMS.items():
            root_name = plat["global_root"] if (args.global_install and "global_root" in plat) else plat["root"]
            rel_path = f"{root_name}/{plat['sub']}"
            if rel_path not in seen_paths:
                seen_paths.add(rel_path)
                targets.append(key)
    else:
        targets = [args.ai]

    success = failed = 0
    for plat in targets:
        if install_for_platform(plat, target_root, args.global_install, args.offline):
            success += 1
        else:
            failed += 1

    print()
    print(f"✅ 完成：{success} 個平台成功" + (f"，{failed} 個失敗" if failed else ""))
    if failed:
        sys.exit(1)


# ══════════════════════════════════════════════════════
#  uninstall — 移除 skill
# ══════════════════════════════════════════════════════

def _find_installed_platforms(search_root):
    """掃描目錄，找出所有已安裝 blog-pro-max 的平台。"""
    found = []
    seen_dirs = set()
    for key, plat in PLATFORMS.items():
        candidates = [search_root / plat["root"] / plat["sub"]]
        if "global_root" in plat:
            candidates.append(search_root / plat["global_root"] / plat["sub"])
        for skill_dir in candidates:
            if skill_dir in seen_dirs:
                continue
            manifest = skill_dir / ".blogpro-manifest.json"
            if manifest.is_file() or (skill_dir / plat["filename"]).is_file():
                seen_dirs.add(skill_dir)
                found.append((key, plat, skill_dir))
    return found


def _remove_skill_dir(platform_key, skill_dir):
    plat = PLATFORMS[platform_key]
    display = plat["display"]
    print(f"  🗑️  {display}...")
    try:
        if skill_dir.is_dir():
            shutil.rmtree(skill_dir)
            print(f"     ✅ 已移除 {skill_dir}")
            return True
        else:
            print(f"     ⚠️  目錄不存在：{skill_dir}")
            return False
    except Exception as e:
        print(f"     ❌ 失敗：{e}")
        return False


def cmd_uninstall(args):
    if args.global_install:
        search_root = Path.home()
        scope = "全域"
    else:
        search_root = Path.cwd()
        scope = "本地"

    print(f"🗑️  blog-pro-max skill 移除（{scope}）")
    print(f"📂 搜尋目錄：{search_root}")
    print()

    if args.ai:
        # Remove specific platform(s)
        if args.ai == "all":
            targets = list(PLATFORMS.keys())
        else:
            targets = [args.ai]

        success = failed = 0
        for key in targets:
            plat = PLATFORMS[key]
            skill_dir = search_root / plat["root"] / plat["sub"]
            if _remove_skill_dir(key, skill_dir):
                success += 1
            else:
                failed += 1

        print()
        print(f"✅ 完成：{success} 個平台已移除" + (f"，{failed} 個失敗" if failed else ""))
    else:
        # Auto-detect installed platforms
        found = _find_installed_platforms(search_root)
        if not found:
            print("  ℹ️  未偵測到任何已安裝的 blog-pro-max skill。")
            return

        print(f"  偵測到 {len(found)} 個已安裝平台：")
        for key, plat, skill_dir in found:
            print(f"    • {plat['display']} → {skill_dir}")
        print()

        success = failed = 0
        for key, plat, skill_dir in found:
            if _remove_skill_dir(key, skill_dir):
                success += 1
            else:
                failed += 1

        print()
        print(f"✅ 完成：{success} 個平台已移除" + (f"，{failed} 個失敗" if failed else ""))


# ══════════════════════════════════════════════════════
#  versions — 顯示版本資訊
# ══════════════════════════════════════════════════════

def cmd_versions(args):
    print("📦 blog-pro-max")
    print(f"   目前版本：v{VERSION}")
    print(f"   安裝位置：{RESOURCE_ROOT}")
    print(f"   工作目錄：{Path.cwd()}")
    print()
    print("📋 版本歷史：")
    print()
    for entry in VERSION_HISTORY[:3]:
        print(f"  v{entry['version']}  ({entry['date']})")
        print(f"    {entry['changes']}")
        print()

    # Show installed platforms
    print("📍 已安裝平台（本地）：")
    local_found = _find_installed_platforms(Path.cwd())
    if local_found:
        for key, plat, skill_dir in local_found:
            # Read version from manifest if available
            manifest_path = skill_dir / ".blogpro-manifest.json"
            installed_ver = "?"
            if manifest_path.is_file():
                try:
                    m = json.loads(manifest_path.read_text(encoding="utf-8"))
                    installed_ver = m.get("version", "?")
                except Exception:
                    pass
            print(f"  ✅ {plat['display']:20s} v{installed_ver}  {skill_dir}")
    else:
        print("  （無）")

    print()
    print("📍 已安裝平台（全域 ~）：")
    global_found = _find_installed_platforms(Path.home())
    if global_found:
        for key, plat, skill_dir in global_found:
            manifest_path = skill_dir / ".blogpro-manifest.json"
            installed_ver = "?"
            if manifest_path.is_file():
                try:
                    m = json.loads(manifest_path.read_text(encoding="utf-8"))
                    installed_ver = m.get("version", "?")
                except Exception:
                    pass
            print(f"  ✅ {plat['display']:20s} v{installed_ver}  {skill_dir}")
    else:
        print("  （無）")


# ══════════════════════════════════════════════════════
#  update — 更新到最新版本
# ══════════════════════════════════════════════════════

def cmd_update(args):
    print("🔄 blog-pro-max 更新")
    print(f"   目前版本：v{VERSION}")
    print()

    # Collect all installed platforms (local + global)
    local_found = _find_installed_platforms(Path.cwd())
    global_found = _find_installed_platforms(Path.home())

    all_found = []
    for key, plat, skill_dir in local_found:
        all_found.append((key, skill_dir, False))
    for key, plat, skill_dir in global_found:
        all_found.append((key, skill_dir, True))

    if not all_found:
        print("  ℹ️  未偵測到任何已安裝的平台。請先執行 blogpro init。")
        return

    print(f"  偵測到 {len(all_found)} 個已安裝平台，開始更新...")
    print()

    success = failed = 0
    for key, skill_dir, is_global in all_found:
        target_root = Path.home() if is_global else Path.cwd()
        if install_for_platform(key, target_root, is_global):
            success += 1
        else:
            failed += 1

    print()
    print(f"✅ 更新完成：{success} 個平台成功" + (f"，{failed} 個失敗" if failed else ""))
    print(f"   版本：v{VERSION}")
    if failed:
        sys.exit(1)


# ══════════════════════════════════════════════════════
#  CLI 主入口
# ══════════════════════════════════════════════════════

def main():
    platform_choices = list(PLATFORMS.keys()) + ["all"]

    parser = argparse.ArgumentParser(
        prog="blogpro",
        description="blog-pro-max CLI — 自動化 SEO 內容創作與 AI assistant skill 管理",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="可用指令")

    # ── init ──
    p_init = subparsers.add_parser(
        "init", help="將 skill 注入到 AI assistant",
        epilog=_build_platform_list(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p_init.add_argument(
        "--ai", required=True, choices=platform_choices,
        metavar="ASSISTANT",
        help="目標 AI assistant（或 all）",
    )
    p_init.add_argument("--global", dest="global_install", action="store_true", help="安裝到使用者家目錄（全域）")
    p_init.add_argument("--target", default=None, help="自訂安裝根目錄")
    p_init.add_argument("--offline", action="store_true", help="跳過下載，使用本地資源")

    # ── uninstall ──
    p_uninstall = subparsers.add_parser(
        "uninstall", help="移除已安裝的 skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p_uninstall.add_argument(
        "--ai", default=None, choices=platform_choices,
        metavar="ASSISTANT",
        help="指定移除的平台（留空則自動偵測）",
    )
    p_uninstall.add_argument("--global", dest="global_install", action="store_true", help="從全域安裝移除")

    # ── versions ──
    subparsers.add_parser("versions", help="顯示版本資訊與已安裝平台")

    # ── update ──
    subparsers.add_parser("update", help="更新所有已安裝平台到最新版本")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args)
    elif args.command == "uninstall":
        cmd_uninstall(args)
    elif args.command == "versions":
        cmd_versions(args)
    elif args.command == "update":
        cmd_update(args)
    else:
        parser.print_help()
        sys.exit(1)


def _build_platform_list():
    lines = ["", "支援的 AI assistants：", ""]
    for key, plat in PLATFORMS.items():
        lines.append(f"  blogpro init --ai {key:15s}  # {plat['display']}")
    lines.append(f"  blogpro init --ai {'all':15s}  # All assistants")
    lines.append("")
    lines.append("全域安裝：")
    lines.append("  blogpro init --ai claude --global   # Install to ~/.claude/skills/")
    lines.append("  blogpro init --ai cursor --global   # Install to ~/.cursor/skills/")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
