# blog-pro-max

自動化 SEO 內容創作與部落格文章生成工具。支援一鍵將寫作 Skill 注入到 18 種 AI 編輯器與 Assistant。

## 功能亮點

- **AI 驅動寫作**：根據關鍵字自動進行內容研究並生成 SEO 最佳化的部落格文章。
- **流式 AI 生成**：透過 `quick_generate.py` 支援實時文字輸出，無需等待完整內容生成即可開始閱讀。
- **多 LLM 支援**：Script Mode 支援 OpenAI GPT 與 GitHub Models；快速生成模式額外支援 Google Gemini 與 Azure OpenAI。
- **品牌風格一致性**：自動套用品牌寫作風格規範（`writing-style.md`）。
- **內建風格檢查器**：自動驗證產出內容是否符合排版與語氣規範。
- **多樣化模板**：支援多種寫作風格（SEO 專業 / Max 個人風格 / FB 貼文 / LINE 訊息）。
- **三維度審稿專家**：邏輯與事實、深度與結構、讀者視角三位專家審查，附問題點與修改前後對比。
- **時事趨勢專家**：透過 DuckDuckGo 搜尋當前時事後注入 LLM，分析文章與真實趨勢的關聯，提供切入角度、高流量關鍵字/Hashtag、內容改寫示範（需安裝 `ddgs`，詳見 [FAQ](docs/faq.md)）。
- **標題專家**：產出 4 個風格不同的標題建議（含英文 WordPress permalink），附加到輸出檔案供人工選擇。
- **封面提示詞專家**：產出 3 組 AI 繪圖提示詞（Midjourney / DALL-E / Stable Diffusion），附加到輸出檔案。
- **插話專家**：針對每個段落提供一個具體舉例說明，幫助讀者更容易理解核心概念。
- **插畫專家**：針對每個段落產出 3 組風格（寫實攝影、插畫、極簡圖示）的 AI 圖片提示詞，作為段落示意圖。
- **唱反調專家**：針對每個段落提出反駁觀點與建議回應，幫助作者預先化解讀者質疑、強化說服力。
- **發散專家**：針對每個段落運用想像力與獨創力，從一個概念延伸到相關話題與跨領域聯想，發現更多寫作方向。
- **問題專家**：針對每個段落提出 3-5 個讀者可能浮現的疑問，幫助作者發現論述缺口，也可作為 FAQ 靈感。
- **迷因專家**：針對每個段落提出迷因、梗圖與幽默元素關鍵字，讓嚴肅內容更輕鬆有趣、容易分享。
- **AI Skill 注入**：一鍵將 Prompt 與工具鏈注入到 Claude Code, Cursor, GitHub Copilot 等 18 種平台。
- **自動格式轉換**：內建 Markdown 轉 HTML 引擎，支援代碼高亮與 SEO 優化排版。
- **會話管理**：透過 `quick_generate.py` 自動保存生成記錄與元數據，支援隨時恢復編輯。

---

## 快速開始（5 分鐘上手）

YouTube 教學: https://youtu.be/nLnFU_Bk93s

### Step 1：安裝

**從 PyPI 安裝（推薦使用者）**

```bash
pip install blog-pro-max

# 選用：啟用時事趨勢分析的 Web Search 功能（DuckDuckGo，免費）
pip install "blog-pro-max[web]"
# 或直接：pip install ddgs
```

安裝後您將獲得 `blogpro` 全域指令。

**從 GitHub 安裝（開發者）**

```bash
git clone https://github.com/max32002/blog-pro-max.git
cd blog-pro-max
pip install -e .
```

### Step 2：設定 API 金鑰（僅 Script Mode 需要）

> **💡 如果你只使用 Skill Mode（透過 AI Assistant 生成文章），可跳過此步驟。**
> AI Assistant 使用自己內建的 LLM 能力，不需要額外的 API 金鑰。
>
> 只有在直接執行 Python 腳本（Script Mode）時，才需要設定 API 金鑰。

在您的工作目錄建立 `.env` 檔案：

```bash
# 推薦：GitHub PAT（免費，不需 OpenAI 帳號）
GITHUB_TOKEN=ghp_your-token-here

# 或：OpenAI API Key
OPENAI_API_KEY=sk-your-key-here
```

