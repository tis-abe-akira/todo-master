import { cn } from "@/lib/cn";
import { HTMLAttributes } from "react";

type CardProps = HTMLAttributes<HTMLDivElement>;

export function Card({ className, children, ...props }: CardProps) {
  return (
    <div
      className={cn("bg-white border border-[#E8E6E1] rounded-sm", className)}
      {...props}
    >
      {children}
    </div>
  );
}
