# ❓ FAQ — 常見問題

> 以下整理了使用 blog-pro-max 時最常遇到的問題與解答。

---

## 目錄

1. [資料來源與內容生成](#1-資料來源與內容生成)
2. [版權與法律問題](#2-版權與法律問題)
3. [API 與金鑰設定](#3-api-與金鑰設定)
4. [模板與風格](#4-模板與風格)
5. [安裝與環境](#5-安裝與環境)
6. [輸出與格式](#6-輸出與格式)
7. [AI 平台整合](#7-ai-平台整合)
8. [疑難排解](#8-疑難排解)

---

## 1. 資料來源與內容生成

### Q：content_research.py 的資料來源是哪裡？

**content_research.py 本身不做網路搜尋或資料抓取。** 它的運作方式是：

1. 根據你指定的關鍵字、受眾、模板，組裝一組精心設計的 prompt
2. 將 prompt 送給 LLM（如 GPT-4o）
3. LLM 根據其訓練資料生成文章

也就是說，**資料來源是 LLM 模型本身的訓練語料**——包括網路上公開的文章、書籍、百科等（截止至模型的訓練截止日期）。工具不會即時搜尋 Google 或爬取任何網站。

### Q：生成的文章內容可靠嗎？

LLM 生成的內容可能包含**事實性錯誤**（幻覺）。建議：

- ✅ 將生成內容視為**初稿**，而非成品
- ✅ 人工核實數據、日期、引用來源
- ✅ 特別留意技術細節、法律條文、醫療資訊等敏感領域
- ✅ 善用 `--dry-run` 先檢視 prompt，確保指令方向正確

### Q：是否可以自定義資料來源？

目前工具不直接支援外部資料來源注入，但你可以透過以下方式達成類似效果：

**方法一：修改模板**

在 `templates/` 目錄下建立自訂模板，在模板中加入你的參考資料：

```markdown
## 參考資料

以下是你必須參考的資料來源，請基於這些內容撰寫文章：

- 資料 1：{你的內容}
- 資料 2：{你的內容}
```

**方法二：透過 AI Assistant 的對話上下文**

在 Skill Mode 下，先貼上參考資料，再要求 AI 根據這些資料生成文章：

```
以下是我的研究筆記：
[貼上你的資料]

請根據以上資料，用 blog-pro-max 的 SEO 模板寫一篇關於「量子運算」的文章。
```

**方法三：修改 blog_generator.py**

進階開發者可以修改 `generate_article()` 函式，在呼叫 LLM 之前加入 RAG（檢索增強生成）邏輯，例如：
- 接入向量資料庫（如 ChromaDB、Pinecone）
- 接入搜尋 API（如 Tavily、Serper）
- 從本地檔案讀取參考資料

### Q：每次生成同一個關鍵字，結果會不同嗎？

會的。生成使用 `temperature=0.7`，每次呼叫都會產生不同的文章。如果你想要更穩定的輸出，可以修改 `blog_generator.py` 中的 `temperature` 值（降低到 0.2–0.3）。

---

## 2. 版權與法律問題

### Q：直接使用 AI 生成的文章有版權問題嗎？

這是一個重要且尚無統一定論的法律議題。以下是目前的共識：

**AI 生成內容的版權現況：**

| 面向 | 說明 |
|------|------|
| **著作權歸屬** | 多數國家（包括美國）目前認為**純 AI 生成的內容不具著作權**，因為著作權要求「人類作者」。但如果人類有實質性的創作貢獻（如大幅編輯、選擇、安排），則可能享有著作權。 |
| **台灣法律** | 台灣智慧財產局的見解是：如果 AI 生成物是在人類「精神作用」介入下產出（如精心設計 prompt、大量修改），有可能被認定為著作。但純粹按下按鈕生成的內容，不受著作權保護。 |
| **抄襲風險** | LLM 可能在輸出中無意間重現訓練資料中的片段。機率低但非零，尤其在高度專業或小眾的主題上。 |
| **平台政策** | Google 不反對 AI 生成內容，但強調內容必須**對讀者有幫助**。低品質的純 AI 內容可能被降權。 |

**建議做法：**

- ✅ **將 AI 生成視為初稿**：加入個人觀點、經驗、案例後發佈
- ✅ **人工編輯與審核**：確保事實正確、語氣符合品牌
- ✅ **加入原創價值**：個人經驗、獨家數據、專業分析
- ✅ **標註 AI 輔助**（可選）：部分平台建議揭露 AI 輔助創作
- ⚠️ **避免直接發佈未修改的 AI 輸出**：既有品質疑慮，也有法律灰色地帶

### Q：生成的文章會不會和別人的文章重複？

LLM 生成的文章是**機率性產出**，不是複製貼上。但以下情況可能產生相似內容：

- 極為通用的主題（如「時間管理的 5 個方法」）
- 模型可能產出常見的寫作結構和慣用語

**降低重複風險：**
- 使用 `max-personal-style` 模板（個人化風格降低相似度）
- 指定具體的受眾和角度
- 生成後加入個人經驗和獨特觀點

### Q：我可以將生成的文章用於商業用途嗎？

取決於你使用的 API 服務條款：

| API 提供者 | 商業使用 | 備註 |
|------------|----------|------|
| **OpenAI** | ✅ 允許 | 輸出內容的權利歸使用者，但需遵守使用政策 |
| **GitHub Models** | ⚠️ 請查閱 | GitHub Models 目前為預覽階段，條款可能變動 |

建議在商業使用前，確認你所使用 API 的最新服務條款。

---

## 3. API 與金鑰設定

### Q：GITHUB_TOKEN 和 OPENAI_API_KEY 有什麼差別？

| | GITHUB_TOKEN | OPENAI_API_KEY |
|---|---|---|
| **來源** | GitHub → Settings → Developer settings → Personal access tokens | OpenAI Platform → API Keys |
| **費用** | 免費（GitHub Models 免費額度） | 按用量計費 |
| **端點** | `https://models.inference.ai.azure.com` | `https://api.openai.com` |
| **適合** | 個人使用、試用、輕度使用 | 商業使用、大量生成 |
| **建議** | ✅ 推薦新手使用 | 適合重度使用者 |

### Q：GitHub Token 需要什麼權限（scope）？

**不需要任何 scope。** 建立 Personal Access Token (classic) 時，可以不勾選任何權限。GitHub Models API 只需要有效的 token 即可。

### Q：兩個都設定了會怎樣？

系統會**優先使用 GITHUB_TOKEN**。只有在 GITHUB_TOKEN 未設定時，才會使用 OPENAI_API_KEY。

### Q：可以使用其他 LLM（如 Claude、Gemini）嗎？

目前工具使用 OpenAI 相容 API。任何提供 OpenAI 相容端點的服務都可以使用，包括：

- **Azure OpenAI**：設定 `OPENAI_API_KEY` 和修改 `base_url`
- **本地模型**：透過 Ollama、LM Studio 等工具提供 OpenAI 相容端點
- **其他雲端服務**：如 Together AI、Groq 等

需要修改 `blog_generator.py` 中的 `_make_client()` 函式來支援其他端點。

---

## 4. 模板與風格

### Q：目前有哪些模板可用？

| 模板名稱 | 說明 | 適合場景 |
|----------|------|----------|
| `blog-skill-content` | SEO 專業文章，結構化、精簡 | 部落格、企業內容行銷 |
| `max-personal-style` | 作家 Max 風格，心情筆記、第一人稱 | 個人部落格、散文、生活分享 |
| `fb-post-style` | Facebook 貼文，▋ 標題、口語化、社群互動 | Facebook 粉專、社群貼文 |
| `line-message-style` | LINE 訊息，簡短親切、emoji、好朋友分享 | LINE 群組、LINE 官方帳號 |

### Q：如何新增自訂模板？

1. 在 `blog_pro_max/templates/` 目錄下新增模板檔案，例如 `my-style.md`
2. 在 `blog_pro_max/core.py` 的 `TEMPLATES` 字典中註冊：

```python
"my-style": {
    "path": "templates/my-style.md",
    "description": "我的自訂風格",
    "style_guide": "writing-style.md",  # 或 None
    "system_prompt": "你是一位...的寫作者。\n{style_guide}"
}
```

3. 使用：`--template my-style`

### Q：`writing-style.md` 和模板有什麼不同？

| | `writing-style.md` | 模板（`templates/*.md`） |
|---|---|---|
| **角色** | 品牌寫作規範（通用） | 特定文章結構的指令 |
| **內容** | 禁用詞、標點規則、SEO 原則 | 變數佔位符、結構要求 |
| **注入方式** | 被 `build_system_prompt()` 注入 system prompt | 被 `render_template()` 填入變數 |
| **適用範圍** | 所有使用 `style_guide` 的模板共用 | 每個模板獨立 |

### Q：風格檢查器會檢查什麼？

六項規則：

1. **禁用詞**：掃描 7 個常見 AI 口癖（如「值得注意的是」、「不可否認地」）
2. **標題層級**：只允許 H1 + H2，禁止 H3 以下
3. **段落長度**：單一段落不超過 5 行
4. **SEO 基本功**：H1 含關鍵字、關鍵字出現在前 100 字元
5. **標點符號**：中文語境使用全形標點
6. **中英間距**：中文字和英文/數字之間需有空格

### Q：標題專家是什麼？怎麼運作？

**標題專家**（blog-title-writer）是內建的 AI 角色，在文章生成後自動執行。它會分析文章內容，產出 4 個不同風格的標題建議：

1. **直述型**：直接點明主題
2. **提問型**：以問句引起好奇
3. **數字型**：使用數字增加信任感
4. **情感型**：訴諸情感共鳴

每個標題都附帶**英文 WordPress permalink slug**，方便直接複製貼上。標題會附加在輸出的 `.md` 和 `.html` 檔案末尾，供人工選擇最終標題。

也可以單獨使用斜線命令觸發：`幫我取標題 output/article.md`

### Q：封面提示詞專家是什麼？

**封面提示詞專家**（cover-prompt-writer）會分析文章內容，自動產出 3 組 AI 繪圖封面提示詞：

1. **寫實攝影風格** — 適合新聞、專業文章
2. **插畫風格** — 適合生活、教學類文章
3. **極簡設計風格** — 適合科技、商業文章

每組提示詞都是**英文**，可直接貼到 Midjourney、DALL-E、Stable Diffusion 等 AI 繪圖工具。同時附帶中文說明，幫助你理解每組提示詞的風格意圖。

也可以單獨使用斜線命令觸發：`幫我生成封面 output/article.md`

### Q：什麼是三維度審稿專家？

文章生成後，系統會自動執行三位審稿專家，從不同角度深度檢查：

**🔬 邏輯與事實專家**（logic-fact-checker）
- 數據正確性：引用的數字、年份是否合理
- 邏輯矛盾：論點是否前後一致、因果是否成立
- 錯別字：錯字、同音字誤用、語法不通
- AI 幻覺偵測：引用的觀點是否缺乏根據

**📐 深度與結構專家**（depth-structure-reviewer）
- 遺漏面向：讀者可能感興趣但文章未涵蓋的角度
- 段落轉折：段落銜接是否自然、有無突兀跳躍
- 論述深度：哪些段落太淺薄、缺乏具體例子
- 結構平衡：各段落篇幅比例是否合理

**👁️ 讀者視角專家**（reader-perspective-reviewer）
- 口吻適配：語氣是否符合目標受眾
- 易讀性：術語是否過難、有無解釋
- 注意力留存：哪些段落可能讓讀者跳過
- 情感共鳴：開頭是否吸引人、結尾是否有力

每位專家的輸出都包含結構化表格：**問題點 → 修改建議 → 原文 → 修改後**，讓你立刻知道如何動手修改。

觸發方式：
- **自動**：文章生成後自動執行
- `全科檢查 output/article.md` — 三位專家全面審查
- `檢查邏輯 output/article.md` — 只執行邏輯專家
- `檢查結構 output/article.md` — 只執行結構專家
- `檢查讀者 output/article.md` — 只執行讀者專家

### Q：什麼是時事趨勢專家？

**📰 時事趨勢專家**（trend-scout）會分析文章與當前社會熱議話題的關聯，讓文章更有時效性與傳播力。輸出包含四個結構化區塊：

1. **🔗 趨勢關聯分析**：點出文章與哪些時事相關、關聯合理性、討論熱度（高/中/低）
2. **🎯 切入角度建議**：針對同一時事提供 2-3 個不同的發揮方向，各標註適合的品牌或讀者類型
3. **🏷️ 關鍵字與標籤優化**：5-8 個高流量搜尋關鍵字 + 5-8 個社群 Hashtag（可直接複製使用）
4. **✍️ 內容改寫示範**：選取原文一段，示範加入時事元素的修改前後對比

觸發方式：
- **自動**：文章生成後自動執行（在三位審稿專家之後）
- `分析趨勢 output/article.md` — 單獨執行趨勢分析

### Q：時事趨勢專家如何取得「當前」資料？

趨勢分析會先透過 **DuckDuckGo** 搜尋與關鍵字相關的最新動態，再將搜尋結果注入 LLM，讓分析貼近真實時事而非依賴訓練資料的舊知識。

搜尋的三個 query：
- `{關鍵字} 趨勢 {今年}`
- `{關鍵字} 最新消息`
- `{關鍵字} 熱門話題`

若搜尋套件未安裝或網路不可用，系統會自動降回 LLM-only 模式（不影響文章生成）。

**啟用 Web Search 搜尋功能：**

```bash
# 方法 1：單獨安裝套件
pip install ddgs

# 方法 2：透過 blog-pro-max 的 optional extra 安裝
pip install "blog-pro-max[web]"
```

安裝後無需任何設定，下次執行自動啟用。

### Q：Facebook 和 LINE 模板有什麼特別？

這兩個模板的輸出是**純文字**（非 Markdown），針對各平台的閱讀習慣優化：

- **Facebook 貼文**（`fb-post-style`）：使用 `▋` 做標題、段落間明顯留白、口語化、結尾加 hashtag 和互動提問
- **LINE 訊息**（`line-message-style`）：句子簡短（≤20 字）、使用 emoji、親切口語、國中生也能理解的用詞

---

## 5. 安裝與環境

### Q：需要什麼 Python 版本？

Python 3.9 以上。建議使用 3.10 或 3.11。

### Q：`pip install` 和 `git clone` 有什麼差別？

| | `pip install blog-pro-max` | `git clone` + `pip install -e .` |
|---|---|---|
| **適合** | 一般使用者 | 開發者、想修改程式碼 |
| **更新方式** | `pip install --upgrade blog-pro-max` | `git pull && pip install -e .` |
| **修改程式碼** | 需要找到 site-packages 目錄 | 直接修改專案目錄 |
| **資源位置** | `site-packages/blog_pro_max/` | 專案根目錄 |

### Q：Windows 終端機顯示亂碼怎麼辦？

這是 Windows 終端機編碼問題（cp950 不支援部分 Unicode 字元）。解決方式：

```powershell
# 方法 1：使用 Windows Terminal（推薦）
# 從 Microsoft Store 安裝 Windows Terminal

# 方法 2：設定 PowerShell 編碼
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
```

程式本身的功能不受影響，只是顯示問題。

### Q：可以在虛擬環境中使用嗎？

可以，而且推薦：

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install blog-pro-max
```

---

## 6. 輸出與格式

### Q：輸出檔案在哪裡？

輸出檔案在**你執行指令的工作目錄**下的 `output/` 資料夾：

```
你的工作目錄/
└── output/
    ├── 你的關鍵字.md     ← Markdown 原始檔
    └── 你的關鍵字.html   ← HTML 轉換檔
```

### Q：HTML 輸出可以直接貼到 WordPress 嗎？

可以。HTML 輸出設計為 WordPress 相容格式：

- 只使用 `<p>` 段落和 `<h2>` 標題
- 不包含 `<h3>` 以下的標題
- 內含基本 CSS 樣式
- 支援程式碼高亮

在 WordPress 編輯器中，切換到「程式碼編輯器」模式，貼上 HTML 內容即可。

### Q：可以自訂輸出路徑嗎？

可以，使用 `--output` 參數：

```bash
python -m blog_pro_max.content_research --keyword "Python" --output ~/Desktop/my-article.md
```

---

## 7. AI 平台整合

### Q：`blogpro init` 做了什麼？

它會在指定平台的約定目錄下建立一組檔案：

```
.claude/skills/blog-pro-max/    （以 Claude 為例）
├── SKILL.md                    ← AI 讀取的主要指令文件
├── scripts/                    ← Python 腳本
├── templates/                  ← 寫作模板
├── writing-style.md            ← 風格指南
├── copilot.json                ← 設定
├── requirements.txt            ← Python 依賴
├── output/                     ← 輸出目錄
└── .blogpro-manifest.json      ← 安裝追蹤
```

### Q：安裝到 `--global` 和本地有什麼差別？

| | 本地（預設） | 全域（`--global`） |
|---|---|---|
| **安裝位置** | 當前工作目錄 | 使用者家目錄（`~`） |
| **適用範圍** | 僅此專案 | 電腦上所有專案 |
| **範例路徑** | `./github/prompts/blog-pro-max/` | `~/.github/prompts/blog-pro-max/` |

### Q：可以同時安裝多個平台嗎？

可以。使用 `--ai all` 一次安裝所有 18 個平台：

```bash
blogpro init --ai all
blogpro init --ai all --global
```

### Q：如何移除已安裝的 Skill？

```bash
# 自動偵測並移除所有已安裝的平台
blogpro uninstall

# 移除特定平台
blogpro uninstall --ai claude

# 移除全域安裝
blogpro uninstall --global
```

---

## 8. 疑難排解

### Q：出現「未設定 API 金鑰」錯誤

確認 `.env` 檔案存在於你的**工作目錄**（不是套件安裝目錄）：

```bash
# 確認 .env 在正確位置
cat .env
# 應該看到：
# GITHUB_TOKEN=ghp_...
# 或
# OPENAI_API_KEY=sk-...
```

### Q：出現「模板不存在」警告

可能是套件安裝不完整。嘗試重新安裝：

```bash
pip install --force-reinstall blog-pro-max
```

### Q：`blogpro` 指令找不到

確認 pip 的 scripts 目錄在 PATH 中：

```bash
# 查看 blogpro 安裝位置
pip show blog-pro-max

# 如果是在虛擬環境中
# 確認已 activate
```

### Q：生成的文章品質不佳

嘗試以下調整：

- **換模型**：`--model gpt-4o`（預設）通常品質最好
- **調整關鍵字**：更具體的關鍵字 = 更精準的文章
- **指定受眾**：明確的受眾描述有助於 LLM 調整語氣和深度
- **使用 dry-run**：先檢視 prompt 是否合理，再正式生成
- **調整 temperature**：在 `blog_generator.py` 中降低 `temperature`（0.3–0.5）可提高一致性

### Q：風格檢查一直報錯怎麼辦？

風格檢查是**建議性的**，ERROR 表示需要關注，WARNING 可以忽略。常見情況：

- **「禁用詞」報錯**：LLM 喜歡用「值得注意的是」等詞，可以在生成後手動替換
- **「H1 不含關鍵字」**：可能模型沒完全遵守指令，手動修改標題即可
- **「中英間距」警告**：可自行決定是否修正

如果覺得某項規則太嚴格，可以在 `style_checker.py` 中調整或移除對應的檢查函式。
