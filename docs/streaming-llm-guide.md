# 流式 LLM 文章生成教學

## 功能簡介

- 支援實時流式產生文章內容
- 邊生成邊顯示，無需等待完整結果
- 支援多個 LLM（Gemini、GPT、Azure、Claude）
- 可讀取本地文件進行內容生成
- 實時進度反饋和溫度控制

## 核心概念

### 流式 vs 傳統生成

```
傳統方式（等待全部完成）：
  開始生成 → ... 等待 30 秒 ... → 一次性輸出整篇文章

流式方式（即時反饋）：
  開始生成 → 逐詞輸出 → 逐句顯示 → 即時看到進度
  優勢：可立即檢視內容、不用等待、感受更流暢
```

### 支援的 LLM 模型

- **Google Gemini** (推薦) - 免費、快速、額度充足
- **OpenAI GPT-4** - 高質量、需付費
- **OpenAI GPT-3.5** - 快速、經濟
- **Azure OpenAI** - 企業級
- **Claude** - 深度推理、長文本支援

---

## Python 使用範例

### 範例 1：直接輸入提示詞生成

```python
from blog_pro_max.quick_stream import QuickStreamingGenerator

# 初始化生成器
generator = QuickStreamingGenerator(model='gemini-pro', temperature=0.7)

# 生成文章
prompt = "請用繁體中文寫一篇關於 AI 倫理的部落格文章，2000 字"
print("正在生成文章...\n")

collected = ""
for chunk in generator.generate(prompt):
    print(chunk, end='', flush=True)
    collected += chunk

print(f"\n\n✓ 文章生成完成 ({len(collected)} 字)")
```

### 範例 2：讀取本地文件內容生成

```python
from pathlib import Path
from blog_pro_max.quick_stream import QuickStreamingGenerator

# 讀取參考資料
reference = Path("research.txt").read_text(encoding='utf-8')

# 基於參考資料生成文章
generator = QuickStreamingGenerator(model='gpt-4')
prompt = f"""根據以下參考資料，寫一篇 1500 字的文章：

{reference}

要求：
- 繁體中文
- 專業但易讀
- 包含個人見解"""

for chunk in generator.generate(prompt):
    print(chunk, end='', flush=True)
```

### 範例 3：自訂溫度和模型

```python
from blog_pro_max.quick_stream import QuickStreamingGenerator

# 不同溫度的生成
# 低溫度 (0.3) → 更確定、更一致
# 中溫度 (0.7) → 平衡
# 高溫度 (1.0) → 更有創意、更多樣

# 創意寫作
creative = QuickStreamingGenerator(
    model='gemini-pro',
    temperature=0.9
)

for chunk in creative.generate("寫一個有趣的故事"):
    print(chunk, end='', flush=True)
```

### 範例 4：使用不同 LLM

```python
from blog_pro_max.quick_stream import QuickStreamingGenerator

# OpenAI GPT-4
gpt_gen = QuickStreamingGenerator(model='gpt-4')

# Azure OpenAI
azure_gen = QuickStreamingGenerator(model='azure')

# 輪流試用
models = [
    ('gemini-pro', 'Google Gemini'),
    ('gpt-4', 'OpenAI GPT-4'),
    ('claude-3', 'Anthropic Claude')
]

for model, name in models:
    print(f"\n--- 使用 {name} ---")
    gen = QuickStreamingGenerator(model=model)
    for chunk in gen.generate("寫一句話"):
        print(chunk, end='', flush=True)
    print()
```

### 範例 5：直接貼文章內容生成

```python
from blog_pro_max.quick_stream import QuickStreamingGenerator

# 貼入現有文章，要求改進
article = """
AI 的發展越來越快。
每天都有新的技術出現。
...（文章內容）...
"""

generator = QuickStreamingGenerator(model='gpt-4')
prompt = f"""請改進以下文章的品質，增加深度和可讀性：

{article}

要求改進：
1. 增加數據和例子
2. 改進段落結構
3. 加入讀者關心的點"""

for chunk in generator.generate(prompt):
    print(chunk, end='', flush=True)
```

### 範例 6：錯誤處理和重試

```python
from blog_pro_max.quick_stream import QuickStreamingGenerator

generator = QuickStreamingGenerator(model='gemini-pro')

try:
    for chunk in generator.generate("寫一篇文章"):
        print(chunk, end='', flush=True)
except Exception as e:
    print(f"❌ 生成失敗: {e}")
    print("提示：檢查 API 金鑰是否正確設置")
```

