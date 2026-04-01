#!/usr/bin/env python3
"""
quick_generate.py - 個人版文章快速生成工具

簡化版本，針對單人使用。
無需權限系統、工具註冊表等複雜組件。

使用方式：
    # 快速生成
    python quick_generate.py "寫一篇 AI 的文章"
    
    # 恢復編輯
    python quick_generate.py --resume last
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# 簡化配置
def get_config() -> Dict[str, Any]:
    """從環境變數讀取配置，無複雜驗證。"""
    return {
        "model": os.getenv("LLM_MODEL", "gemini-pro"),
        "temperature": float(os.getenv("LLM_TEMP", "0.7")),
        "output_dir": Path(os.getenv("OUTPUT_DIR", "./articles")),
        "sessions_dir": Path(os.getenv("SESSIONS_DIR", "./.sessions")),
    }


def ensure_dirs(config: Dict[str, Any]) -> None:
    """確保輸出目錄存在。"""
    config["output_dir"].mkdir(parents=True, exist_ok=True)
    config["sessions_dir"].mkdir(parents=True, exist_ok=True)


class SimpleSession:
    """簡單會話管理，只保存 JSON 文件。"""

    def __init__(self, sessions_dir: Path):
        self.sessions_dir = sessions_dir
        self.current_session = None

    def create_session(self, prompt: str) -> Dict[str, Any]:
        """建立新會話。"""
        self.current_session = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "content": "",
            "status": "generating",
        }
        return self.current_session

    def save_session(self, content: str, session: Optional[Dict] = None) -> Path:
        """保存會話和內容。"""
        if session is None:
            session = self.current_session

        session["content"] = content
        session["status"] = "completed"
        session["updated_at"] = datetime.now().isoformat()

        # 使用時間戳作為檔案名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_file = self.sessions_dir / f"session_{timestamp}.json"
        
        session_file.write_text(
            json.dumps(session, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        # 保存 Markdown 版本
        article_file = self.sessions_dir / f"article_{timestamp}.md"
        article_file.write_text(content, encoding="utf-8")

        return session_file

    def get_last_session(self) -> Optional[Dict[str, Any]]:
        """取得最後一個會話。"""
        session_files = sorted(self.sessions_dir.glob("session_*.json"))
        if not session_files:
            return None

        last_file = session_files[-1]
        return json.loads(last_file.read_text(encoding="utf-8"))


def generate_article(prompt: str, model: str, temperature: float) -> str:
    """使用流式生成器生成文章。"""
    try:
        from blog_pro_max.quick_stream import QuickStreamingGenerator
    except ImportError:
        print("✗ 錯誤：無法導入 QuickStreamingGenerator")
        sys.exit(1)

    print(f"\n🚀 正在生成文章...\n")
    print("-" * 60)

    generator = QuickStreamingGenerator(model=model, temperature=temperature)
    content = ""

    # 流式輸出
    for chunk in generator.generate(prompt):
        print(chunk, end="", flush=True)
        content += chunk

    print("\n" + "-" * 60)
    print(f"\n✓ 文章生成完成 ({len(content)} 字)\n")

    return content


def main():
    """主程序入口。"""
    parser = argparse.ArgumentParser(
        description="個人版文章快速生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例：
  # 快速生成
  python quick_generate.py "寫一篇 AI 的文章"
  
  # 恢復編輯
  python quick_generate.py --resume last
  
  # 自訂模型
  python quick_generate.py "寫一篇文章" --model gpt-4 --temperature 0.9
        """,
    )

    parser.add_argument("prompt", nargs="?", help="生成文章的提示詞")
    parser.add_argument(
        "--resume", metavar="SESSION_ID", help="恢復之前的會話 (e.g., 'last')"
    )
    parser.add_argument(
        "--model", default=None, help="使用的 LLM 模型 (default: from env or gemini-pro)"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="生成溫度，越高越有創意 (0-1, default: from env or 0.7)",
    )

    args = parser.parse_args()

    # 載入配置
    config = get_config()
    ensure_dirs(config)

    # 覆蓋模型和溫度
    if args.model:
        config["model"] = args.model
    if args.temperature is not None:
        config["temperature"] = args.temperature

    # 初始化會話
    session_mgr = SimpleSession(config["sessions_dir"])

    # 恢復模式
    if args.resume:
        session = session_mgr.get_last_session()
        if session:
            print(f"✓ 恢復會話：{session['timestamp']}")
            print(f"原始提示：{session['prompt']}")
            print(f"字數：{len(session['content'])}")
            print("\n內容預覽:")
            print("-" * 60)
            print(session["content"][:500] + "..." if len(session["content"]) > 500 else session["content"])
            print("-" * 60)
        else:
            print("✗ 無法找到會話")
        return

    # 生成模式
    if not args.prompt:
        parser.print_help()
        sys.exit(1)

    # 建立會話
    session_mgr.create_session(args.prompt)

    # 生成文章
    content = generate_article(
        prompt=args.prompt,
        model=config["model"],
        temperature=config["temperature"],
    )

    # 保存會話
    session_file = session_mgr.save_session(content)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    article_file = session_file.parent / f'article_{timestamp}.md'
    print(f"💾 會話已保存：{session_file}")
    print(f"📄 文章已保存：{article_file}")


if __name__ == "__main__":
    main()
