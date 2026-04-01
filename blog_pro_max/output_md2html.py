import argparse
import re

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
    text = re.sub(r'^\*\*Prompt:\*\*\s+(.+)$', wrap_prompt, text, flags=re.MULTILINE)
    # for debug.
    #print(text)

    return text

def convert_file(input_path, output_path):
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        # 執行前置格式清理
        clean_content = preprocess_markdown(raw_content)

        # 轉換為 HTML，加入 extra 擴充以支援表格與任務清單
        html_output = markdown.markdown(clean_content, extensions=['extra', 'fenced_code'])

        # 封裝成完整的 HTML 結構，方便直接預覽
        full_html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <title>Converted Markdown</title>
    <style>
        body {{ font-family: sans-serif; line-height: 1.6; padding: 20px; max-width: 1024px; margin: auto; }}
        pre {{ position: relative; background: #e4e4e4; padding: 25px; border-radius: 10px; white-space: pre-wrap; word-wrap: break-word; }}
        code {{ font-family: monospace; }}
        .copy-btn {{
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
        }}
        .copy-btn:hover {{ opacity: 1; }}
    </style>
</head>
<body>
{html_output}
<script>
    document.querySelectorAll('pre').forEach(pre => {{
        const btn = document.createElement('button');
        btn.className = 'copy-btn';
        btn.innerText = 'Copy';
        btn.addEventListener('click', () => {{
            const code = pre.innerText.replace('Copy', '').trim();
            navigator.clipboard.writeText(code).then(() => {{
                btn.innerText = 'Copied!';
                setTimeout(() => btn.innerText = 'Copy', 2000);
            }});
        }});
        pre.appendChild(btn);
    }});
</script>
</body>
</html>"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_html)

        print(f"轉換成功：{output_path}")

    except FileNotFoundError:
        print(f"錯誤：找不到檔案 {input_path}")
    except Exception as e:
        print(f"處理過程中發生錯誤：{e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='強化的 Markdown 轉 HTML 工具')

    parser.add_argument('input', help='輸入的 .md 檔案路記')
    parser.add_argument('output', help='輸出的 .html 檔案路徑')

    args = parser.parse_args()

    convert_file(args.input, args.output)
