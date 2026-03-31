"""
blog_generator.py — LLM 驅動的部落格文章生成引擎
"""

import os
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

try:
    from blog_pro_max.core import (
        build_system_prompt,
        render_template,
    )
except ImportError:
    from core import (
        build_system_prompt,
        render_template,
    )


def _web_search(keyword: str, max_results: int = 3) -> str:
    """使用 DuckDuckGo 搜尋與關鍵字相關的當前趨勢資料。

    需要 duckduckgo-search 套件（pip install duckduckgo-search）。
    若套件未安裝或搜尋失敗，回傳空字串（graceful fallback）。

    Returns:
        格式化的搜尋摘要字串，供注入 LLM prompt。
    """
    try:
        from ddgs import DDGS
    except ImportError:
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            return ""

    year = datetime.now().year
    queries = [
        f"{keyword} 趨勢 {year}",
        f"{keyword} 最新消息",
        f"{keyword} 熱門話題",
    ]

    results = []
    try:
        with DDGS() as ddgs:
            for query in queries:
                hits = list(ddgs.text(query, max_results=max_results))
                for h in hits:
                    title = h.get("title", "").strip()
                    body = h.get("body", "").strip()
                    if title and body:
                        results.append(f"- {title}：{body[:150]}")
    except Exception:
        return ""

    if not results:
        return ""

    return "【當前網路搜尋資料】\n" + "\n".join(results[:9])


def build_prompt(
    keyword: str,
    audience: str = "30-45 歲知識工作者",
    word_count: int = 1200,
    language: str = "zh-TW",
    template: str = "blog-skill-content",
) -> tuple[str, str]:
    """Build user prompt and system prompt from a registered template."""
    user_prompt = render_template(template, keyword, audience, word_count, language)
    system_prompt = build_system_prompt(template)
    return user_prompt, system_prompt


GITHUB_MODELS_ENDPOINT = "https://models.inference.ai.azure.com"


def _make_client() -> OpenAI:
    """Return an OpenAI-compatible client.

    Priority:
    1. GITHUB_TOKEN  → GitHub Models endpoint (free tier, no OpenAI account needed)
    2. OPENAI_API_KEY → OpenAI directly
    """
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        return OpenAI(api_key=github_token, base_url=GITHUB_MODELS_ENDPOINT)

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        return OpenAI(api_key=openai_key)

    raise EnvironmentError(
        "未設定 API 金鑰。請在 .env 中設定：\n"
        "  GITHUB_TOKEN=ghp_...   ← GitHub PAT（免費，推薦）\n"
        "  OPENAI_API_KEY=sk-...  ← OpenAI API Key"
    )


def generate_article(
    keyword: str,
    audience: str = "30-45 歲知識工作者",
    word_count: int = 1200,
    language: str = "zh-TW",
    model: str = "gpt-4o",
    template: str = "blog-skill-content",
) -> str:
    client = _make_client()
    prompt, system_message = build_prompt(
        keyword, audience, word_count, language, template
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=4096,
    )

    content = response.choices[0].message.content
    return content.strip()


