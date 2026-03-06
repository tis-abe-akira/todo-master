"""
Task 2.1: サブタスク用データモデルの実装テスト
- Subtask / SubtaskListOutput Pydantic モデルの検証
- GeminiServiceError / GeminiConfigError 例外クラスの検証
"""

import pytest
from pydantic import ValidationError


class TestSubtaskModel:
    """Subtask Pydantic モデルのテスト"""

    def test_subtask_has_title_field(self):
        """Subtask モデルが title フィールドを持つことを確認する"""
        from app.subtask_service import Subtask

        subtask = Subtask(
            title="ステークホルダーマップ作成：関係者影響度マトリクスの策定"
        )
        assert (
            subtask.title == "ステークホルダーマップ作成：関係者影響度マトリクスの策定"
        )

    def test_subtask_requires_title(self):
        """title が未指定の場合 ValidationError が発生することを確認する"""
        from app.subtask_service import Subtask

        with pytest.raises(ValidationError):
            Subtask()

    def test_subtask_title_must_be_string(self):
        """title に文字列以外を指定した場合 ValidationError が発生することを確認する"""
        from app.subtask_service import Subtask

        # Pydantic v2 では int は str に変換されるため、None で検証
        with pytest.raises(ValidationError):
            Subtask(title=None)


class TestSubtaskListOutputModel:
    """SubtaskListOutput Pydantic モデルのテスト"""

    def test_subtask_list_output_with_five_subtasks(self):
        """5件のサブタスクリストを正常に作成できることを確認する"""
        from app.subtask_service import Subtask, SubtaskListOutput

        subtasks = [Subtask(title=f"サブタスク {i}") for i in range(5)]
        output = SubtaskListOutput(subtasks=subtasks)
        assert len(output.subtasks) == 5

    def test_subtask_list_output_with_six_subtasks(self):
        """6件のサブタスクリストを正常に作成できることを確認する"""
        from app.subtask_service import Subtask, SubtaskListOutput

        subtasks = [Subtask(title=f"サブタスク {i}") for i in range(6)]
        output = SubtaskListOutput(subtasks=subtasks)
        assert len(output.subtasks) == 6

    def test_subtask_list_output_rejects_less_than_five(self):
        """4件以下のサブタスクリストで ValidationError が発生することを確認する"""
        from app.subtask_service import Subtask, SubtaskListOutput

        subtasks = [Subtask(title=f"サブタスク {i}") for i in range(4)]
        with pytest.raises(ValidationError):
            SubtaskListOutput(subtasks=subtasks)

    def test_subtask_list_output_rejects_more_than_six(self):
        """7件以上のサブタスクリストで ValidationError が発生することを確認する"""
        from app.subtask_service import Subtask, SubtaskListOutput

        subtasks = [Subtask(title=f"サブタスク {i}") for i in range(7)]
        with pytest.raises(ValidationError):
            SubtaskListOutput(subtasks=subtasks)

    def test_subtask_list_output_requires_subtasks(self):
        """subtasks フィールドが必須であることを確認する"""
        from app.subtask_service import SubtaskListOutput

        with pytest.raises(ValidationError):
            SubtaskListOutput()


class TestSubtasksResponseModel:
    """SubtasksResponse Pydantic モデルのテスト"""

    def test_subtasks_response_has_subtasks_field(self):
        """SubtasksResponse が subtasks フィールドを持つことを確認する"""
        from app.subtask_service import Subtask, SubtasksResponse

        subtasks = [Subtask(title="テストサブタスク")]
        response = SubtasksResponse(subtasks=subtasks)
        assert len(response.subtasks) == 1
        assert response.subtasks[0].title == "テストサブタスク"

    def test_subtasks_response_accepts_empty_list(self):
        """SubtasksResponse は空リストも受け付けることを確認する（API レスポンス用）"""
        from app.subtask_service import SubtasksResponse

        response = SubtasksResponse(subtasks=[])
        assert response.subtasks == []


class TestGeminiExceptions:
    """GeminiServiceError / GeminiConfigError 例外クラスのテスト"""

    def test_gemini_service_error_is_exception(self):
        """GeminiServiceError が Exception のサブクラスであることを確認する"""
        from app.subtask_service import GeminiServiceError

        assert issubclass(GeminiServiceError, Exception)

    def test_gemini_config_error_is_exception(self):
        """GeminiConfigError が Exception のサブクラスであることを確認する"""
        from app.subtask_service import GeminiConfigError

        assert issubclass(GeminiConfigError, Exception)

    def test_gemini_service_error_can_be_raised_with_message(self):
        """GeminiServiceError がメッセージ付きで送出・キャッチできることを確認する"""
        from app.subtask_service import GeminiServiceError

        with pytest.raises(GeminiServiceError) as exc_info:
            raise GeminiServiceError("Gemini API 呼び出しに失敗しました")
        assert "Gemini API 呼び出しに失敗しました" in str(exc_info.value)

    def test_gemini_config_error_can_be_raised_with_message(self):
        """GeminiConfigError がメッセージ付きで送出・キャッチできることを確認する"""
        from app.subtask_service import GeminiConfigError

        with pytest.raises(GeminiConfigError) as exc_info:
            raise GeminiConfigError("GEMINI_API_KEY が設定されていません")
        assert "GEMINI_API_KEY が設定されていません" in str(exc_info.value)

    def test_gemini_service_error_distinct_from_config_error(self):
        """GeminiServiceError と GeminiConfigError が別の例外クラスであることを確認する"""
        from app.subtask_service import GeminiConfigError, GeminiServiceError

        assert GeminiServiceError is not GeminiConfigError

    def test_gemini_config_error_not_caught_as_service_error(self):
        """GeminiConfigError が GeminiServiceError としてキャッチされないことを確認する"""
        from app.subtask_service import GeminiConfigError, GeminiServiceError

        with pytest.raises(GeminiConfigError):
            try:
                raise GeminiConfigError("設定エラー")
            except GeminiServiceError:
                pass  # ここには到達しないはず
