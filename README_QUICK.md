# blog-pro-max 個人版快速指南

## 概述

這是針對單人使用的簡化版本，無需複雜的權限系統和工具管理。

- ✅ **快速上手**：5 分鐘內開始生成文章
- ✅ **簡單直觀**：直接命令行調用，無需配置
- ✅ **質量檢查**：可選的並行專家審查
- ✅ **自動保存**：文章和會話自動保存

---

## 快速開始

### 最簡單的用法

```bash
# 生成一篇文章
python quick_generate.py "寫一篇關於 AI 的部落格文章，1500 字"
```

就這樣！文章會實時流式輸出，自動保存到 `.sessions/` 目錄。

### 進階選項

```bash
# 使用自訂模型
python quick_generate.py "寫一篇文章" --model gpt-4 --temperature 0.9

# 生成並進行專家審查
python quick_generate.py "寫一篇文章" --review

# 恢復上一個會話（查看之前生成的文章）
python quick_generate.py --resume last

# 自訂輸出目錄
export OUTPUT_DIR=./my_articles
python quick_generate.py "寫一篇文章"
```

---

## 工作流程

### 1️⃣ 第一步：生成文章

```bash
python quick_generate.py "寫一篇 AI 倫理的分析，2000 字"

🚀 正在生成文章...
------------------------------------------------------------
人工智能的倫理議題正日益引起廣泛關注...
[實時流式輸出，逐詞顯示...]
------------------------------------------------------------

✓ 文章生成完成 (2047 字)

💾 會話已保存：.sessions/session_20260401_120000.json
📄 文章已保存：.sessions/article_20260401_120000.md
```

### 2️⃣ 第二步（可選）：進行質量檢查

```bash
python quick_generate.py "寫一篇 AI 倫理的分析，2000 字" --review

[同上輸出...]

🔍 執行專家審查...

審查結果:
------------------------------------------------------------
【內容檢查官】
✓ 事實準確性: 良好
⚠ 缺少 1 個具體案例
...

【SEO 優化師】
✓ 關鍵字分佈合理
💡 建議改進標題
...

[其他專家評審...]
------------------------------------------------------------
```

### 3️⃣ 第三步（未來）：恢復和編輯

```bash
# 查看上一篇生成的文章
python quick_generate.py --resume last

✓ 恢復會議：2026-04-01T12:00:00.000000
原始提示：寫一篇 AI 倫理的分析，2000 字
字數：2047

內容預覽:
------------------------------------------------------------
人工智能的倫理議題正日益引起廣泛關注...
[前 500 字預覽...]
------------------------------------------------------------
```

---

## 環境配置

### 可選：自訂環境變數

```bash
# 設定默認模型
export LLM_MODEL=gpt-4

# 設定默認溫度（0-1，越高越有創意）
export LLM_TEMP=0.8

# 設定輸出目錄
export OUTPUT_DIR=./my_articles

# 設定會話目錄
export SESSIONS_DIR=./.my_sessions

# 然後直接執行
python quick_generate.py "寫一篇文章"
```

### 不設定環境變數也可以

直接用默認值：

```bash
# 模型預設：gemini-pro
# 溫度預設：0.7
# 輸出目錄預設：./articles
# 會話目錄預設：./.sessions

python quick_generate.py "寫一篇文章"
```

---

## 文件位置

```
blog-pro-max/
├── quick_generate.py          # 主程序 ← 直接執行這個
├── README_QUICK.md             # 本文件
├── articles/                   # 輸出的文章
│   ├── article_20260401_120000.md
│   └── article_20260401_120030.md
└── .sessions/                  # 會話數據
    ├── session_20260401_120000.json
    ├── article_20260401_120000.md
    └── ...
```

---

## 功能說明

### 功能 1：流式生成

- 實時輸出，不用等待完成
- 支援多個 LLM 模型（Gemini、GPT-4 等）
- 可調節溫度控制創意度

### 功能 2：可選審查

- 12 位並行專家同時審查文章
- 評分、建議、改進方向
- 不會大幅延長等待時間（< 1 分鐘）

### 功能 3：會話管理

- 自動保存文章和提示詞
- 保存會話元數據（時間、狀態等）
- 可恢復之前的生成內容

---

## 常見問題

### Q1：如何更換 LLM 模型？

**方式 A**：命令行參數（推薦）
```bash
python quick_generate.py "寫文章" --model gpt-4
```

**方式 B**：環境變數
```bash
export LLM_MODEL=gpt-4
python quick_generate.py "寫文章"
```

