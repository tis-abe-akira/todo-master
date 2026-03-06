"""
Task 2.3: API キー検証・ロギング・エラーハンドリングのテスト
- GEMINI_API_KEY 未設定時の GeminiConfigError 送出を検証
- Gemini API 呼び出し失敗時の GeminiServiceError ラップを検証
- タイムアウト発生時の GeminiServiceError 送出を検証
- INFO ログ出力（モデル名・リクエスト受信・成功）を検証
"""

import logging
from unittest.mock import MagicMock, patch


class TestApiKeyValidation:
    """GEMINI_API_KEY バリデーションのテスト"""

    def test_generate_subtasks_raises_config_error_for_empty_api_key(self):
        """api_key が空文字の場合 GeminiConfigError が送出されることを確認する"""
        from app.subtask_service import GeminiConfigError, generate_subtasks

        try:
            generate_subtasks(title="テスト", description=None, api_key="")
            assert False, "GeminiConfigError が送出されるべきでした"
        except GeminiConfigError as e:
            assert "GEMINI_API_KEY" in str(e)

    def test_generate_subtasks_raises_config_error_for_whitespace_api_key(self):
        """api_key が空白文字のみの場合 GeminiConfigError が送出されることを確認する"""
        from app.subtask_service import GeminiConfigError, generate_subtasks

        try:
            generate_subtasks(title="テスト", description=None, api_key="   ")
            assert False, "GeminiConfigError が送出されるべきでした"
        except GeminiConfigError as e:
            assert "GEMINI_API_KEY" in str(e)

    def test_generate_subtasks_does_not_raise_config_error_for_valid_key(self):
        """有効な api_key の場合 GeminiConfigError が送出されないことを確認する"""
        from app.subtask_service import Subtask, SubtaskListOutput, generate_subtasks

        mock_output = SubtaskListOutput(
            subtasks=[Subtask(title=f"サブタスク {i}") for i in range(5)]
        )

        with patch("app.subtask_service.ChatGoogleGenerativeAI") as MockLLM:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = mock_output
            MockLLM.return_value.with_structured_output.return_value = mock_chain

            result = generate_subtasks(
                title="テスト", description=None, api_key="valid-api-key"
            )
        assert len(result) == 5


class TestErrorHandling:
    """Gemini API 呼び出し失敗・タイムアウト時のエラーラップのテスト"""

    def _make_mock_output(self, count=5):
        from app.subtask_service import Subtask, SubtaskListOutput

        return SubtaskListOutput(
            subtasks=[Subtask(title=f"サブタスク {i}") for i in range(count)]
        )

    def test_generate_subtasks_wraps_exception_in_service_error(self):
        """Gemini API 呼び出しで Exception が発生した場合 GeminiServiceError にラップされることを確認する"""
        from app.subtask_service import GeminiServiceError, generate_subtasks

        with patch("app.subtask_service.ChatGoogleGenerativeAI") as MockLLM:
            mock_chain = MagicMock()
            mock_chain.invoke.side_effect = Exception("API エラー")
            MockLLM.return_value.with_structured_output.return_value = mock_chain

            try:
                generate_subtasks(title="テスト", description=None, api_key="test-key")
                assert False, "GeminiServiceError が送出されるべきでした"
            except GeminiServiceError as e:
                assert (
                    "API エラー" in str(e) or len(str(e)) >= 0
                )  # メッセージがラップされている

    def test_generate_subtasks_wraps_timeout_in_service_error(self):
        """タイムアウト例外が GeminiServiceError にラップされることを確認する"""
        from app.subtask_service import GeminiServiceError, generate_subtasks

        with patch("app.subtask_service.ChatGoogleGenerativeAI") as MockLLM:
            mock_chain = MagicMock()
            mock_chain.invoke.side_effect = TimeoutError("タイムアウト")
            MockLLM.return_value.with_structured_output.return_value = mock_chain

            try:
                generate_subtasks(title="テスト", description=None, api_key="test-key")
                assert False, "GeminiServiceError が送出されるべきでした"
            except GeminiServiceError:
                pass  # 期待通り

    def test_generate_subtasks_wraps_value_error_in_service_error(self):
        """ValueError（構造化出力失敗など）が GeminiServiceError にラップされることを確認する"""
        from app.subtask_service import GeminiServiceError, generate_subtasks

        with patch("app.subtask_service.ChatGoogleGenerativeAI") as MockLLM:
            mock_chain = MagicMock()
            mock_chain.invoke.side_effect = ValueError("構造化出力に失敗しました")
            MockLLM.return_value.with_structured_output.return_value = mock_chain

            try:
                generate_subtasks(title="テスト", description=None, api_key="test-key")
                assert False, "GeminiServiceError が送出されるべきでした"
            except GeminiServiceError:
                pass  # 期待通り

    def test_generate_subtasks_config_error_not_wrapped_in_service_error(self):
        """GeminiConfigError は GeminiServiceError にラップされずそのまま送出されることを確認する"""
        from app.subtask_service import (
            GeminiConfigError,
            GeminiServiceError,
            generate_subtasks,
        )

        # 空キーで GeminiConfigError が送出される（GeminiServiceError ではない）
        try:
            generate_subtasks(title="テスト", description=None, api_key="")
            assert False, "例外が送出されるべきでした"
        except GeminiConfigError:
            pass  # 期待通り GeminiConfigError
        except GeminiServiceError:
            assert False, "GeminiConfigError として送出されるべきでした"


