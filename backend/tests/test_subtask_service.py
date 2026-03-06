"""
Task 2.2: 大仰プロンプトテンプレートと generate_subtasks() 関数のテスト
- POMPOUS_SYSTEM_PROMPT 定数の存在・内容を検証
- ChatPromptTemplate の構造を検証
- generate_subtasks() 関数の振る舞いを Mock で検証
"""

from unittest.mock import MagicMock, patch


class TestPompousSystemPrompt:
    """POMPOUS_SYSTEM_PROMPT 定数のテスト"""

    def test_pompous_system_prompt_exists(self):
        """POMPOUS_SYSTEM_PROMPT 定数が定義されていることを確認する"""
        from app.subtask_service import POMPOUS_SYSTEM_PROMPT

        assert POMPOUS_SYSTEM_PROMPT is not None
        assert isinstance(POMPOUS_SYSTEM_PROMPT, str)

    def test_pompous_system_prompt_contains_pmbok(self):
        """POMPOUS_SYSTEM_PROMPT に PMBOK が含まれることを確認する"""
        from app.subtask_service import POMPOUS_SYSTEM_PROMPT

        assert "PMBOK" in POMPOUS_SYSTEM_PROMPT

    def test_pompous_system_prompt_contains_roi(self):
        """POMPOUS_SYSTEM_PROMPT に ROI が含まれることを確認する"""
        from app.subtask_service import POMPOUS_SYSTEM_PROMPT

        assert "ROI" in POMPOUS_SYSTEM_PROMPT

    def test_pompous_system_prompt_contains_stakeholder(self):
        """POMPOUS_SYSTEM_PROMPT にステークホルダー関連の語句が含まれることを確認する"""
        from app.subtask_service import POMPOUS_SYSTEM_PROMPT

        assert "ステークホルダー" in POMPOUS_SYSTEM_PROMPT

    def test_pompous_system_prompt_instructs_five_to_six_subtasks(self):
        """POMPOUS_SYSTEM_PROMPT に 5〜6 件のサブタスク生成指示が含まれることを確認する"""
        from app.subtask_service import POMPOUS_SYSTEM_PROMPT

        assert "5" in POMPOUS_SYSTEM_PROMPT and "6" in POMPOUS_SYSTEM_PROMPT

    def test_pompous_system_prompt_nonempty(self):
        """POMPOUS_SYSTEM_PROMPT が空でないことを確認する"""
        from app.subtask_service import POMPOUS_SYSTEM_PROMPT

        assert len(POMPOUS_SYSTEM_PROMPT.strip()) > 50


