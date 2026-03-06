"""
Task 6.1: API と LocalStore の統合テスト
- FastAPI TestClient を使い、実際の一時ファイルに対して CRUD 全パスを検証する
- 正常系・異常系・バリデーション・データ永続化を網羅
"""

import os
import tempfile
import unittest

from fastapi.testclient import TestClient

from backend.app.main import create_app


class TestApiIntegration(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.store_path = os.path.join(self.tmpdir.name, "todos.json")
        self.app = create_app(self.store_path)
        self.client = TestClient(self.app)

    def tearDown(self):
        self.tmpdir.cleanup()

    # ─── 正常系: 作成 ───────────────────────────────────────────────
    def test_create_returns_201_with_todo(self):
        """POST /api/todos → 201 と Todo オブジェクトを返す"""
        resp = self.client.post("/api/todos", json={"title": "牛乳を買う"})
        self.assertEqual(resp.status_code, 201)
        body = resp.json()
        self.assertEqual(body["title"], "牛乳を買う")
        self.assertIn("id", body)
        self.assertFalse(body["completed"])

    def test_create_with_description(self):
        """POST /api/todos （description あり）→ 説明が保存される"""
        resp = self.client.post(
            "/api/todos", json={"title": "買い物", "description": "スーパーへ"}
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()["description"], "スーパーへ")

    def test_create_persists_to_file(self):
        """作成後に GET で取得できる（ファイル永続化確認）"""
        self.client.post("/api/todos", json={"title": "永続化テスト"})
        resp = self.client.get("/api/todos")
        self.assertEqual(resp.status_code, 200)
        titles = [t["title"] for t in resp.json()]
        self.assertIn("永続化テスト", titles)

    # ─── 正常系: 一覧取得 ────────────────────────────────────────────
    def test_list_empty_at_start(self):
        """初期状態で GET /api/todos → 空リスト"""
        resp = self.client.get("/api/todos")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), [])

    def test_list_returns_all_created(self):
        """複数作成後 GET /api/todos → 全件返す"""
        self.client.post("/api/todos", json={"title": "A"})
        self.client.post("/api/todos", json={"title": "B"})
        resp = self.client.get("/api/todos")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 2)

    # ─── 正常系: 更新 ───────────────────────────────────────────────
    def test_update_title(self):
        """PUT /api/todos/{id} でタイトルを更新できる"""
        todo_id = self.client.post("/api/todos", json={"title": "旧タイトル"}).json()[
            "id"
        ]
        resp = self.client.put(f"/api/todos/{todo_id}", json={"title": "新タイトル"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["title"], "新タイトル")

    def test_update_completed_flag(self):
        """PUT /api/todos/{id} で completed を true に更新できる"""
        todo_id = self.client.post("/api/todos", json={"title": "完了テスト"}).json()[
            "id"
        ]
        resp = self.client.put(f"/api/todos/{todo_id}", json={"completed": True})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["completed"])

    def test_update_persists(self):
        """更新後に GET で新しい値が返る"""
        todo_id = self.client.post("/api/todos", json={"title": "変更前"}).json()["id"]
        self.client.put(f"/api/todos/{todo_id}", json={"title": "変更後"})
        todos = self.client.get("/api/todos").json()
        titles = [t["title"] for t in todos]
        self.assertIn("変更後", titles)
        self.assertNotIn("変更前", titles)

    # ─── 正常系: 削除 ───────────────────────────────────────────────
    def test_delete_returns_204(self):
        """DELETE /api/todos/{id} → 204"""
        todo_id = self.client.post("/api/todos", json={"title": "削除対象"}).json()[
            "id"
        ]
        resp = self.client.delete(f"/api/todos/{todo_id}")
        self.assertEqual(resp.status_code, 204)

    def test_delete_removes_from_list(self):
        """削除後に GET で該当 Todo が消える"""
        todo_id = self.client.post("/api/todos", json={"title": "消す"}).json()["id"]
        self.client.delete(f"/api/todos/{todo_id}")
        ids = [t["id"] for t in self.client.get("/api/todos").json()]
        self.assertNotIn(todo_id, ids)

    def test_delete_does_not_affect_others(self):
        """削除しても他の Todo は残る"""
        id_a = self.client.post("/api/todos", json={"title": "残す"}).json()["id"]
        id_b = self.client.post("/api/todos", json={"title": "消す"}).json()["id"]
        self.client.delete(f"/api/todos/{id_b}")
        ids = [t["id"] for t in self.client.get("/api/todos").json()]
        self.assertIn(id_a, ids)
        self.assertNotIn(id_b, ids)

    # ─── 異常系 ─────────────────────────────────────────────────────
    def test_create_without_title_returns_422(self):
        """title なし POST → 422"""
        resp = self.client.post("/api/todos", json={"description": "タイトルなし"})
        self.assertEqual(resp.status_code, 422)

    def test_create_title_too_long_returns_422(self):
        """title 201 文字超 POST → 422"""
        resp = self.client.post("/api/todos", json={"title": "a" * 201})
        self.assertEqual(resp.status_code, 422)

    def test_update_nonexistent_returns_404(self):
        """存在しない id への PUT → 404"""
        resp = self.client.put("/api/todos/no-such-id", json={"title": "x"})
        self.assertEqual(resp.status_code, 404)

    def test_delete_nonexistent_returns_404(self):
        """存在しない id への DELETE → 404"""
        resp = self.client.delete("/api/todos/no-such-id")
        self.assertEqual(resp.status_code, 404)

    # ─── データ整合性 ────────────────────────────────────────────────
    def test_required_fields_present(self):
        """作成した Todo に必須フィールドが全て含まれる"""
        body = self.client.post("/api/todos", json={"title": "フィールド確認"}).json()
        for field in ["id", "title", "completed", "created_at", "updated_at"]:
            self.assertIn(field, body, f"フィールド '{field}' がない")

    def test_updated_at_changes_on_update(self):
        """更新後に updated_at が変わる"""
        import time

        todo = self.client.post("/api/todos", json={"title": "更新前"}).json()
        time.sleep(1)
        updated = self.client.put(
            f"/api/todos/{todo['id']}", json={"title": "更新後"}
        ).json()
        self.assertNotEqual(todo["updated_at"], updated["updated_at"])


if __name__ == "__main__":
    unittest.main()
