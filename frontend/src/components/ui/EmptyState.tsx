type EmptyStateProps = {
  title?: string;
  description?: string;
};

export function EmptyState({
  title = "タスクがありません",
  description = "上のフォームから最初のタスクを追加しましょう",
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-3 text-center">
      <p className="text-sm font-semibold text-[#2D2D2D]">{title}</p>
      <p className="text-xs text-[#9E9C97]">{description}</p>
    </div>
  );
}
