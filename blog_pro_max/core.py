"""
core.py — blog-pro-max 核心調度器

負責環境初始化、腳本調度、配置管理、輸出格式化。
相當於專案經理，統一管理所有資源與子程序的執行。
"""

import json
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

# Ensure UTF-8 output on all platforms
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

try:
    from blog_pro_max._resources import RESOURCE_ROOT, get_resource_path, get_writing_style_path
except ImportError:
    # Fallback for scripts/ direct execution
    RESOURCE_ROOT = Path(__file__).resolve().parent.parent

    def get_resource_path(relative_path: str) -> Path:
        return RESOURCE_ROOT / relative_path

    def get_writing_style_path() -> Path:
        return RESOURCE_ROOT / "writing-style.md"

# RESOURCE_ROOT = where bundled assets live (package dir or project root in dev mode)
# WORKING_DIR   = user's current working directory (for output, status scanning)

# ── 目錄結構定義 ──────────────────────────────────────

# In package mode, scripts are Python modules (no scripts/ dir needed).
# templates/ and resource files are checked from RESOURCE_ROOT.
# output/ is in the working directory.
REQUIRED_RESOURCE_DIRS = ["templates"]
REQUIRED_FILES = {
    "copilot.json": "Copilot skill 設定",
    "writing-style.md": "品牌寫作風格指南",
}

# ── 模板註冊表 ────────────────────────────────────────

TEMPLATES = {
    "blog-skill-content": {
        "path": "templates/blog-skill-content.md",
        "description": "SEO 部落格文章（專業、精簡、直接）",
        "style_guide": "writing-style.md",
        "system_prompt": (
            "你是一位專業的中文 SEO 內容創作者。"
            "請嚴格遵守以下寫作風格指南：\n\n{style_guide}\n\n"
            "重要規則：\n"
            "1. 開頭直接切入主題，不寫空泛引言\n"
            "2. 每句話要有明確目的\n"
            "3. 提供具體觀點，不模糊帶過\n"
            "4. 輸出純 Markdown 格式，包含 frontmatter"
        ),
    },
    "max-personal-style": {
        "path": "templates/max-personal-style.md",
        "description": "Max 個人風格（心情筆記、生活化、自我反思）",
        "style_guide": None,
        "system_prompt": (
            "你是作家 Max 的代筆 AI。"
            "請以 Max 的寫作風格來撰寫——注重個人真實感受、生活化敘事、自我反思與哲學內涵。\n\n"
            "核心規則：\n"
            "1. 第一人稱「我」，語調口語自然，像和朋友聊天\n"
            "2. 誠實直白，偶爾自嘲，不包裝情緒\n"
            "3. 用生活經驗呈現哲理，不說教\n"
            "4. 短句為主，像心情筆記\n"
            "5. Emoji 僅限臉部表情（😊 😅 🤔 😢 😂）\n"
            "6. 只用 H1、H2，不用 H3 以下\n"
            "7. 輸出純 Markdown 格式，包含 frontmatter"
        ),
    },
    "fb-post-style": {
        "path": "templates/fb-post-style.md",
        "description": "Facebook 貼文風格（口語化、純文字、社群互動）",
        "style_guide": None,
        "system_prompt": (
            "你是一位擅長經營 Facebook 的社群內容創作者。\n\n"
            "核心規則：\n"
            "1. 口語化句子，像在咖啡廳跟朋友聊天\n"
            "2. 段落之間一定要有明顯的空行\n"
            "3. 段落標題用「▋ 」（方塊 + 空格）開頭，不用 Markdown #\n"
            "4. 完全避免內縮，所有文字靠左\n"
            "5. 第一句話要是鉤子，讓人停下來看\n"
            "6. 結尾加互動提問，引導留言\n"
            "7. 適度使用表情符號，不過度裝飾\n"
            "8. 輸出純文字格式，不使用 Markdown 語法\n"
            "9. 結尾附上相關 hashtag"
        ),
    },
    "line-message-style": {
        "path": "templates/line-message-style.md",
        "description": "LINE 訊息風格（簡短、親切、純文字、好朋友分享）",
        "style_guide": None,
        "system_prompt": (
            "你是一位擅長用 LINE 分享好文的內容創作者。\n\n"
            "核心規則：\n"
            "1. 每句話控制在 20 字以內，簡短為王\n"
            "2. 語氣像好朋友傳 LINE 訊息，親切口語化\n"
            "3. 國中生也能理解的用詞\n"
            "4. 不可使用 Markdown 語法或內縮\n"
            "5. 子項目用符號（✦ ◆ ●）+ 斷行，第二層用「　→ 」\n"
            "6. 大方使用表情符號增加親切感\n"
            "7. 分享心得為主，不是寫論文\n"
            "8. 輸出純文字格式，適合直接貼到 LINE"
        ),
    },
}


