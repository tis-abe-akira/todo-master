# Implementation Plan for ai-pompous-subtask-decomposer

## Major tasks and subtasks

- [x] 1. 依存ライブラリとプロジェクト初期設定
- [x] 1.1 バックエンド依存パッケージの追加
  - `pyproject.toml` に `langchain-google-genai>=2.1.0` および `python-dotenv>=1.0.0` を追加する
  - 仮想環境を再作成または `uv sync` を実行してパッケージをインストールし、既存の 51 件テストが引き続きパスすることを確認する
  - _Requirements: 6.1, 6.2, 6.3_
- [x] 1.2 環境変数テンプレートの作成
  - リポジトリルートに `.env.example` を作成し `GEMINI_API_KEY=` を記載する
  - `.gitignore` に `.env` が含まれていることを確認する（未記載の場合は追記する）
  - _Requirements: 5.1_

- [ ] 2. AI サブタスク生成サービスの実装
- [ ] 2.1 サブタスク用データモデルの実装
  - `Subtask`（`title` フィールドのみ）と `SubtaskListOutput`（5〜6 件の `subtasks` リスト）の Pydantic モデルを定義する
  - `GeminiServiceError`（API 呼び出し失敗・タイムアウト用）と `GeminiConfigError`（API キー未設定用）の例外クラスを定義する
  - _Requirements: 1.5, 1.2_
- [ ] 2.2 大仰プロンプトテンプレートと生成関数の実装
  - PMBOK・ROI・ステークホルダー分析・競合分析・サプライチェーンリスク管理などのコンサルティングフレームワークを駆使して些細なタスクを壮大なプロジェクトに昇華させる System プロンプトを定数として定義する
  - `ChatPromptTemplate` で System + Human メッセージを組み立て、`ChatGoogleGenerativeAI` と `with_structured_output(SubtaskListOutput)` を連結したチェーンを構築する
  - `generate_subtasks(title, description, api_key, model, timeout)` 関数を実装し、チェーンを呼び出して `list[Subtask]` を返す
  - _Requirements: 1.1, 2.1, 2.2, 2.3, 2.4, 2.5_
- [ ] 2.3 API キー検証・ロギング・エラーハンドリングの実装
  - `GEMINI_API_KEY` が空の場合は `GeminiConfigError` を送出し、INFO ログに使用モデル名を出力する
  - タイムアウト（30 秒）超過・Gemini API 呼び出し失敗をすべて `GeminiServiceError` にラップする
  - サブタスク生成リクエスト受信時と成功時に INFO レベルでログを出力する
  - _Requirements: 1.6, 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 3. サブタスク生成 API エンドポイントの実装
  - `create_app()` 内に `POST /api/todos/{id}/subtasks` ルートを追加する
  - 指定された `id` の Todo が存在しない場合は 404 を返す（既存の update/delete パターンと同様）
  - `generate_subtasks()` を呼び出し、成功時は HTTP 200 + `SubtasksResponse` JSON を返す
  - `GeminiServiceError` および `GeminiConfigError` 発生時は HTTP 503 + 再試行案内 JSON を返す `@app.exception_handler` を追加する
  - _Requirements: 1.1, 1.3, 1.4, 5.2_

- [ ] 4. バックエンドテスト
- [ ] 4.1 SubtaskService 単体テスト
  - `ChatGoogleGenerativeAI` を `unittest.mock.patch` でモックし、`generate_subtasks()` が `SubtaskListOutput` を正しく返すことを検証する
  - `GEMINI_API_KEY` 未設定時に `GeminiConfigError` が送出されることを検証する
  - Gemini API 呼び出し失敗時に `GeminiServiceError` が送出されることを検証する
  - タイムアウト発生時に `GeminiServiceError` が送出されることを検証する
  - _Requirements: 1.1, 1.5, 5.1, 5.2, 5.4_
- [ ] 4.2 エンドポイント統合テスト
  - `generate_subtasks` をモックして `POST /api/todos/{id}/subtasks` が HTTP 200 + subtasks 配列を返すことを `TestClient` で検証する
  - 存在しない `id` に対して HTTP 404 が返ることを検証する
  - `GeminiServiceError` 発生時に HTTP 503 が返ることを検証する
  - 既存の 51 件テストをすべて実行して regression がないことを確認する
  - _Requirements: 1.3, 1.4, 6.3_

- [ ] 5. フロントエンド型定義と API フック (P)
- [ ] 5.1 (P) サブタスク関連の TypeScript 型定義の追加
  - `Subtask`（`title: string`）と `SubtasksResponse`（`subtasks: Subtask[]`）型を追加する
  - `any` の使用を禁止し、すべてのフィールドを明示的な型で定義する
  - _Requirements: 1.5_
- [ ] 5.2 (P) useGenerateSubtasks カスタムフックの実装
  - `subtasks`・`isGenerating`・`error` の state と `generate(todoId)` 関数を持つフックを実装する
  - `api.post<SubtasksResponse>` でバックエンドを呼び出し、成功時は `subtasks` state を更新（再生成時は上書き）する
  - `ApiError` をキャッチして `error` state に文字列をセットし、`finally` で `isGenerating` をリセットする（`useUpdateTodo` と同パターン）
  - _Requirements: 3.2, 3.4, 4.4_

- [ ] 6. サブタスク表示コンポーネントの実装 (P)
- [ ] 6.1 (P) SubtaskItem コンポーネントの実装
  - `index`（番号表示用）と `title` を props として受け取り、`index + 1` を前置した番号付き表示をレンダリングする
  - 既存の UI カラー変数（`text-[#5C5A55]`・`text-xs` 等）に準拠したスタイリングを適用する
  - _Requirements: 4.2, 3.6_
- [ ] 6.2 (P) SubtaskList コンポーネントの実装
  - `subtasks` props が空配列のとき `null` を返す（非表示）
  - Tailwind の `transition-all` + `max-height` によるアニメーション付き展開・収縮を実装する
  - `SubtaskItem` を `subtasks.map()` でレンダリングし、上部に境界線（`border-t border-[#E8E6E1]`）を設ける
  - _Requirements: 4.1, 4.3, 4.5_

- [ ] 7. TodoCard への統合とエンドツーエンド動作確認
  - `useGenerateSubtasks` フックを `TodoCard` に追加し、「🤖 サブタスク分解」ボタンを非編集モード時のボタン群に追加する
  - `isGenerating` を既存の `isSaving || isDeleting` の disabled 判定に加え、ボタンクリック中の多重送信を防止する
  - `subtasks.length > 0` のとき `<SubtaskList subtasks={subtasks} />` を `Card` 最下部にレンダリングし、エラー時は `<ErrorMessage>` を表示する
  - バックエンドを起動した状態でブラウザから動作確認（ボタン押下 → スピナー → サブタスク展開）を実施する
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.4_

## Notes
- タスク 5（フロントエンド型定義・フック）とタスク 6（表示コンポーネント）はバックエンド実装（タスク 2〜4）と並列実行可能。ただし、両者の API 型契約（`SubtasksResponse`）はタスク 1 完了後にタスク 5.1 で確定するため、タスク 5.2 と 6.x はタスク 5.1 の完了後に開始すること。
- タスク 7 はタスク 5・6 の両方が完了してから実施すること。
- `(P)` は並列実行可能なサブタスクに付与している。
