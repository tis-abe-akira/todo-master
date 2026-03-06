# Requirements Document

## はじめに

本ドキュメントは「AI 大仰サブタスク分解機能（ai-pompous-subtask-decomposer）」の要件を定義する。  
ユーザーが入力した TODO を LangChain + Gemini API で分析し、**過度に仰々しい一般論・原理原則・コンサル的フレームワーク**を駆使して 5〜6 個の大仰なサブタスクへ分解する機能を追加する。  
既存の Todo アプリ（FastAPI バックエンド + Next.js フロントエンド）に統合する。

## Requirements

### Requirement 1: AI サブタスク分解エンドポイント

**Objective:** 開発者として、TODO のタイトル・説明を送信すると AI が 5〜6 個のサブタスクを返してほしい。そうすることで、フロントエンドからワンクリックでサブタスクを取得できる。

#### Acceptance Criteria

1. When ユーザーが特定の Todo ID に対してサブタスク生成リクエストを送信したとき、the Subtask Decomposition API shall LangChain + Gemini API を呼び出してサブタスクリストを返す
2. The Subtask Decomposition API shall 1 件の TODO につき 5〜6 件のサブタスクを含む JSON レスポンスを返す
3. When Gemini API の呼び出しに成功したとき、the Subtask Decomposition API shall HTTP 200 とサブタスク配列を返す
4. If Gemini API の呼び出しが失敗した場合、the Subtask Decomposition API shall HTTP 503 とエラーメッセージを返す
5. The Subtask Decomposition API shall 各サブタスクに `title`（文字列）フィールドを持つオブジェクトを含める
6. The Subtask Decomposition API shall サブタスク生成リクエストを INFO レベルでログ出力する

---

### Requirement 2: 大仰プロンプト戦略

**Objective:** ユーザーとして、日常的な TODO に対して仰々しいコンサルティング用語・PMBOKフレームワーク・費用対効果分析などを含むサブタスクを受け取りたい。そうすることで、どんな些細なタスクも壮大なプロジェクトとして楽しめる。

#### Acceptance Criteria

1. The Subtask Decomposition API shall System プロンプトに「あらゆるタスクを PMBOK・ROI・競合分析・ステークホルダー分析などのフレームワークで大仰に表現すること」という指示を必ず含める
2. When TODO のタイトルが日常的な内容（例：「牛乳を買う」）のとき、the Subtask Decomposition API shall 栄養学的考察・サプライチェーンリスク評価・アレルギーインパクト分析などの大仰なサブタスクを生成する
3. When TODO がプロジェクト関連の内容のとき、the Subtask Decomposition API shall PMBOK 準拠のプロジェクトチャーター策定・WBS 構築・リスク登録簿作成などのサブタスクを生成する
4. The Subtask Decomposition API shall 生成するすべてのサブタスクタイトルにコンサルティング・ビジネス用語を含める
5. The Subtask Decomposition API shall 各サブタスクが実行困難に見えるほど壮大な表現になるよう Gemini へ指示するプロンプトを送信する

---

### Requirement 3: フロントエンド「サブタスク分解ボタン」UI

**Objective:** ユーザーとして、各 TodoCard に「サブタスク分解」ボタンを表示し、押すとサブタスクが TodoCard の下部に展開表示されてほしい。そうすることで、ワンクリックで大仰なサブタスクを確認できる。

#### Acceptance Criteria

1. The Todo App UI shall 各 TodoCard に「🤖 サブタスク分解」ボタンを表示する
2. When ユーザーが「🤖 サブタスク分解」ボタンをクリックしたとき、the Todo App UI shall バックエンドのサブタスク生成 API を呼び出し、ローディングスピナーを表示する
3. When サブタスク生成 API が正常にレスポンスを返したとき、the Todo App UI shall サブタスクリストを TodoCard の下部に展開表示する
4. While サブタスク生成 API を呼び出し中のとき、the Todo App UI shall ボタンを disabled 状態にし、多重クリックを防止する
5. If サブタスク生成 API がエラーを返した場合、the Todo App UI shall エラーメッセージを TodoCard 内に表示する
6. The Todo App UI shall サブタスクは番号付きリスト形式で、各タイトルを読みやすく表示する

---

### Requirement 4: サブタスク表示コンポーネント

**Objective:** フロントエンド開発者として、再利用可能なサブタスク表示コンポーネントが必要である。そうすることで、TodoCard への統合が容易になる。

#### Acceptance Criteria

1. The Todo App UI shall サブタスクリストを表示する専用コンポーネント（`SubtaskList`）を提供する
2. The Todo App UI shall 各サブタスク項目を `SubtaskItem` コンポーネントとして個別にレンダリングする
3. When サブタスクが 0 件のとき、the Todo App UI shall サブタスクリストを表示しない
4. The Todo App UI shall サブタスクが既に生成済みの場合、ボタン再押下で再生成（上書き）できる
5. The Todo App UI shall サブタスク表示エリアはアニメーション付きで展開・収縮する

---

### Requirement 5: 環境設定・セキュリティ

**Objective:** 運用者として、Gemini API キーを安全に管理し、API コストを制御したい。そうすることで、セキュリティリスクとコストを適切にコントロールできる。

#### Acceptance Criteria

1. The Subtask Decomposition API shall Gemini API キーを環境変数 `GEMINI_API_KEY` から取得し、ソースコードにハードコードしない
2. If `GEMINI_API_KEY` が設定されていない場合、the Subtask Decomposition API shall アプリケーション起動時に明確なエラーメッセージをログ出力する
3. The Subtask Decomposition API shall 1 リクエストあたりの Gemini API 呼び出しを 1 回に制限する
4. The Subtask Decomposition API shall タイムアウト（30 秒）を設定し、Gemini API が応答しない場合に 503 を返す
5. Where `GEMINI_API_KEY` が設定されている場合、the Subtask Decomposition API shall 使用モデル名（例：`gemini-1.5-flash`）をログに出力する

---

### Requirement 6: 依存ライブラリ追加

**Objective:** バックエンド開発者として、LangChain と Gemini 連携に必要なパッケージを pyproject.toml に追加したい。そうすることで、環境を統一できる。

#### Acceptance Criteria

1. The Todo App Backend shall `langchain`、`langchain-google-genai`、`google-generativeai` を依存関係に追加する
2. The Todo App Backend shall `python-dotenv` を依存関係に追加し、`.env` ファイルによる環境変数管理を可能にする
3. When 新たな依存関係を追加した場合、the Todo App Backend shall 既存の 51 件のテストがすべてパスし続けることを保証する

