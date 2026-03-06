"""
AI サブタスク生成サービス

LangChain + Gemini API を使用して TODO を大仰なサブタスクに分解する。
"""

from __future__ import annotations

import logging
from typing import Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# データモデル
# ---------------------------------------------------------------------------


class Subtask(BaseModel):
    """サブタスク単体のデータモデル"""

    title: str = Field(..., description="大仰なサブタスクタイトル")


class SubtaskListOutput(BaseModel):
    """Gemini 構造化出力の型 — 5〜6 件のサブタスクリスト"""

    subtasks: list[Subtask] = Field(
        ...,
        min_length=5,
        max_length=6,
        description="5〜6件のサブタスクリスト",
    )


class SubtasksResponse(BaseModel):
    """API レスポンス用モデル"""

    subtasks: list[Subtask]


# ---------------------------------------------------------------------------
# 例外クラス
# ---------------------------------------------------------------------------


class GeminiServiceError(Exception):
    """Gemini API 呼び出し失敗・タイムアウト時に送出される例外"""


class GeminiConfigError(Exception):
    """GEMINI_API_KEY 未設定などの設定不備時に送出される例外"""


# ---------------------------------------------------------------------------
# プロンプトテンプレート
# ---------------------------------------------------------------------------

POMPOUS_SYSTEM_PROMPT = """あなたは世界最高峰のビジネスコンサルタントです。
マッキンゼー・BCG・ベイン出身の超エリートとして、いかなる些細なタスクも、
PMBOK・ROI・ステークホルダー分析・競合分析・サプライチェーンリスク管理・
変革管理フレームワーク・バランスト・スコアカード・ブルーオーシャン戦略などを
駆使して、国際的・組織的・哲学的な重大課題として昇華させてください。

ユーザーから TODO のタイトルと説明を受け取り、5〜6 個の大仰なサブタスクを生成してください。
各サブタスクは以下の条件を満たすこと：
- 「〇〇の策定」「〇〇の構築」「〇〇の確立」「〇〇の分析」「〇〇の最適化」などの壮大な動名詞表現で始めること
- PMBOK・ROI・KPI・ステークホルダー・バリューチェーン・シナジー・コアコンピタンス等の
  コンサルティング用語を必ず含めること
- 些細な日常タスクも、グローバルな経営課題・組織変革・イノベーション戦略として位置づけること
- 日本語で記述すること
"""

_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        ("system", POMPOUS_SYSTEM_PROMPT),
        (
            "human",
            "TODO タイトル: {title}\nTODO 説明: {description}\n\nサブタスクを生成してください。",
        ),
    ]
)


# ---------------------------------------------------------------------------
# サービス関数
# ---------------------------------------------------------------------------


def generate_subtasks(
    title: str,
    description: Optional[str],
    api_key: str,
    model: str = "gemini-3.1-flash-lite-preview",
    timeout: int = 30,
) -> list[Subtask]:
    """
    Gemini API を呼び出して大仰なサブタスクリストを返す。

    Preconditions: api_key が非空文字列
    Postconditions: len(result) が 5 以上 6 以下
    Raises: GeminiConfigError — API キー未設定・空文字時
            GeminiServiceError — API 呼び出し失敗・タイムアウト時
    """
    # API キーバリデーション
    if not api_key or not api_key.strip():
        raise GeminiConfigError(
            "GEMINI_API_KEY が設定されていません。環境変数 GEMINI_API_KEY を設定してください。"
        )

    logger.info("generate_subtasks: 開始 title=%r model=%s", title, model)

    try:
        llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            timeout=timeout,
        )
        chain = llm.with_structured_output(SubtaskListOutput)

        result: SubtaskListOutput = chain.invoke(
            _PROMPT_TEMPLATE.format_messages(
                title=title,
                description=description or "（説明なし）",
            )
        )
    except Exception as e:
        logger.error(
            "generate_subtasks: Gemini API 呼び出し失敗 title=%r error=%s", title, e
        )
        raise GeminiServiceError(f"Gemini API 呼び出しに失敗しました: {e}") from e

    logger.info(
        "generate_subtasks: 完了 title=%r subtasks_count=%d",
        title,
        len(result.subtasks),
    )
    return result.subtasks
