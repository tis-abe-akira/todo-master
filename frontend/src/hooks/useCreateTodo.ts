import { useState } from "react";
import { mutate } from "swr";
import { api, ApiError } from "@/lib/api";
import type { CreateTodoRequest, Todo } from "@/types/todo";

export function useCreateTodo() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function create(req: CreateTodoRequest): Promise<Todo | null> {
    setIsSubmitting(true);
    setError(null);
    try {
      const result = await api.post<Todo>("/api/todos", req);
      await mutate("/api/todos");
      return result;
    } catch (err) {
      setError(
        err instanceof ApiError
          ? `エラー ${err.status}: ${err.message}`
          : "作成に失敗しました。もう一度お試しください。",
      );
      return null;
    } finally {
      setIsSubmitting(false);
    }
  }

  return { create, isSubmitting, error, reset: () => setError(null) };
}
