'use client'

import { cloneElement, isValidElement, ButtonHTMLAttributes, ReactNode } from 'react'
import { cn } from '@/lib/utils'

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger'
type Size = 'sm' | 'md' | 'lg'

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant
  size?: Size
  icon?: ReactNode
  loading?: boolean
}

const variantStyle: Record<Variant, string> = {
  primary:   'bg-brand text-white hover:bg-brand-hover active:bg-brand-active',
  secondary: 'bg-surface text-text-primary border border-surface-border hover:bg-surface-hover',
  ghost:     'bg-transparent text-text-secondary hover:bg-surface hover:text-text-primary',
  danger:    'bg-status-error/15 text-status-error hover:bg-status-error/25',
}
const sizeStyle: Record<Size, string> = {
  sm: 'px-3 py-1.5 text-xs',
  md: 'px-4 py-2 text-sm',
  lg: 'px-5 py-2.5 text-base',
}

export function Button({
  variant = 'primary',
  size = 'md',
  icon,
  loading,
  children,
  className,
  disabled,
  ...rest
}: ButtonProps) {
  return (
    <button
      {...rest}
      disabled={disabled || loading}
      className={cn(
        'inline-flex items-center gap-2 rounded font-medium transition-all duration-100 select-none',
        'disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer',
        variantStyle[variant],
        sizeStyle[size],
        className
      )}
    >
      {loading ? (
        <span className="h-3 w-3 rounded-full border-2 border-white/30 border-t-white animate-spin" />
      ) : icon && isValidElement(icon) ? (
        cloneElement(icon as any, { className: 'h-4 w-4' })
      ) : null}
      {children}
    </button>
  )
}
