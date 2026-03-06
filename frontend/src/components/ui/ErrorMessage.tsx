import { cn } from "@/lib/cn";

type ErrorMessageProps = { message?: string; className?: string };

export function ErrorMessage({ message, className }: ErrorMessageProps) {
  return (
    <div
      className={cn(
        "flex items-center gap-2 p-4 bg-[#FDF0F0] border border-[#F0CECE] rounded-sm text-sm text-[#C53D43]",
        className,
      )}
    >
      <span>{message ?? "予期しないエラーが発生しました。"}</span>
    </div>
  );
}
