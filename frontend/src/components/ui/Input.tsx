import React, { forwardRef } from "react";

// Input de texto genérico
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, className = "", id, ...props }, ref) => {
    const inputId = id || React.useId();
    return (
      <div className="w-full flex flex-col gap-1.5">
        {label && (
          <label
            htmlFor={inputId}
            className="text-xs font-bold font-display uppercase tracking-wider text-text-muted"
          >
            {label}
          </label>
        )}
        <input
          id={inputId}
          ref={ref}
          className={`w-full min-h-[42px] px-3.5 py-2 rounded-lg bg-surface border text-sm text-text-primary placeholder:text-text-muted/60 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary disabled:bg-background disabled:text-text-muted/70 disabled:cursor-not-allowed ${
            error ? "border-error focus:ring-error/20 focus:border-error" : "border-border"
          } ${className}`}
          {...props}
        />
        {error && <span className="text-xs font-semibold text-error mt-0.5">{error}</span>}
        {!error && helperText && <span className="text-xs text-text-muted mt-0.5">{helperText}</span>}
      </div>
    );
  }
);

Input.displayName = "Input";

// Select estilizado
interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  helperText?: string;
  placeholder?: string;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, helperText, placeholder, children, className = "", id, ...props }, ref) => {
    const selectId = id || React.useId();
    return (
      <div className="w-full flex flex-col gap-1.5">
        {label && (
          <label
            htmlFor={selectId}
            className="text-xs font-bold font-display uppercase tracking-wider text-text-muted"
          >
            {label}
          </label>
        )}
        <select
          id={selectId}
          ref={ref}
          className={`w-full min-h-[42px] px-3.5 py-2 rounded-lg bg-surface border text-sm text-text-primary transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary disabled:bg-background disabled:text-text-muted/70 disabled:cursor-not-allowed ${
            error ? "border-error focus:ring-error/20 focus:border-error" : "border-border"
          } ${className}`}
          {...props}
        >
          {placeholder && <option value="">{placeholder}</option>}
          {children}
        </select>
        {error && <span className="text-xs font-semibold text-error mt-0.5">{error}</span>}
        {!error && helperText && <span className="text-xs text-text-muted mt-0.5">{helperText}</span>}
      </div>
    );
  }
);

Select.displayName = "Select";

// Textarea estilizado
interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ label, error, helperText, className = "", id, ...props }, ref) => {
    const textareaId = id || React.useId();
    return (
      <div className="w-full flex flex-col gap-1.5">
        {label && (
          <label
            htmlFor={textareaId}
            className="text-xs font-bold font-display uppercase tracking-wider text-text-muted"
          >
            {label}
          </label>
        )}
        <textarea
          id={textareaId}
          ref={ref}
          className={`w-full min-h-[80px] px-3.5 py-2.5 rounded-lg bg-surface border text-sm text-text-primary placeholder:text-text-muted/60 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary disabled:bg-background disabled:text-text-muted/70 disabled:cursor-not-allowed resize-y ${
            error ? "border-error focus:ring-error/20 focus:border-error" : "border-border"
          } ${className}`}
          {...props}
        />
        {error && <span className="text-xs font-semibold text-error mt-0.5">{error}</span>}
        {!error && helperText && <span className="text-xs text-text-muted mt-0.5">{helperText}</span>}
      </div>
    );
  }
);

Textarea.displayName = "Textarea";

// Checkbox customizado
interface CheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "type"> {
  label: string;
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ label, className = "", id, ...props }, ref) => {
    const checkboxId = id || React.useId();
    return (
      <label
        htmlFor={checkboxId}
        className="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-background border border-border cursor-pointer hover:bg-surface-hover transition-colors duration-150 select-none text-sm text-text-primary"
      >
        <input
          id={checkboxId}
          type="checkbox"
          ref={ref}
          className={`w-4 h-4 text-primary bg-surface border-border rounded focus:ring-primary focus:ring-2 focus:ring-offset-2 ${className}`}
          {...props}
        />
        <span>{label}</span>
      </label>
    );
  }
);

Checkbox.displayName = "Checkbox";