@dataclass
class ProjectConfig:
    """從 copilot.json 與環境變數讀取的專案設定"""
    name: str = "blog-pro-max"
    description: str = ""
    runtime: str = "python3"
    entrypoint: str = "scripts/content_research.py"
    default_template: str = "blog-skill-content"
    default_language: str = "zh-TW"
    default_audience: str = "30-45 歲知識工作者"
    default_word_count: int = 1200
    default_model: str = "gpt-4o"
    project_root: Path = field(default_factory=lambda: RESOURCE_ROOT)

    @classmethod
    def load(cls) -> "ProjectConfig":
        config_path = RESOURCE_ROOT / "copilot.json"
        config = cls()
        if config_path.exists():
            data = json.loads(config_path.read_text(encoding="utf-8"))
            config.name = data.get("name", config.name)
            config.description = data.get("description", config.description)
            config.runtime = data.get("runtime", config.runtime)
            config.entrypoint = data.get("entrypoint", config.entrypoint)
        return config


# ── 環境初始化 (Bootstrap) ────────────────────────────

@dataclass
class BootstrapIssue:
    level: str  # "error" or "warning"
    message: str


def bootstrap() -> list[BootstrapIssue]:
    """檢查專案目錄結構是否完整，回傳問題清單。

    資源檔案 (templates, config) 從 RESOURCE_ROOT 檢查，
    output 目錄自動在工作目錄建立。
    """
    issues = []

    # Check bundled resource directories
    for dir_name in REQUIRED_RESOURCE_DIRS:
        dir_path = RESOURCE_ROOT / dir_name
        if not dir_path.is_dir():
            issues.append(BootstrapIssue(
                level="error",
                message=f"缺少必要目錄：{dir_name}/",
            ))

    for filename, desc in REQUIRED_FILES.items():
        file_path = RESOURCE_ROOT / filename
        if not file_path.is_file():
            issues.append(BootstrapIssue(
                level="error",
                message=f"缺少必要檔案：{filename}（{desc}）",
            ))

    for name, tmpl in TEMPLATES.items():
        tmpl_path = RESOURCE_ROOT / tmpl["path"]
        if not tmpl_path.is_file():
            issues.append(BootstrapIssue(
                level="warning",
                message=f"模板不存在：{tmpl['path']}（{name}）",
            ))

    return issues


def ensure_environment() -> bool:
    """執行環境檢查，印出結果，回傳是否通過。"""
    issues = bootstrap()
    errors = [i for i in issues if i.level == "error"]
    warnings = [i for i in issues if i.level == "warning"]

    if not issues:
        return True

    if warnings:
        for w in warnings:
            print(f"  ⚠️  {w.message}")

    if errors:
        for e in errors:
            print(f"  ❌ {e.message}")
        return False

    return True


# ── 模板管理 ──────────────────────────────────────────

def list_templates() -> dict[str, dict]:
    """回傳所有已註冊的模板資訊。"""
    result = {}
    for name, tmpl in TEMPLATES.items():
        tmpl_path = RESOURCE_ROOT / tmpl["path"]
        result[name] = {
            "description": tmpl["description"],
            "path": tmpl["path"],
            "exists": tmpl_path.is_file(),
        }
    return result


def get_template(name: str) -> dict:
    """取得指定模板設定。若不存在則 raise KeyError。"""
    if name not in TEMPLATES:
        available = ", ".join(TEMPLATES.keys())
        raise KeyError(f"模板「{name}」不存在。可用模板：{available}")
    return TEMPLATES[name]


