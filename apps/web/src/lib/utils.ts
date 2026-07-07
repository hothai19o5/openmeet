import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function initials(name?: string | null): string {
  if (!name) return '?'
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase() ?? '')
    .join('')
}

export function hashColor(seed: string): string {
  let h = 0
  for (let i = 0; i < seed.length; i++) h = (h << 5) - h + seed.charCodeAt(i)
  const palette = ['#5e6ad2', '#3dd68c', '#f5a623', '#e5484d', '#a48df5', '#4ec5d4', '#f08bd4']
  return palette[Math.abs(h) % palette.length]
}
