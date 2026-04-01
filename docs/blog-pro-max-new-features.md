# blog-pro-max 核心功能

本文檔介紹 blog-pro-max 個人版的核心功能。

## 功能清單

### 1. 流式 LLM 文章生成（QuickStreamingGenerator）
- **位置**: `blog_pro_max/quick_stream.py`
- **教學文檔**: [streaming-llm-guide.md](./streaming-llm-guide.md)
- **概述**: 實時流式生成高品質文章
- **核心功能**:
  - 邊生成邊顯示（流式輸出）
  - 支援多個 LLM（Gemini、GPT、Azure、Claude）
  - 溫度控制和模型選擇
  - 自動客戶端初始化
- **適用場景**: 快速寫文章、實時反饋、多 LLM 支援

### 2. 專家並行化（Parallel Expert Review）
- **位置**: `blog_pro_max/content_research.py`
- **教學文檔**: [expert-parallel-guide.md](./expert-parallel-guide.md)
- **概述**: 12 位專家並行審查文章
- **核心功能**:
  - 並行專家審查（12 位角色）
  - 多維度評分和反饋
  - 邏輯、結構、讀者視角檢查
  - 性能優化（<1 分鐘完成）
- **適用場景**: 內容質量控制、多方面評估、質量保證

---

## 快速開始

### 安裝和配置

```bash
# 安裝依賴
pip install -r requirements.txt

# 設置 API 金鑰（任選一個）
export GOOGLE_API_KEY=your-key      # Google Gemini（推薦）
export OPENAI_API_KEY=sk-...        # OpenAI GPT
export AZURE_ENDPOINT=https://...   # Azure OpenAI
export AZURE_API_KEY=...
```

### 核心功能使用

#### 1️⃣ 流式文章生成（快速寫文章）
```bash
python quick_generate.py "寫一篇關於 AI 的文章"
```

```python
from blog_pro_max.quick_stream import QuickStreamingGenerator

generator = QuickStreamingGenerator(model="gemini-pro", temperature=0.7)
for chunk in generator.generate("寫一篇文章"):
    print(chunk, end='', flush=True)
```

👉 詳見 [streaming-llm-guide.md](./streaming-llm-guide.md)

#### 2️⃣ 專家並行審查（檢查質量）
```bash
python -m blog_pro_max.content_research --keyword "我的文章" --check-only output/article.md
```

```python
from blog_pro_max.content_research import parallel_expert_review

content = "## 我的文章\n..."
results = parallel_expert_review(content)
for expert, feedback in results.items():
    print(f"{expert}: {feedback}")
```

👉 詳見 [expert-parallel-guide.md](./expert-parallel-guide.md)

---

## 功能對比

| 功能 | 用途 | 複雜度 | 效能 |
|------|------|--------|------|
| 流式生成 | 生成內容 | 低 | <10秒/千字 |
| 專家審查 | 質量控制 | 低 | <1分鐘/文章 |

---

## 集成場景

### 場景 1：個人部落格
```
提示詞 → 流式生成 → 文章保存
```
- 快速生成新文章
- 邊生成邊查看進度
- 自動保存會話

### 場景 2：寫文章 + 檢查質量
```
提示詞 → 流式生成 → 專家審查 → 改進
```
- 生成初稿
- 進行並行審查
- 根據反饋改進

### 場景 3：批量內容生成
```
列表 → 逐篇生成 → 批量審查 → 統計結果
```
- 一次生成多篇文章
- 統一進行質量檢查
- 生成審查報告

---

## 使用方式

### 命令行使用

```bash
# 生成文章
python quick_generate.py "我的主題"

# 恢復之前的會話
python quick_generate.py --resume last

# 自訂參數
python quick_generate.py "主題" --model gpt-4 --temperature 0.8

# 檢查現有文章
python -m blog_pro_max.content_research --check-only output/article.md

# 只看 prompt（不執行）
python -m blog_pro_max.content_research --keyword "主題" --dry-run
```

### 環境變數配置

| 變數 | 說明 | 預設值 |
|------|------|--------|
| `LLM_MODEL` | LLM 模型 | `gemini-pro` |
| `LLM_TEMP` | 生成溫度 | `0.7` |
| `OUTPUT_DIR` | 輸出目錄 | `./articles` |
| `SESSIONS_DIR` | 會話目錄 | `./.sessions` |
| `GOOGLE_API_KEY` | Gemini 金鑰 | — |
| `OPENAI_API_KEY` | OpenAI 金鑰 | — |

---

## 下一步

1. **安裝依賴** - `pip install -r requirements.txt`
2. **設置 API 金鑰** - 選擇一個 LLM 提供商
3. **試試流式生成** - `python quick_generate.py "測試"`
4. **查看結果** - 會話保存在 `.sessions/` 目錄
5. **選擇審查** - 使用 `--check-only` 檢查質量

---

## 常見問題

**Q: 需要哪些 API 金鑰？**  
A: 選一個即可：
- Google Gemini（免費，推薦）
- OpenAI GPT（付費，性能好）
- Azure OpenAI（企業版）

**Q: 文章保存在哪裡？**  
A: 
- 會話元資料：`.sessions/session_*.json`
- 文章內容：`.sessions/session_*.md`

**Q: 怎樣恢復之前的文章？**  
A: `python quick_generate.py --resume last`

**Q: 有企業版本嗎？**  
A: 有。本目錄還有以下企業版文檔供參考：
- streaming-llm-guide.md（詳細用法）
- expert-parallel-guide.md（專家配置）
- faq.md（常見問題）
- architecture.md（系統架構）
- scripts-reference.md（完整參考）

---

**版本**: 2.0 (Personal Edition)  
**最後更新**: 2026-04-01

