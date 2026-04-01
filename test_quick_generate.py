#!/usr/bin/env python3
"""
test_quick_generate.py - 測試 quick_generate 的核心邏輯

不實際調用 LLM API，只測試配置、會話管理等。
"""

import tempfile
import json
from pathlib import Path
from datetime import datetime

# 導入測試目標
import sys
sys.path.insert(0, str(Path(__file__).parent))

from quick_generate import get_config, SimpleSession, ensure_dirs


def test_config():
    """測試配置加載。"""
    print("✓ 測試 1: 配置加載")
    config = get_config()
    assert "model" in config
    assert "temperature" in config
    assert isinstance(config["output_dir"], Path)
    print(f"  - 模型: {config['model']}")
    print(f"  - 溫度: {config['temperature']}")
    print(f"  - 輸出目錄: {config['output_dir']}\n")


def test_dirs():
    """測試目錄創建。"""
    print("✓ 測試 2: 目錄創建")
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {
            "output_dir": Path(tmpdir) / "articles",
            "sessions_dir": Path(tmpdir) / "sessions",
        }
        ensure_dirs(config)
        assert config["output_dir"].exists()
        assert config["sessions_dir"].exists()
        print(f"  - 已創建: {config['output_dir']}")
        print(f"  - 已創建: {config['sessions_dir']}\n")


def test_session():
    """測試會話管理。"""
    print("✓ 測試 3: 會話管理")
    with tempfile.TemporaryDirectory() as tmpdir:
        sessions_dir = Path(tmpdir)
        mgr = SimpleSession(sessions_dir)

        # 創建會話
        prompt = "測試提示詞"
        session = mgr.create_session(prompt)
        assert session["prompt"] == prompt
        assert session["status"] == "generating"
        print(f"  - 會話已創建")
        print(f"  - 提示詞: {session['prompt']}")

        # 保存會話
        test_content = "# 測試文章\n\n這是一篇測試文章。"
        session_file = mgr.save_session(test_content)
        assert session_file.exists()
        print(f"  - 會話已保存: {session_file.name}")

        # 驗證內容
        saved_session = json.loads(session_file.read_text(encoding="utf-8"))
        assert saved_session["content"] == test_content
        assert saved_session["status"] == "completed"
        print(f"  - 內容驗證: ✓")

        # 恢復會話
        recovered = mgr.get_last_session()
        assert recovered is not None
        assert recovered["content"] == test_content
        print(f"  - 會話恢復: ✓\n")


def test_session_file_format():
    """測試會話文件格式。"""
    print("✓ 測試 4: 會話文件格式")
    with tempfile.TemporaryDirectory() as tmpdir:
        sessions_dir = Path(tmpdir)
        mgr = SimpleSession(sessions_dir)

        prompt = "# 測試標題\n寫一篇關於 AI 的文章"
        session = mgr.create_session(prompt)

        test_content = """# AI 的未來

人工智能正在改變世界。

## 應用領域

- 醫療
- 金融
- 教育

## 結論

AI 將繼續發展。"""

        session_file = mgr.save_session(test_content)

        # 檢查文件
        files = list(sessions_dir.glob("*"))
        assert len(files) == 2  # JSON + Markdown
        print(f"  - 生成了 {len(files)} 個文件:")
        for f in files:
            print(f"    - {f.name}")

        # 檢查 JSON 格式
        json_file = next(f for f in files if f.suffix == ".json")
        json_data = json.loads(json_file.read_text(encoding="utf-8"))
        assert "timestamp" in json_data
        assert "prompt" in json_data
        assert "content" in json_data
        assert "status" in json_data
        print(f"  - JSON 格式驗證: ✓")

        # 檢查 Markdown 格式
        md_file = next(f for f in files if f.suffix == ".md")
        md_content = md_file.read_text(encoding="utf-8")
        assert "# AI 的未來" in md_content
        print(f"  - Markdown 格式驗證: ✓\n")


def main():
    """執行所有測試。"""
    print("=" * 60)
    print("quick_generate.py - 核心邏輯測試")
    print("=" * 60 + "\n")

    try:
        test_config()
        test_dirs()
        test_session()
        test_session_file_format()

        print("=" * 60)
        print("✅ 所有測試通過！")
        print("=" * 60)
        print("\n可以放心使用 quick_generate.py")
        print("執行命令: python quick_generate.py \"寫一篇文章\"")

    except AssertionError as e:
        print(f"\n❌ 測試失敗: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