def generate_titles(
    article_content: str,
    keyword: str,
    audience: str = "30-45 歲知識工作者",
    language: str = "zh-TW",
    model: str = "gpt-4o",
    count: int = 4,
) -> list[dict[str, str]]:
    """根據文章內容產出多個標題建議（含英文 permalink slug）。

    Returns:
        list of {"title": "中文標題", "slug": "english-permalink-slug"}
    """
    client = _make_client()

    system_prompt = (
        "你是一位部落格標題專家（blog-title-writer）。"
        "你擅長分析文章內容後，產出簡潔、專業、吸引人的標題。\n\n"
        "規則：\n"
        "1. 每個標題控制在 15-25 字（中文）以內\n"
        "2. 標題必須包含核心關鍵字或其同義詞\n"
        "3. 標題要適合目標受眾的閱讀偏好\n"
        "4. 風格多元：分別提供「直述型」「提問型」「數字型」「情感型」各一個\n"
        "5. 不要使用引號包住標題\n"
        "6. 每個標題同時提供英文版 permalink slug（全小寫、用連字號分隔、去除停用詞、適合 WordPress 網址）\n\n"
        "輸出格式（嚴格遵守）：\n"
        "TITLE: 中文標題\n"
        "SLUG: english-permalink-slug\n"
        "---"
    )

    user_prompt = (
        f"請根據以下文章內容，為目標受眾「{audience}」產出 {count} 個標題建議。\n\n"
        f"核心關鍵字：{keyword}\n"
        f"語言：{language}\n\n"
        f"文章內容（前 1500 字）：\n\n"
        f"{article_content[:1500]}"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.8,
        max_tokens=512,
    )

    raw = response.choices[0].message.content.strip()

    # Parse structured output
    import re
    results = []
    current = {}
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("TITLE:"):
            current["title"] = line[6:].strip()
        elif line.startswith("SLUG:"):
            slug = line[5:].strip().lower()
            slug = re.sub(r"[^a-z0-9-]", "-", slug)
            slug = re.sub(r"-+", "-", slug).strip("-")
            current["slug"] = slug
        elif line == "---" or (not line and "title" in current):
            if current.get("title"):
                current.setdefault("slug", "")
                results.append(current)
            current = {}

    # Catch last entry
    if current.get("title"):
        current.setdefault("slug", "")
        results.append(current)

    return results[:count]


def generate_cover_prompts(
    article_content: str,
    keyword: str,
    audience: str = "30-45 歲知識工作者",
    model: str = "gpt-4o",
    count: int = 3,
) -> list[dict[str, str]]:
    """根據文章內容產出封面圖片的 AI 繪圖提示詞。

    Returns:
        list of {"style": "風格名稱", "prompt": "英文提示詞", "description": "中文說明"}
    """
    client = _make_client()

    system_prompt = (
        "你是一位封面提示詞專家（cover-prompt-writer）。"
        "你擅長根據文章內容，產出適合用於 AI 繪圖工具（如 Midjourney、DALL-E、Stable Diffusion）"
        "的封面圖片提示詞。\n\n"
        "規則：\n"
        "1. 提示詞必須是英文（AI 繪圖工具主要支援英文）\n"
        "2. 每個提示詞包含：主體描述、風格、色調、構圖、氛圍\n"
        "3. 避免包含文字元素（AI 繪圖不擅長生成文字）\n"
        "4. 提供不同風格：寫實攝影風、插畫風、極簡設計風\n"
        "5. 每個提示詞控制在 50-100 個英文單詞\n"
        "6. 適合作為部落格文章封面，16:9 或 3:2 比例\n\n"
        "輸出格式（嚴格遵守，每個提示詞一組）：\n"
        "STYLE: 風格名稱（中文）\n"
        "PROMPT: 英文提示詞\n"
        "DESC: 中文說明（一句話描述這張圖的意境）\n"
        "---"
    )

    user_prompt = (
        f"請根據以下文章內容，產出 {count} 組封面圖片的 AI 繪圖提示詞。\n\n"
        f"核心關鍵字：{keyword}\n"
        f"目標受眾：{audience}\n\n"
        f"文章內容（前 1000 字）：\n\n"
        f"{article_content[:1000]}"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.8,
        max_tokens=1024,
    )

    raw = response.choices[0].message.content.strip()

    # Parse structured output
    results = []
    current = {}
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("STYLE:"):
            current["style"] = line[6:].strip()
        elif line.startswith("PROMPT:"):
            current["prompt"] = line[7:].strip()
        elif line.startswith("DESC:"):
            current["description"] = line[5:].strip()
        elif line == "---" or (not line and "style" in current and "prompt" in current):
            if current.get("style") and current.get("prompt"):
                current.setdefault("description", "")
                results.append(current)
            current = {}

    # Catch last entry
    if current.get("style") and current.get("prompt"):
        current.setdefault("description", "")
        results.append(current)

    return results[:count]