**支援的模型**：
- `gemini-pro` (預設，快速且便宜)
- `gemini-flash` (超快速)
- `gpt-4` (高質量)
- `gpt-3.5-turbo` (經濟)
- `claude-3` (深度分析)

### Q2：生成速度如何？

**預計耗時**：
- Gemini Pro：1000 字 = 20-30 秒
- Gemini Flash：1000 字 = 10-15 秒
- GPT-4：1000 字 = 40-60 秒

含審查時間：額外 < 1 分鐘

### Q3：生成的文章在哪裡？

自動保存到兩個地方：

1. **會話 JSON**：`.sessions/session_YYYYMMDD_HHMMSS.json`
   - 包含原始提示詞、生成時間、文章內容

2. **Markdown 文件**：`.sessions/article_YYYYMMDD_HHMMSS.md`
   - 純文本格式，可直接編輯

### Q4：可以改變創意度嗎？

```bash
# 更保守、更可靠的輸出
python quick_generate.py "寫文章" --temperature 0.3

# 平衡（預設）
python quick_generate.py "寫文章" --temperature 0.7

# 更創意、更多樣化
python quick_generate.py "寫文章" --temperature 0.95
```

### Q5：審查會延長多久？

審查是**並行**執行：
- 不審查：20-60 秒
- 加審查：+30-60 秒（多位專家同時進行，不是串行）

### Q6：可以只用部分功能嗎？

完全可以：

```bash
# 只生成，不審查
python quick_generate.py "寫文章"

# 生成 + 審查
python quick_generate.py "寫文章" --review

# 只查看之前的會話
python quick_generate.py --resume last
```

---

## Gemini CLI 集成

如果您安裝了 Gemini CLI，也可以這樣用：

```bash
# 直接在 Gemini CLI 中使用
gemini "使用 quick_generate.py 生成一篇 AI 的文章"

# 或者設定身份後使用
export BLOG_USER=personal
gemini -p "使用 quick_generate 生成文章"
```

---

## 後續升級路徑

如果未來需要團隊協作，只需啟用更多模塊，無需改寫任何代碼：

- ✅ 啟用權限系統（如果有多人）
- ✅ 啟用工具註冊表（如果工具多）
- ✅ 啟用完整會話管理（追蹤成本）
- ✅ 啟用配置管理（多環境部署）

現在的簡化版本完全**向前兼容**。

---

## 故障排除

### 問題 1：無法導入 StreamingBlogGenerator

**錯誤**：`ImportError: cannot import name 'StreamingBlogGenerator'`

**解決**：
```bash
# 確保在 blog-pro-max 目錄運行
cd C:\max\git\blog-pro-max

# 安裝依賴
pip install -r requirements.txt

# 再試
python quick_generate.py "寫文章"
```

### 問題 2：API 金鑰缺失

**錯誤**：`AuthenticationError` 或 `API key not found`

**解決**：
```bash
# 設定 Gemini API 金鑰
export GOOGLE_API_KEY=your_key_here

# 或 OpenAI
export OPENAI_API_KEY=your_key_here

# 然後運行
python quick_generate.py "寫文章"
```

### 問題 3：字符編碼問題（Windows）

如果看到亂碼：

```bash
# 運行前設定 UTF-8
chcp 65001

# 然後運行
python quick_generate.py "寫文章"
```

### 問題 4：會話目錄權限問題

**解決**：
```bash
# 手動建立目錄
mkdir .sessions
mkdir articles

# 授予讀寫權限
# Windows: 右鍵 → 屬性 → 安全 → 編輯
# Linux: chmod 755 .sessions articles
```

---

## 下一步

1. **立即使用**：
   ```bash
   python quick_generate.py "寫一篇 AI 趨勢的文章"
   ```

2. **查看文章**：
   ```bash
   cat .sessions/article_*.md
   ```

3. **試試審查**：
   ```bash
   python quick_generate.py "寫一篇文章" --review
   ```

4. **恢復會話**：
   ```bash
   python quick_generate.py --resume last
   ```

---

## 更多幫助

如需了解更多功能（權限系統、工具管理、成本追蹤等），請參考：

- 📖 [完整文檔](./docs/blog-pro-max-new-features.md)
- 🚀 [權限系統教學](./docs/authmanager-guide.md)
- ⚡ [流式生成詳解](./docs/streaming-llm-guide.md)
- 👥 [專家審查說明](./docs/expert-parallel-guide.md)

---

**開始吧！** 🚀

```bash
python quick_generate.py "寫一篇文章"
```
