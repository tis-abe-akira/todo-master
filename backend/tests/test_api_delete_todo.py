import unittest
import tempfile
import os


class TestApiDeleteTodo(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.filepath = os.path.join(self.tmpdir.name, "todos.json")

    def tearDown(self):
        self.tmpdir.cleanup()

    def _make_store_with_todo(self, title="To Delete"):
        from backend.app.main import create_and_persist_todo
        from backend.app.local_store import LocalStore
        from backend.app.models import CreateTodo

        store = LocalStore(self.filepath)
        todo = create_and_persist_todo(store, CreateTodo(title=title))
        return store, todo["id"]

    def test_delete_removes_todo_from_store(self):
        """削除後に一覧から該当 Todo が消える"""
        from backend.app.main import delete_todo, list_todos

        store, todo_id = self._make_store_with_todo()
        delete_todo(store, todo_id)

        items = list_todos(store)
        ids = [item["id"] for item in items]
        self.assertNotIn(todo_id, ids)

    def test_delete_returns_none(self):
        """削除成功時は None を返す（204 No Content に対応）"""
        from backend.app.main import delete_todo

        store, todo_id = self._make_store_with_todo()
        result = delete_todo(store, todo_id)

        self.assertIsNone(result)

    def test_delete_nonexistent_raises_key_error(self):
        """存在しない id の削除は KeyError を送出する"""
        from backend.app.main import delete_todo
        from backend.app.local_store import LocalStore

        store = LocalStore(self.filepath)
        with self.assertRaises(KeyError):
            delete_todo(store, "no-such-id")

    def test_delete_does_not_affect_other_todos(self):
        """特定の Todo を削除しても他の Todo は残る"""
        from backend.app.main import create_and_persist_todo, delete_todo, list_todos
        from backend.app.local_store import LocalStore
        from backend.app.models import CreateTodo

        store = LocalStore(self.filepath)
        todo_a = create_and_persist_todo(store, CreateTodo(title="Keep A"))
        todo_b = create_and_persist_todo(store, CreateTodo(title="Delete B"))
        todo_c = create_and_persist_todo(store, CreateTodo(title="Keep C"))

        delete_todo(store, todo_b["id"])

        items = list_todos(store)
        ids = [item["id"] for item in items]
        self.assertIn(todo_a["id"], ids)
        self.assertNotIn(todo_b["id"], ids)
        self.assertIn(todo_c["id"], ids)


if __name__ == "__main__":
    unittest.main()