# ── 三維度審稿專家 ────────────────────────────────────

def _parse_review_items(raw: str) -> list[dict[str, str]]:
    """Parse structured review output (ISSUE/SUGGEST/BEFORE/AFTER blocks)."""
    results = []
    current: dict[str, str] = {}
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("ISSUE:"):
            if current.get("issue"):
                results.append(current)
            current = {"issue": line[6:].strip()}
        elif line.startswith("SUGGEST:"):
            current["suggest"] = line[8:].strip()
        elif line.startswith("BEFORE:"):
            current["before"] = line[7:].strip()
        elif line.startswith("AFTER:"):
            current["after"] = line[6:].strip()
        elif line == "---":
            if current.get("issue"):
                results.append(current)
            current = {}
    if current.get("issue"):
        results.append(current)
    return results


def review_logic(
    article_content: str,
    keyword: str,
    audience: str = "30-45 歲知識工作者",
    model: str = "gpt-4o",
) -> list[dict[str, str]]:
    """邏輯與事實專家：檢查數據正確性、邏輯一致性、錯別字。

    Returns:
        list of {"issue": ..., "suggest": ..., "before": ..., "after": ...}
    """
    client = _make_client()

    system_prompt = (
        "你是一位邏輯與事實專家（logic-fact-checker）。\n"
        "你的任務是嚴格校對文章，找出所有硬傷，包括：\n\n"
        "1. **數據錯誤**：引用的數據、百分比、年份是否合理且正確；若無來源，請標記為「需查證」\n"
        "2. **邏輯矛盾**：論點是否前後矛盾、因果關係是否真的成立，還是只是相關性被誤當因果\n"
        "3. **論點跳躍**：是否有從 A 直接跳到 C 而略過 B 的情況，讓讀者無法跟上推理過程\n"
        "4. **錯別字與用詞錯誤**：錯字、同音字誤用、語法不通、不合邏輯的用詞\n"
        "5. **來源可信度**：引用的觀點是否缺乏根據，是否有常見的 AI 幻覺（例如：捏造的研究或名人語錄）\n\n"
        "你就像嚴格的校對人員，確保文章基礎穩固且具公信力。\n"
        "每個問題必須附上可直接套用的修改後版本（AFTER），不能只說「建議修改」而不給出範例。\n\n"
        "輸出格式（嚴格遵守，每個問題一組）：\n"
        "ISSUE: 問題描述（含位置提示，如「第 X 段」）\n"
        "SUGGEST: 具體修改建議（說明為什麼這樣改）\n"
        "BEFORE: 原文片段\n"
        "AFTER: 修改後的完整文字\n"
        "---\n\n"
        "如果沒有發現任何問題，輸出：\n"
        "ISSUE: 未發現邏輯或事實問題\n"
        "SUGGEST: 文章在邏輯與事實層面表現良好\n"
        "---"
    )

    user_prompt = (
        f"請檢查以下文章的邏輯與事實正確性。\n\n"
        f"核心關鍵字：{keyword}\n"
        f"目標受眾：{audience}\n\n"
        f"文章內容：\n\n{article_content[:3000]}"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=2048,
    )

    return _parse_review_items(response.choices[0].message.content.strip())


