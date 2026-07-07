'use client'

import { signIn } from 'next-auth/react'
import { useState, FormEvent } from 'react'
import { Video, Eye, EyeOff, LogIn, Shield } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useToast } from '@/components/ui/toast'

export default function LoginPage() {
  const toast = useToast()
  const [show, setShow] = useState(false)
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({ username: '', password: '' })

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await signIn('credentials', {
        username: form.username,
        password: form.password,
        redirect: false,
      })
      if (res?.error) {
        toast('Invalid credentials. Please try again.', 'error')
      } else {
        window.location.href = '/dashboard'
      }
    } catch {
      toast('Connection error. Please try again.', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      {/* Background glow */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 left-1/2 -translate-x-1/2 h-96 w-96 rounded-full bg-brand/10 blur-3xl" />
      </div>

      <div className="relative w-full max-w-sm">
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-brand mb-4 shadow-glow">
            <Video className="h-6 w-6 text-white" />
          </div>
          <h1 className="text-xl font-bold text-text-primary">Sign in to OpenMeet</h1>
          <p className="text-sm text-text-secondary mt-1">Secure, self-hosted video conferencing</p>
        </div>

        {/* Card */}
        <div className="card p-6 shadow-popup">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-text-secondary mb-1.5">
                Username
              </label>
              <input
                className="input"
                type="text"
                autoComplete="username"
                placeholder="Enter your username"
                value={form.username}
                onChange={(e) => setForm({ ...form, username: e.target.value })}
                required
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-text-secondary mb-1.5">
                Password
              </label>
              <div className="relative">
                <input
                  className="input pr-10"
                  type={show ? 'text' : 'password'}
                  autoComplete="current-password"
                  placeholder="Enter your password"
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShow((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-text-tertiary hover:text-text-secondary"
                >
                  {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="md"
              className="w-full justify-center mt-2"
              loading={loading}
              icon={<LogIn />}
            >
              Sign in
            </Button>
          </form>

          {/* SSO divider */}
          <div className="flex items-center gap-3 my-5">
            <div className="divider flex-1" />
            <span className="text-xs text-text-tertiary">or</span>
            <div className="divider flex-1" />
          </div>

          <Button
            variant="secondary"
            size="md"
            className="w-full justify-center"
            onClick={() => signIn('keycloak', { callbackUrl: '/dashboard' })}
            icon={<Shield />}
          >
            Sign in with SSO (Keycloak)
          </Button>
        </div>

        <p className="text-center text-xs text-text-tertiary mt-6">
          Your credentials are verified on-premises. Nothing leaves your network.
        </p>
      </div>
    </div>
  )
}
