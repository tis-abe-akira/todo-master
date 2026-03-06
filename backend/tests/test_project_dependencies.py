"""Task 1.1 verification test: langchain-google-genai と python-dotenv がインストール済みであることを確認する。"""

import importlib
import unittest


class TestDependenciesInstalled(unittest.TestCase):
    def test_langchain_google_genai_importable(self):
        """langchain-google-genai がインストール済みでインポート可能であること。"""
        mod = importlib.import_module("langchain_google_genai")
        self.assertIsNotNone(mod)

    def test_chat_google_generative_ai_importable(self):
        """ChatGoogleGenerativeAI クラスがインポート可能であること。"""
        from langchain_google_genai import ChatGoogleGenerativeAI  # noqa: F401

    def test_dotenv_importable(self):
        """python-dotenv がインストール済みでインポート可能であること。"""
        mod = importlib.import_module("dotenv")
        self.assertIsNotNone(mod)

    def test_langchain_core_prompt_importable(self):
        """langchain-core の ChatPromptTemplate がインポート可能であること。"""
        from langchain_core.prompts import ChatPromptTemplate  # noqa: F401


if __name__ == "__main__":
    unittest.main()
