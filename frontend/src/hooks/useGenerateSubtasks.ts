import { useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { Subtask, SubtasksResponse } from "@/types/todo";

export function useGenerateSubtasks() {
  const [subtasks, setSubtasks] = useState<Subtask[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function generate(id: string): Promise<Subtask[] | null> {
    setIsGenerating(true);
    setError(null);
    try {
      const result = await api.post<SubtasksResponse>(
        `/api/todos/${id}/subtasks`,
        {},
      );
      setSubtasks(result.subtasks);
      return result.subtasks;
    } catch (err) {
      if (err instanceof ApiError) {
        // バックエンドから返される詳細エラーメッセージを抽出しようと試みる
        try {
          const body = JSON.parse(err.message);
          if (body.detail) {
            setError(`エラー ${err.status}: ${body.detail}`);
          } else {
            setError(`エラー ${err.status}: ${err.message}`);
          }
        } catch {
          setError(`エラー ${err.status}: ${err.message}`);
        }
      } else {
        setError("サブタスクの生成に失敗しました。もう一度お試しください。");
      }
      return null;
    } finally {
      setIsGenerating(false);
    }
  }

  return {
    generate,
    subtasks,
    isGenerating,
    error,
    reset: () => setError(null),
  };
}
