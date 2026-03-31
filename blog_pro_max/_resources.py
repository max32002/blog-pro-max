"""
_resources.py — 資源路徑解析器

支援兩種執行環境：
1. pip install 後的 package（從 importlib.resources 讀取）
2. scripts/ 目錄下直接執行（從 PROJECT_ROOT 讀取）
"""

from pathlib import Path

# Package 根目錄（blog_pro_max/）
PACKAGE_DIR = Path(__file__).resolve().parent

# 嘗試偵測是否為 pip installed package
_is_package = (PACKAGE_DIR / "__init__.py").is_file() and (PACKAGE_DIR / "templates").is_dir()

if _is_package:
    # pip install 模式：資源在 package 目錄內
    RESOURCE_ROOT = PACKAGE_DIR
else:
    # scripts/ 直接執行模式：資源在專案根目錄
    RESOURCE_ROOT = PACKAGE_DIR.parent


def get_resource_path(relative_path: str) -> Path:
    """取得資源檔案的絕對路徑。

    Args:
        relative_path: 相對於資源根目錄的路徑，例如 "templates/blog-skill-content.md"
    """
    path = RESOURCE_ROOT / relative_path
    return path


def get_templates_dir() -> Path:
    return RESOURCE_ROOT / "templates"


def get_writing_style_path() -> Path:
    return RESOURCE_ROOT / "writing-style.md"


def get_copilot_json_path() -> Path:
    return RESOURCE_ROOT / "copilot.json"