### Step 3：注入 Skill 到您的 AI Assistant

```bash
blogpro init --ai claude      # 針對 Claude Code
blogpro init --ai copilot     # 針對 GitHub Copilot
blogpro init --ai cursor      # 針對 Cursor
blogpro init --ai all         # 注入到所有支援的平台
```

### Step 4：開始創作

在已注入 Skill 的 AI Assistant 中直接輸入：

```
/blog-pro-max 寫一篇[AI 寫作工具]文章,受眾[內容行銷人員],以專業SEO風格
```

---

## AI Assistant 整合支援

`blog-pro-max` 支援將寫作能力無縫整合進 **18 個** AI 助手平台：

| 分類 | 平台 | `--ai` 參數 |
|------|------|-------------|
| **專業開發工具** | Claude Code | `claude` |
| | Cursor | `cursor` |
| | Windsurf | `windsurf` |
| | Trae | `trae` |
| | Roo Code | `roocode` |
| **擴充套件** | GitHub Copilot | `copilot` |
| | Continue | `continue` |
| | CodeBuddy | `codebuddy` |
| | OpenCode | `opencode` |
| | Augment | `augment` |
| **終端機 / CLI** | Gemini CLI | `gemini` |
| | Codex CLI | `codex` |
| | Warp | `warp` |
| **新興 Agent** | Antigravity | `antigravity` |
| | Kiro | `kiro` |
| | Qoder | `qoder` |
| | Droid (Factory) | `droid` |
| | KiloCode | `kilocode` |

### 全域安裝（適用於電腦上所有專案）

```bash
blogpro init --ai all --global
```

---

## 使用方式

> **API 金鑰需求一覽：**
>
> | 模式 | 需要 API 金鑰？ | 說明 |
> |------|----------------|------|
> | Skill Mode | ❌ 不需要 | AI Assistant 用自己的 LLM 生成 |
> | Workflow Mode | ❌ 不需要 | 同上 |
> | Script Mode | ✅ 需要 | Python 腳本直接呼叫 OpenAI / GitHub Models |
> | 快速生成模式 | ✅ 需要 | 支援 Gemini / OpenAI / Azure OpenAI |

### Skill Mode（自動啟動）

**支援平台：** Claude Code, Cursor, Windsurf, Antigravity, Codex CLI, Continue, Gemini CLI, OpenCode, Qoder, CodeBuddy, Droid (Factory), KiloCode, Warp, Augment

> 💡 **CLI 用戶建議：啟用 YOLO Mode**
> 
> 使用終端機 CLI（如 Gemini CLI、Codex CLI）時，AI 在執行每個步驟前都可能停下來請求確認，這會打斷寫作流程。建議啟動時加上 **YOLO（自動確認）** 參數，讓 AI 不中斷地完成整個生成流程：
> 
> ```bash
> # Gemini CLI：加上 -y 進入 YOLO mode
> gemini -y
> 
> # Codex CLI：加上 --full-auto 進入自動模式
> codex --full-auto
> ```
> 
> 啟用後，AI 將自動完成所有步驟（搜尋、生成、存檔），無需逐步確認。

安裝 Skill 後，AI Assistant 會**自動讀取** SKILL.md，您只需用自然語言下達指令：

```
幫我寫一篇關於「遠端工作生產力」的 SEO 文章，目標讀者是科技業上班族
```

或是先貼上參考資料，再要求 AI 根據這些資料生成文章：

```
以下是我收集的資料：
[貼上你的資料]

請根據以上資料，用標準模板寫一篇文章，受眾是一般讀者。
```

```
用 Max 的風格寫一篇「失去才懂珍惜」的心情筆記
```

```
幫我寫一篇「時間管理」的 Facebook 貼文，受眾是上班族
```

```
用 LINE 訊息風格分享一篇「讀書心得」，讓朋友看得輕鬆
```

```
檢查 output/my-article.md 的寫作風格
```

#### Skill Mode 輸出行為

依 AI 平台能力分兩種模式：

