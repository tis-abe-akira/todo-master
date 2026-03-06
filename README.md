# Todo App — FastAPI + Next.js

シンプルな Todo 管理アプリ。バックエンドに **FastAPI**、フロントエンドに **Next.js 16 (App Router)** を使用しています。

---

## 構成

```
todo-master/
├── backend/          # FastAPI (Python 3.11, uv 管理)
│   ├── app/
│   │   ├── main.py         # エンドポイント + ビジネスロジック
│   │   ├── models.py       # Pydantic モデル (バリデーション付き)
│   │   └── local_store.py  # JSON ファイル永続化 (原子書き込み)
│   ├── tests/        # unittest (51 件)
│   │   ├── test_api_*.py         # API 単体テスト
│   │   ├── test_integration.py   # LocalStore 統合テスト
│   │   ├── test_localstore.py    # 永続化層テスト
│   │   ├── test_logging.py       # ログ出力テスト
│   │   └── test_persistence_failure.py  # エラーハンドリングテスト
│   ├── pyproject.toml
│   └── .venv/        # uv で作成した仮想環境
└── frontend/         # Next.js 16 (TypeScript, Tailwind CSS v4, SWR)
    ├── src/
    │   ├── app/          # App Router ページ
    │   ├── components/   # UI + Todo コンポーネント
    │   ├── hooks/        # SWR カスタムフック
    │   ├── lib/          # API クライアント / ユーティリティ
    │   └── types/        # 型定義
    ├── e2e/          # Playwright E2E テスト (13 件)
    ├── playwright.config.ts
    └── package.json
```

---

## セットアップ

### 前提条件

| ツール | バージョン | 備考 |
|-------|-----------|------|
| Python | 3.11+ | |
| uv | 最新 | `curl -Ls https://astral.sh/uv/install.sh \| sh` |
| Node.js | 18+ | |
| npm | 9+ | Node.js に同梱 |

### バックエンド（初回のみ）

```bash
# uv がなければ先にインストール
curl -Ls https://astral.sh/uv/install.sh | sh

cd backend
uv sync          # .venv/ を作成して依存パッケージをインストール
```

### フロントエンド（初回のみ）

```bash
cd frontend
npm install
# Playwright ブラウザのインストール (E2E テスト用)
npx playwright install chromium
```

---

## 起動方法

**ターミナルを 2 つ用意してください。**

### ① バックエンド起動（ターミナル 1）

```bash
cd /path/to/todo-master/backend
PYTHONPATH=. /path/to/todo-master/backend/.venv/bin/uvicorn app.main:app --reload --port 8000
```

> **ショートカット（backend ディレクトリ内から）**
> ```bash
> cd todo-master/backend
> PYTHONPATH=. .venv/bin/uvicorn app.main:app --reload --port 8000
> ```
>
> ※ macOS/zsh で `.venv/bin/uvicorn` が見つからない場合は絶対パスで指定してください。

起動後 → [http://localhost:8000/docs](http://localhost:8000/docs) で Swagger UI が確認できます。

### ② フロントエンド起動（ターミナル 2）

```bash
cd todo-master/frontend
npm run dev
```

起動後 → [http://localhost:3000](http://localhost:3000) をブラウザで開く（自動で `/todos` にリダイレクト）。

---

## 動作確認チェックリスト

| 操作 | 確認ポイント |
|---|---|
| ページ表示 | `/todos` に遷移し「タスクがありません」が表示される |
| Todo 追加 | タイトルを入力して「+ 追加」→ 一覧に表示される |
| 完了チェック | チェックボックスをクリック → タイトルに打ち消し線がつく |
| 編集 | 「編集」ボタン → タイトル/説明を変更して「保存」 |
| 削除 | 「削除」ボタン → 一覧から消える |
| データ永続化 | バックエンド再起動後もデータが残る（`backend/todos.json` に保存） |

---

## テスト実行

### バックエンド単体・統合テスト（51 件）

```bash
# リポジトリルートから実行
cd todo-master
PYTHONPATH=. backend/.venv/bin/python -m unittest discover backend/tests
```

すべて `OK (ran 51 tests)` になることを確認してください。

### フロントエンド E2E テスト — Playwright（13 件）

E2E テストはバックエンドとフロントエンドの両サーバーが起動している状態で実行します。

```bash
# ① バックエンド起動（ターミナル 1）
cd todo-master/backend
PYTHONPATH=. .venv/bin/uvicorn app.main:app --port 8000

# ② フロントエンド起動（ターミナル 2）
cd todo-master/frontend
npm run dev

# ③ E2E 実行（ターミナル 3）
cd todo-master/frontend
npm run test:e2e
```

インタラクティブな UI モードで確認する場合:

```bash
cd todo-master/frontend
npm run test:e2e:ui
```

---

## API エンドポイント

バックエンド起動後、[http://localhost:8000/docs](http://localhost:8000/docs) で Swagger UI、[http://localhost:8000/redoc](http://localhost:8000/redoc) で ReDoc が利用できます。

| メソッド | パス | 説明 | 成功レスポンス |
|---|---|---|---|
| `GET` | `/api/todos` | Todo 一覧取得 | `200 OK` — `Todo[]` |
| `POST` | `/api/todos` | Todo 作成 | `201 Created` — `Todo` |
| `PUT` | `/api/todos/{id}` | Todo 更新（部分更新可） | `200 OK` — `Todo` |
| `DELETE` | `/api/todos/{id}` | Todo 削除 | `204 No Content` |

### スキーマ

#### `Todo`（レスポンス）

```json
{
  "id": "uuid-string",
  "title": "string",
  "description": "string | null",
  "completed": false,
  "created_at": "2026-03-06T00:00:00Z",
  "updated_at": "2026-03-06T00:00:00Z"
}
```

#### `CreateTodo`（POST リクエスト）

```json
{
  "title": "string (必須, 最大 200 文字)",
  "description": "string | null (任意, 最大 1000 文字)"
}
```

#### `UpdateTodo`（PUT リクエスト — すべてのフィールドが任意）

```json
{
  "title": "string | null (最大 200 文字)",
  "description": "string | null (最大 1000 文字)",
  "completed": "boolean | null"
}
```

### エラーレスポンス

| ステータス | 原因 |
|---|---|
| `404 Not Found` | 指定 ID の Todo が存在しない |
| `422 Unprocessable Entity` | バリデーションエラー（title が空、文字数超過など） |
| `500 Internal Server Error` | 永続化ファイルへの書き込み失敗 |

### OpenAPI スキーマ取得

```bash
curl http://localhost:8000/openapi.json
```

---

## 技術スタック

| レイヤー | 技術 / バージョン | 役割 |
|--------|-----------------|------|
| フロントエンド | Next.js 16 (React 19), TypeScript | UI・ルーティング |
| データフェッチ | SWR v2 | サーバー状態管理 |
| スタイリング | Tailwind CSS v4 | CSS フレームワーク |
| バックエンド | FastAPI + Uvicorn (Python 3.11+) | REST API |
| バリデーション | Pydantic v2 | 入力スキーマ検証 |
| 永続化 | ローカル JSON ファイル | 原子書き込み + `.bak` バックアップ |
| 単体・統合テスト | Python unittest, httpx | バックエンドテスト (51 件) |
| E2E テスト | Playwright 1.58 + Chromium | ブラウザ自動テスト (13 件) |
