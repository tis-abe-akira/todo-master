import { cn } from "@/lib/cn";

type SpinnerProps = { className?: string };

export function Spinner({ className }: SpinnerProps) {
  return (
    <div
      className={cn(
        "inline-block w-5 h-5 border-2 border-[#E8E6E1] border-t-[#2D2D2D] rounded-full animate-spin",
        className,
      )}
      role="status"
      aria-label="Loading"
    />
  );
}
