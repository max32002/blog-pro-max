"""
quick_stream.py - 簡化的流式生成包裝

提供簡單的流式生成接口，適合 quick_generate.py 使用。
"""

import os
from typing import Iterator

from openai import AzureOpenAI, OpenAI


class QuickStreamingGenerator:
    """
    簡化的流式生成器，自動配置和錯誤處理。

    使用方式：
        generator = QuickStreamingGenerator(model='gemini-pro')
        for chunk in generator.generate(prompt):
            print(chunk, end='', flush=True)
    """

    def __init__(self, model: str = "gemini-pro", temperature: float = 0.7):
        """初始化生成器。"""
        self.model = model
        self.temperature = temperature
        self.client = self._init_client()

    def _init_client(self) -> OpenAI:
        """初始化 API 客戶端。"""
        # 嘗試 OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and self.model.startswith("gpt"):
            return OpenAI(api_key=api_key)

        # 嘗試 Gemini (通過 OpenAI 兼容接口)
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key and self.model.startswith("gemini"):
            # Gemini 可通過多種方式訪問，這裡使用標準 OpenAI 接口
            return OpenAI(
                api_key=api_key,
                base_url="https://generativelanguage.googleapis.com/openai/"
            )

        # 嘗試 Azure
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if api_key:
            return AzureOpenAI(
                api_key=api_key,
                api_version=os.getenv("AZURE_API_VERSION", "2024-02-15"),
                azure_endpoint=os.getenv("AZURE_ENDPOINT", ""),
            )

        # 使用 OpenAI 預設（需設定環境變數）
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

    def generate(self, prompt: str) -> Iterator[str]:
        """
        流式生成文章。

        Args:
            prompt: 生成提示詞

        Yields:
            生成的文本片段
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=self.temperature,
                stream=True,
            )

            for event in response:
                if hasattr(event.choices[0].delta, "content") and event.choices[0].delta.content:
                    yield event.choices[0].delta.content

        except Exception as e:
            raise RuntimeError(f"流式生成失敗: {e}") from e


# 為了兼容 quick_generate.py，提供別名
StreamingBlogGenerator = QuickStreamingGenerator


if __name__ == "__main__":
    # 簡單測試
    import sys

    prompt = "寫一篇 100 字的短文章，關於今天的天氣。"
    print(f"生成提示：{prompt}\n")
    print("-" * 60)

    try:
        generator = QuickStreamingGenerator()
        for chunk in generator.generate(prompt):
            print(chunk, end="", flush=True)
        print("\n" + "-" * 60)
        print("\n✓ 生成完成")
    except Exception as e:
        print(f"\n✗ 錯誤: {e}")
        sys.exit(1)
