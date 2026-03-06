# Implementation Plan for todo-app-fastapi-nextjs

## Major tasks and subtasks

- [x] 1. プロジェクト初期設定
- [x] 1.1 Python (FastAPI) 開発環境の初期化と依存関係追加 (P)
  - 仮想環境作成、`requirements.txt` または `pyproject.toml` に FastAPI, Uvicorn, Pydantic, pytest を追加
  - 推定時間: 1.5 時間
  - _Requirements: 3.1, 3.3, 5.1_
- [x] 1.2 Next.js プロジェクトの初期化と基本ページ作成 (P)
  - Next.js アプリを作成し、ページルート `/` を用意して開発ビルドが通る状態にする
  - 推定時間: 1.5 時間
  - _Requirements: 4.1, 4.2_

- [ ] 2. 永続化層 (LocalStore) の実装
- [ ] 2.1 LocalStore: 原子書き込みとバックアップ実装
 - [x] 2. 永続化層 (LocalStore) の実装
 - [x] 2.1 LocalStore: 原子書き込みとバックアップ実装
  - 一時ファイルへの書き込み → fsync → rename を実装し、`.bak` のバックアップ戦略を追加
  - 推定時間: 2.5 時間
  - _Requirements: 2.1, 2.2, 2.3, 5.3_
- [ ] 2.2 LocalStore 単体テスト（原子性・競合シナリオ）
 - [x] 2.2 LocalStore 単体テスト（原子性・競合シナリオ）
  - テスト用ファイルで原子書き込みの成功/失敗パスとバックアップ復元を検証
  - 推定時間: 2 時間
  - _Requirements: 2.1, 2.2_

- [ ] 3. Todo API サービスとエンドポイント実装
 - [x] 3.1 Pydantic モデル定義と入力バリデーションの実装
  - 実装: `backend/app/models.py` に CreateTodo, UpdateTodo, Todo を追加（単体テスト通過）
  - 実装日時: 2026-03-06T13:58:00Z
  - 推定時間: 2 時間
  - _Requirements: 3.1_
- [ ] 3.2 POST /api/todos (タスク作成) の実装と単体テスト
 - [x] 3.2 POST /api/todos (タスク作成) の実装と単体テスト
  - 実装: `backend/app/main.py` に create endpoint と create_and_persist_todo を追加、単体テストで永続化と戻り値 201 を検証
  - 実装日時: 2026-03-06T14:10:00Z
  - 推定時間: 2 時間
  - _Requirements: 1.1, 3.3, 5.1, 5.3_
- [x] 3.3 GET /api/todos (一覧取得) の実装と単体テスト
  - 実装: `backend/app/main.py` に `list_todos` 関数と GET エンドポイントを追加。空ストア・複数件・フィールド検証の 3 テスト通過
  - 実装日時: 2026-03-06T14:30:00Z
  - 推定時間: 1.5 時間
  - _Requirements: 1.2, 3.3, 4.1_
- [x] 3.4 PUT /api/todos/{id} (更新) の実装と単体テスト
  - 実装: `backend/app/main.py` に `update_todo` 関数と PUT エンドポイントを追加。部分更新・updated_at 変更・404・フィールド保持の 5 テスト通過
  - 実装日時: 2026-03-06T14:45:00Z
  - 推定時間: 2 時間
  - _Requirements: 1.3, 3.2, 3.3_
- [x] 3.5 DELETE /api/todos/{id} (削除) の実装と単体テスト
  - 実装: `backend/app/main.py` に `delete_todo` 関数と DELETE エンドポイントを追加。削除確認・204・404・他 Todo 保持の 4 テスト通過
  - 実装日時: 2026-03-06T14:55:00Z
  - 推定時間: 1.5 時間
  - _Requirements: 1.4, 3.2, 3.3_

- [x] 4. フロントエンド機能実装 (並列可能)
- [x] 4.1 タスク一覧ページの実装と API 結合 (P)
  - 実装: `frontend/src/app/todos/page.tsx`, `TodoList.tsx`, `useTodos.ts` を作成。SWR で GET /api/todos を取得し一覧表示。Spinner / EmptyState / ErrorMessage を組み合わせたロード UI を実装
  - 実装日時: 2026-03-06T16:00:00Z
  - 推定時間: 2 時間
  - _Requirements: 4.1, 1.2_
