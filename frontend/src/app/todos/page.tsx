import { TodoList } from "@/components/todos/TodoList";
import { AddTodoForm } from "@/components/todos/AddTodoForm";

export default function TodosPage() {
  return (
    <div className="min-h-screen bg-[#F7F6F3]">
      {/* Header */}
      <header className="border-b border-[#E8E6E1] bg-white px-6 py-4 flex items-center gap-3">
        <span className="text-lg font-semibold text-[#2D2D2D]">Todo</span>
        <span
          className="text-xs uppercase tracking-widest text-[#9E9C97]"
          style={{ fontFamily: "var(--font-ibm-plex-mono)" }}
        >
          App
        </span>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-8 flex flex-col gap-8">
        {/* 作成フォーム */}
        <AddTodoForm />
        {/* 一覧 */}
        <TodoList />
      </main>
    </div>
  );
}