| AI 類型 | 範例平台 | 輸出方式 |
|---------|----------|----------|
| **可執行腳本** | Claude Code, Cursor, Windsurf | 執行 Python 腳本，自動產出 `.md` + `.html` 檔案 |
| **純 LLM 生成** | Gemini CLI, 一般聊天模式 | 直接生成文字輸出，詢問是否存檔為 `.md` |

> 💾 **如果 AI 沒有自動觸發存檔，請手動輸入：**
> ```
> save .md and .html
> ```
> AI 會將文章存成 `output/關鍵字.md` 與 `output/關鍵字.html`。

兩種模式都會完整輸出所有 12 個區塊：
- 文章本文（依選定模板格式）
- `## 🔬 邏輯與事實專家審查報告`
- `## 📐 深度與結構專家審查報告`
- `## 👁️ 讀者視角專家審查報告`
- `## 📰 時事趨勢分析報告`
- `## 📝 推薦標題選項`（4 個標題 + WordPress permalink）
- `## 🎨 推薦封面提示詞`（3 組 AI 繪圖 prompt）
- `## 🌀 發散專家建議`
- `## ❓ 問題專家建議`
- `## 😂 迷因專家建議`
- `## 💬 插話專家建議`
- `## 🖼️ 插畫專家建議`
- `## 🔴 唱反調專家報告`

### Workflow Mode（斜線命令）

**支援平台：** Kiro, GitHub Copilot, Roo Code, KiloCode

使用斜線命令精確控制生成參數：

```
/blog-pro-max 寫一篇[遠端工作生產力]文章,受眾[科技業上班族],以專業SEO風格
```

```
/blog-pro-max 寫一篇[失去才懂珍惜]文章,受眾[一般讀者],以作家Max風格
```

```
/blog-pro-max 寫一篇[時間管理心得]文章,受眾[上班族],以FB風格
```

```
/blog-pro-max 寫一篇[讀書心得分享]文章,受眾[大學生],以LINE風格
```

```
/blog-pro-max 寫一篇[Python 入門指南]文章,受眾[程式初學者],字數[2000]
```

#### 斜線命令解析規則

| 語法 | 對應參數 | 範例 |
|------|----------|------|
| `[關鍵字]`（第一個方括號） | `--keyword` | `[遠端工作生產力]` |
| `受眾[值]` | `--audience` | `受眾[科技業上班族]` |
| `字數[N]` | `--word-count` | `字數[2000]` |
| `作家Max風格` / `心情筆記` | `--template max-personal-style` | |
| `SEO風格` / `專業風格` / `部落格風格` | `--template blog-skill-content` | |
| `FB風格` / `Facebook風格` / `臉書風格` | `--template fb-post-style` | |
| `LINE風格` / `LINE訊息` / `賴風格` | `--template line-message-style` | |
| `幫我取標題 <路徑>` | 呼叫標題專家 | `幫我取標題 output/article.md` |
| `幫我生成封面 <路徑>` | 呼叫封面提示詞專家 | `幫我生成封面 output/article.md` |
| `全科檢查 <路徑>` | 三位專家全面審查 | `全科檢查 output/article.md` |
| `檢查邏輯 <路徑>` | 邏輯與事實專家 | `檢查邏輯 output/article.md` |
| `檢查結構 <路徑>` | 深度與結構專家 | `檢查結構 output/article.md` |
| `檢查讀者 <路徑>` | 讀者視角專家 | `檢查讀者 output/article.md` |
| `分析趨勢 <路徑>` | 時事趨勢專家 | `分析趨勢 output/article.md` |
| `插話建議 <路徑>` | 插話專家：每段落舉例說明 | `插話建議 output/article.md` |
| `段落插畫 <路徑>` | 插畫專家：每段落 3 組 AI 圖片提示詞 | `段落插畫 output/article.md` |
| `唱反調 <路徑>` | 唱反調專家：每段落反駁觀點 | `唱反調 output/article.md` |
| `發散思考 <路徑>` | 發散專家：每段落延伸相關話題與聯想 | `發散思考 output/article.md` |
| `提出問題 <路徑>` | 問題專家：每段落提出 3-5 個相關問題 | `提出問題 output/article.md` |
| `迷因建議 <路徑>` | 迷因專家：每段落提出迷因/幽默關鍵字 | `迷因建議 output/article.md` |
| `檢查風格 <路徑>` | 執行 style_checker | `檢查風格 output/article.md` |
| `列出模板` | 列出可用模板 | |
| `專案狀態` | 顯示專案狀態報告 | |