def review_structure(
    article_content: str,
    keyword: str,
    audience: str = "30-45 歲知識工作者",
    model: str = "gpt-4o",
) -> list[dict[str, str]]:
    """深度與結構專家：分析內容廣度、遺漏面向、段落轉折。

    Returns:
        list of {"issue": ..., "suggest": ..., "before": ..., "after": ...}
    """
    client = _make_client()

    system_prompt = (
        "你是一位深度與結構專家（depth-structure-reviewer）。\n"
        "你的任務是分析文章的內容廣度、結構品質與敘事連貫性，包括：\n\n"
        "1. **敘事主線**：全文是否有一條清楚的邏輯或敘事主線？讀者讀完能不能說出「這篇在講什麼」？\n"
        "2. **段落轉折與銜接**：段落之間是否有自然的銜接語句？是否有突兀的話題跳躍？\n"
        "   - 例如：從 A 段到 B 段，讀者是否能理解「為什麼接下來要講這個」？\n"
        "3. **遺漏面向**：讀者可能感興趣但文章未涵蓋的關鍵角度，補上後能讓文章更完整\n"
        "4. **論述深度**：哪些段落只有表面陳述，缺乏具體例子或說明？\n"
        "5. **引用後的說明**：引用數據、例子或比喻後，是否有說明「這對讀者意味著什麼」？\n"
        "6. **結構平衡**：各段落的篇幅比例是否合理，重點是否突出？開頭是否夠強？結尾是否呼應開頭？\n\n"
        "你提供的加值在於：讓文章從「資訊堆疊」升級為「有邏輯有溫度的完整敘事」。\n"
        "每個問題必須附上可直接套用的修改後版本（AFTER），不能只說「建議增加」而不給出範例。\n\n"
        "輸出格式（嚴格遵守，每個問題一組）：\n"
        "ISSUE: 問題描述（如「缺少 XX 面向」或「第 X→Y 段轉折生硬」）\n"
        "SUGGEST: 具體修改建議（說明如何改善，及為什麼這樣改讀者更能理解）\n"
        "BEFORE: 原文片段（轉折或銜接問題時必須提供）\n"
        "AFTER: 修改後的完整文字\n"
        "---\n\n"
        "如果沒有發現任何問題，輸出：\n"
        "ISSUE: 未發現結構或連貫性問題\n"
        "SUGGEST: 文章在深度與結構層面表現良好\n"
        "---"
    )

    user_prompt = (
        f"請分析以下文章的內容深度、結構品質與敘事連貫性。\n\n"
        f"核心關鍵字：{keyword}\n"
        f"目標受眾：{audience}\n\n"
        f"文章內容：\n\n{article_content[:3000]}"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.5,
        max_tokens=2048,
    )

    return _parse_review_items(response.choices[0].message.content.strip())


def review_reader(
    article_content: str,
    keyword: str,
    audience: str = "30-45 歲知識工作者",
    model: str = "gpt-4o",
) -> list[dict[str, str]]:
    """讀者視角專家：評估口吻、易讀性、受眾適配度。

    Returns:
        list of {"issue": ..., "suggest": ..., "before": ..., "after": ...}
    """
    client = _make_client()

    system_prompt = (
        "你是一位讀者視角專家（reader-perspective-reviewer）。\n"
        "你的任務是站在目標受眾的角度，評估文章的可讀性、理解難度與情感吸引力：\n\n"
        "1. **理解難度**：是否有讓讀者「看不懂」的地方？\n"
        "   - 術語未解釋、省略太多背景、句子之間缺乏過渡讓讀者摸不著頭緒\n"
        "   - 讀者不應該需要回頭重讀才能理解一段話的意思\n"
        "2. **口吻適配**：語氣是否適合目標受眾？太正式或太隨意？有無讓人感到被說教的語句？\n"
        "3. **注意力留存**：哪些段落太長、太枯燥、或資訊密度過高，可能讓讀者分心或想跳過？\n"
        "4. **上下文連貫**：讀者是否能輕鬆跟上文章的思路？有無段落讓人感覺「突然換話題」？\n"
        "5. **情感共鳴**：開頭是否吸引人？結尾是否有力？讀者讀完後會有什麼感受，是否達到文章想要的效果？\n"
        "6. **語言友善度**：用詞是否在目標受眾能理解的範圍內？有無過於生硬的成語或學術術語？\n\n"
        "你的標準是：讀者看不懂就是無效文章。每個建議必須具體說明「讀者在哪裡會卡住，以及如何讓他不卡住」。\n"
        "每個問題必須附上可直接套用的修改後版本（AFTER），不能只說「建議簡化」而不給出範例。\n\n"
        "輸出格式（嚴格遵守，每個問題一組）：\n"
        "ISSUE: 問題描述（如「第 X 段術語過多，讀者可能在此流失」）\n"
        "SUGGEST: 具體修改建議（說明為什麼讀者會卡在這裡，以及改後為何更好理解）\n"
        "BEFORE: 原文片段\n"
        "AFTER: 修改後的完整文字\n"
        "---\n\n"
        "如果沒有發現任何問題，輸出：\n"
        "ISSUE: 未發現讀者體驗問題\n"
        "SUGGEST: 文章在讀者視角層面表現良好\n"
        "---"
    )

    user_prompt = (
        f"請站在以下目標受眾的角度，嚴格評估這篇文章的可讀性、理解難度與情感吸引力。\n"
        f"標準是：讀者看不懂就是無效文章。\n\n"
        f"核心關鍵字：{keyword}\n"
        f"目標受眾：{audience}\n\n"
        f"文章內容：\n\n{article_content[:3000]}"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.5,
        max_tokens=2048,
    )

    return _parse_review_items(response.choices[0].message.content.strip())


