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
VERSION = "1.0.33"
VERSION_HISTORY = [
    {"version": "1.0.33", "date": "2026-03-31", "changes": "Script Mode 補齊 6 個段落級專家（發散、問題、迷因、插話、插畫、唱反調），與 Skill Mode 輸出的 12 個區塊一致；移除已棄用的 Pygments 依賴（requirements.txt、pyproject.toml、Skill 安裝產生的 requirements）；刪除根目錄 scripts/ 與 templates/ 後確認三種模式（Package、Skill、Script）皆不受影響"},
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
    "gemini": {
        "display": "Gemini CLI",
        "root": ".gemini",
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
        "支援 SEO 專業風格、Max 個人風格、Facebook 貼文、LINE 訊息等多種模板，"
        "內建風格檢查器、Markdown 轉 HTML，"
        "以及多模板管理系統。"
    )
    if platform_key == "claude":
        desc = (
            "Blog content intelligence. "
            "自動化 SEO 內容創作與部落格文章生成。"
            "4 種寫作模板（SEO 專業 / Max 個人風格 / FB 貼文 / LINE 訊息）、"
            "風格檢查器、MD→HTML 轉換。"
            "Actions: generate, check, convert, plan, write, review, "
            "optimize SEO, create blog posts, analyze style."
        )
    return "\n".join([
        "---",
        f"name: {SKILL_NAME}",
        f"version: {VERSION}",
        f'description: "{desc}"',
        "---",
    ])


def _build_skill_content(platform_key, script_prefix):
    fm = _build_frontmatter(platform_key)
    writing_style = (RESOURCE_ROOT / "writing-style.md").read_text(encoding="utf-8")
    max_template = (RESOURCE_ROOT / "templates" / "max-personal-style.md").read_text(encoding="utf-8")
    seo_template = (RESOURCE_ROOT / "templates" / "blog-skill-content.md").read_text(encoding="utf-8")
    fb_template = (RESOURCE_ROOT / "templates" / "fb-post-style.md").read_text(encoding="utf-8")
    line_template = (RESOURCE_ROOT / "templates" / "line-message-style.md").read_text(encoding="utf-8")

    return f"""{fm}

# Blog Pro Max — 自動化 SEO 內容創作與部落格文章生成

## 概述

blog-pro-max 是一套自動化部落格內容生成工具，支援：

- **SEO 專業風格**：精簡、直接、關鍵字最佳化
- **Max 個人風格**：心情筆記、生活化敘事、自我反思
- **Facebook 貼文風格**：口語化、純文字、「▋ 」標題、社群互動
- **LINE 訊息風格**：簡短親切、純文字、好朋友分享
- **風格檢查器**：自動驗證禁止詞彙、標題層級、SEO 規則、標點
- **MD→HTML 轉換**：生成後自動輸出 WordPress 相容 HTML

## 觸發方式

### Workflow Mode（Slash Command）

支援平台：Kiro、GitHub Copilot、Roo Code、KiloCode

使用者輸入 `/blog-pro-max` 開頭的指令時，解析並執行對應的文章生成任務。

**指令格式：**

```
/blog-pro-max 寫一篇[主題關鍵字]文章,受眾[目標讀者],以[風格名稱]風格
```

**範例：**

```
/blog-pro-max 寫一篇[失去才懂珍惜]文章,受眾[一般讀者],以作家Max風格
/blog-pro-max 寫一篇[Python 非同步入門]文章,受眾[中階開發者],以SEO風格
/blog-pro-max 寫一篇[遠端工作的真實面貌]文章,受眾[上班族],以FB風格
/blog-pro-max 寫一篇[時間管理心得]文章,受眾[大學生],以LINE風格
/blog-pro-max 寫一篇[遠端工作的真實面貌]文章
/blog-pro-max 幫我取標題 output/my-article.md
/blog-pro-max 檢查風格 output/my-article.md
/blog-pro-max 列出模板
/blog-pro-max 專案狀態
```

**解析規則：**

當使用者輸入 `/blog-pro-max` 時，AI 應依以下規則解析：

1. `[...]` 中的第一個值 → `--keyword`（核心關鍵字）
2. `受眾[...]` → `--audience`（目標讀者），未指定則預設 `30-45 歲知識工作者`
3. 風格關鍵字對應：
   - `作家Max風格` / `Max風格` / `心情筆記` / `日記` / `日記風格` / `心情` / `感受` → `--template max-personal-style`
   - `SEO風格` / `專業風格` / `部落格風格` / `部落客風格` / `實用文章` / `技巧` / `教學` → `--template blog-skill-content`（預設）
   - `FB風格` / `Facebook風格` / `臉書風格` / `社群貼文` / `貼文` / `分享` / `社群` → `--template fb-post-style`
   - `LINE風格` / `LINE訊息` / `賴風格` / `短訊` / `聊天` / `輕鬆` → `--template line-message-style`
   - 若無法識別風格，預設使用 `blog-skill-content`，並提示使用者：「未識別風格 [xxx]，改用 SEO 預設模板。」
4. `字數[N]` → `--word-count N`
5. `幫我取標題 <路徑>` → 讀取文章後呼叫「部落格標題專家」產出 4 個標題建議
6. `幫我生成封面 <路徑>` → 讀取文章後呼叫「封面提示詞專家」產出 3 組 AI 繪圖提示詞
7. `全科檢查 <路徑>` → 依序執行邏輯與事實專家、深度與結構專家、讀者視角專家
8. `檢查邏輯 <路徑>` → 執行「邏輯與事實專家」
9. `檢查結構 <路徑>` → 執行「深度與結構專家」
10. `檢查讀者 <路徑>` → 執行「讀者視角專家」
11. `分析趨勢 <路徑>` → 執行「時事趨勢專家」
12. `插話建議 <路徑>` → 執行「插話專家」，針對每個段落提供舉例說明
13. `段落插畫 <路徑>` → 執行「插畫專家」，針對每個段落產出 3 組風格的 AI 圖片提示詞
14. `唱反調 <路徑>` → 執行「唱反調專家」，針對每個段落提出反駁觀點
15. `發散思考 <路徑>` → 執行「發散專家」，針對每個段落延伸相關話題與創意觀點
16. `提出問題 <路徑>` → 執行「問題專家」，針對每個段落提出多個相關問題
17. `迷因建議 <路徑>` → 執行「迷因專家」，針對每個段落提出迷因/梗圖/幽默相關關鍵字
18. `檢查風格 <路徑>` → 執行 `style_checker.py`
16. `列出模板` → 執行 `core.py templates`
17. `專案狀態` → 執行 `core.py status`

### 參考資料生成模式（Reference Material Mode）

**觸發條件（以下任一即觸發）：**
- 訊息含「以下是我收集的資料」、「根據以下資料」、「這是參考資料」、「以下是參考資料」等關鍵句
- 訊息結構為：[一段貼上的原始素材] + [生成指令，例如「請根據以上資料寫一篇文章」、「整理成一篇部落格文章」]
- 使用者明確說「參考資料模式」

**⚠️ 重要：此模式以貼入的原始素材為內容基礎，重新生成一篇完整文章，並執行所有後處理步驟。**

**AI 執行步驟：**

1. 識別並提取使用者貼入的參考資料區塊（新聞、筆記、條列重點、網頁擷取文字等）
   - **提取邏輯**：從觸發關鍵句開始，到下一個明確指令句（以「請」「幫」「寫」開頭）或訊息結尾之間，視為參考資料
   - **若超過 5000 字**：只使用前 5000 字，並提示使用者：「⚠️ 參考資料過長已截斷至 5000 字，若需完整處理請分段輸入。」
   - **若不足 100 字**：提示使用者：「⚠️ 參考資料過少（＜100 字），建議提供更多內容以生成完整文章。」
2. 從生成指令中提取：
   - 受眾（未指定 → 預設 `30-45 歲知識工作者`）
   - 風格（未指定 → 預設 `blog-skill-content` SEO 標準模板）
3. 若未明確指定關鍵字，從參考資料中**自動推斷核心主題**作為關鍵字，推斷後向使用者確認：
   「推斷主題為「[推斷的主題]」，若需更換請直接輸入正確關鍵字，或輸入「確認」繼續。」
4. 以參考資料為內容基礎，依照選定模板的格式與風格要求生成一篇完整文章
5. 文章生成後，依序逐一完整輸出以下全部 12 個區塊（**不得省略任何一個，不得在中途停止**）：

   **⚠️ 警告：必須完整輸出以下全部 12 個區塊。輸出三維度審稿後不代表完成，必須繼續輸出第 4-12 項。**

   - **第 1 項（必須輸出）：** `## 🔬 邏輯與事實專家審查報告`
   - **第 2 項（必須輸出）：** `## 📐 深度與結構專家審查報告`
   - **第 3 項（必須輸出）：** `## 👁️ 讀者視角專家審查報告`
   - **第 4 項（必須輸出，不得省略）：** `## 📰 時事趨勢分析報告`（含趨勢關聯、切入角度、關鍵字標籤、改寫示範）
   - **第 5 項（必須輸出，不得省略）：** `## 📝 推薦標題選項`（含表格與英文 WordPress permalink）
   - **第 6 項（必須輸出，不得省略）：** `## 🎨 推薦封面提示詞`（含 3 組英文 prompt：寫實攝影風、插畫風、極簡設計風）
   - **第 7 項（必須輸出，不得省略）：** `## 🌀 發散專家建議`（針對每個 H2 段落提供 3 個延伸方向與後續文章題目）
   - **第 8 項（必須輸出，不得省略）：** `## ❓ 問題專家建議`（針對每個 H2 段落提出 3-5 個讀者可能浮現的疑問）
   - **第 9 項（必須輸出，不得省略）：** `## 😂 迷因專家建議`（針對每個 H2 段落提出迷因關鍵字、梗圖場景、輕鬆開場句）
   - **第 10 項（必須輸出，不得省略）：** `## 💬 插話專家建議`（針對每個 H2 段落提供一個具體舉例說明，附建議插入位置）
   - **第 11 項（必須輸出，不得省略）：** `## 🖼️ 插畫專家建議`（針對每個 H2 段落產出 3 組風格 AI 圖片提示詞：寫實攝影風、插畫風、極簡圖示風）
   - **第 12 項（必須輸出，不得省略）：** `## 🔴 唱反調專家報告`（針對每個 H2 段落提出反駁觀點、理由，並建議如何回應）

   **📋 若因 token 限制無法輸出全部 12 項，請依以下優先級處理：**
   - 優先級 1（必須完成）：文章本文 + 第 1-3 項（三維度審稿）
   - 優先級 2（盡力完成）：第 4-6 項（時事趨勢 / 標題 / 封面）
   - 優先級 3（條件完成）：第 7-12 項（延伸 / 插話 / 插畫 / 反調）

   未完成時，**必須在最後明確列出**：
   ```
   ⚠️ 以下區塊因 token 限制未能完成，請輸入「繼續」接續輸出：
   - 第 N 項：[區塊名稱]
   ```

6. 所有報告輸出完畢後，**必須輸出以下完成報告**：

   ```
   ✅ 輸出完成：12/12 個區塊
   📁 準備儲存至：output/關鍵字.md + .html
   ```

   然後詢問使用者以下問題：

   > 「文章已依據參考資料生成完畢。請問要如何儲存？
   > 1. 只存這個風格（output/關鍵字.md + .html）
   > 2. 生成所有風格，各存一份（SEO、Max、FB、LINE，共 4 組 .md + .html）」

7. 依使用者選擇儲存對應檔案到工作目錄的 `output/` 資料夾。
   **儲存的 `.md` 必須包含本次對話中所有已輸出的內容**（文章本文 + 全部 12 個專家區塊），不得只存文章本文。

### 內部角色：部落格標題專家（blog-title-writer）

觸發方式：`幫我取標題`、文章生成後自動執行、參考資料生成模式自動執行

此角色會分析文章內容，根據受眾偏好產出 4 個風格不同的標題建議：

- **直述型**：直接說明文章主題
- **提問型**：用問句引發好奇心
- **數字型**：帶數字的清單式標題
- **情感型**：引發情感共鳴

**輸出格式（必須嚴格遵守）：**

**⚠️ WordPress Permalink 規則：使用有意義的英文單字，不使用中文拼音。**
例如：流暢度 → `/fluency`，遠端工作 → `/remote-work`，時間管理 → `/time-management`

```markdown
---

## 📝 推薦標題選項

> 以下由「部落格標題專家」自動產出，請人工選擇最適合的標題。

| # | 標題 | WordPress Permalink |
|---|------|---------------------|
| 1 | 直述型標題範例 | `/direct-title-example` |
| 2 | 提問型標題範例？ | `/question-title-example` |
| 3 | 5 個數字型標題技巧 | `/5-numbered-title-tips` |
| 4 | 情感型標題範例 | `/emotional-title-example` |
```

### 內部角色：封面提示詞專家（cover-prompt-writer）

觸發方式：`幫我生成封面`、文章生成後自動執行、參考資料生成模式自動執行

此角色會分析文章內容與主題，產出 3 組適合 AI 繪圖工具的封面圖片提示詞：

- **寫實攝影風**：適合專業、商務類文章
- **插畫風**：適合生活、故事類文章
- **極簡設計風**：適合科技、教學類文章

每組提示詞包含：
- **英文 Prompt**：可直接貼到 Midjourney、DALL-E、Stable Diffusion
- **中文說明**：一句話描述圖片意境

**輸出格式（必須嚴格遵守）：**

```markdown
---

## 🎨 推薦封面提示詞

> 以下由「封面提示詞專家」自動產出，可直接貼到 Midjourney、DALL-E 或 Stable Diffusion 使用。

### 1. 寫實攝影風

**Prompt:**

```
A professional photo of ... , soft natural lighting, shallow depth of field --ar 16:9
```

*適合專業、商務類文章的封面*

### 2. 插畫風
...

### 3. 極簡設計風
...
```

### 內部角色：邏輯與事實專家（logic-fact-checker）

觸發方式：`檢查邏輯`、`全科檢查`、文章生成後自動執行、參考資料生成模式自動執行

此角色嚴格校對文章的硬傷，包括：

- **數據錯誤**：引用的數據、百分比、年份是否合理且正確
- **邏輯矛盾**：論點是否前後矛盾、因果關係是否成立
- **錯別字與用詞錯誤**：錯字、同音字誤用、語法不通
- **來源可信度**：引用的觀點是否缺乏根據，是否有 AI 幻覺

### 內部角色：深度與結構專家（depth-structure-reviewer）

觸發方式：`檢查結構`、`全科檢查`、文章生成後自動執行、參考資料生成模式自動執行

此角色分析文章的內容廣度與結構品質：

- **遺漏面向**：讀者可能感興趣但文章未涵蓋的關鍵角度
- **段落轉折**：段落之間的銜接是否自然，是否有突兀的跳躍
- **論述深度**：哪些段落太淺薄、缺乏具體例子
- **結構平衡**：各段落篇幅比例是否合理，重點是否突出

### 內部角色：讀者視角專家（reader-perspective-reviewer）

觸發方式：`檢查讀者`、`全科檢查`、文章生成後自動執行、參考資料生成模式自動執行

此角色從受眾角度評估可讀性與吸引力：

- **口吻適配**：語氣是否適合目標受眾
- **易讀性**：術語是否過於艱深、概念是否有做解釋
- **注意力留存**：哪些段落可能讓讀者分心或跳過
- **情感共鳴**：開頭是否吸引人、結尾是否有力

### 三維度審稿專家輸出格式（必須嚴格遵守）

每位專家的輸出都使用相同格式，包含問題點、修改建議、修改前後對比。
**禁止使用 Markdown 表格**，改用編號條列，方便使用者直接複製給 AI 進行下一輪修改：

```markdown
---

## 🔬 邏輯與事實專家審查報告（或 📐 深度與結構、👁️ 讀者視角）

> 以下由「XX 專家」自動產出，含問題點、修改建議與修改前後對比。

**1. 第 3 段數據缺乏來源**
- 修改建議：補充來源或移除
- 原文：根據研究顯示...
- 修改後：根據 2024 年 Gartner 報告...

**2. 第 5 段與第 2 段矛盾**
- 修改建議：統一論述
- 原文：遠端工作效率更高
- 修改後：遠端工作在特定條件下效率更高
```

### 內部角色：時事趨勢專家（trend-scout）

觸發方式：`分析趨勢`、文章生成後自動執行、參考資料生成模式自動執行

此角色將文章內容與當前社會熱議話題建立關聯，讓文章更有時效性與傳播力。

分析包含四個結構化區塊：

1. **🔗 趨勢關聯分析**：點出文章與哪些時事相關、關聯的合理性、討論熱度
2. **🎯 切入角度建議**：提供 2-3 個不同的時事發揮方向
3. **🏷️ 關鍵字與標籤優化**：高流量搜尋關鍵字 + 社群 Hashtag（可直接複製）
4. **✍️ 內容改寫示範**：選取原文一段，示範加入時事元素的修改前後對比

**輸出格式（必須嚴格遵守）：**

```markdown
---

## 📰 時事趨勢分析報告

> 以下由「時事趨勢專家」自動產出，協助文章與當前趨勢建立連結。

### 🔗 趨勢關聯分析

文章主題「XX」與近期「YY 事件」有直接關聯...
討論熱度：高

### 🎯 切入角度建議

1. **角度 A**：適合科技類品牌。核心訴求：...
2. **角度 B**：適合生活類讀者。核心訴求：...

### 🏷️ 關鍵字與標籤優化

**搜尋關鍵字**：關鍵字1（↑上升）、關鍵字2、關鍵字3...
**社群 Hashtag**：#tag1 #tag2 #tag3 #tag4 #tag5

### ✍️ 內容改寫示範

**原文：** 原始段落...
**改寫：** 加入時事元素的新版本...
**策略：** 說明為什麼這樣改更好...
```

### 內部角色：插話專家（example-inserter）

觸發方式：`插話建議`

此角色針對文章的每一個 H2 段落，提供一個具體的舉例說明，幫助讀者更容易理解段落的核心概念。

**輸出格式（必須嚴格遵守）：**

```markdown
---

## 💬 插話專家建議

> 以下由「插話專家」自動產出，每個段落附上舉例說明，可直接插入對應段落。

### 段落：{{H2 子標題}}

**建議插入的舉例：**

舉例說明內容（以「舉個例子來說，」或「就好比說，」開頭，100 字以內）

**建議插入位置：** 段落第 N 句之後
```

（每個 H2 段落各輸出一組，格式相同）

### 內部角色：插畫專家（illustration-prompter）

觸發方式：`段落插畫`

此角色針對文章的每一個 H2 段落，產出 3 組風格不同的 AI 圖片生成提示詞，作為該段落的示意圖使用。

每組提示詞風格：
- **寫實攝影風**：照片感，適合真實場景呈現
- **插畫風**：溫暖手繪感，適合生活或故事類段落
- **極簡圖示風**：乾淨的線條圖形，適合說明步驟或概念

**輸出格式（必須嚴格遵守）：**

```markdown
---

## 🖼️ 插畫專家建議

> 以下由「插畫專家」自動產出，每個段落提供 3 組風格的 AI 圖片提示詞。

### 段落：{{H2 子標題}}

**1. 寫實攝影風**
Prompt: A realistic photo of ..., natural lighting, --ar 16:9

**2. 插畫風**
Prompt: A warm hand-drawn illustration of ..., soft colors, flat style --ar 16:9

**3. 極簡圖示風**
Prompt: A minimal icon illustration of ..., clean lines, white background --ar 1:1
```

（每個 H2 段落各輸出一組，格式相同）

### 內部角色：唱反調專家（devil-advocate）

觸發方式：`唱反調`

此角色針對文章每一個 H2 段落的核心論點，提出反駁觀點或反例，幫助作者預先思考讀者的疑問與挑戰，強化文章的說服力。

**輸出格式（必須嚴格遵守）：**

```markdown
---

## 🔴 唱反調專家報告

> 以下由「唱反調專家」自動產出，針對每個段落提出反駁，供作者參考強化論點。

### 段落：{{H2 子標題}}

**反駁觀點：** 一句話提出反面立場

**理由：** 簡短說明為什麼這個論點可能不成立（2-3 句話）

**建議回應：** 作者可以如何在文章中預先化解這個質疑（1-2 句話）
```

（每個 H2 段落各輸出一組，格式相同）

### 內部角色：發散專家（divergent-thinker）

觸發方式：`發散思考`

此角色針對文章每一個 H2 段落的核心概念，運用想像力與獨創力，從該概念延伸到相關話題、跨領域聯想或意想不到的切入角度，幫助作者發現更多寫作方向與延伸素材。

**輸出格式（必須嚴格遵守）：**

```markdown
---

## 🌀 發散專家建議

> 以下由「發散專家」自動產出，針對每個段落提供創意延伸話題，供作者參考發展後續內容。

### 段落：{{H2 子標題}}

**延伸方向 1：** 與 {{相關領域/話題}} 的連結 — 一句話說明如何延伸

**延伸方向 2：** 跨領域聯想 — 例如把這個概念套用在 {{完全不同的情境}} 上

**延伸方向 3：** 更深一層 — 如果追問「為什麼」或「然後呢」，可以發展到哪裡

**潛在後續文章題目：** 根據上述延伸，建議 1-2 個可以獨立成篇的相關主題
```

（每個 H2 段落各輸出一組，格式相同）

### 內部角色：問題專家（question-raiser）

觸發方式：`提出問題`

此角色針對文章每一個 H2 段落，提出多個讀者可能浮現的疑問或深入探討的問題，幫助作者發現文章的論述缺口，也可作為 FAQ、留言互動或後續文章的靈感來源。

**輸出格式（必須嚴格遵守）：**

```markdown
---

## ❓ 問題專家建議

> 以下由「問題專家」自動產出，針對每個段落提出讀者可能的疑問，供作者補充說明或延伸討論。

### 段落：{{H2 子標題}}

1. {{問題 1}}
2. {{問題 2}}
3. {{問題 3}}
4. {{問題 4}}
5. {{問題 5}}
```

（每個 H2 段落各輸出 3-5 個問題，格式相同）

### 內部角色：迷因專家（meme-suggester）

觸發方式：`迷因建議`

此角色針對文章每一個 H2 段落，提出與段落內容相關的迷因、梗圖或幽默元素關鍵字，幫助作者找到輕鬆有趣的切入點，讓嚴肅的內容更容易讓讀者接受與分享。

**輸出格式（必須嚴格遵守）：**

```markdown
---

## 😂 迷因專家建議

> 以下由「迷因專家」自動產出，針對每個段落提出幽默/迷因元素，幫助讀者在輕鬆氛圍中吸收內容。

### 段落：{{H2 子標題}}

**迷因關鍵字：** 關鍵字1、關鍵字2、關鍵字3

**梗圖場景：** 一句話描述可以做成梗圖的場景（例：「當你說要開始XX，結果發現YY」）

**輕鬆開場句：** 用幽默方式重新描述這個段落的核心概念（一句話，可直接用在文章或社群貼文）
```

（每個 H2 段落各輸出一組，格式相同）

**AI 執行步驟：**

收到 `/blog-pro-max` 指令後，依以下判斷執行：

**⚠️ 輸出路徑規則（所有模式通用）：**
- 所有產出的 .md 和 .html 檔案，必須儲存在**使用者的工作目錄**（即使用者執行 Gemini CLI 的目錄）下的 `output/` 資料夾
- 絕對不能存到 Skill 安裝目錄（例如 `.gemini/skills/blog-pro-max/output/`）
- 使用者的工作目錄可用環境變數 `$PWD` 或 `$(pwd)` 取得

**當 AI 具備執行腳本能力時（Claude Code、Cursor、Gemini CLI 等）：**

1. 解析使用者意圖，提取關鍵字、受眾、風格、字數
2. 先確認使用者的工作目錄，並建立 `output/` 資料夾（若不存在）：
   ```bash
   mkdir -p output
   ```
3. 執行對應的 Python 腳本，明確使用 `--output` 參數指定輸出到使用者工作目錄：
   ```bash
   python {script_prefix}scripts/content_research.py --keyword "關鍵字" --audience "受眾" --template 模板名稱
   ```
   > 腳本預設輸出到執行時的當前工作目錄下的 `output/`，因此請確認是在使用者的專案根目錄執行，而非 Skill 目錄。
4. 腳本會自動完成：風格檢查 → 三維度審稿（邏輯/結構/讀者）→ 時事趨勢分析 → 標題建議 → 封面提示詞 → .html 轉換
5. 回報結果與檔案位置（`./output/關鍵字.md` 與 `./output/關鍵字.html`，路徑相對於使用者工作目錄）

**當 AI 不具備執行腳本能力時（一般聊天模式等）：**

1. 解析使用者意圖，提取關鍵字、受眾、風格、字數
2. 使用自身 LLM 能力，依照選定模板的格式與風格要求生成文章
3. 套用風格規範，**優先級如下（高→低）**：
   1. 使用者明確指令（若有，例如「請使用較口語的語氣」）
   2. 選定模板的風格指南（例：fb-post-style 的社群語氣規則）
   3. `writing-style.md` 全域規則（禁用詞、標題層級、標點等）
   - 模板風格與 writing-style.md 衝突時，以模板為準，但禁用詞規則永遠適用
4. 依照下列順序，**逐一完整輸出所有 12 個區塊，不得省略任何一個，不得在中途停止**：

   **⚠️ 警告：必須完整輸出以下全部 12 個區塊。輸出三維度審稿後不代表完成，必須繼續輸出第 4-12 項。**

   **第 1 項（必須輸出）：**
   `## 🔬 邏輯與事實專家審查報告`

   **第 2 項（必須輸出）：**
   `## 📐 深度與結構專家審查報告`

   **第 3 項（必須輸出）：**
   `## 👁️ 讀者視角專家審查報告`

   **第 4 項（必須輸出，不得省略）：**
   `## 📰 時事趨勢分析報告`（含趨勢關聯、切入角度、關鍵字標籤、改寫示範）

   **第 5 項（必須輸出，不得省略）：**
   `## 📝 推薦標題選項`（含表格與英文 WordPress permalink）

   **第 6 項（必須輸出，不得省略）：**
   `## 🎨 推薦封面提示詞`（含 3 組英文 prompt：寫實攝影風、插畫風、極簡設計風）

   **第 7 項（必須輸出，不得省略）：**
   `## 🌀 發散專家建議`（針對每個 H2 段落提供 3 個延伸方向與後續文章題目）

   **第 8 項（必須輸出，不得省略）：**
   `## ❓ 問題專家建議`（針對每個 H2 段落提出 3-5 個讀者可能浮現的疑問）

   **第 9 項（必須輸出，不得省略）：**
   `## 😂 迷因專家建議`（針對每個 H2 段落提出迷因關鍵字、梗圖場景、輕鬆開場句）

   **第 10 項（必須輸出，不得省略）：**
   `## 💬 插話專家建議`（針對每個 H2 段落提供一個具體舉例說明，附建議插入位置）

   **第 11 項（必須輸出，不得省略）：**
   `## 🖼️ 插畫專家建議`（針對每個 H2 段落產出 3 組風格 AI 圖片提示詞：寫實攝影風、插畫風、極簡圖示風）

   **第 12 項（必須輸出，不得省略）：**
   `## 🔴 唱反調專家報告`（針對每個 H2 段落提出反駁觀點、理由，並建議如何回應）

   **📋 若因 token 限制無法輸出全部 12 項，請依以下優先級處理：**
   - 優先級 1（必須完成）：文章本文 + 第 1-3 項（三維度審稿）
   - 優先級 2（盡力完成）：第 4-6 項（時事趨勢 / 標題 / 封面）
   - 優先級 3（條件完成）：第 7-12 項（延伸 / 插話 / 插畫 / 反調）

   未完成時，**必須在最後明確列出**：
   ```
   ⚠️ 以下區塊因 token 限制未能完成，請輸入「繼續」接續輸出：
   - 第 N 項：[區塊名稱]
   ```

5. 全部 12 個區塊輸出完畢後，**必須輸出以下完成報告**：

   ```
   ✅ 輸出完成：12/12 個區塊
   📁 準備儲存至：output/關鍵字.md + .html
   ```

   然後詢問使用者以下問題：

   > 「文章已生成完畢。請問要如何儲存？
   > 1. 只存這個風格（output/關鍵字.md + .html）
   > 2. 生成所有風格，各存一份（SEO、Max、FB、LINE，共 4 組 .md + .html）」

6. 若選擇「1. 只存這個風格」：
   - 儲存 `output/關鍵字.md`（路徑相對於使用者工作目錄，不是 Skill 目錄）
   - **`.md` 檔案必須包含本次對話中輸出的完整內容**，依序為：
     1. 文章本文
     2. `## 🔬 邏輯與事實專家審查報告`
     3. `## 📐 深度與結構專家審查報告`
     4. `## 👁️ 讀者視角專家審查報告`
     5. `## 📰 時事趨勢分析報告`
     6. `## 📝 推薦標題選項`
     7. `## 🎨 推薦封面提示詞`
     8. `## 🌀 發散專家建議`
     9. `## ❓ 問題專家建議`
     10. `## 😂 迷因專家建議`
     11. `## 💬 插話專家建議`
     12. `## 🖼️ 插畫專家建議`
     13. `## 🔴 唱反調專家報告`
   - 同時儲存 `output/關鍵字.html`：
     - 若 AI 具備執行腳本能力，執行 `python {script_prefix}scripts/output_md2html.py output/關鍵字.md output/關鍵字.html`
     - 若 AI 不具備執行腳本能力，直接將 .md 內容轉換為 HTML（以 `<h1>`, `<h2>`, `<p>`, `<ul>` 等基本 HTML 標籤組成）並寫入 `output/關鍵字.html`

7. 若選擇「2. 生成所有風格」：
   - 依序以 4 個模板重新生成文章，各自附加標題建議與封面提示詞，儲存為：
     - `output/關鍵字-seo.md` + `output/關鍵字-seo.html`（blog-skill-content）
     - `output/關鍵字-max.md` + `output/關鍵字-max.html`（max-personal-style）
     - `output/關鍵字-fb.md` + `output/關鍵字-fb.html`（fb-post-style）
     - `output/關鍵字-line.md` + `output/關鍵字-line.html`（line-message-style）
   - 所有路徑均相對於使用者工作目錄
   - .html 的產生方式同第 6 步（腳本優先，不能執行腳本時直接轉換）

### Script Mode（直接執行）

| 使用情境 | 指令 |
|---|---|
| 生成 SEO 文章 | `python {script_prefix}scripts/content_research.py --keyword "關鍵字"` |
| 生成 Max 風格文章 | `python {script_prefix}scripts/content_research.py --keyword "主題" --template max-personal-style` |
| 生成 FB 貼文 | `python {script_prefix}scripts/content_research.py --keyword "主題" --template fb-post-style` |
| 生成 LINE 訊息 | `python {script_prefix}scripts/content_research.py --keyword "主題" --template line-message-style` |
| 僅檢查風格 | `python {script_prefix}scripts/style_checker.py output/文章.md "關鍵字"` |
| 預覽 prompt（不呼叫 API） | `python {script_prefix}scripts/content_research.py --keyword "關鍵字" --dry-run` |
| 查看專案狀態 | `python {script_prefix}scripts/core.py status` |
| 列出可用模板 | `python {script_prefix}scripts/core.py templates` |
| 轉換 MD→HTML | `python {script_prefix}scripts/output_md2html.py input.md output.html` |

## 前置需求

需要 Python 3.10+ 與以下套件：

```bash
pip install -r {script_prefix}requirements.txt
```

## 參數說明

| 參數 | 說明 | 預設值 |
|---|---|---|
| `--keyword` | 核心關鍵字（必填） | — |
| `--audience` | 目標讀者 | 30-45 歲知識工作者 |
| `--word-count` | 目標字數 | 1200 |
| `--language` | 輸出語言 | zh-TW |
| `--template` | 寫作風格模板 | blog-skill-content |
| `--model` | LLM 模型 | gpt-4o |
| `--output` | 輸出檔案路徑 | output/{{keyword}}.md |
| `--dry-run` | 預覽 prompt 不呼叫 API | — |

## 可用模板

| 模板 | 說明 | 輸出格式 |
|---|---|---|
| `blog-skill-content` | SEO 部落格文章（專業、精簡、直接） | Markdown |
| `max-personal-style` | Max 個人風格（心情筆記、生活化、自我反思） | Markdown |
| `fb-post-style` | Facebook 貼文（口語化、▋ 標題、社群互動） | 純文字 |
| `line-message-style` | LINE 訊息（簡短、親切、好朋友分享） | 純文字 |

## API 金鑰設定

在專案根目錄建立 `.env` 檔案：

```
# 推薦：GitHub PAT（免費）
GITHUB_TOKEN=ghp_your-token-here

# 或：OpenAI API Key
OPENAI_API_KEY=sk-your-key-here
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
    skill_dir = target_root / plat["root"] / plat["sub"]
    skill_file = skill_dir / plat["filename"]

    if global_install:
        prefix = str(skill_dir).replace("\\", "/") + "/"
    else:
        prefix = plat["root"] + "/" + plat["sub"] + "/"

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
        targets = list(PLATFORMS.keys())
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
    for key, plat in PLATFORMS.items():
        skill_dir = search_root / plat["root"] / plat["sub"]
        manifest = skill_dir / ".blogpro-manifest.json"
        if manifest.is_file() or (skill_dir / plat["filename"]).is_file():
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
