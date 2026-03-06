# Research & Design Decisions — ai-pompous-subtask-decomposer

---
**Purpose**: 調査結果・アーキテクチャ検討・設計判断の根拠を記録する。

---

## Summary

- **Feature**: `ai-pompous-subtask-decomposer`
- **Discovery Scope**: Complex Integration（既存 FastAPI + Next.js への LangChain/Gemini 統合）
- **Key Findings**:
  - `langchain-google-genai` は 2025年時点で安定版 `2.1.x`（PyPI 最新）。`ChatGoogleGenerativeAI` + `with_structured_output()` で Pydantic モデルへの型安全な変換が可能。
  - Gemini API へのアクセスは `GEMINI_API_KEY` 環境変数のみで完結し、`google-generativeai` の直接インポートは不要（`langchain-google-genai` 内部で解決）。
  - 既存 FastAPI アプリは `create_app()` ファクトリパターンを採用しており、新エンドポイントは同ファクトリ内に追加するのが最小変更で整合性が高い。

---

## Research Log

### LangChain Google GenAI パッケージ調査

- **Context**: LangChain + Gemini を FastAPI に統合するための適切なパッケージ・バージョンを特定する必要があった。
- **Sources Consulted**:
  - https://reference.langchain.com/python/integrations/langchain_google_genai/
  - https://python.langchain.com/api_reference/google_genai/
  - https://pypi.org/project/langchain-google-genai/
- **Findings**:
  - `langchain-google-genai 2.1.x` が 2025年3月時点の安定最新版（4.x は SDK 移行版で近日リリース予定）。
  - `ChatGoogleGenerativeAI(model="gemini-1.5-flash")` で呼び出し可能。
  - `llm.with_structured_output(PydanticModel)` で JSON スキーマ強制による型安全な出力が得られる。
  - API キーは `GOOGLE_API_KEY` または `GEMINI_API_KEY`（`google-generativeai` SDK 側の環境変数名と混在注意）→ `ChatGoogleGenerativeAI(google_api_key=os.environ["GEMINI_API_KEY"])` で明示指定が安全。
- **Implications**: `pyproject.toml` への追加は `langchain-google-genai>=2.1.0` と `python-dotenv` の 2 パッケージのみで十分。`google-generativeai` を別途追加する必要はない。

### 既存 FastAPI コードベース分析

- **Context**: 新エンドポイントをどこに追加するかを判断するために既存アーキテクチャを分析。
- **Sources Consulted**: `backend/app/main.py`, `backend/app/models.py`, `backend/app/local_store.py`
- **Findings**:
  - `create_app(store_path)` ファクトリ関数内でルートを定義する一貫したパターン。
  - ビジネスロジック関数（`create_and_persist_todo` 等）はファクトリ外のモジュール関数として定義 → テスタビリティが高い。
  - エラーハンドリングは `@app.exception_handler(IOError)` で横断的に処理。
- **Implications**: `generate_subtasks(todo: Todo, llm: ChatGoogleGenerativeAI) -> list[Subtask]` をモジュール関数として定義し、エンドポイントから呼び出すパターンが既存コードと整合する。

### プロンプト設計（大仰戦略）

- **Context**: 大仰サブタスクを確実に生成させるシステムプロンプトの設計。
- **Findings**:
  - LangChain `ChatPromptTemplate` の `SystemMessage` + `HumanMessage` で役割付与と入力変数置換を組み合わせるのが標準パターン。
  - `with_structured_output()` 使用時は出力形式の指定をプロンプト本文に含める必要はない（モデルが自動で JSON に変換する）ため、システムプロンプトは「大仰指示」に専念できる。
- **Implications**: システムプロンプトに PMBOK / ROI / ステークホルダー分析 / 競合分析 / サプライチェーンリスクなどのキーワードを列挙し、「どんな些細なタスクも国際的・組織的・哲学的次元に昇華せよ」と指示する。

### フロントエンド統合パターン分析