### Script Mode（直接執行）

不透過 AI Assistant，直接在終端機執行：

```bash
# 生成文章
python -m blog_pro_max.content_research --keyword "Python 基礎教學" --template blog-skill-content

# 關鍵字太長？從檔案讀取（兩種方式皆可）
python -m blog_pro_max.content_research --keyword @topic.txt
python -m blog_pro_max.content_research --keyword-file topic.txt

# 只看 prompt（不呼叫 API）
python -m blog_pro_max.content_research --keyword "Python 基礎教學" --dry-run

# 檢查現有 Markdown 檔案風格
python -m blog_pro_max.content_research --keyword "Python" --check-only output/my-article.md
```

### 快速生成模式（個人版）

使用 `quick_generate.py` 入口點，適合追求效率的單人使用場景，支援流式輸出與會話管理。

```bash
# 快速生成
python quick_generate.py "寫一篇 AI 的文章"

# 自訂模型與參數
python quick_generate.py "文章主題" --model gpt-4 --temperature 0.9

# 恢復上次的會話
python quick_generate.py --resume last
```

`quick_generate.py` 支援的 LLM 提供者：

| 環境變數 | 提供者 | 說明 |
|----------|--------|------|
| `GOOGLE_API_KEY` | Google Gemini | 透過 OpenAI 相容介面呼叫 |
| `OPENAI_API_KEY` | OpenAI GPT | 直接呼叫 OpenAI API |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI | 需額外設定 `AZURE_ENDPOINT` |
| `GITHUB_TOKEN` | GitHub Models | 免費，不需 OpenAI 帳號 |

---

## CLI 指令參考

### 初始化與管理
- `blogpro init`: 偵測環境並注入 Skill 檔案。
- `blogpro uninstall`: 移除已注入的 Skill。
- `blogpro versions`: 檢查版本與已安裝的平台狀態。
- `blogpro update`: 同步更新所有平台的 Skill 檔案至最新版。

### Skill 對話中的斜線命令

在 AI 助理對話框中（啟用 SKILL.md 後）可使用以下命令：

| 命令 | 說明 |
|------|------|
| `/blog [關鍵字]` | 以預設模板生成文章 |
| `/blog [關鍵字] --template [模板名]` | 指定模板 |
| `/blog [關鍵字] --audience [受眾]` | 指定目標受眾 |
| `/blog [關鍵字] --language [語言]` | 指定輸出語言（如 `en`、`ja`，預設：繁體中文） |
| `/blog --list-templates` | 列出所有可用模板 |
| `/blog --status` | 顯示目前設定狀態（模板、路徑等） |

---

## 生成 Pipeline

文章生成時會自動執行完整 pipeline（全部 12 個區塊皆自動輸出）：

```
文章生成 → 風格檢查 → 三維度審稿(邏輯/結構/讀者) → 時事趨勢分析 → 標題建議(4個+permalink) → 封面提示詞(3組) → 發散專家 → 問題專家 → 迷因專家 → 插話專家 → 插畫專家 → 唱反調專家 → MD→HTML
```

每個步驟的失敗不會阻擋後續步驟。最終輸出的 `.md` 和 `.html` 包含：
- 文章本文
- 三維度審稿報告（含問題點、修改建議、修改前後對比）
- 時事趨勢報告（趨勢關聯、切入角度、關鍵字/Hashtag、改寫示範）
- 推薦標題選項（含英文 WordPress permalink）
- 推薦封面 AI 繪圖提示詞
- 發散專家建議（每段落延伸方向與後續文章題目）
- 問題專家建議（每段落 3-5 個讀者疑問）
- 迷因專家建議（每段落迷因/幽默關鍵字）
- 插話專家建議（每段落具體舉例說明）
- 插畫專家建議（每段落 3 組風格 AI 圖片提示詞）
- 唱反調專家報告（每段落反駁觀點與建議回應）

