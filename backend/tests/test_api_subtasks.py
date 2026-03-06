"""
Task 3: POST /api/todos/{id}/subtasks エンドポイントの統合テスト
- 正常系: HTTP 200 + subtasks 配列を返す
- 404: 存在しない todo_id の場合
- 503: GeminiServiceError 発生時
- 503: GeminiConfigError 発生時
"""

import os
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app.main import create_app


class TestSubtasksEndpoint(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.store_path = os.path.join(self.tmpdir.name, "todos.json")
        self.app = create_app(self.store_path)
        self.client = TestClient(self.app)

    def tearDown(self):
        self.tmpdir.cleanup()

    def _create_todo(self, title="牛乳を買う", description=None):
        """テスト用 Todo を作成してその id を返すヘルパー"""
        payload = {"title": title}
        if description:
            payload["description"] = description
        resp = self.client.post("/api/todos", json=payload)
        self.assertEqual(resp.status_code, 201)
        return resp.json()["id"]

    def _make_mock_subtasks(self, count=5):
        """テスト用のモックサブタスクリストを返すヘルパー"""
        from backend.app.subtask_service import Subtask

        return [
            Subtask(title=f"大仰なサブタスク {i + 1}：ROI と PMBOK を駆使した施策")
            for i in range(count)
        ]

    # ─── 正常系 ───────────────────────────────────────────────────────────

    def test_post_subtasks_returns_200_with_subtasks(self):
        """POST /api/todos/{id}/subtasks → 200 と subtasks 配列を返す"""
        todo_id = self._create_todo("牛乳を買う")
        mock_subtasks = self._make_mock_subtasks(5)

        with patch("backend.app.main.generate_subtasks", return_value=mock_subtasks):
            resp = self.client.post(f"/api/todos/{todo_id}/subtasks")

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("subtasks", body)
        self.assertEqual(len(body["subtasks"]), 5)
        self.assertEqual(
            body["subtasks"][0]["title"],
            "大仰なサブタスク 1：ROI と PMBOK を駆使した施策",
        )

    def test_post_subtasks_response_contains_title_field(self):
        """レスポンスの各サブタスクに title フィールドが存在する"""
        todo_id = self._create_todo("会議室を予約する")
        mock_subtasks = self._make_mock_subtasks(5)

        with patch("backend.app.main.generate_subtasks", return_value=mock_subtasks):
            resp = self.client.post(f"/api/todos/{todo_id}/subtasks")

        self.assertEqual(resp.status_code, 200)
        for subtask in resp.json()["subtasks"]:
            self.assertIn("title", subtask)
            self.assertIsInstance(subtask["title"], str)

    # ─── 404: Todo 不在 ──────────────────────────────────────────────────

    def test_post_subtasks_returns_404_for_nonexistent_id(self):
        """存在しない todo_id に対して HTTP 404 を返す"""
        resp = self.client.post("/api/todos/nonexistent-id-12345/subtasks")
        self.assertEqual(resp.status_code, 404)

    def test_post_subtasks_404_body_contains_detail(self):
        """404 レスポンスのボディに detail フィールドが存在する"""
        resp = self.client.post("/api/todos/nonexistent-id/subtasks")
        self.assertEqual(resp.status_code, 404)
        self.assertIn("detail", resp.json())

    # ─── 503: GeminiServiceError ─────────────────────────────────────────

    def test_post_subtasks_returns_503_on_gemini_service_error(self):
        """GeminiServiceError 発生時に HTTP 503 を返す"""
        from backend.app.subtask_service import GeminiServiceError

        todo_id = self._create_todo("テストタスク")

        with patch(
            "backend.app.main.generate_subtasks",
            side_effect=GeminiServiceError("API 呼び出し失敗"),
        ):
            resp = self.client.post(f"/api/todos/{todo_id}/subtasks")

        self.assertEqual(resp.status_code, 503)

    def test_post_subtasks_503_body_contains_detail(self):
        """503 レスポンスのボディに detail フィールドが存在する"""
        from backend.app.subtask_service import GeminiServiceError

        todo_id = self._create_todo("テストタスク")

        with patch(
            "backend.app.main.generate_subtasks",
            side_effect=GeminiServiceError("タイムアウト"),
        ):
            resp = self.client.post(f"/api/todos/{todo_id}/subtasks")

        self.assertEqual(resp.status_code, 503)
        body = resp.json()
        self.assertIn("detail", body)
        self.assertIn("再試行", body["detail"])

    # ─── 503: GeminiConfigError ──────────────────────────────────────────

    def test_post_subtasks_returns_503_on_gemini_config_error(self):
        """GeminiConfigError 発生時に HTTP 503 を返す"""
        from backend.app.subtask_service import GeminiConfigError

        todo_id = self._create_todo("テストタスク")

        with patch(
            "backend.app.main.generate_subtasks",
            side_effect=GeminiConfigError("GEMINI_API_KEY が設定されていません"),
        ):
            resp = self.client.post(f"/api/todos/{todo_id}/subtasks")

        self.assertEqual(resp.status_code, 503)

    def test_post_subtasks_503_on_config_error_contains_detail(self):
        """GeminiConfigError 503 レスポンスに detail が含まれる"""
        from backend.app.subtask_service import GeminiConfigError

        todo_id = self._create_todo("テストタスク")

        with patch(
            "backend.app.main.generate_subtasks",
            side_effect=GeminiConfigError("キー未設定"),
        ):
            resp = self.client.post(f"/api/todos/{todo_id}/subtasks")

        self.assertEqual(resp.status_code, 503)
        self.assertIn("detail", resp.json())
