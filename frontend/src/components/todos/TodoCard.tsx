"use client";

import { useState, type ChangeEvent } from "react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { Spinner } from "@/components/ui/Spinner";
import { useUpdateTodo } from "@/hooks/useUpdateTodo";
import { useDeleteTodo } from "@/hooks/useDeleteTodo";
import { useGenerateSubtasks } from "@/hooks/useGenerateSubtasks";
import { SubtaskList } from "./SubtaskList";
import type { Todo } from "@/types/todo";

type TodoCardProps = { todo: Todo };

export function TodoCard({ todo }: TodoCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(todo.title);
  const [editDesc, setEditDesc] = useState(todo.description ?? "");

  const {
    update,
    isSubmitting: isSaving,
    error: updateError,
    reset: resetUpdate,
  } = useUpdateTodo();
  const { remove, isDeleting, error: deleteError } = useDeleteTodo();
  const {
    generate,
    subtasks,
    isGenerating,
    error: generateError,
  } = useGenerateSubtasks();

  async function handleToggleCompleted() {
    await update(todo.id, { completed: !todo.completed });
  }

  async function handleSave() {
    if (!editTitle.trim()) return;
    const result = await update(todo.id, {
      title: editTitle.trim(),
      description: editDesc.trim() || undefined,
    });
    if (result) setIsEditing(false);
  }

  function handleCancelEdit() {
    setEditTitle(todo.title);
    setEditDesc(todo.description ?? "");
    resetUpdate();
    setIsEditing(false);
  }

  function handleTitleChange(e: import("react").ChangeEvent<HTMLInputElement>) {
    setEditTitle(e.target.value);
  }

  function handleDescChange(e: import("react").ChangeEvent<HTMLInputElement>) {
    setEditDesc(e.target.value);
  }

  return (
    <Card className="p-4 flex flex-col gap-3">
      {/* ヘッダー行：チェックボックス＋タイトル＋操作ボタン */}
      <div className="flex items-start gap-3">
        {/* 完了チェックボックス（多重送信ガード） */}
        <input
          type="checkbox"
          checked={todo.completed}
          disabled={isSaving || isDeleting || isGenerating}
          onChange={handleToggleCompleted}
          className="mt-0.5 w-4 h-4 accent-[#2D2D2D] cursor-pointer disabled:cursor-not-allowed"
          aria-label={todo.completed ? "未完了に戻す" : "完了にする"}
        />

        {isEditing ? (
          /* 編集モード */
          <div className="flex-1 flex flex-col gap-2">
            <input
              autoFocus
              value={editTitle}
              onChange={handleTitleChange}
              className="w-full h-9 px-3 text-sm rounded-full bg-[#F2F3F0] border border-transparent focus:border-[#2D2D2D] focus:outline-none"
              placeholder="タイトル"
            />
            <input
              value={editDesc}
              onChange={handleDescChange}
              className="w-full h-9 px-3 text-sm rounded-full bg-[#F2F3F0] border border-transparent focus:border-[#2D2D2D] focus:outline-none"
              placeholder="説明（任意）"
            />
            <div className="flex gap-2">
              <Button
                variant="primary"
                onClick={handleSave}
                disabled={isSaving || !editTitle.trim()}
              >
                {isSaving ? "保存中…" : "保存"}
              </Button>
              <Button
                variant="secondary"
                onClick={handleCancelEdit}
                disabled={isSaving}
              >
                キャンセル
              </Button>
            </div>
          </div>
        ) : (
          /* 表示モード */
          <div className="flex-1 min-w-0">
            <p
              className={`text-sm font-medium text-[#2D2D2D] ${
                todo.completed ? "line-through text-[#9E9C97]" : ""
              }`}
            >
              {todo.title}
            </p>
            {todo.description && (
              <p className="text-xs text-[#9E9C97] mt-0.5">
                {todo.description}
              </p>
            )}
            <p
              className="text-[10px] uppercase tracking-wide text-[#B0ADA8] mt-1"
              style={{ fontFamily: "var(--font-ibm-plex-mono)" }}
            >
              {new Date(todo.created_at).toLocaleDateString("ja-JP")}
            </p>
          </div>
        )}

        {/* 編集・削除・サブタスク分解ボタン（表示モード時のみ） */}
        {!isEditing && (
          <div className="flex items-center gap-1 shrink-0 flex-wrap justify-end">
            <Button
              variant="secondary"
              onClick={() => generate(todo.id)}
              disabled={isDeleting || isSaving || isGenerating}
              className="px-3 h-8 text-xs flex items-center gap-1"
            >
              {isGenerating ? <Spinner /> : "🤖"} サブタスク分解
            </Button>
            <Button
              variant="secondary"
              onClick={() => setIsEditing(true)}
              disabled={isDeleting || isSaving || isGenerating}
              className="px-3 h-8 text-xs"
            >
              編集
            </Button>
            <Button
              variant="danger"
              onClick={() => remove(todo.id)}
              disabled={isDeleting || isSaving || isGenerating}
              className="px-3 h-8 text-xs"
            >
              {isDeleting ? "削除中…" : "削除"}
            </Button>
          </div>
        )}
      </div>

      {/* エラー表示 */}
      {(updateError || deleteError || generateError) && (
        <ErrorMessage
          message={updateError ?? deleteError ?? generateError ?? undefined}
        />
      )}

      {/* サブタスクリスト */}
      {subtasks.length > 0 && <SubtaskList subtasks={subtasks} />}
    </Card>
  );
}
