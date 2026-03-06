# Todo App — FastAPI + Next.js

シンプルな Todo 管理アプリ。バックエンドに **FastAPI**、フロントエンドに **Next.js 16 (App Router)** を使用しています。

---

## 構成

```
todo-master/
├── backend/          # FastAPI (Python 3.11, uv 管理)
│   ├── app/
│   │   ├── main.py         # エンドポイント + ビジネスロジック
│   │   ├── models.py       # Pydantic モデル
│   │   └── local_store.py  # JSON ファイル永続化
│   ├── tests/        # unittest (21 件)
│   ├── pyproject.toml
│   └── .venv/        # uv で作成した仮想環境
└── frontend/         # Next.js 16 (TypeScript, Tailwind CSS v4, SWR)
    ├── src/
    │   ├── app/          # App Router ページ
    │   ├── components/   # UI + Todo コンポーネント
    │   ├── hooks/        # SWR カスタムフック
    │   ├── lib/          # API クライアント / ユーティリティ
    │   └── types/        # 型定義
    └── package.json
```

---

## セットアップ

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
| ページ表示 | `/todos` に遷移し「Todoがありません」が表示される |
| Todo 追加 | タイトルを入力して「+ 追加」→ 一覧に表示される |
| 完了チェック | チェックボックスをクリック → タイトルに打ち消し線がつく |
| 編集 | 「編集」ボタン → タイトル/説明を変更して「保存」 |
| 削除 | 「削除」ボタン → 一覧から消える |
| データ永続化 | バックエンド再起動後もデータが残る（`backend/todos.json` に保存） |

---

## テスト実行（バックエンド）

```bash
# リポジトリルートから実行
cd todo-master
PYTHONPATH=. backend/.venv/bin/python -m unittest discover -v backend/tests
```

21 件のテストがすべて `OK` になることを確認してください。

---

## API エンドポイント

| メソッド | パス | 説明 |
|---|---|---|
| `GET` | `/api/todos` | Todo 一覧取得 |
| `POST` | `/api/todos` | Todo 作成 |
| `PUT` | `/api/todos/{id}` | Todo 更新（部分更新可） |
| `DELETE` | `/api/todos/{id}` | Todo 削除 |

詳細は [http://localhost:8000/docs](http://localhost:8000/docs) を参照。
