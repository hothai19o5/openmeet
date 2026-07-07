'use client'

import { createContext, useContext, useState, useCallback, ReactNode } from 'react'
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react'
import { cn } from '@/lib/utils'

type ToastType = 'success' | 'error' | 'info'
type ToastItem = { id: number; type: ToastType; message: string }
type ToastCtx = (message: string, type?: ToastType) => void

const ToastContext = createContext<ToastCtx | null>(null)

const icons: Record<ToastType, React.ReactNode> = {
  success: <CheckCircle2 className="h-4 w-4 text-status-success" />,
  error:   <AlertCircle className="h-4 w-4 text-status-error" />,
  info:    <Info className="h-4 w-4 text-text-secondary" />,
}

const styles: Record<ToastType, string> = {
  success: 'border-l-status-success',
  error:   'border-l-status-error',
  info:    'border-l-brand',
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([])

  const push = useCallback<ToastCtx>((message, type = 'info') => {
    const id = Date.now() + Math.random()
    setToasts((t) => [...t, { id, message, type }])
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 3500)
  }, [])

  return (
    <ToastContext.Provider value={push}>
      {children}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2 max-w-sm">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={cn(
              'flex items-center gap-3 px-4 py-3 rounded bg-surface border border-surface-border border-l-4 shadow-popup animate-slide-up',
              styles[t.type]
            )}
          >
            {icons[t.type]}
            <span className="text-sm text-text-primary flex-1">{t.message}</span>
            <button
              onClick={() => setToasts((x) => x.filter((y) => y.id !== t.id))}
              className="text-text-secondary hover:text-text-primary"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be inside ToastProvider')
  return ctx
}
