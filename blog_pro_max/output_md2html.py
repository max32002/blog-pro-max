import argparse
import re
from pathlib import Path

import markdown

def preprocess_markdown(text):
    # 修正 1：確保每個 - 開頭後方至少有一個空格
    text = re.sub(r'^-([^\s])', r'- \1', text, flags=re.MULTILINE)

    # 修正 2：確保清單與上方段落之間有空行
    text = re.sub(r'([^\n])\n-', r'\1\n\n-', text)

    # 修正 3：將 **Prompt:** 開頭的行轉為 code block 格式
    def wrap_prompt(m):
        prompt_text = m.group(1).strip()
        return f"\n```\n{prompt_text}\n```\n"
    pattern = r'^\*\*Prompt:\*\*\s+(.+)$'
    text = re.sub(pattern, wrap_prompt, text, flags=re.MULTILINE)

    # 修正 4：將 - **插畫風 Prompt**： 開頭的行轉為 code block 格式
    def wrap_prompt2(m):
        # m.group(1) 是標題（如：插畫風）
        # m.group(2) 是具體的 Prompt 內容
        prompt_title = m.group(1).strip()
        prompt_content = m.group(2).strip()
        return f"- **{prompt_title} Prompt**\n```\n{prompt_content}\n```\n"

    pattern = r'^- \*\*(.+) Prompt\*\*：(.+)$'
    text = re.sub(pattern, wrap_prompt2, text, flags=re.MULTILINE)
    # for debug.
    #print(text)

    return text

_HTML_STYLES = """
        body { font-family: sans-serif; line-height: 1.6; padding: 20px; max-width: 1024px; margin: auto; }
        pre { position: relative; background: #e4e4e4; padding: 25px; border-radius: 10px; white-space: pre-wrap; word-wrap: break-word; }
        code { font-family: monospace; }
        .copy-btn {
            position: absolute;
            top: 5px;
            right: 5px;
            padding: 4px 8px;
            background: #333;
            color: #fff;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            opacity: 0.5;
            transition: opacity 0.2s;
        }
        .copy-btn:hover { opacity: 1; }
        .analysis-section {
            margin-top: 48px;
            padding: 24px 28px;
            background: #f8f8f8;
            border-left: 4px solid #888;
            border-radius: 6px;
        }
        .analysis-title {
            font-size: 1.4em;
            color: #444;
            margin-bottom: 16px;
        }
        .section-divider {
            border: none;
            border-top: 2px dashed #ccc;
            margin: 40px 0 8px;
        }
"""

_COPY_SCRIPT = """
    document.querySelectorAll('pre').forEach(pre => {
        const btn = document.createElement('button');
        btn.className = 'copy-btn';
        btn.innerText = 'Copy';
        btn.addEventListener('click', () => {
            const code = pre.innerText.replace('Copy', '').trim();
            navigator.clipboard.writeText(code).then(() => {
                btn.innerText = 'Copied!';
                setTimeout(() => btn.innerText = 'Copy', 2000);
            });
        });
        pre.appendChild(btn);
    });
"""


def _to_html(md_text: str) -> str:
    return markdown.markdown(preprocess_markdown(md_text), extensions=['extra', 'fenced_code'])


def _wrap_html(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>{_HTML_STYLES}
    </style>
</head>
<body>
{body}
<script>{_COPY_SCRIPT}
</script>
</body>
</html>"""


def convert_file(input_path, output_path):
    try:
        raw_content = Path(input_path).read_text(encoding='utf-8')
        html_output = _to_html(raw_content)
        full_html = _wrap_html("Converted Markdown", html_output)
        Path(output_path).write_text(full_html, encoding='utf-8')
        print(f"轉換成功：{output_path}")
    except FileNotFoundError:
        print(f"錯誤：找不到檔案 {input_path}")
    except Exception as e:
        print(f"處理過程中發生錯誤：{e}")


def convert_with_analysis(article_path, analysis_path, output_path):
    """Merge article .md + analysis .md into one HTML file for easy reading."""
    try:
        article_html = _to_html(Path(article_path).read_text(encoding='utf-8'))
        analysis_html = _to_html(Path(analysis_path).read_text(encoding='utf-8'))

        body = f"""<div id="article">
{article_html}
</div>
<hr class="section-divider">
<div id="analysis" class="analysis-section">
<h2 class="analysis-title">📊 全文分析報告</h2>
{analysis_html}
</div>"""

        title = Path(article_path).stem
        full_html = _wrap_html(title, body)
        Path(output_path).write_text(full_html, encoding='utf-8')
        print(f"轉換成功（文章＋分析）：{output_path}")
    except FileNotFoundError as e:
        print(f"錯誤：找不到檔案 {e.filename}")
    except Exception as e:
        print(f"處理過程中發生錯誤：{e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='強化的 Markdown 轉 HTML 工具')
    parser.add_argument('input', help='輸入的 .md 檔案路徑')
    parser.add_argument('output', help='輸出的 .html 檔案路徑')
    parser.add_argument('--analysis', '-a', default=None, help='分析 .md 檔案路徑（選填）；提供時與文章合併輸出')
    args = parser.parse_args()

    if args.analysis:
        convert_with_analysis(args.input, args.analysis, args.output)
    else:
        convert_file(args.input, args.output)
