import unittest
from pydantic import ValidationError


class TestTodoModels(unittest.TestCase):
    def test_create_todo_requires_title(self):
        # Missing title should raise ValidationError
        from backend.app.models import CreateTodo

        with self.assertRaises(ValidationError):
            CreateTodo(description="no title")

    def test_create_todo_title_must_be_string(self):
        from backend.app.models import CreateTodo

        with self.assertRaises(ValidationError):
            CreateTodo(title=123)

    def test_update_todo_allows_partial_fields(self):
        from backend.app.models import UpdateTodo

        # Should allow creating update payload with only one field
        upd = UpdateTodo(completed=True)
        self.assertTrue(upd.completed)

    def test_todo_model_fields_and_defaults(self):
        from backend.app.models import Todo

        t = Todo(
            id="1",
            title="t",
            created_at="2026-03-06T00:00:00Z",
            updated_at="2026-03-06T00:00:00Z",
        )
        self.assertFalse(t.completed)
        self.assertEqual(t.id, "1")


if __name__ == "__main__":
    unittest.main()
