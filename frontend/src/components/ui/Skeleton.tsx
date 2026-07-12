import React from "react";

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "text" | "rectangular" | "circular";
  width?: string | number;
  height?: string | number;
}

export function Skeleton({
  variant = "rectangular",
  width,
  height,
  className = "",
  style,
  ...props
}: SkeletonProps) {
  const baseStyles = "animate-pulse-skeleton bg-border/40 dark:bg-border/20";
  
  const variants = {
    text: "h-3.5 w-full rounded-md",
    rectangular: "rounded-lg",
    circular: "rounded-full",
  };

  const customStyle: React.CSSProperties = {
    width: width !== undefined ? width : undefined,
    height: height !== undefined ? height : undefined,
    ...style,
  };

  return (
    <div
      className={`${baseStyles} ${variants[variant]} ${className}`}
      style={customStyle}
      {...props}
    />
  );
}

export function SkeletonList({ count = 3 }: { count?: number }) {
  return (
    <div className="flex flex-col gap-3.5 w-full">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="flex items-center gap-3.5 p-3.5 border border-border/60 rounded-xl bg-surface/30">
          <Skeleton variant="circular" width={40} height={40} className="flex-shrink-0" />
          <div className="flex-1 flex flex-col gap-2">
            <Skeleton variant="text" width="60%" height={16} />
            <Skeleton variant="text" width="35%" height={12} />
          </div>
        </div>
      ))}
    </div>
  );
}