# ── 時事趨勢專家 ──────────────────────────────────────

def _parse_trend_sections(raw: str) -> dict[str, str]:
    """Parse structured trend analysis output into 4 sections."""
    sections = {}
    current_key = None
    current_lines: list[str] = []

    section_markers = {
        "TREND_ANALYSIS:": "trend_analysis",
        "ANGLE_SUGGESTIONS:": "angle_suggestions",
        "KEYWORDS_TAGS:": "keywords_tags",
        "REWRITE_DEMO:": "rewrite_demo",
    }

    for line in raw.splitlines():
        stripped = line.strip()
        matched = False
        for marker, key in section_markers.items():
            if stripped.startswith(marker):
                if current_key and current_lines:
                    sections[current_key] = "\n".join(current_lines).strip()
                current_key = key
                remainder = stripped[len(marker):].strip()
                current_lines = [remainder] if remainder else []
                matched = True
                break
        if not matched and current_key is not None:
            current_lines.append(line.rstrip())

    if current_key and current_lines:
        sections[current_key] = "\n".join(current_lines).strip()

    return sections


def review_trend(
    article_content: str,
    keyword: str,
    audience: str = "30-45 歲知識工作者",
    model: str = "gpt-4o",
) -> dict[str, str]:
    """時事趨勢專家：分析文章與當前趨勢的關聯，提供時事切入建議。

    Returns:
        dict with keys: trend_analysis, angle_suggestions, keywords_tags, rewrite_demo
    """
    client = _make_client()

    system_prompt = (
        "你是一位時事趨勢專家（trend-scout）。\n"
        "你擅長將文章內容與當前社會熱議話題、新聞事件、社群趨勢建立關聯，\n"
        "並提供具體的時事切入角度，讓文章更有時效性與傳播力。\n\n"
        "你的分析必須包含以下四個區塊，嚴格遵守輸出格式：\n\n"
        "TREND_ANALYSIS:\n"
        "（趨勢關聯分析）\n"
        "- 點出文章內容與哪些當前社會熱議話題、新聞事件或社群梗圖有關聯\n"
        "- 說明為什麼這個連結是合理的\n"
        "- 分析目前的討論熱度（高/中/低）\n"
        "- 列出 2-3 個相關的趨勢話題\n\n"
        "ANGLE_SUGGESTIONS:\n"
        "（切入角度建議）\n"
        "- 針對同一個時事，提供 2-3 個不同的發揮方向\n"
        "- 每個方向說明適合什麼類型的品牌或讀者\n"
        "- 用一句話描述該角度的核心訴求\n\n"
        "KEYWORDS_TAGS:\n"
        "（關鍵字與標籤優化）\n"
        "- 列出 5-8 個與該時事相關的高流量搜尋關鍵字\n"
        "- 提供 5-8 個建議的社群 Hashtag（可直接複製使用）\n"
        "- 標註哪些關鍵字目前搜尋趨勢上升中\n\n"
        "REWRITE_DEMO:\n"
        "（內容改寫示範）\n"
        "- 選取原文章的一小段（2-3 句），標示為「原文」\n"
        "- 示範如何加入時事元素進行修飾，標示為「改寫」\n"
        "- 簡要說明改寫的策略與效果\n\n"
        "以繁體中文回答。"
    )

    user_prompt = (
        f"請分析以下文章與當前時事趨勢的關聯，並提供切入建議。\n\n"
        f"核心關鍵字：{keyword}\n"
        f"目標受眾：{audience}\n\n"
    )

    web_context = _web_search(keyword)
    if web_context:
        user_prompt += f"{web_context}\n\n請根據以上搜尋資料進行分析，讓建議貼近當前實際趨勢。\n\n"
    else:
        user_prompt += "（網路搜尋不可用，請依照你的知識庫進行分析）\n\n"

    user_prompt += f"文章內容：\n\n{article_content[:3000]}"

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.6,
        max_tokens=2048,
    )

    return _parse_trend_sections(response.choices[0].message.content.strip())


