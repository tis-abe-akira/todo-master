"""Task 1.2 verification test: .env.example が正しく存在し、GEMINI_API_KEY= を含むことを確認する。"""
import os
import unittest


REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)


class TestEnvExample(unittest.TestCase):
    def test_env_example_exists(self):
        """.env.example がリポジトリルートに存在すること。"""
        path = os.path.join(REPO_ROOT, ".env.example")
        self.assertTrue(
            os.path.exists(path),
            f".env.example が見つかりません: {path}",
        )

    def test_env_example_contains_gemini_api_key(self):
        """.env.example に GEMINI_API_KEY= が記載されていること。"""
        path = os.path.join(REPO_ROOT, ".env.example")
        with open(path, encoding="utf-8") as f:
            content = f.read()
        self.assertIn(
            "GEMINI_API_KEY=",
            content,
            ".env.example に GEMINI_API_KEY= が含まれていません",
        )

    def test_gitignore_excludes_dotenv(self):
        """.gitignore に .env が記載されていること。"""
        path = os.path.join(REPO_ROOT, ".gitignore")
        self.assertTrue(
            os.path.exists(path),
            f".gitignore が見つかりません: {path}",
        )
        with open(path, encoding="utf-8") as f:
            content = f.read()
        # .env または .env（行単位）が含まれていることを確認
        lines = [line.strip() for line in content.splitlines()]
        self.assertIn(
            ".env",
            lines,
            ".gitignore に .env エントリが含まれていません",
        )


if __name__ == "__main__":
    unittest.main()