def load_template_content(name: str) -> str:
    """讀取模板檔案內容。"""
    tmpl = get_template(name)
    tmpl_path = RESOURCE_ROOT / tmpl["path"]
    if not tmpl_path.is_file():
        raise FileNotFoundError(f"模板檔案不存在：{tmpl_path}")
    return tmpl_path.read_text(encoding="utf-8")


def build_system_prompt(template_name: str) -> str:
    """根據模板組裝 system prompt，包含風格指南（如適用）。"""
    tmpl = get_template(template_name)
    system_prompt = tmpl["system_prompt"]

    if tmpl["style_guide"]:
        guide_path = RESOURCE_ROOT / tmpl["style_guide"]
        if guide_path.is_file():
            guide_content = guide_path.read_text(encoding="utf-8")
            system_prompt = system_prompt.replace("{style_guide}", guide_content)

    return system_prompt


def render_template(
    template_name: str,
    keyword: str,
    audience: str = "30-45 歲知識工作者",
    word_count: int = 1200,
    language: str = "zh-TW",
) -> str:
    """讀取模板並填入變數。"""
    content = load_template_content(template_name)
    content = content.replace("{keyword}", keyword)
    content = content.replace("{audience}", audience)
    content = content.replace("{word_count}", str(word_count))
    content = content.replace("{language}", language)
    content = content.replace("{date}", date.today().isoformat())
    return content


# ── 輸出格式化 ────────────────────────────────────────

def format_output_path(keyword: str, template_name: str = "") -> Path:
    """產生輸出檔案路徑。"""
    import re
    slug = re.sub(r"[^\w\s-]", "", keyword)
    slug = re.sub(r"[\s]+", "-", slug.strip()).lower()[:80]
    return Path.cwd() / "output" / f"{slug}.md"


def format_status_report(
    keyword: str,
    template_name: str,
    output_path: Path,
    style_passed: bool | None = None,
) -> str:
    """產生結構化的狀態報告 Markdown。"""
    tmpl = TEMPLATES.get(template_name, {})
    lines = [
        "---",
        "## 📊 文章生成狀態報告",
        "",
        f"- **關鍵字**：{keyword}",
        f"- **模板**：{template_name}（{tmpl.get('description', '未知')}）",
        f"- **輸出路徑**：{output_path}",
        f"- **檔案存在**：{'✅ 是' if output_path.is_file() else '❌ 否'}",
    ]
    if style_passed is not None:
        lines.append(f"- **風格檢查**：{'✅ 通過' if style_passed else '⚠️ 有問題'})")
    lines.append("---")
    return "\n".join(lines)


# ── 專案狀態掃描 ──────────────────────────────────────

def scan_project_status() -> str:
    """掃描專案現況，回傳結構化報告。"""
    lines = [
        "# 📋 blog-pro-max 專案狀態",
        "",
    ]

    # Environment check
    issues = bootstrap()
    if issues:
        lines.append("## 環境問題")
        for issue in issues:
            prefix = "❌" if issue.level == "error" else "⚠️"
            lines.append(f"- {prefix} {issue.message}")
        lines.append("")
    else:
        lines.append("## ✅ 環境完整")
        lines.append("")

    # Templates
    lines.append("## 可用模板")
    for name, info in list_templates().items():
        status = "✅" if info["exists"] else "❌"
        lines.append(f"- {status} `{name}` — {info['description']}")
    lines.append("")

    # Output files
    output_dir = Path.cwd() / "output"
    if output_dir.is_dir():
        md_files = list(output_dir.glob("*.md"))
        lines.append(f"## 已生成文章（{len(md_files)} 篇）")
        for f in sorted(md_files):
            size = f.stat().st_size
            lines.append(f"- `{f.name}`（{size:,} bytes）")
    else:
        lines.append("## 已生成文章：0 篇")
    lines.append("")

    return "\n".join(lines)


# ── CLI 入口（除錯用）─────────────────────────────────

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"

    if cmd == "status":
        print(scan_project_status())
    elif cmd == "check":
        ok = ensure_environment()
        sys.exit(0 if ok else 1)
    elif cmd == "templates":
        for name, info in list_templates().items():
            status = "✅" if info["exists"] else "❌"
            print(f"  {status} {name:25s} {info['description']}")
    else:
        print("用法：python core.py [status|check|templates]")
        sys.exit(1)