- **Context**: 既存 `useUpdateTodo`, `useDeleteTodo` フックのパターンを踏襲して `useGenerateSubtasks` を設計。
- **Sources Consulted**: `frontend/src/hooks/useUpdateTodo.ts`, `frontend/src/components/todos/TodoCard.tsx`
- **Findings**:
  - すべてのフックは `useState` + `async function` + `ApiError` キャッチ + `finally` でのフラグリセットという統一パターン。
  - `TodoCard` はすでに `isDeleting`/`isSaving` を `disabled` 判定に使用しており、`isGenerating` フラグを追加するパターンは自然。
  - SWR の `mutate` は TODO リスト全体の再取得用であり、サブタスクはローカル state で保持する方が API コストを抑えられる。
- **Implications**: サブタスクデータは SWR キャッシュではなく `TodoCard` の `useState` に保持する。再生成時に上書き更新する。

---

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| A: サービス関数 + エンドポイント追加 | `generate_subtasks()` をモジュール関数として定義し `create_app()` 内のルートから呼び出す | 既存パターンと完全一致、テストが書きやすい | なし | **採用** |
| B: 専用サービスモジュール `subtask_service.py` | 別ファイルに分離 | 関心の分離が明確 | 現状の規模には過剰 | 将来の分割に備え検討余地あり |
| C: LangChain Agent/Tool | ツールチェーン化 | 拡張性が高い | 複雑度が高い・レイテンシ増加 | 現フェーズでは不要 |

---

## Design Decisions

### Decision: `with_structured_output` vs プロンプト内 JSON 指定

- **Context**: Gemini からサブタスクリストを型安全に取得する方法の選択。
- **Alternatives Considered**:
  1. `with_structured_output(SubtaskListOutput)` — Pydantic モデルで型強制
  2. プロンプト内に JSON フォーマット指定 + `StrOutputParser` + `json.loads` — 自由度高いが型安全性低い
- **Selected Approach**: `with_structured_output(SubtaskListOutput)` を採用。
- **Rationale**: 型安全性が高く、パースエラー時に LangChain が例外を送出するため FastAPI 側でのエラーハンドリングが統一できる。
- **Trade-offs**: Gemini 1.5 Flash 以上が必要（1.0 Pro では JSON スキーマ強制非対応）。
- **Follow-up**: `gemini-1.5-flash` のレート制限（無料枠: 15 req/min）を考慮したエラーハンドリングの実装を確認すること。

### Decision: サブタスクデータの保持場所（クライアント state vs サーバー永続化）

- **Context**: 生成されたサブタスクをどこに保存するか。
- **Alternatives Considered**:
  1. クライアント `useState` のみ — シンプル、ページリロードで消える
  2. サーバー側 `todos.json` に `subtasks` フィールドを追加して永続化 — リロード後も保持
- **Selected Approach**: フェーズ 1 はクライアント `useState` のみ。
- **Rationale**: 要件に永続化の記述がない。実装コストを最小化し、大仰サブタスク生成の体験を優先する。永続化は将来の拡張で対応可能。
- **Trade-offs**: ページリロードでサブタスクが消えるが、ボタン一押しで再生成できるため UX 上問題ない。

---

## Risks & Mitigations

- **Gemini API レート制限** — 無料枠は 15 req/min。429 エラー時に 503 として返し、フロントエンドにリトライ案内を表示する。
- **GEMINI_API_KEY 未設定** — 起動時に `ValueError` を送出してログに残す。`GEMINI_API_KEY` が空の場合は `/api/todos/{id}/subtasks` が 503 を返すフォールバックを実装。
- **プロンプトインジェクション** — TODO タイトル・説明は `HumanMessage` の変数として埋め込み、システムプロンプトとは分離。Pydantic バリデーション（max_length=200/1000）が既存で機能しているため追加フィルタは不要。
- **レスポンスタイム** — Gemini API の平均レイテンシ 2〜5 秒。フロントエンドにはローディングスピナーと disabled ボタンで対応済み。

---

## References

- [ChatGoogleGenerativeAI — LangChain Docs](https://reference.langchain.com/python/integrations/langchain_google_genai/ChatGoogleGenerativeAI/) — API シグネチャ・認証方法
- [Structured Output | langchain-google](https://deepwiki.com/langchain-ai/langchain-google/6.1-structured-output) — `with_structured_output` の使用方法
- [langchain-google-genai PyPI](https://pypi.org/project/langchain-google-genai/) — 最新バージョン確認