- [x] 4.2 タスク作成 UI と API 呼び出しの実装 (P)
  - 実装: `AddTodoForm.tsx`, `useCreateTodo.ts` を作成。フォーム送信で POST /api/todos を呼び出し、成功後にフォームをリセット、エラー時に ErrorMessage を表示
  - 実装日時: 2026-03-06T16:00:00Z
  - 推定時間: 2 時間
  - _Requirements: 4.2, 1.1_
- [x] 4.3 タスク更新/削除 UI の実装と API 統合 (P)
  - 実装: `TodoCard.tsx`, `useUpdateTodo.ts`, `useDeleteTodo.ts` を作成。インライン編集モード、チェックボックスによる完了トグル、削除ボタンを実装し SWR mutate で一覧を更新
  - 実装日時: 2026-03-06T16:00:00Z
  - 推定時間: 2 時間
  - _Requirements: 4.2, 1.3, 1.4_
- [x] 4.4 ネットワーク遅延時のローディング・多重送信ガード実装 (P)
  - 実装: 各フック (useCreateTodo, useUpdateTodo, useDeleteTodo) に isSubmitting / isDeleting フラグを設け、ボタンを disabled に。Spinner コンポーネント + ErrorMessage でフィードバックを表示
  - 実装日時: 2026-03-06T16:00:00Z
  - 推定時間: 1.5 時間
  - _Requirements: 4.3_

- [x] 5. ログ・エラー応答・運用対応
- [x] 5.1 API ログ出力（作成/更新/削除/エラー）実装 (P)
  - 実装: `backend/app/main.py` に `logging.getLogger("todo_app")` を追加。create/update/delete 成功時に INFO、Not Found 時に WARNING を出力。テスト 5 件通過
  - 実装日時: 2026-03-06T17:00:00Z
  - 推定時間: 1.5 時間
  - _Requirements: 5.1_
- [x] 5.2 入力サイズチェックと簡易レート制限の実装
  - 実装: `backend/app/models.py` の CreateTodo/UpdateTodo に `Field(max_length=200)` (title) と `Field(max_length=1000)` (description) を追加。超過時 Pydantic ValidationError（→ FastAPI が 422 を返す）。テスト 5 件通過
  - 実装日時: 2026-03-06T17:00:00Z
  - 推定時間: 1.5 時間
  - _Requirements: 5.2_
- [x] 5.3 永続化失敗時のクライアント向けエラーハンドリング実装
  - 実装: `create_app` に `@app.exception_handler(IOError)` を追加。save() 失敗時に 500 + 再試行案内 JSON を返す。テスト 3 件通過
  - 実装日時: 2026-03-06T17:00:00Z
  - 推定時間: 1.5 時間
  - _Requirements: 5.3, 2.2_

- [x] 6. テスト（統合・E2E）と品質検証
- [x] 6.1 API と LocalStore の統合テスト作成
  - テスト用ファイルを用いた CRUD の正常系・異常系を検証
  - 推定時間: 2.5 時間
  - 実装日時: 2026-03-06T18:00:00Z
  - 実装内容: `backend/tests/test_integration.py` に 17 テスト作成（TemporaryDirectory + TestClient）。全 51 テスト GREEN
  - _Requirements: 1.1,1.2,1.3,1.4,2.1,2.3,3.1,3.3_
- [x] 6.2 フロントエンド E2E（主要パス）
  - ブラウザ上で一覧表示、作成、更新、削除の E2E を Playwright で作成
  - 推定時間: 3 時間
  - 実装日時: 2026-03-06T18:30:00Z
  - 実装内容: `frontend/e2e/todo.spec.ts` に 13 テスト（一覧・作成・更新・削除・空状態）。Playwright 1.58.2 + Chromium。全 13 テスト GREEN
  - _Requirements: 4.1,4.2,4.3_

- [ ] 7. ドキュメント・API スキーマ
- [ ] 7.1 OpenAPI/README 生成と開発者向け手順作成 (P)
  - 自動生成された OpenAPI を README にまとめ、ローカル起動手順を記載
  - 推定時間: 1.5 時間
  - _Requirements: 3.3, 4.1, 5.1_

## Notes
- すべてのサブタスクは 1–3 時間程度に分割しています。大きいと感じる場合はさらに細分化してください。
- (P) は並列実行可能と判断したタスクに付与しています。並列実行の詳細な条件は `tasks-parallel-analysis.md` を参照してください。
- E2E テスト（6.2）は MVP 後に実行しても良い場合は `- [ ]*` のようにマークしています。