def generate_divergent(
    article_content: str,
    keyword: str,
    audience: str = "30-45 歲知識工作者",
    model: str = "gpt-4o",
) -> str:
    """發散專家：針對每個 H2 段落延伸相關話題、跨領域聯想，提供後續文章題目建議。

    Returns:
        格式化的 Markdown 區塊字串。
    """
    client = _make_client()

    system_prompt = (
        "你是一位發散專家（divergent-thinker）。\n"
        "針對文章的每一個 H2 段落，運用想像力與獨創力，延伸到相關話題、跨領域聯想或意想不到的切入角度。\n\n"
        "嚴格按照以下格式輸出，每個 H2 段落各輸出一組：\n\n"
        "### 段落：[H2 標題]\n\n"
        "**延伸方向 1：** 與 [相關領域/話題] 的連結 — 一句話說明如何延伸\n\n"
        "**延伸方向 2：** 跨領域聯想 — 把這個概念套用在 [完全不同的情境] 上\n\n"
        "**延伸方向 3：** 更深一層 — 追問「為什麼」或「然後呢」可以發展到哪裡\n\n"
        "**潛在後續文章題目：** 1-2 個可以獨立成篇的相關主題\n\n"
        "以繁體中文回答。"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": (
                f"請針對以下文章的每個 H2 段落進行發散思考。\n\n"
                f"核心關鍵字：{keyword}\n目標受眾：{audience}\n\n"
                f"文章內容：\n\n{article_content[:4000]}"
            )},
        ],
        temperature=0.8,
        max_tokens=2048,
    )

    raw = response.choices[0].message.content.strip()
    block = "\n\n---\n\n## 🌀 發散專家建議\n\n"
    block += "> 以下由「發散專家」自動產出，針對每個段落提供創意延伸話題，供作者參考發展後續內容。\n\n"
    block += raw
    return block


def generate_questions(
    article_content: str,
    keyword: str,
    audience: str = "30-45 歲知識工作者",
    model: str = "gpt-4o",
) -> str:
    """問題專家：針對每個 H2 段落提出 3-5 個讀者可能浮現的疑問。

    Returns:
        格式化的 Markdown 區塊字串。
    """
    client = _make_client()

    system_prompt = (
        "你是一位問題專家（question-raiser）。\n"
        "針對文章的每一個 H2 段落，提出 3-5 個讀者可能浮現的疑問，幫助作者發現論述缺口。\n\n"
        "嚴格按照以下格式輸出，每個 H2 段落各輸出一組：\n\n"
        "### 段落：[H2 標題]\n\n"
        "1. [問題 1]\n"
        "2. [問題 2]\n"
        "3. [問題 3]\n"
        "4. [問題 4]（選填）\n"
        "5. [問題 5]（選填）\n\n"
        "以繁體中文回答。"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": (
                f"請針對以下文章的每個 H2 段落提出讀者可能的疑問。\n\n"
                f"核心關鍵字：{keyword}\n目標受眾：{audience}\n\n"
                f"文章內容：\n\n{article_content[:4000]}"
            )},
        ],
        temperature=0.7,
        max_tokens=1536,
    )

    raw = response.choices[0].message.content.strip()
    block = "\n\n---\n\n## ❓ 問題專家建議\n\n"
    block += "> 以下由「問題專家」自動產出，針對每個段落提出讀者可能的疑問，供作者補充說明或延伸討論。\n\n"
    block += raw
    return block


