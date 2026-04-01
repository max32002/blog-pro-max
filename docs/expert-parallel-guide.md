# 專家並行化教學

## 功能簡介
- 支援多位專家（預設 6~12）同時對文章內容進行審稿、建議或評分。
- 大幅縮短評審等待時間，適用於內容審查、AI 輔助決策等場景。
- 可直接分析貼入的文本或讀取硬碟檔案進行並行評審。

## 核心概念

### 為什麼需要並行化？
```
傳統順序審查：
  審查專家 1 → 等待完成 → 審查專家 2 → 等待完成 → ... → 總時間 3-5 分鐘

並行化審查：
  專家 1, 2, 3, 4, 5, 6 同時進行 → 總時間 < 1 分鐘
```

### 12 位專家角色
1. **內容檢查官** - 檢查事實準確性、引用來源
2. **SEO 優化師** - 關鍵字、標題、描述優化
3. **可讀性顧問** - 文段長度、句子複雜度、易讀性
4. **品牌守門人** - 品牌調性、聲調一致性
5. **技術審查員** - 程式碼正確性、技術準確性
6. **編輯審查** - 語法、拼寫、標點符號
7. **結構分析師** - 邏輯流程、章節組織
8. **受眾分析師** - 目標受眾適配度、相關性
9. **創意顧問** - 創新性、獨特角度
10. **競爭分析師** - 與現有內容的差異化
11. **法律合規師** - 免責聲明、法律風險
12. **行銷顧問** - 分享性、訴求力

---

## Python 使用範例

### 範例 1：直接貼文章內容
```python
from blog_pro_max.content_research import parallel_expert_review

# 直接貼入文章
article = """
人工智能正在改變世界。AI 技術應用於各個領域，
從醫療到金融，從教育到製造。這篇文章探討 AI 的
最新發展趨勢與未來挑戰。
"""

# 12 位專家並行審查
results = parallel_expert_review(article)

# 列出所有審查結果
for expert, feedback in results.items():
    print(f"✓ {expert}:")
    print(f"  {feedback}\n")
```

### 範例 2：讀取硬碟檔案進行分析
```python
from blog_pro_max.content_research import parallel_expert_review
from pathlib import Path

# 讀取檔案
article_path = Path("./articles/ai-trends-2026.md")
article_content = article_path.read_text(encoding='utf-8')

# 執行並行審查
results = parallel_expert_review(article_content)

# 生成審查報告
report_path = Path("./reviews/ai-trends-report.txt")
with open(report_path, 'w', encoding='utf-8') as f:
    for expert, feedback in results.items():
        f.write(f"【{expert}】\n{feedback}\n\n")

print(f"✓ 審查報告已保存至: {report_path}")
```

### 範例 3：批量審查多篇文章
```python
from blog_pro_max.content_research import parallel_expert_review
from pathlib import Path
import json

# 掃描所有 markdown 檔案
article_dir = Path("./articles")
articles = list(article_dir.glob("*.md"))

all_reviews = {}

for article_file in articles:
    content = article_file.read_text(encoding='utf-8')
    print(f"正在審查: {article_file.name}...")
    
    # 並行審查
    reviews = parallel_expert_review(content)
    all_reviews[article_file.name] = reviews

# 儲存所有審查結果為 JSON
output = Path("./reviews/all-reviews.json")
output.write_text(json.dumps(all_reviews, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"✓ 批量審查完成，結果已保存")
```

### 範例 4：自訂專家和評分
```python
from blog_pro_max.content_research import parallel_expert_review

article = "你的文章內容..."

# 只指定某些專家進行評審
focus_experts = ["內容檢查官", "SEO優化師", "可讀性顧問"]
results = parallel_expert_review(article, experts=focus_experts)

# 收集評分（0-10）
scores = {}
for expert, feedback in results.items():
    # 假設 feedback 包含評分（格式示例）
    if "評分:" in feedback:
        score = int(feedback.split("評分:")[1].split("/")[0].strip())
        scores[expert] = score

# 計算平均評分
avg_score = sum(scores.values()) / len(scores) if scores else 0
print(f"平均評分: {avg_score:.1f}/10")
```

## 使用方式

### 命令行使用

