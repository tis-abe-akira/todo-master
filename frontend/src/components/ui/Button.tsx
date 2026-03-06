"use client";

import { cn } from "@/lib/cn";
import { ButtonHTMLAttributes, forwardRef } from "react";

type ButtonVariant = "primary" | "secondary" | "danger";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
};

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = "primary", className, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center gap-2 px-5 h-9 text-sm font-medium rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed",
          variant === "primary" &&
            "bg-[#2D2D2D] text-white hover:bg-[#1a1a1a] focus-visible:ring-[#2D2D2D]",
          variant === "secondary" &&
            "bg-[#F2F3F0] text-[#2D2D2D] hover:bg-[#E8E6E1] border border-[#E8E6E1] focus-visible:ring-[#2D2D2D]",
          variant === "danger" &&
            "bg-[#FDF0F0] text-[#C53D43] hover:bg-[#F0CECE] border border-[#F0CECE] focus-visible:ring-[#C53D43]",
          className,
        )}
        {...props}
      >
        {children}
      </button>
    );
  },
);

Button.displayName = "Button";

export { Button };
