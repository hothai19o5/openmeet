'use client'

import { hashColor, initials } from '@/lib/utils'
import { cn } from '@/lib/utils'

type AvatarProps = {
  name?: string | null
  size?: 'xs' | 'sm' | 'md' | 'lg'
  className?: string
  online?: boolean
}

const sizes = {
  xs: 'h-6 w-6 text-[10px]',
  sm: 'h-8 w-8 text-xs',
  md: 'h-10 w-10 text-sm',
  lg: 'h-14 w-14 text-base',
}

export function Avatar({ name, size = 'sm', className, online }: AvatarProps) {
  const color = hashColor(name ?? '?')
  return (
    <div className={cn('relative shrink-0', className)}>
      <div
        className={cn(
          'rounded-full flex items-center justify-center font-semibold text-white',
          sizes[size]
        )}
        style={{ backgroundColor: color }}
      >
        {initials(name)}
      </div>
      {online !== undefined && (
        <span
          className={cn(
            'absolute bottom-0 right-0 h-2.5 w-2.5 rounded-full border-2 border-background',
            online ? 'bg-status-success' : 'bg-room-offline'
          )}
        />
      )}
    </div>
  )
}
