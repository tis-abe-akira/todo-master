"""
Task 5.3: 永続化失敗時のクライアント向けエラーハンドリングのテスト
- LocalStore.save() が IOError を送出したとき、create_and_persist_todo は
  HTTPException(500) を送出する（FastAPI エンドポイント経由）
- エンドポイントは 500 レスポンスと再試行可能なメッセージを返す
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app.local_store import LocalStore
from backend.app.models import CreateTodo
from backend.app import main as app_main


class TestPersistenceFailure(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.store_path = os.path.join(self.tmpdir.name, "todos.json")
        self.store = LocalStore(self.store_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    # 5.3-1: save() が失敗したとき create_and_persist_todo は例外を伝播する
    def test_create_raises_on_save_failure(self):
        with patch.object(self.store, "save", side_effect=IOError("disk full")):
            with self.assertRaises(Exception):
                app_main.create_and_persist_todo(
                    self.store, CreateTodo(title="fail test")
                )

    # 5.3-2: エンドポイント POST /api/todos が永続化失敗時に 500 を返す
    def test_post_endpoint_returns_500_on_save_failure(self):
        from fastapi.testclient import TestClient

        test_app = app_main.create_app(self.store_path)
        client = TestClient(test_app, raise_server_exceptions=False)

        with patch.object(
            test_app.state.store, "save", side_effect=IOError("disk full")
        ):
            resp = client.post("/api/todos", json={"title": "fail"})
        self.assertEqual(resp.status_code, 500)

    # 5.3-3: 500 レスポンスに retryable を示すメッセージが含まれる
    def test_post_endpoint_500_body_has_retry_hint(self):
        from fastapi.testclient import TestClient

        test_app = app_main.create_app(self.store_path)
        client = TestClient(test_app, raise_server_exceptions=False)

        with patch.object(
            test_app.state.store, "save", side_effect=IOError("disk full")
        ):
            resp = client.post("/api/todos", json={"title": "fail"})
        body = resp.json()
        # detail フィールドに再試行案内が含まれること
        detail = body.get("detail", "")
        self.assertTrue(
            "retry" in detail.lower() or "再試行" in detail or "再度" in detail,
            f"retry hint not found in detail: {detail}",
        )


if __name__ == "__main__":
    unittest.main()
