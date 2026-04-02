#!/usr/bin/env python3
"""
content_research.py — blog-pro-max 主程式進入點

用法：
  python scripts/content_research.py --keyword "關鍵字" [選項]
"""

import argparse
import re
import sys
from pathlib import Path

# Ensure UTF-8 output on all platforms (e.g., Windows cp950 terminals)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

try:
    from blog_pro_max._resources import RESOURCE_ROOT
    from blog_pro_max.blog_generator import (
        build_prompt,
        generate_cover_prompts,
        generate_devil_advocate,
        generate_divergent,
        generate_illustrations,
        generate_interjections,
        generate_memes,
        generate_questions,
        generate_titles,
        review_logic,
        review_reader,
        review_structure,
        review_trend,
    )
    from blog_pro_max.core import TEMPLATES, ensure_environment, list_templates, scan_project_status
    from blog_pro_max.output_md2html import convert_file as md2html
    from blog_pro_max.output_md2html import convert_with_analysis as md2html_with_analysis
    from blog_pro_max.style_checker import check_content, check_file
except ImportError:
    RESOURCE_ROOT = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(RESOURCE_ROOT / "scripts"))
    from blog_generator import (
        build_prompt,
        generate_cover_prompts,
        generate_devil_advocate,
        generate_divergent,
        generate_illustrations,
        generate_interjections,
        generate_memes,
        generate_questions,
        generate_titles,
        review_logic,
        review_reader,
        review_structure,
        review_trend,
    )
    from core import TEMPLATES, ensure_environment, list_templates, scan_project_status
    from output_md2html import convert_file as md2html
    from output_md2html import convert_with_analysis as md2html_with_analysis
    from quick_stream import QuickStreamingGenerator
    from style_checker import check_content, check_file


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s]+", "-", text.strip())
    return text.lower()[:80]


def resolve_keyword(args) -> str:
    """Resolve keyword from --keyword (with @file support) or --keyword-file."""
    raw = args.keyword
    kf = getattr(args, "keyword_file", None)

    if kf:
        p = Path(kf)
        if not p.exists():
            print(f"❌ 找不到關鍵字檔案：{kf}")
            sys.exit(1)
        return p.read_text(encoding="utf-8").strip()

    if raw.startswith("@"):
        p = Path(raw[1:])
        if not p.exists():
            print(f"❌ 找不到關鍵字檔案：{p}")
            sys.exit(1)
        return p.read_text(encoding="utf-8").strip()

    return raw


