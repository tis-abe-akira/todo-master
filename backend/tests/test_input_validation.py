"""
Task 5.2: 入力サイズチェックのテスト
- title が 200 文字超の場合 ValidationError（Pydantic）または ValueError を送出する
- description が 1000 文字超の場合も同様
- 正常なサイズは通過する
"""

import unittest

from backend.app.models import CreateTodo, UpdateTodo


class TestInputSizeValidation(unittest.TestCase):
    # 5.2-1: title が 200 文字以下なら正常
    def test_create_todo_title_within_limit(self):
        todo = CreateTodo(title="a" * 200)
        self.assertEqual(len(todo.title), 200)

    # 5.2-2: title が 201 文字超なら ValidationError
    def test_create_todo_title_too_long_raises(self):
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            CreateTodo(title="a" * 201)

    # 5.2-3: description が 1000 文字以下なら正常
    def test_create_todo_description_within_limit(self):
        todo = CreateTodo(title="ok", description="b" * 1000)
        self.assertEqual(len(todo.description), 1000)

    # 5.2-4: description が 1001 文字超なら ValidationError
    def test_create_todo_description_too_long_raises(self):
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            CreateTodo(title="ok", description="b" * 1001)

    # 5.2-5: UpdateTodo の title 上限チェック
    def test_update_todo_title_too_long_raises(self):
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            UpdateTodo(title="a" * 201)


if __name__ == "__main__":
    unittest.main()