### 範例 2：基於現有文章擴充內容
```python
from blog_pro_max.streaming_generator import StreamingBlogGenerator

sg = StreamingBlogGenerator(model='gemini-pro')

# 原始文章內容
original = """
# AI 的未來

人工智能正在快速發展。
隨著技術進步，AI 應用越來越廣泛。
"""

# 基於原文生成擴充版本
prompt = f"""
請基於以下文章內容，擴充成 1500 字的完整部落格文章。
保持原有主題和邏輯，添加具體例子、數據和深度分析。

原文：
{original}

擴充版本：
"""

print("正在擴充文章...\n")
for chunk in sg.generate_stream(prompt):
    print(chunk, end='', flush=True)
```

### 範例 3：讀取硬碟檔案進行優化
```python
from blog_pro_max.streaming_generator import StreamingBlogGenerator
from pathlib import Path

# 讀取原始文章
article_path = Path("./articles/draft.md")
original_content = article_path.read_text(encoding='utf-8')

sg = StreamingBlogGenerator(model='gemini-pro')

# 優化指令
optimization_prompt = f"""
請優化以下文章，改進：
1. 文筆和表達清晰度
2. 邏輯流程和段落組織
3. 添加更多具體例子
4. 改進 SEO 相關性

原文：
{original_content}

優化版本：
"""

print("正在優化文章...\n")
optimized = ""
for chunk in sg.generate_stream(optimization_prompt):
    print(chunk, end='', flush=True)
    optimized += chunk

# 儲存優化結果
output_path = Path("./articles/optimized.md")
output_path.write_text(optimized, encoding='utf-8')
print(f"\n✓ 優化完成，已保存至: {output_path}")
```

### 範例 4：批量生成多篇文章
```python
from blog_pro_max.streaming_generator import StreamingBlogGenerator
from pathlib import Path
import json

sg = StreamingBlogGenerator(model='gemini-pro')

# 待生成的主題列表
topics = [
    "AI 在醫療領域的應用",
    "機器學習工程師的職業發展",
    "自然語言處理的最新進展"
]

results = {}

for topic in topics:
    print(f"\n正在生成: {topic}")
    print("=" * 50)
    
    prompt = f"請寫一篇 1500 字的部落格文章，主題是：{topic}"
    
    article = ""
    for chunk in sg.generate_stream(prompt):
        print(chunk, end='', flush=True)
        article += chunk
    
    results[topic] = article
    print("\n")

# 儲存所有生成的文章
output = Path("./articles/generated.json")
output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"✓ 已生成 {len(results)} 篇文章，保存至: {output}")
```

### 範例 5：帶進度回調的流式生成
```python
from blog_pro_max.streaming_generator import StreamingBlogGenerator
from pathlib import Path

sg = StreamingBlogGenerator(model='gemini-pro')

# 讀取要改寫的文章
article_path = Path("./articles/original.md")
original = article_path.read_text(encoding='utf-8')

prompt = f"請用簡單易懂的方式改寫以下文章：\n\n{original}"

print("正在改寫文章...")
progress = 0
rewritten = ""

for chunk in sg.generate_stream(prompt):
    rewritten += chunk
    progress += len(chunk)
    
    # 每生成 100 字顯示進度
    if progress % 100 < len(chunk):
        print(f"[進度] {progress} 字已生成...", end='\r')

print(f"\n✓ 完成！共生成 {progress} 字")

# 儲存結果
output_path = Path("./articles/rewritten.md")
output_path.write_text(rewritten, encoding='utf-8')
```

### 範例 6：自訂流式參數
```python
from blog_pro_max.streaming_generator import StreamingBlogGenerator

sg = StreamingBlogGenerator(
    model='gemini-pro',
    temperature=0.7,  # 創意度 (0-1)
    max_tokens=2000,  # 最大產出字數
    top_p=0.95        # 多樣性參數
)

prompt = "創意寫一篇關於未來工作的科幻文章"

for chunk in sg.generate_stream(prompt):
    print(chunk, end='', flush=True)
```

---

## 在 Gemini CLI 中使用

### 方式 A：直接輸入提示詞（互動模式）
```bash
gemini "請用繁體中文寫一篇 1500 字的 AI 倫理文章，流式顯示"
```

### 方式 B：混合互動和提示（推薦）
```bash
gemini -i "我想寫一篇關於 AI 的文章"

# 然後在互動模式中：
# > 我想寫一篇關於 AI 的文章
# > 流式生成，1500 字，包含具體案例
# > 優化文筆和邏輯
```

### 方式 C：基於檔案優化（非互動模式）
```bash
gemini -p "請優化 ./articles/draft.md 這篇文章，改進文筆和結構，流式顯示結果"
```

### 方式 D：批量生成（非互動模式）
```bash
gemini -p "流式生成以下 3 個主題的文章各 1000 字：1. AI 趨勢 2. 機器學習 3. 深度學習"
```