```bash
# 檢查現有文章
python -m blog_pro_max.content_research --check-only output/article.md

# 只看 prompt（不執行 API）
python -m blog_pro_max.content_research --keyword "主題" --dry-run
```

---

## 在 Gemini CLI 中使用

### 方式 A：互動模式

```bash
gemini
```

然後在互動模式中提示：
```
我有一篇文章要 12 位專家並行審查，內容如下：
[貼入文章內容]
```

### 方式 B：直接執行

```bash
gemini -p "請審查以下文章：[文章內容]"
```

---
```bash
export BLOG_USER=admin
gemini -p "批量審查 ./articles/ 目錄中的所有文章"
```

### 方式 D：特定焦點審查
```bash
export BLOG_USER=admin
gemini "請讓 SEO優化師、內容檢查官、可讀性顧問這 3 位專家審查我的文章"

# 貼入文章內容，CLI 會執行並行審查
```

---

## 實際輸出示例

### 審查結果格式
```
專家並行審查結果
═════════════════════════════════════

【內容檢查官】
✓ 事實準確性: 良好
⚠ 缺少 2 個引用來源
✓ 建議補充最新數據

【SEO優化師】
⚠ 標題需要優化，建議加入主關鍵字
✓ 長尾關鍵字分佈良好
💡 建議添加目錄

【可讀性顧問】
✓ 平均句子長度: 15 詞（建議 ≤20）
⚠ 第 3 段過長（247 詞），建議分割
✓ 使用難度: 中等

[還有 9 位專家的評審結果...]

整體評分: 7.8/10 ⭐
估計閱讀時間: 4 分鐘
建議發佈: 經過小修改後可發佈
```

---

## 驗證方式

### 方式 1：觀察輸出速度
```bash
# 記錄開始時間
time gemini -p "審查文章：[文章內容]"

# 預期：< 1 分鐘完成 12 位專家審查
# 如果 > 3 分鐘，可能是順序執行而非並行
```

### 方式 2：Python 端驗證
```python
import time
from blog_pro_max.content_research import parallel_expert_review

article = "測試文章..."
start = time.time()
results = parallel_expert_review(article)
elapsed = time.time() - start

print(f"審查耗時: {elapsed:.1f} 秒")
print(f"專家數: {len(results)}")

# 並行化判斷
if elapsed < 60 and len(results) >= 6:
    print("✓ 確認為並行執行")
else:
    print("✗ 可能為順序執行，請檢查配置")
```

### 方式 3：檢查硬碟檔案讀取是否正常
```python
from pathlib import Path
from blog_pro_max.content_research import parallel_expert_review

# 創建測試檔案
test_file = Path("test_article.md")
test_content = """
# AI 測試文章
這是一篇用於測試並行審查的示範文章。
內容包含技術概念和實際應用案例。
"""
test_file.write_text(test_content, encoding='utf-8')

# 讀取並審查
content = test_file.read_text(encoding='utf-8')
results = parallel_expert_review(content)

if results and len(results) > 1:
    print("✓ 檔案讀取和並行審查成功")
else:
    print("✗ 檢查 file I/O 或並行執行配置")

# 清理
test_file.unlink()
```

---

## 常見問題

### Q: 12 位專家審查速度真的快嗎？
**A:** 是的。順序執行每個專家需 20-30 秒，12 位共需 4-5 分鐘。  
並行執行時所有專家同時進行，總耗時 < 1 分鐘。

### Q: 可以自訂專家數量嗎？
**A:** 可以。傳入 `experts` 參數：
```python
# 只用 3 位專家
results = parallel_expert_review(article, experts=3)
```

### Q: 支援哪些檔案格式？
**A:** 支援：
- `.md` (Markdown)
- `.txt` (純文本)
- `.html` (HTML)
- 其他文本格式（只要是 UTF-8 編碼）

### Q: 可以只審查特定部分嗎？
**A:** 可以。提取相關段落後傳入：
```python
# 只審查第一段
first_paragraph = article.split('\n\n')[0]
results = parallel_expert_review(first_paragraph)
```

---

如需進階自訂專家行為、調整超時時間或擴展新專家，請參考 blog_pro_max/content_research.py 原始碼與 docstring。
