import Link from 'next/link'
import { Video, Shield, Cpu, Lock, ArrowRight, Github } from 'lucide-react'

const features = [
  {
    icon: Video,
    title: 'Crystal-clear video',
    desc: 'WebRTC SFU with simulcast, adaptive bitrate, and up to 100 participants per room.',
  },
  {
    icon: Lock,
    title: 'End-to-end encrypted',
    desc: 'Optional E2EE via Insertable Streams — even the server sees only opaque bytes.',
  },
  {
    icon: Cpu,
    title: 'On-prem AI Assistant',
    desc: 'Real-time transcription + meeting summaries powered by Whisper + Llama 3 — no cloud APIs.',
  },
  {
    icon: Shield,
    title: 'Built for high-security orgs',
    desc: 'Air-gapped deployment, LDAP/AD integration, audit logs, MFA, classified-tier rooms.',
  },
]

const stats = [
  { label: 'Concurrent users / room', value: '100' },
  { label: 'Latency (LAN)', value: '<50ms' },
  { label: 'Encryption', value: 'AES-GCM 256' },
  { label: 'License', value: 'Apache 2.0' },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Nav */}
      <nav className="flex items-center px-8 h-14 border-b border-surface-border bg-background-subtle">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-md bg-brand">
            <Video className="h-4 w-4 text-white" />
          </div>
          <span className="font-semibold text-text-primary tracking-tight">OpenMeet</span>
        </div>
        <div className="flex items-center gap-6 ml-10 text-sm text-text-secondary">
          <Link href="#features" className="hover:text-text-primary transition-colors">Features</Link>
          <Link href="#security" className="hover:text-text-primary transition-colors">Security</Link>
          <Link href="https://github.com/openmeet" className="hover:text-text-primary transition-colors flex items-center gap-1.5">
            <Github className="h-4 w-4" /> GitHub
          </Link>
        </div>
        <div className="ml-auto flex items-center gap-3">
          <Link href="/login" className="btn-ghost btn-sm text-text-secondary hover:text-text-primary">
            Sign in
          </Link>
          <Link href="/login" className="btn-primary btn-sm">
            Get started <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="flex flex-col items-center text-center px-6 pt-24 pb-20">
        <div className="badge badge-brand mb-6">
          <span className="h-1.5 w-1.5 rounded-full bg-brand animate-pulse-dot" />
          Self-hosted · Open Source · Air-gappable
        </div>

        <h1 className="text-5xl font-bold tracking-tight text-text-primary max-w-3xl leading-tight">
          Video conferencing built for{' '}
          <span className="text-gradient">high-security</span> organizations
        </h1>

        <p className="mt-6 text-lg text-text-secondary max-w-xl leading-relaxed">
          A self-hosted alternative to Google Meet with on-prem AI transcription,
          end-to-end encryption, and compliance features designed for military, police,
          and government operations.
        </p>

        <div className="flex items-center gap-4 mt-10">
          <Link href="/login" className="btn-primary btn-lg">
            Start a meeting <ArrowRight className="h-4 w-4" />
          </Link>
          <Link href="https://github.com/openmeet" className="btn-secondary btn-lg">
            <Github className="h-4 w-4" /> View on GitHub
          </Link>
        </div>

        {/* Stats bar */}
        <div className="mt-16 flex items-center gap-px rounded-lg overflow-hidden border border-surface-border">
          {stats.map((s, i) => (
            <div
              key={i}
              className="flex flex-col items-center px-8 py-4 bg-surface hover:bg-surface-hover transition-colors"
            >
              <span className="text-2xl font-bold text-text-primary">{s.value}</span>
              <span className="text-xs text-text-secondary mt-0.5">{s.label}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section id="features" className="px-8 pb-24 max-w-5xl mx-auto w-full">
        <h2 className="text-2xl font-bold text-text-primary text-center mb-12">
          Everything you need, nothing you don't
        </h2>
        <div className="grid grid-cols-2 gap-4">
          {features.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="card p-6 group hover:border-brand/40 transition-colors">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand/10 mb-4 group-hover:bg-brand/20 transition-colors">
                <Icon className="h-5 w-5 text-brand" />
              </div>
              <h3 className="font-semibold text-text-primary mb-2">{title}</h3>
              <p className="text-sm text-text-secondary leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Security callout */}
      <section id="security" className="mx-8 mb-24 rounded-xl border border-brand/20 bg-brand/5 p-10 max-w-5xl mx-auto w-full">
        <div className="flex items-start gap-6">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-brand/15">
            <Shield className="h-6 w-6 text-brand" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-text-primary mb-2">
              Designed for air-gapped, classified environments
            </h2>
            <p className="text-sm text-text-secondary leading-relaxed max-w-2xl">
              OpenMeet can be deployed with zero internet egress — all LLM inference, STT, and
              media routing run on your own hardware. Integrate with existing LDAP / Active Directory,
              enforce MFA, set per-room classification tiers (Confidential / Secret / Top Secret),
              and maintain tamper-evident audit logs compliant with Vietnam Cybersecurity Law 2018
              and ISO 27001.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto border-t border-surface-border px-8 py-6 flex items-center justify-between text-xs text-text-secondary">
        <span>© 2025 OpenMeet — Apache 2.0</span>
        <span>Built with LiveKit · Next.js · Whisper · Llama 3</span>
      </footer>
    </div>
  )
}
