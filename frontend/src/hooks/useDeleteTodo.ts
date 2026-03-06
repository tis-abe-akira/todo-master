import { useState } from "react";
import { mutate } from "swr";
import { api, ApiError } from "@/lib/api";

export function useDeleteTodo() {
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function remove(id: string): Promise<boolean> {
    setIsDeleting(true);
    setError(null);
    try {
      await api.delete(`/api/todos/${id}`);
      await mutate("/api/todos");
      return true;
    } catch (err) {
      setError(
        err instanceof ApiError
          ? `エラー ${err.status}: ${err.message}`
          : "削除に失敗しました。もう一度お試しください。",
      );
      return false;
    } finally {
      setIsDeleting(false);
    }
  }

  return { remove, isDeleting, error, reset: () => setError(null) };
}