def generate_memes(
    article_content: str,
    keyword: str,
    audience: str = "30-45 歲知識工作者",
    model: str = "gpt-4o",
) -> str:
    """迷因專家：針對每個 H2 段落提出迷因、梗圖與幽默元素關鍵字。

    Returns:
        格式化的 Markdown 區塊字串。
    """
    client = _make_client()

    system_prompt = (
        "你是一位迷因專家（meme-suggester）。\n"
        "針對文章的每一個 H2 段落，提出相關的迷因、梗圖或幽默元素，讓嚴肅內容更輕鬆易讀。\n\n"
        "嚴格按照以下格式輸出，每個 H2 段落各輸出一組：\n\n"
        "### 段落：[H2 標題]\n\n"
        "**迷因關鍵字：** 關鍵字1、關鍵字2、關鍵字3\n\n"
        "**梗圖場景：** 一句話描述可以做成梗圖的場景（例：「當你說要開始XX，結果發現YY」）\n\n"
        "**輕鬆開場句：** 用幽默方式重新描述這個段落的核心概念（一句話，可直接用在文章或社群貼文）\n\n"
        "以繁體中文回答。"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": (
                f"請針對以下文章的每個 H2 段落提出迷因與幽默元素。\n\n"
                f"核心關鍵字：{keyword}\n目標受眾：{audience}\n\n"
                f"文章內容：\n\n{article_content[:4000]}"
            )},
        ],
        temperature=0.9,
        max_tokens=1536,
    )

    raw = response.choices[0].message.content.strip()
    block = "\n\n---\n\n## 😂 迷因專家建議\n\n"
    block += "> 以下由「迷因專家」自動產出，針對每個段落提出幽默/迷因元素，幫助讀者在輕鬆氛圍中吸收內容。\n\n"
    block += raw
    return block


def generate_interjections(
    article_content: str,
    keyword: str,
    audience: str = "30-45 歲知識工作者",
    model: str = "gpt-4o",
) -> str:
    """插話專家：針對每個 H2 段落提供一個具體舉例說明，附建議插入位置。

    Returns:
        格式化的 Markdown 區塊字串。
    """
    client = _make_client()

    system_prompt = (
        "你是一位插話專家（example-inserter）。\n"
        "針對文章的每一個 H2 段落，提供一個具體的舉例說明，幫助讀者更容易理解段落的核心概念。\n\n"
        "嚴格按照以下格式輸出，每個 H2 段落各輸出一組：\n\n"
        "### 段落：[H2 標題]\n\n"
        "**建議插入的舉例：**\n\n"
        "舉例說明內容（以「舉個例子來說，」或「就好比說，」開頭，100 字以內）\n\n"
        "**建議插入位置：** 段落第 N 句之後\n\n"
        "以繁體中文回答。"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": (
                f"請針對以下文章的每個 H2 段落提供舉例說明。\n\n"
                f"核心關鍵字：{keyword}\n目標受眾：{audience}\n\n"
                f"文章內容：\n\n{article_content[:4000]}"
            )},
        ],
        temperature=0.7,
        max_tokens=1536,
    )

    raw = response.choices[0].message.content.strip()
    block = "\n\n---\n\n## 💬 插話專家建議\n\n"
    block += "> 以下由「插話專家」自動產出，每個段落附上舉例說明，可直接插入對應段落。\n\n"
    block += raw
    return block


