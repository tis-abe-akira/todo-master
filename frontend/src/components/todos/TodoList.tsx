"use client";

import { Spinner } from "@/components/ui/Spinner";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { EmptyState } from "@/components/ui/EmptyState";
import { TodoCard } from "@/components/todos/TodoCard";
import { useTodos } from "@/hooks/useTodos";

export function TodoList() {
  const { todos, isLoading, error } = useTodos();

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner />
      </div>
    );
  }

  if (error) {
    return <ErrorMessage message="Todoの取得に失敗しました。" />;
  }

  if (!todos || todos.length === 0) {
    return <EmptyState />;
  }

  return (
    <ul className="flex flex-col gap-3">
      {todos.map((todo) => (
        <li key={todo.id}>
          <TodoCard todo={todo} />
        </li>
      ))}
    </ul>
  );
}
