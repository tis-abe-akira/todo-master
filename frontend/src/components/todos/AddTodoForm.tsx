"use client";

import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/Button";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { useCreateTodo } from "@/hooks/useCreateTodo";

export function AddTodoForm() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const { create, isSubmitting, error } = useCreateTodo();

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!title.trim()) return;
    const result = await create({
      title: title.trim(),
      description: description.trim() || undefined,
    });
    if (result) {
      setTitle("");
      setDescription("");
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
      <div className="flex flex-col gap-1.5">
        <label
          htmlFor="todo-title"
          className="text-[11px] uppercase tracking-widest text-[#2D2D2D]"
          style={{ fontFamily: "var(--font-ibm-plex-mono)" }}
        >
          タイトル *
        </label>
        <input
          id="todo-title"
          type="text"
          value={title}
          onChange={(e: import("react").ChangeEvent<HTMLInputElement>) =>
            setTitle(e.target.value)
          }
          required
          placeholder="何をしますか？"
          className="h-10 px-4 text-sm rounded-full bg-[#F2F3F0] border border-transparent focus:border-[#2D2D2D] focus:outline-none placeholder:text-[#B0ADA8]"
        />
      </div>

      <div className="flex flex-col gap-1.5">
        <label
          htmlFor="todo-description"
          className="text-[11px] uppercase tracking-widest text-[#2D2D2D]"
          style={{ fontFamily: "var(--font-ibm-plex-mono)" }}
        >
          説明（任意）
        </label>
        <input
          id="todo-description"
          type="text"
          value={description}
          onChange={(e: import("react").ChangeEvent<HTMLInputElement>) =>
            setDescription(e.target.value)
          }
          placeholder="詳細メモ"
          className="h-10 px-4 text-sm rounded-full bg-[#F2F3F0] border border-transparent focus:border-[#2D2D2D] focus:outline-none placeholder:text-[#B0ADA8]"
        />
      </div>

      {error && <ErrorMessage message={error} />}

      <Button
        type="submit"
        variant="primary"
        disabled={isSubmitting || !title.trim()}
        className="self-end"
      >
        {isSubmitting ? "追加中…" : "+ 追加"}
      </Button>
    </form>
  );
}