### 內部角色

| 角色 | 說明 |
|------|------|
| **🔬 邏輯與事實專家** | 數據正確性、邏輯一致性、錯別字、AI 幻覺偵測 |
| **📐 深度與結構專家** | 遺漏面向、段落轉折、論述深度、結構平衡 |
| **👁️ 讀者視角專家** | 口吻適配、易讀性、注意力留存、情感共鳴 |
| **📰 時事趨勢專家** | 趨勢關聯分析、切入角度、關鍵字/Hashtag、改寫示範 |
| **📝 部落格標題專家** | 產出 4 個風格標題（直述、提問、數字、情感）+ 英文 permalink slug |
| **🎨 封面提示詞專家** | 產出 3 組 AI 繪圖 prompt（寫實攝影、插畫、極簡設計） |
| **🌀 發散專家** | 針對每個 H2 段落延伸相關話題、跨領域聯想，提供後續文章題目建議 |
| **❓ 問題專家** | 針對每個 H2 段落提出 3-5 個讀者可能浮現的疑問 |
| **😂 迷因專家** | 針對每個 H2 段落提出迷因/梗圖/幽默關鍵字，讓氣氛輕鬆 |
| **💬 插話專家** | 針對每個 H2 段落提供一個具體舉例說明，建議插入位置 |
| **🖼️ 插畫專家** | 針對每個 H2 段落產出 3 組風格（寫實攝影、插畫、極簡圖示）的 AI 圖片提示詞 |
| **🔴 唱反調專家** | 針對每個 H2 段落提出反駁觀點、理由，並建議如何回應 |

---

## 參數說明

| 參數 | 說明 | 預設值 |
|---|---|---|
| `--keyword` | 核心關鍵字，或 `@檔案路徑` 從檔案讀取 | — |
| `--keyword-file` | 從指定檔案讀取關鍵字（替代 `--keyword`） | — |
| `--audience` | 目標讀者（如：初學者、資深工程師） | 30-45 歲知識工作者 |
| `--word-count` | 目標字數 | 1200 |
| `--template` | 寫作風格模板 (`blog-skill-content` / `max-personal-style` / `fb-post-style` / `line-message-style`) | blog-skill-content |
| `--check-only` | 僅對指定檔案執行風格檢查 | — |
| `--dry-run` | 顯示 prompt 但不呼叫 API | — |
| `--model` | OpenAI 模型名稱 | gpt-4o |
| `--output` | 自訂輸出路徑 | `output/{keyword}.md` |

> **💡 提示**：`--keyword` 和 `--keyword-file` 二擇一，至少提供一個。當關鍵字很長（如完整的文章主題描述），建議寫入檔案後使用 `@` 語法讀取。

---

## 環境變數配置

### Script Mode（`content_research.py` / `blog_generator.py`）

| 變數名 | 說明 | 預設值 |
|--------|------|--------|
| `GITHUB_TOKEN` | GitHub PAT（免費，推薦） | — |
| `OPENAI_API_KEY` | OpenAI API Key | — |

### 快速生成模式（`quick_generate.py`）

| 變數名 | 說明 | 預設值 |
|--------|------|--------|
| `LLM_MODEL` | 使用的模型名稱 | `gemini-pro` |
| `LLM_TEMP` | 生成溫度 (0-1) | `0.7` |
| `OUTPUT_DIR` | 文章輸出目錄 | `./articles` |
| `SESSIONS_DIR` | 會話保存目錄 | `./.sessions` |
| `GOOGLE_API_KEY` | Google Gemini API Key | — |
| `OPENAI_API_KEY` | OpenAI API Key | — |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API Key | — |
| `AZURE_ENDPOINT` | Azure OpenAI Endpoint | — |

---

## 專案結構

