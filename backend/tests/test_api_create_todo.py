import unittest
import tempfile
import os
import json


class TestApiCreateTodo(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.filepath = os.path.join(self.tmpdir.name, "todos.json")

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_post_creates_todo_and_persists(self):
        # Use the core creation function directly to avoid requiring FastAPI in test env
        from backend.app.main import create_and_persist_todo
        from backend.app.local_store import LocalStore
        from backend.app.models import CreateTodo

        store = LocalStore(self.filepath)
        payload = CreateTodo(title="Buy milk", description="2L whole")
        data = create_and_persist_todo(store, payload)

        # Expect created dict
        self.assertIsInstance(data, dict)
        self.assertIn("id", data)
        self.assertEqual(data["title"], payload.title)
        self.assertEqual(data.get("description"), payload.description)
        self.assertFalse(data.get("completed", True))
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)

        # Check persisted file contains the todo
        with open(self.filepath, "r", encoding="utf-8") as f:
            stored = json.load(f)
        self.assertIsInstance(stored, list)
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0]["id"], data["id"])


if __name__ == "__main__":
    unittest.main()
