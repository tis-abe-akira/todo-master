import { useState } from "react";
import { mutate } from "swr";
import { api, ApiError } from "@/lib/api";
import type { UpdateTodoRequest, Todo } from "@/types/todo";

export function useUpdateTodo() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function update(
    id: string,
    req: UpdateTodoRequest,
  ): Promise<Todo | null> {
    setIsSubmitting(true);
    setError(null);
    try {
      const result = await api.put<Todo>(`/api/todos/${id}`, req);
      await mutate("/api/todos");
      return result;
    } catch (err) {
      setError(
        err instanceof ApiError
          ? `エラー ${err.status}: ${err.message}`
          : "更新に失敗しました。もう一度お試しください。",
      );
      return null;
    } finally {
      setIsSubmitting(false);
    }
  }

  return { update, isSubmitting, error, reset: () => setError(null) };
}
