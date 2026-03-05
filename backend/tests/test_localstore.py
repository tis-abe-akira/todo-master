import unittest
import tempfile
import os
import json


class TestLocalStore(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.filepath = os.path.join(self.tmpdir.name, "todos.json")
        # LocalStore is implemented in backend.app.local_store
        from backend.app.local_store import LocalStore

        self.LocalStore = LocalStore

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_atomic_write_and_read(self):
        store = self.LocalStore(self.filepath)
        data = [{"id": "1", "title": "task1"}]
        store.save(data)
        loaded = store.load()
        self.assertEqual(loaded, data)

    def test_backup_and_recovery_on_corruption(self):
        store = self.LocalStore(self.filepath)
        data1 = [{"id": "1", "title": "original"}]
        data2 = [{"id": "2", "title": "updated"}]
        store.save(data1)
        # create a backup by saving a new version
        store.save(data2)
        # Corrupt the file
        with open(self.filepath, "w", encoding="utf-8") as f:
            f.write("not a json")
        # Loading should recover from backup
        loaded = store.load()
        # recovery should return the previous valid content (data1)
        self.assertEqual(loaded, data1)
        # File should be restored to valid JSON
        with open(self.filepath, "r", encoding="utf-8") as f:
            content = json.load(f)
        self.assertEqual(content, data1)


if __name__ == "__main__":
    unittest.main()