def generate_illustrations(
    article_content: str,
    keyword: str,
    audience: str = "30-45 歲知識工作者",
    model: str = "gpt-4o",
) -> str:
    """插畫專家：針對每個 H2 段落產出 3 組風格的 AI 圖片生成提示詞。

    Returns:
        格式化的 Markdown 區塊字串。
    """
    client = _make_client()

    system_prompt = (
        "你是一位插畫專家（illustration-prompter）。\n"
        "針對文章的每一個 H2 段落，產出 3 組風格不同的 AI 圖片生成提示詞（英文），"
        "作為該段落的示意圖使用。\n\n"
        "三種風格：\n"
        "- 寫實攝影風：照片感，適合真實場景呈現\n"
        "- 插畫風：溫暖手繪感，適合生活或故事類段落\n"
        "- 極簡圖示風：乾淨的線條圖形，適合說明步驟或概念\n\n"
        "嚴格按照以下格式輸出，每個 H2 段落各輸出一組：\n\n"
        "### 段落：[H2 標題]\n\n"
        "**1. 寫實攝影風**\n"
        "Prompt: A realistic photo of ..., natural lighting, --ar 16:9\n\n"
        "**2. 插畫風**\n"
        "Prompt: A warm hand-drawn illustration of ..., soft colors, flat style --ar 16:9\n\n"
        "**3. 極簡圖示風**\n"
        "Prompt: A minimal icon illustration of ..., clean lines, white background --ar 1:1\n\n"
        "Prompt 必須用英文撰寫。以繁體中文輸出段落標題即可。"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": (
                f"請針對以下文章的每個 H2 段落產出 AI 圖片提示詞。\n\n"
                f"核心關鍵字：{keyword}\n目標受眾：{audience}\n\n"
                f"文章內容：\n\n{article_content[:4000]}"
            )},
        ],
        temperature=0.8,
        max_tokens=2048,
    )

    raw = response.choices[0].message.content.strip()
    block = "\n\n---\n\n## 🖼️ 插畫專家建議\n\n"
    block += "> 以下由「插畫專家」自動產出，每個段落提供 3 組風格的 AI 圖片提示詞。\n\n"
    block += raw
    return block


def generate_devil_advocate(
    article_content: str,
    keyword: str,
    audience: str = "30-45 歲知識工作者",
    model: str = "gpt-4o",
) -> str:
    """唱反調專家：針對每個 H2 段落提出反駁觀點，幫助作者強化說服力。

    Returns:
        格式化的 Markdown 區塊字串。
    """
    client = _make_client()

    system_prompt = (
        "你是一位唱反調專家（devil-advocate）。\n"
        "針對文章每一個 H2 段落的核心論點，提出反駁觀點或反例，"
        "幫助作者預先思考讀者的挑戰，強化文章的說服力。\n\n"
        "嚴格按照以下格式輸出，每個 H2 段落各輸出一組：\n\n"
        "### 段落：[H2 標題]\n\n"
        "**反駁觀點：** 一句話提出反面立場\n\n"
        "**理由：** 簡短說明為什麼這個論點可能不成立（2-3 句話）\n\n"
        "**建議回應：** 作者可以如何在文章中預先化解這個質疑（1-2 句話）\n\n"
        "以繁體中文回答。"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": (
                f"請針對以下文章的每個 H2 段落提出反駁觀點。\n\n"
                f"核心關鍵字：{keyword}\n目標受眾：{audience}\n\n"
                f"文章內容：\n\n{article_content[:4000]}"
            )},
        ],
        temperature=0.7,
        max_tokens=2048,
    )

    raw = response.choices[0].message.content.strip()
    block = "\n\n---\n\n## 🔴 唱反調專家報告\n\n"
    block += "> 以下由「唱反調專家」自動產出，針對每個段落提出反駁，供作者參考強化論點。\n\n"
    block += raw
    return block