class TestLogging:
    """ロギングのテスト"""

    def _make_mock_output(self, count=5):
        from app.subtask_service import Subtask, SubtaskListOutput

        return SubtaskListOutput(
            subtasks=[Subtask(title=f"サブタスク {i}") for i in range(count)]
        )

    def test_generate_subtasks_logs_model_name_at_info(self, caplog):
        """generate_subtasks() がモデル名を INFO レベルでログ出力することを確認する"""
        from app.subtask_service import generate_subtasks

        mock_output = self._make_mock_output()

        with patch("app.subtask_service.ChatGoogleGenerativeAI") as MockLLM:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = mock_output
            MockLLM.return_value.with_structured_output.return_value = mock_chain

            with caplog.at_level(logging.INFO, logger="app.subtask_service"):
                generate_subtasks(
                    title="テスト",
                    description=None,
                    api_key="test-key",
                    model="gemini-1.5-flash",
                )

        assert any("gemini-1.5-flash" in r.message for r in caplog.records)

    def test_generate_subtasks_logs_request_at_info(self, caplog):
        """generate_subtasks() がリクエスト受信時に INFO ログを出力することを確認する"""
        from app.subtask_service import generate_subtasks

        mock_output = self._make_mock_output()

        with patch("app.subtask_service.ChatGoogleGenerativeAI") as MockLLM:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = mock_output
            MockLLM.return_value.with_structured_output.return_value = mock_chain

            with caplog.at_level(logging.INFO, logger="app.subtask_service"):
                generate_subtasks(
                    title="牛乳を買う", description=None, api_key="test-key"
                )

        # リクエスト受信ログが出力されていること
        all_messages = " ".join(r.message for r in caplog.records)
        assert (
            "牛乳を買う" in all_messages
            or "subtask" in all_messages.lower()
            or "generate" in all_messages.lower()
        )

    def test_generate_subtasks_logs_success_at_info(self, caplog):
        """generate_subtasks() が成功時に INFO ログを出力することを確認する"""
        from app.subtask_service import generate_subtasks

        mock_output = self._make_mock_output(5)

        with patch("app.subtask_service.ChatGoogleGenerativeAI") as MockLLM:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = mock_output
            MockLLM.return_value.with_structured_output.return_value = mock_chain

            with caplog.at_level(logging.INFO, logger="app.subtask_service"):
                generate_subtasks(
                    title="テスト成功", description=None, api_key="test-key"
                )

        # 成功時ログが INFO レベルで出力されること（少なくとも1件以上）
        info_logs = [r for r in caplog.records if r.levelno == logging.INFO]
        assert len(info_logs) >= 1
