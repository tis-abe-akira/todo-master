import useSWR from "swr";
import { api } from "@/lib/api";
import type { Todo } from "@/types/todo";

const fetcher = (path: string) => api.get<Todo[]>(path);

export function useTodos() {
  const { data, error, isLoading, mutate } = useSWR<Todo[]>(
    "/api/todos",
    fetcher,
    { revalidateOnFocus: false },
  );

  return {
    todos: data ?? [],
    isLoading,
    error,
    mutate,
  };
}
