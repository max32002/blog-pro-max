"""
style_checker.py — 根據 writing-style.md 規範驗證文章內容
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

FORBIDDEN_WORDS = [
    "值得注意的是",
    "不可否認地",
    "在這個日新月異的時代",
    "顯而易見",
    "毋庸置疑",
    "筆者認為",
    "相信讀者",
]

FORBIDDEN_REPLACEMENTS = {
    "值得注意的是": "重點是",
    "不可否認地": "（直接陳述）",
    "在這個日新月異的時代": "（刪除，直接切入）",
    "顯而易見": "（直接說結論）",
    "毋庸置疑": "（直接陳述）",
    "筆者認為": "我認為",
    "相信讀者": "（刪除，直接說）",
}


@dataclass
class StyleIssue:
    rule: str
    message: str
    line: int | None = None
    severity: str = "warning"  # "warning" or "error"


@dataclass
class StyleReport:
    issues: list[StyleIssue] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")

    def summary(self) -> str:
        if not self.issues:
            return "✅ 所有檢查通過"
        lines = [f"共 {self.error_count} 個錯誤，{self.warning_count} 個警告："]
        for issue in self.issues:
            prefix = "❌" if issue.severity == "error" else "⚠️"
            loc = f" (第 {issue.line} 行)" if issue.line else ""
            lines.append(f"  {prefix} [{issue.rule}]{loc} {issue.message}")
        return "\n".join(lines)


def check_forbidden_words(content: str) -> list[StyleIssue]:
    issues = []
    for i, line in enumerate(content.splitlines(), 1):
        for word in FORBIDDEN_WORDS:
            if word in line:
                replacement = FORBIDDEN_REPLACEMENTS.get(word, "")
                issues.append(StyleIssue(
                    rule="forbidden-word",
                    message=f"禁止詞彙「{word}」→ 建議替換為「{replacement}」",
                    line=i,
                    severity="error",
                ))
    return issues


def check_heading_hierarchy(content: str) -> list[StyleIssue]:
    issues = []
    h1_count = 0
    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("## "):
            h1_count += 1
        if re.match(r"^#{3,}\s", stripped):
            issues.append(StyleIssue(
                rule="heading-depth",
                message="不應使用 H3 以下標題",
                line=i,
                severity="error",
            ))
    if h1_count == 0:
        issues.append(StyleIssue(
            rule="missing-h1",
            message="文章缺少 H1 標題",
            severity="error",
        ))
    elif h1_count > 1:
        issues.append(StyleIssue(
            rule="multiple-h1",
            message=f"H1 標題出現 {h1_count} 次，應只出現 1 次",
            severity="error",
        ))
    return issues


def check_paragraph_length(content: str) -> list[StyleIssue]:
    issues = []
    lines = content.splitlines()
    para_start = None
    para_lines = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        is_content = (
            stripped
            and not stripped.startswith("#")
            and not stripped.startswith("-")
            and not stripped.startswith("*")
            and not stripped.startswith("|")
            and not stripped.startswith("```")
            and not stripped.startswith("---")
            and not stripped.startswith("[")
            and not stripped.startswith("!")
        )
        if is_content:
            if para_start is None:
                para_start = i + 1
            para_lines += 1
        else:
            if para_lines > 5:
                issues.append(StyleIssue(
                    rule="paragraph-length",
                    message=f"段落過長（{para_lines} 行），建議不超過 5 行",
                    line=para_start,
                    severity="warning",
                ))
            para_start = None
            para_lines = 0

    if para_lines > 5:
        issues.append(StyleIssue(
            rule="paragraph-length",
            message=f"段落過長（{para_lines} 行），建議不超過 5 行",
            line=para_start,
            severity="warning",
        ))
    return issues


def check_seo_basics(content: str, keyword: str | None = None) -> list[StyleIssue]:
    issues = []
    if not keyword:
        return issues

    # Check H1 contains keyword
    h1_has_keyword = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("## "):
            if keyword in stripped:
                h1_has_keyword = True
            break

    if not h1_has_keyword:
        issues.append(StyleIssue(
            rule="seo-h1-keyword",
            message=f"H1 標題未包含核心關鍵字「{keyword}」",
            severity="error",
        ))

    # Check keyword in first 100 chars of body
    body_lines = []
    in_frontmatter = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "---":
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter or stripped.startswith("#"):
            continue
        if stripped:
            body_lines.append(stripped)

    body_text = "".join(body_lines)
    if body_text[:100] and keyword not in body_text[:100]:
        issues.append(StyleIssue(
            rule="seo-intro-keyword",
            message=f"前 100 字未包含核心關鍵字「{keyword}」",
            severity="warning",
        ))

    # Check internal link placeholder
    if "[" in content and "](internal-link)" in content:
        pass
    else:
        issues.append(StyleIssue(
            rule="seo-internal-link",
            message="缺少內部連結佔位符 [相關文章](internal-link)",
            severity="warning",
        ))

    return issues


def check_punctuation(content: str) -> list[StyleIssue]:
    issues = []
    half_width = re.compile(r"[\u4e00-\u9fff][,;:!?]|[,;:!?][\u4e00-\u9fff]")
    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("|") or stripped.startswith("---"):
            continue
        if half_width.search(stripped):
            issues.append(StyleIssue(
                rule="punctuation",
                message="中文語境應使用全形標點",
                line=i,
                severity="warning",
            ))
    return issues


def check_spacing(content: str) -> list[StyleIssue]:
    issues = []
    # Check: CJK char directly adjacent to ASCII letter/digit (no space)
    no_space = re.compile(
        r"[\u4e00-\u9fff][A-Za-z0-9]|[A-Za-z0-9][\u4e00-\u9fff]"
    )
    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("|") or stripped.startswith("---"):
            continue
        if stripped.startswith("#"):
            continue
        if no_space.search(stripped):
            issues.append(StyleIssue(
                rule="spacing",
                message="數字與英文單字前後應加半形空格",
                line=i,
                severity="warning",
            ))
    return issues


def check_content(content: str, keyword: str | None = None) -> StyleReport:
    report = StyleReport()

    # Strip frontmatter for content checks
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            body = parts[2]

    report.issues.extend(check_forbidden_words(body))
    report.issues.extend(check_heading_hierarchy(body))
    report.issues.extend(check_paragraph_length(body))
    report.issues.extend(check_seo_basics(content, keyword))
    report.issues.extend(check_punctuation(body))
    report.issues.extend(check_spacing(body))

    return report


def check_file(filepath: str, keyword: str | None = None) -> StyleReport:
    path = Path(filepath)
    if not path.exists():
        report = StyleReport()
        report.issues.append(StyleIssue(
            rule="file-not-found",
            message=f"檔案不存在：{filepath}",
            severity="error",
        ))
        return report
    content = path.read_text(encoding="utf-8")
    return check_content(content, keyword)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法：python style_checker.py <檔案路徑> [關鍵字]")
        sys.exit(1)

    filepath = sys.argv[1]
    kw = sys.argv[2] if len(sys.argv) > 2 else None
    report = check_file(filepath, kw)
    print(report.summary())
    sys.exit(0 if report.passed else 1)
