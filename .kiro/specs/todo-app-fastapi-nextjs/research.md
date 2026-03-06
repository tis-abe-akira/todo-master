# Research & Design Decisions for todo-app-fastapi-nextjs

## Summary
- **Feature**: todo-app-fastapi-nextjs
- **Discovery Scope**: Simple Addition
- **Key Findings**:
  - ローカル JSON ファイルはプロトタイプとして十分だが、同時書き込みと破損リスクがある
  - FastAPI + Pydantic は入力バリデーションと高速な開発に適合する
  - Next.js は CSR（クライアントサイドフェッチ）と SWR/React Query による簡易な UX を実現しやすい

## Research Log

### 永続化アプローチ
- **Context**: 要件はローカル JSON での永続化を明示
- **Sources Consulted**: ローカルファイル原子書き込みの一般慣行、OS レベルのファイルロックの注意点（複数プロセス環境）
- **Findings**:
  - 安全な永続化には「一時ファイルへ書き込み → fsync → rename（原子リネーム）」が有効
  - 単一プロセスでの運用なら簡易ロックで十分だが、複数プロセスや複数インスタンスでは競合が発生する
- **Implications**: LocalStore は原子操作と簡易バックアップ（.bak）を組み合わせる。将来クラウド DB へ移行する設計余地を残す

### API 契約とバリデーション
- **Context**: フロントエンドが期待する CRUD API を安定して提供する必要あり
- **Sources Consulted**: FastAPI ドキュメント、Pydantic のバリデーションパターン
- **Findings**:
  - Pydantic によるスキーマ定義はエラー応答を一貫して提供できる
  - エンドポイントは単純かつ RESTful に設計する（GET/POST/PUT/DELETE）
- **Implications**: API は明確なステータスコードとエラーペイロードを返すよう仕様化する

### フロントエンドのデータ取得パターン
- **Context**: ユーザー体験（ローディング、失敗時フィードバック）を担保する
- **Sources Consulted**: Next.js と SWR / React Query の一般的なパターン
- **Findings**:
  - CSR とクライアント側キャッシュ（SWR 等）で UX を単純化できる
  - 操作に対しては楽観的更新は初期段階では導入せず、確実な API 応答で更新反映する方針が安全
- **Implications**: NextApp は GET/POST/PUT/DELETE を呼び、ローディングとエラーフィードバックを表示する

## Architecture Pattern Evaluation
| Option | Description | Strengths | Risks / Limitations |
|--------|-------------|-----------|---------------------|
| Local JSON + API | API 層でファイル永続化を行う | 実装が簡単、低コスト | 同時書き込み、スケール困難 |

## Design Decisions

### Decision: 永続化方式はローカル JSON を採用
- **Context**: 要求はローカル永続化でプロトタイプを作ること
- **Alternatives Considered**:
  1. ローカル JSON（選択）
  2. SQLite（将来的検討）
  3. リモート DB（スコープ外）
- **Selected Approach**: ローカル JSON + 原子書き込み + バックアップ
- **Rationale**: 実装が最小で済み、早期のフィードバックを得やすい
- **Trade-offs**: スケーラビリティを犠牲にする。将来 SQLite/クラウド DB への移行が想定される

### Decision: API バリデーションは Pydantic を利用
- **Context**: 型安全と一貫したエラー処理が必要
- **Rationale**: FastAPI と自然に統合できるため実装コストが低い

## Risks & Mitigations
- リスク: 同時書き込みでデータ競合 → Mitigation: ファイルロック + 原子書き込み + テストカバレッジ
- リスク: ファイル破損 → Mitigation: 操作前にバックアップを作成、リカバリ手順を設ける
- リスク: UX の多重送信 → Mitigation: フロントで操作中はボタンを非活性化しローディング表示

## References
- FastAPI ドキュメント — Pydantic を使ったバリデーション
- 原子書き込みパターンに関する一般記事