### 方式 E：自訂參數生成
```bash
export LLM_TEMPERATURE=0.8
export LLM_MODEL=gemini-flash
gemini "請創意寫一篇科幻部落格文章，關於 AI 統治世界"
```

---

## 流式生成的實時輸出示例

### 初期（第 1-5 秒）
```
正在生成文章...
人工智能（AI）正在成為 21 世紀最重要的技術革命。從醫療診斷到自動駕駛，從語言翻譯到圖像識別，
```

### 中期（第 5-15 秒）
```
人工智能（AI）正在成為 21 世紀最重要的技術革命。從醫療診斷到自動駕駛，從語言翻譯到圖像識別，
AI 已經滲透到我們日常生活的各個角落。但隨著 AI 能力的增強，伴隨而來的是倫理問題的加劇。

本文探討四大核心議題：
1. 演算法偏見和公平性
2. 隱私保護和數據安全
3. 工作替代和經濟影響
4. 長期安全性和對齊問題
```

### 完成（第 15-25 秒）
```
[完整文章 1500 字，持續流式輸出...]
✓ 文章生成完成
耗時: 23 秒
字數: 1547
```

---

## 驗證方式

### 方式 1：觀察流式效果
```bash
# 記錄時間戳
gemini "請流式生成一篇 500 字的文章"

# 預期現象：
# ✓ 文字逐詞或逐句出現（非一次全部）
# ✓ 能實時看到生成進度
# ✓ 完成時間 < 30 秒
```

### 方式 2：Python 端驗證流式工作
```python
import time
from blog_pro_max.streaming_generator import StreamingBlogGenerator

sg = StreamingBlogGenerator(model='gemini-pro')
prompt = "請寫一篇 500 字的文章"

print("開始時間:", time.strftime("%H:%M:%S"))
chunk_count = 0
start = time.time()

for chunk in sg.generate_stream(prompt):
    print(chunk, end='', flush=True)
    chunk_count += 1
    
    # 顯示流速
    if chunk_count % 10 == 0:
        elapsed = time.time() - start
        rate = chunk_count / elapsed
        print(f" [流速: {rate:.1f} chunk/s]", end='\r')

elapsed = time.time() - start
print(f"\n✓ 生成完成")
print(f"耗時: {elapsed:.1f} 秒")
print(f"Chunks: {chunk_count}")
```

### 方式 3：檔案讀寫驗證
```python
from pathlib import Path
from blog_pro_max.streaming_generator import StreamingBlogGenerator

# 創建測試檔案
test_file = Path("test_input.md")
test_file.write_text("# 測試文章\n這是測試內容。\n", encoding='utf-8')

# 讀取、優化、寫入
content = test_file.read_text(encoding='utf-8')
sg = StreamingBlogGenerator(model='gemini-pro')
prompt = f"請優化此文章：\n{content}"

output = Path("test_output.md")
with open(output, 'w', encoding='utf-8') as f:
    for chunk in sg.generate_stream(prompt):
        f.write(chunk)
        print(chunk, end='', flush=True)

if output.stat().st_size > 0:
    print("\n✓ 檔案讀寫驗證成功")
else:
    print("\n✗ 檔案寫入失敗")

# 清理
test_file.unlink()
output.unlink()
```

---

## 常見問題

### Q: 流式和非流式有什麼差別？
**A:** 
```
流式（Streaming）：逐詞/逐句輸出，用戶可即時看到進度，適合長文本
非流式（Batch）：等待完成後一次性輸出，更簡潔但延遲明顯
```

### Q: 生成速度慢嗎？
**A:** 取決於模型和提示：
- Gemini Flash：最快（1000 字 < 15 秒）
- Gemini Pro：中等（1000 字 20-30 秒）
- GPT-4：較慢但質量最高（1000 字 40-60 秒）

### Q: 可以保存生成的文章嗎？
**A:** 可以，見範例 3、4、5，使用 `Path.write_text()` 保存

### Q: 支援哪些模型？
**A:** 任何支援 streaming API 的模型：
```python
sg = StreamingBlogGenerator(model='gemini-pro')      # Gemini
sg = StreamingBlogGenerator(model='gpt-4')           # OpenAI
sg = StreamingBlogGenerator(model='claude-3')        # Anthropic
```

### Q: 如何控制生成的內容長度和風格？
**A:** 使用 `temperature` 和 `max_tokens` 參數：
```python
sg = StreamingBlogGenerator(
    temperature=0.5,   # 較低 = 保守，較高 = 創意
    max_tokens=1500    # 最多生成 1500 字
)
```

### Q: 可以中斷生成嗎？
**A:** 可以，在任何時刻按 Ctrl+C 中斷，已生成的內容會保留

---

如需進階串接、自訂模型參數或擴展功能，請參考 blog_pro_max/streaming_generator.py 原始碼與 docstring。
