import React from "react";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  subtitle?: string;
  icon?: React.ReactNode;
  headerActions?: React.ReactNode;
  footerActions?: React.ReactNode;
}

export function Card({
  children,
  title,
  subtitle,
  icon,
  headerActions,
  footerActions,
  className = "",
  ...props
}: CardProps) {
  return (
    <div
      className={`bg-surface border border-border rounded-2xl shadow-sm overflow-hidden flex flex-col transition-all duration-200 ${className}`}
      {...props}
    >
      {/* Header do Card */}
      {(title || icon || headerActions) && (
        <div className="px-6 py-5 border-b border-border flex items-center justify-between gap-4">
          <div className="flex items-center gap-2.5 min-w-0">
            {icon && <span className="text-text-muted flex-shrink-0">{icon}</span>}
            <div className="min-w-0">
              {title && (
                <h3 className="text-base md:text-lg font-bold font-display text-text-primary truncate">
                  {title}
                </h3>
              )}
              {subtitle && (
                <p className="text-xs text-text-muted truncate mt-0.5">{subtitle}</p>
              )}
            </div>
          </div>
          {headerActions && <div className="flex items-center gap-2 flex-shrink-0">{headerActions}</div>}
        </div>
      )}

      {/* Conteúdo do Card */}
      <div className="p-6 flex-1 flex flex-col">{children}</div>

      {/* Footer do Card */}
      {footerActions && (
        <div className="px-6 py-4 bg-background/50 border-t border-border flex items-center justify-end gap-3">
          {footerActions}
        </div>
      )}
    </div>
  );
}
