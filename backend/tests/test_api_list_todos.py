import unittest
import tempfile
import os


class TestApiListTodos(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.filepath = os.path.join(self.tmpdir.name, "todos.json")

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_list_todos_empty_when_no_file(self):
        """ファイルが存在しない場合は空リストを返す"""
        from backend.app.main import list_todos
        from backend.app.local_store import LocalStore

        store = LocalStore(self.filepath)
        result = list_todos(store)

        self.assertEqual(result, [])

    def test_list_todos_returns_all_persisted(self):
        """永続化済みの Todo をすべて返す"""
        from backend.app.main import create_and_persist_todo, list_todos
        from backend.app.local_store import LocalStore
        from backend.app.models import CreateTodo

        store = LocalStore(self.filepath)
        create_and_persist_todo(store, CreateTodo(title="Task A"))
        create_and_persist_todo(store, CreateTodo(title="Task B"))

        result = list_todos(store)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        titles = {item["title"] for item in result}
        self.assertIn("Task A", titles)
        self.assertIn("Task B", titles)

    def test_list_todos_items_have_required_fields(self):
        """返却アイテムが必須フィールドをすべて持つ"""
        from backend.app.main import create_and_persist_todo, list_todos
        from backend.app.local_store import LocalStore
        from backend.app.models import CreateTodo

        store = LocalStore(self.filepath)
        create_and_persist_todo(store, CreateTodo(title="Task X", description="desc"))

        result = list_todos(store)
        item = result[0]

        for field in (
            "id",
            "title",
            "description",
            "completed",
            "created_at",
            "updated_at",
        ):
            self.assertIn(field, item, f"フィールド '{field}' が欠落している")
        self.assertFalse(item["completed"])


if __name__ == "__main__":
    unittest.main()
