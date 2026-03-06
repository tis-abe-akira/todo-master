"""
Task 5.1: API ログ出力（作成/更新/削除/エラー）のテスト
- create_and_persist_todo 呼び出し時に INFO ログが出力される
- update_todo 呼び出し時に INFO ログが出力される
- delete_todo 呼び出し時に INFO ログが出力される
- KeyError 発生時に WARNING ログが出力される
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app.local_store import LocalStore
from backend.app.models import CreateTodo, UpdateTodo
from backend.app import main as app_main


class TestLogging(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.store_path = os.path.join(self.tmpdir.name, "todos.json")
        self.store = LocalStore(self.store_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    # 5.1-1: create で INFO ログが出力される
    def test_create_logs_info(self):
        with self.assertLogs("todo_app", level="INFO") as cm:
            payload = CreateTodo(title="ログテスト")
            app_main.create_and_persist_todo(self.store, payload)
        self.assertTrue(
            any("create" in msg.lower() or "作成" in msg for msg in cm.output)
        )

    # 5.1-2: update で INFO ログが出力される
    def test_update_logs_info(self):
        payload = CreateTodo(title="更新前")
        todo = app_main.create_and_persist_todo(self.store, payload)
        with self.assertLogs("todo_app", level="INFO") as cm:
            app_main.update_todo(self.store, todo["id"], UpdateTodo(title="更新後"))
        self.assertTrue(
            any("update" in msg.lower() or "更新" in msg for msg in cm.output)
        )

    # 5.1-3: delete で INFO ログが出力される
    def test_delete_logs_info(self):
        payload = CreateTodo(title="削除対象")
        todo = app_main.create_and_persist_todo(self.store, payload)
        with self.assertLogs("todo_app", level="INFO") as cm:
            app_main.delete_todo(self.store, todo["id"])
        self.assertTrue(
            any("delete" in msg.lower() or "削除" in msg for msg in cm.output)
        )

    # 5.1-4: 存在しない id の update で WARNING ログが出力される
    def test_update_notfound_logs_warning(self):
        with self.assertLogs("todo_app", level="WARNING") as cm:
            try:
                app_main.update_todo(self.store, "no-such-id", UpdateTodo(title="x"))
            except KeyError:
                pass
        self.assertTrue(any("WARNING" in msg for msg in cm.output))

    # 5.1-5: 存在しない id の delete で WARNING ログが出力される
    def test_delete_notfound_logs_warning(self):
        with self.assertLogs("todo_app", level="WARNING") as cm:
            try:
                app_main.delete_todo(self.store, "no-such-id")
            except KeyError:
                pass
        self.assertTrue(any("WARNING" in msg for msg in cm.output))


if __name__ == "__main__":
    unittest.main()
