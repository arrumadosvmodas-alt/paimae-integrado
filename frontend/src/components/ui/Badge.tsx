import React from "react";

type BadgeVariant = "primary" | "secondary" | "tertiary" | "error" | "neutral";

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
}

export function Badge({ children, variant = "neutral", className = "", ...props }: BadgeProps) {
  const baseStyles = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold select-none border";

  const variants = {
    primary: "bg-primary/10 border-primary/20 text-primary dark:text-blue-400",
    secondary: "bg-secondary/10 border-secondary/20 text-secondary dark:text-emerald-400",
    tertiary: "bg-tertiary/10 border-tertiary/20 text-tertiary dark:text-amber-400",
    error: "bg-error/10 border-error/20 text-error dark:text-red-400",
    neutral: "bg-border/20 border-border/40 text-text-muted",
  };

  return (
    <span className={`${baseStyles} ${variants[variant]} ${className}`} {...props}>
      {children}
    </span>
  );
}