def main():
    available_templates = ", ".join(TEMPLATES.keys())

    parser = argparse.ArgumentParser(
        description="blog-pro-max：自動化 SEO 內容創作與部落格文章生成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--keyword", default=None,
        help="核心關鍵字，或使用 @檔案路徑 從檔案讀取（與 --keyword-file 二擇一）",
    )
    parser.add_argument(
        "--keyword-file", default=None,
        help="從指定檔案讀取關鍵字內容（替代 --keyword）",
    )
    parser.add_argument(
        "--audience", default="30-45 歲知識工作者", help="目標讀者（預設：30-45 歲知識工作者）"
    )
    parser.add_argument(
        "--word-count", type=int, default=1200, help="目標字數（預設：1200）"
    )
    parser.add_argument(
        "--language", default="zh-TW", help="輸出語言（預設：zh-TW）"
    )
    parser.add_argument(
        "--output", default=None, help="輸出檔案路徑（預設：output/{keyword}.md）"
    )
    parser.add_argument(
        "--model", default="gpt-4o", help="OpenAI 模型（預設：gpt-4o）"
    )
    parser.add_argument(
        "--template", default="blog-skill-content",
        help=f"寫作風格模板（預設：blog-skill-content）。可用：{available_templates}",
    )
    parser.add_argument(
        "--check-only", default=None,
        help="僅對指定檔案執行風格檢查，不生成文章",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="顯示 prompt 但不呼叫 API",
    )
    parser.add_argument(
        "--status", action="store_true",
        help="顯示專案狀態報告",
    )
    parser.add_argument(
        "--list-templates", action="store_true",
        help="列出所有可用模板",
    )

    args = parser.parse_args()

    # Status mode
    if args.status:
        print(scan_project_status())
        return

    # List templates mode
    if args.list_templates:
        print("📚 可用寫作風格模板：\n")
        for name, info in list_templates().items():
            status = "✅" if info["exists"] else "❌"
            print(f"  {status} {name:25s} {info['description']}")
        return

    # Validate keyword source
    if not args.keyword and not args.keyword_file:
        parser.error("必須提供 --keyword 或 --keyword-file")

    keyword = resolve_keyword(args)

    # Environment check
    if not ensure_environment():
        print("\n❌ 環境檢查未通過，請修正上述問題。")
        sys.exit(1)

    # Style check only mode
    if args.check_only:
        print(f"🔍 檢查檔案：{args.check_only}")
        report = check_file(args.check_only, keyword)
        print(report.summary())
        sys.exit(0 if report.passed else 1)

    template = args.template
    output_path = args.output or str(
        Path.cwd() / "output" / f"{slugify(keyword)}.md"
    )

    print(f"🔑 核心關鍵字：{keyword}")
    print(f"👥 目標讀者：{args.audience}")
    print(f"📏 目標字數：{args.word_count}")
    print(f"🌐 語言：{args.language}")
    print(f"🤖 模型：{args.model}")
    print(f"🎨 模板：{template}")
    print(f"📄 輸出路徑：{output_path}")
    print()

    # Dry run mode
    if args.dry_run:
        prompt, system_prompt = build_prompt(
            keyword, args.audience, args.word_count, args.language, template
        )
        print("=" * 60)
        print("📋 System Prompt")
        print("=" * 60)
        print(system_prompt[:800] + "..." if len(system_prompt) > 800 else system_prompt)
        print()
        print("=" * 60)
        print("📝 User Prompt（文章生成指令）")
        print("=" * 60)
        print(prompt)
        return

    # Generate article
    print("⏳ 正在生成文章...")
    try:
        streamer = QuickStreamingGenerator()
        article_chunks = []
        for chunk in streamer.generate(
            prompt=f"以 {keyword} 為核心寫一篇 {args.word_count} 字的文章給 {args.audience}",
            model=args.model,
            temperature=0.7
        ):
            print(chunk, end="", flush=True)
            article_chunks.append(chunk)
        article = "".join(article_chunks)
    except EnvironmentError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except KeyError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 生成失敗：{e}")
        sys.exit(1)

    # 新增：保存 Session 狀態
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(article, encoding="utf-8")
    print(f"✅ 文章已儲存至：{output_path}")
    print()

    # Analysis file (separate from article)
    analysis_path = str(output_file.with_name(output_file.stem + "_analysis.md"))
    analysis_content = ""


    # Style check
    print("🔍 正在執行風格檢查...")
    report = check_content(article, keyword)
    print(report.summary())

    if not report.passed:
        print()
        print("⚠️  文章已儲存，但有風格問題需要修正。")
    else:
        print()
        print("🎉 文章生成完成，所有檢查通過！")

    # ── 三維度審稿專家 ──────────────────────────────
    review_experts = [
        ("🔬", "邏輯與事實專家", review_logic),
        ("📐", "深度與結構專家", review_structure),
        ("👁️", "讀者視角專家", review_reader),
    ]

    all_review_blocks = ""
    for emoji, name, fn in review_experts:
        print()
        print(f"{emoji} 正在執行{name}分析...")
        try:
            items = fn(
                article_content=article,
                keyword=keyword,
                audience=args.audience,
                model=args.model,
            )
            if items:
                print(f"   📋 {name}發現 {len(items)} 個項目：")
                for i, item in enumerate(items, 1):
                    print(f"   {i}. {item.get('issue', '')}")
                    if item.get("suggest"):
                        print(f"      → {item['suggest']}")

                block = f"\n\n---\n\n## {emoji} {name}審查報告\n\n"
                block += f"> 以下由「{name}」自動產出，含問題點、修改建議與修改前後對比。\n\n"
                for i, item in enumerate(items, 1):
                    issue = item.get("issue", "")
                    suggest = item.get("suggest", "")
                    before = item.get("before", "—")
                    after = item.get("after", "—")
                    block += f"### 問題 {i}：{issue}\n\n"
                    block += f"**修改建議：** {suggest}\n\n"
                    block += f"**原文：** {before}\n\n"
                    block += f"**修改後：** {after}\n\n"
                all_review_blocks += block
                print(f"   ✅ {name}報告已生成")
        except Exception as e:
            print(f"   ⚠️  {name}分析失敗（不影響文章）：{e}")

    if all_review_blocks:
        analysis_content += all_review_blocks
        print("\n   ✅ 審稿報告已生成")

    # ── 時事趨勢專家 ──────────────────────────────
    print()
    print("📰 正在執行時事趨勢分析...")
    try:
        trend = review_trend(
            article_content=article,
            keyword=keyword,
            audience=args.audience,
            model=args.model,
        )
        if trend:
            section_names = {
                "trend_analysis": ("🔗 趨勢關聯分析", "趨勢關聯分析"),
                "angle_suggestions": ("🎯 切入角度建議", "切入角度建議"),
                "keywords_tags": ("🏷️ 關鍵字與標籤優化", "關鍵字與標籤優化"),
                "rewrite_demo": ("✍️ 內容改寫示範", "內容改寫示範"),
            }
            for key, (emoji_title, _) in section_names.items():
                if trend.get(key):
                    preview = trend[key][:80].replace("\n", " ")
                    print(f"   {emoji_title}：{preview}...")

            trend_block = "\n\n---\n\n## 📰 時事趨勢分析報告\n\n"
            trend_block += "> 以下由「時事趨勢專家」自動產出，協助文章與當前趨勢建立連結。\n\n"
            for key, (emoji_title, _) in section_names.items():
                if trend.get(key):
                    trend_block += f"### {emoji_title}\n\n{trend[key]}\n\n"

            analysis_content += trend_block
            print("   ✅ 時事趨勢報告已生成")
    except Exception as e:
        print(f"   ⚠️  時事趨勢分析失敗（不影響文章）：{e}")

    # Generate title suggestions
    print()
    print("📝 正在生成標題建議...")
    try:
        titles = generate_titles(
            article_content=article,
            keyword=keyword,
            audience=args.audience,
            language=args.language,
            model=args.model,
        )
        if titles:
            print("💡 推薦標題選項：")
            for i, t in enumerate(titles, 1):
                slug_display = f"  /{t['slug']}" if t.get('slug') else ""
                print(f"   {i}. {t['title']}{slug_display}")

            # Append title suggestions to .md
            title_block = "\n\n---\n\n## 📝 推薦標題選項\n\n"
            title_block += "> 以下由「部落格標題專家」自動產出，請人工選擇最適合的標題。\n\n"
            title_block += "| # | 標題 | WordPress Permalink |\n"
            title_block += "|---|------|--------------------|\n"
            for i, t in enumerate(titles, 1):
                slug = t.get('slug', '')
                title_block += f"| {i} | {t['title']} | `/{slug}` |\n"

            analysis_content += title_block
            print("   ✅ 標題建議已生成")
    except Exception as e:
        print(f"   ⚠️  標題生成失敗（不影響文章）：{e}")

    # Generate cover image prompts
    print()
    print("🎨 正在生成封面提示詞...")
    try:
        cover_prompts = generate_cover_prompts(
            article_content=article,
            keyword=keyword,
            audience=args.audience,
            model=args.model,
        )
        if cover_prompts:
            print("🖼️  推薦封面提示詞：")
            for i, cp in enumerate(cover_prompts, 1):
                print(f"   {i}. [{cp['style']}] {cp['description']}")

            cover_block = "\n\n---\n\n## 🎨 推薦封面提示詞\n\n"
            cover_block += "> 以下由「封面提示詞專家」自動產出，可直接貼到 Midjourney、DALL-E 或 Stable Diffusion 使用。\n\n"
            for i, cp in enumerate(cover_prompts, 1):
                cover_block += f"### {i}. {cp['style']}\n\n"
                cover_block += f"**Prompt:**\n\n```\n{cp['prompt']}\n```\n\n"
                if cp['description']:
                    cover_block += f"*{cp['description']}*\n\n"

            analysis_content += cover_block
            print("   ✅ 封面提示詞已生成")
    except Exception as e:
        print(f"   ⚠️  封面提示詞生成失敗（不影響文章）：{e}")

    # ── 6 個段落級專家 ──────────────────────────────
    paragraph_experts = [
        ("🌀", "發散專家", generate_divergent),
        ("❓", "問題專家", generate_questions),
        ("😂", "迷因專家", generate_memes),
        ("💬", "插話專家", generate_interjections),
        ("🖼️", "插畫專家", generate_illustrations),
        ("🔴", "唱反調專家", generate_devil_advocate),
    ]

    # 並行化專家分析
    import concurrent.futures
    def run_expert(fn, article, keyword, audience, model):
        try:
            block = fn(
                article_content=article,
                keyword=keyword,
                audience=audience,
                model=model,
            )
            return block, None
        except Exception as e:
            return None, e

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        futures = [
            executor.submit(run_expert, fn, article, keyword, args.audience, args.model)
            for _, _, fn in paragraph_experts
        ]
        for (emoji, name, _), future in zip(paragraph_experts, futures):
            print()
            print(f"{emoji} 正在執行{name}分析...")
            block, err = future.result()
            if block:
                analysis_content += block
                print(f"   ✅ {name}建議已生成")
            elif err:
                print(f"   ⚠️  {name}分析失敗（不影響文章）：{err}")

    # Save all analysis to separate file
    if analysis_content:
        analysis_file = Path(analysis_path)
        analysis_file.write_text(analysis_content, encoding="utf-8")
        print(f"\n✅ 分析報告已儲存至：{analysis_path}")

    # Convert to HTML (merged article + analysis)
    html_path = str(Path(output_path).with_suffix(".html"))
    print("\n📄 正在轉換 HTML...")
    if analysis_content:
        md2html_with_analysis(output_path, analysis_path, html_path)
    else:
        md2html(output_path, html_path)
    print(f"✅ HTML 已儲存至：{html_path}")

    if report.passed:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