class TestGenerateSubtasksFunction:
    """generate_subtasks() 関数のテスト（Mock 使用）"""

    def _make_mock_output(self, titles):
        """テスト用のモック出力を生成するヘルパー"""
        from app.subtask_service import Subtask, SubtaskListOutput

        subtasks = [Subtask(title=t) for t in titles]
        return SubtaskListOutput(subtasks=subtasks)

    def test_generate_subtasks_returns_list_of_subtask(self):
        """generate_subtasks() が list[Subtask] を返すことを確認する"""
        from app.subtask_service import Subtask, generate_subtasks

        mock_titles = [
            "ステークホルダーマップ作成：関係者影響度マトリクスの策定",
            "ROI 試算：投資回収期間の算定と財務モデリング",
            "リスクアセスメント：サプライチェーン脆弱性の包括的評価",
            "変革管理フレームワークの構築と組織変革計画の策定",
            "KPI 体系の確立とパフォーマンス管理ダッシュボードの設計",
        ]
        mock_output = self._make_mock_output(mock_titles)

        with patch("app.subtask_service.ChatGoogleGenerativeAI") as MockLLM:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = mock_output
            MockLLM.return_value.with_structured_output.return_value = mock_chain

            result = generate_subtasks(
                title="牛乳を買う",
                description=None,
                api_key="test-api-key",
            )

        assert isinstance(result, list)
        assert len(result) == 5
        assert all(isinstance(s, Subtask) for s in result)

    def test_generate_subtasks_passes_title_to_chain(self):
        """generate_subtasks() がタイトルをチェーンに渡すことを確認する"""
        from app.subtask_service import generate_subtasks

        mock_titles = [f"サブタスク {i}" for i in range(5)]
        mock_output = self._make_mock_output(mock_titles)

        with patch("app.subtask_service.ChatGoogleGenerativeAI") as MockLLM:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = mock_output
            MockLLM.return_value.with_structured_output.return_value = mock_chain

            generate_subtasks(
                title="会議室を予約する",
                description="来週月曜の午後",
                api_key="test-api-key",
            )

            call_kwargs = mock_chain.invoke.call_args
            assert call_kwargs is not None
            # invoke に渡された引数に title が含まれることを確認
            args, kwargs = call_kwargs
            invoked_input = args[0] if args else kwargs
            input_str = str(invoked_input)
            assert "会議室を予約する" in input_str

    def test_generate_subtasks_uses_specified_model(self):
        """generate_subtasks() が指定したモデルで ChatGoogleGenerativeAI を初期化することを確認する"""
        from app.subtask_service import generate_subtasks

        mock_output = self._make_mock_output([f"サブタスク {i}" for i in range(5)])

        with patch("app.subtask_service.ChatGoogleGenerativeAI") as MockLLM:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = mock_output
            MockLLM.return_value.with_structured_output.return_value = mock_chain

            generate_subtasks(
                title="テスト",
                description=None,
                api_key="test-api-key",
                model="gemini-1.5-flash",
            )

            init_kwargs = MockLLM.call_args.kwargs
            assert init_kwargs.get("model") == "gemini-1.5-flash"

    def test_generate_subtasks_uses_api_key(self):
        """generate_subtasks() が api_key を ChatGoogleGenerativeAI に渡すことを確認する"""
        from app.subtask_service import generate_subtasks

        mock_output = self._make_mock_output([f"サブタスク {i}" for i in range(5)])

        with patch("app.subtask_service.ChatGoogleGenerativeAI") as MockLLM:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = mock_output
            MockLLM.return_value.with_structured_output.return_value = mock_chain

            generate_subtasks(
                title="テスト",
                description=None,
                api_key="my-secret-key",
            )

            init_kwargs = MockLLM.call_args.kwargs
            assert init_kwargs.get("google_api_key") == "my-secret-key"

    def test_generate_subtasks_uses_with_structured_output(self):
        """generate_subtasks() が with_structured_output(SubtaskListOutput) を呼び出すことを確認する"""
        from app.subtask_service import SubtaskListOutput, generate_subtasks

        mock_output = self._make_mock_output([f"サブタスク {i}" for i in range(5)])

        with patch("app.subtask_service.ChatGoogleGenerativeAI") as MockLLM:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = mock_output
            MockLLM.return_value.with_structured_output.return_value = mock_chain

            generate_subtasks(
                title="テスト",
                description=None,
                api_key="test-api-key",
            )

            MockLLM.return_value.with_structured_output.assert_called_once_with(
                SubtaskListOutput
            )

    def test_generate_subtasks_with_description(self):
        """description が指定された場合もサブタスクが正常に返ることを確認する"""
        from app.subtask_service import generate_subtasks

        mock_output = self._make_mock_output([f"サブタスク {i}" for i in range(6)])

        with patch("app.subtask_service.ChatGoogleGenerativeAI") as MockLLM:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = mock_output
            MockLLM.return_value.with_structured_output.return_value = mock_chain

            result = generate_subtasks(
                title="買い物リスト作成",
                description="スーパーで食材を購入する",
                api_key="test-api-key",
            )

        assert len(result) == 6

    def test_generate_subtasks_default_model_is_gemini_flash(self):
        """generate_subtasks() のデフォルトモデルが gemini-1.5-flash であることを確認する"""
        from app.subtask_service import generate_subtasks

        mock_output = self._make_mock_output([f"サブタスク {i}" for i in range(5)])

        with patch("app.subtask_service.ChatGoogleGenerativeAI") as MockLLM:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = mock_output
            MockLLM.return_value.with_structured_output.return_value = mock_chain

            generate_subtasks(title="テスト", description=None, api_key="test-key")

            init_kwargs = MockLLM.call_args.kwargs
            assert init_kwargs.get("model") == "gemini-1.5-flash"
