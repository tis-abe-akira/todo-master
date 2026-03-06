import unittest
import tempfile
import os


class TestApiUpdateTodo(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.filepath = os.path.join(self.tmpdir.name, "todos.json")

    def tearDown(self):
        self.tmpdir.cleanup()

    def _make_store_with_todo(self, title="Original Title"):
        from backend.app.main import create_and_persist_todo
        from backend.app.local_store import LocalStore
        from backend.app.models import CreateTodo

        store = LocalStore(self.filepath)
        todo = create_and_persist_todo(store, CreateTodo(title=title))
        return store, todo["id"]

    def test_update_title_returns_updated_todo(self):
        """title を更新すると更新後の Todo dict が返る"""
        from backend.app.main import update_todo
        from backend.app.models import UpdateTodo

        store, todo_id = self._make_store_with_todo("Before")
        result = update_todo(store, todo_id, UpdateTodo(title="After"))

        self.assertEqual(result["title"], "After")
        self.assertEqual(result["id"], todo_id)

    def test_update_completed_persists(self):
        """completed フラグを更新すると永続化される"""
        from backend.app.main import update_todo, list_todos
        from backend.app.models import UpdateTodo

        store, todo_id = self._make_store_with_todo()
        update_todo(store, todo_id, UpdateTodo(completed=True))

        items = list_todos(store)
        updated = next(item for item in items if item["id"] == todo_id)
        self.assertTrue(updated["completed"])

    def test_update_updated_at_changes(self):
        """updated_at が更新前と異なる値になる"""
        from backend.app.main import update_todo, list_todos
        from backend.app.models import UpdateTodo

        store, todo_id = self._make_store_with_todo()
        original_items = list_todos(store)
        original_updated_at = next(
            item["updated_at"] for item in original_items if item["id"] == todo_id
        )

        import time

        time.sleep(1)  # 秒単位の差を確実に出す

        update_todo(store, todo_id, UpdateTodo(title="Changed"))
        items = list_todos(store)
        new_updated_at = next(
            item["updated_at"] for item in items if item["id"] == todo_id
        )

        self.assertNotEqual(original_updated_at, new_updated_at)

    def test_update_nonexistent_raises_key_error(self):
        """存在しない id で更新しようとすると KeyError を送出する"""
        from backend.app.main import update_todo
        from backend.app.local_store import LocalStore
        from backend.app.models import UpdateTodo

        store = LocalStore(self.filepath)
        with self.assertRaises(KeyError):
            update_todo(store, "no-such-id", UpdateTodo(title="X"))

    def test_update_partial_fields_only_changes_given_fields(self):
        """指定したフィールドだけ変更され、他のフィールドはそのまま"""
        from backend.app.main import create_and_persist_todo, update_todo
        from backend.app.local_store import LocalStore
        from backend.app.models import CreateTodo, UpdateTodo

        store = LocalStore(self.filepath)
        original = create_and_persist_todo(
            store, CreateTodo(title="Keep", description="keep-desc")
        )
        update_todo(store, original["id"], UpdateTodo(completed=True))

        from backend.app.main import list_todos

        items = list_todos(store)
        item = next(i for i in items if i["id"] == original["id"])

        self.assertEqual(item["title"], "Keep")
        self.assertEqual(item["description"], "keep-desc")
        self.assertTrue(item["completed"])


if __name__ == "__main__":
    unittest.main()