```
blog-pro-max/
├── quick_generate.py          # 個人快速入口（流式生成 + 會話管理）
├── writing-style.md           # 品牌寫作風格規範
├── pyproject.toml             # 套件配置與依賴
├── blog_pro_max/              # 核心邏輯包
│   ├── __init__.py
│   ├── blogpro.py             # CLI 管理工具（init / uninstall / versions / update）
│   ├── blog_generator.py      # 文章生成引擎（含 12 位專家）
│   ├── content_research.py    # Script Mode 主程式進入點
│   ├── core.py                # 模板管理與共用函式
│   ├── style_checker.py       # 風格檢核器
│   ├── output_md2html.py      # Markdown 轉 HTML 引擎
│   ├── quick_stream.py        # 流式生成包裝（多 LLM 支援）
│   ├── _resources.py          # 資源路徑管理
│   ├── templates/             # 寫作風格模板
│   │   ├── blog-skill-content.md
│   │   ├── max-personal-style.md
│   │   ├── fb-post-style.md
│   │   └── line-message-style.md
│   └── writing-style.md       # 套件內建風格規範副本
├── articles/                  # 產出的文章目錄
├── .sessions/                 # 會話歷史記錄
└── docs/                      # 延伸文件
    ├── architecture.md
    ├── scripts-reference.md
    ├── faq.md
    ├── streaming-llm-guide.md
    ├── expert-parallel-guide.md
    └── blog-pro-max-new-features.md
```

---

## 常見問題 (FAQ)

- **需要 API 金鑰嗎？**
  若使用 Skill Mode / Workflow Mode（透過 AI 助理對話），不需要金鑰；若使用 Script Mode 或 `quick_generate.py`，需要設定對應的 API 金鑰。

- **支援哪些語言？**
  預設為繁體中文，但支援所有 LLM 涵蓋的語言。可透過 `--language` 參數指定。

- **如何更新到最新版本？**
  執行 `pip install --upgrade blog-pro-max` 後，運行 `blogpro update` 即可刷新所有平台的 Skill 檔案。

- **時事趨勢分析需要額外安裝嗎？**
  是的，需執行 `pip install "blog-pro-max[web]"` 或 `pip install ddgs` 安裝 DuckDuckGo 搜尋套件。

更多 FAQ 請參閱 [docs/faq.md](docs/faq.md)。

---

## 更新到最新版本

### 方法一：從 PyPI 更新（pip 安裝用戶）

```bash
# 更新套件
pip install --upgrade blog-pro-max

# 更新後，刷新所有已安裝平台的 Skill 檔案
blogpro update
```

> `blogpro update` 會自動掃描並重新安裝所有已安裝的平台（本地 + 全域），讓 AI 助手使用最新版的指令與功能。

### 方法二：從 GitHub 更新（git clone 用戶）

```bash
cd blog-pro-max
git pull
pip install -e .

# 同樣需要刷新 Skill
blogpro update
```

### 確認當前版本

```bash
blogpro versions
```

輸出範例：

```
📦 blog-pro-max
  目前版本：v1.0.34

🔌 本地已安裝平台：
  ✅ claude    v1.0.34  .claude/skills/blog-pro-max/
  ✅ copilot   v1.0.34  .github/skills/blog-pro-max/
```

---

## 授權與貢獻

本專案採用 [MIT License](LICENSE) 授權。
歡迎提交 Issue 或 Pull Request 參與貢獻！

---

## 📚 延伸文件

| 文件 | 說明 |
|------|------|
| [docs/architecture.md](docs/architecture.md) | **系統架構說明**：模組職責分工、目錄結構、完整生成 Pipeline 流程圖、函式參考表，適合想深入了解工具內部運作的開發者閱讀 |
| [docs/scripts-reference.md](docs/scripts-reference.md) | **腳本完整參考手冊**：所有函式簽名、參數說明、回傳格式範例、獨立使用情境與範例指令，以及 Skill Mode 斜線命令速查表 |
| [docs/faq.md](docs/faq.md) | **常見問題 FAQ**：25+ 個 Q&A，涵蓋安裝設定、API 金鑰選擇、Skill 注入、各專家功能說明、輸出格式、疑難排解等 |
| [docs/streaming-llm-guide.md](docs/streaming-llm-guide.md) | **流式生成指南**：流式 LLM 呼叫的架構與使用方式 |
| [docs/expert-parallel-guide.md](docs/expert-parallel-guide.md) | **專家並行指南**：如何平行執行多位專家以加速生成流程 |
