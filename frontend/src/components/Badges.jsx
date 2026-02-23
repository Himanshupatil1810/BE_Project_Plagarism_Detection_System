import { useState } from 'react'
import { CheckCircle, AlertTriangle, XCircle, Check, Copy } from 'lucide-react'

export function RiskBadge({ level }) {
  const cls =
    level === 'High' ? 'badge-high' : level === 'Medium' ? 'badge-medium' : 'badge-low'
  const Icon =
    level === 'High' ? XCircle : level === 'Medium' ? AlertTriangle : CheckCircle
  return (
    <span className={`badge ${cls}`}>
      <Icon size={10} />
      {level}
    </span>
  )
}

export function CopyButton({ text }) {
  const [copied, setCopied] = useState(false)
  const copy = () => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  return (
    <button
      onClick={copy}
      className="inline-flex items-center justify-center ml-1.5 p-0.5 rounded transition-colors"
      style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text3)' }}
      onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--accent)')}
      onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text3)')}
      title="Copy"
    >
      {copied ? <Check size={12} /> : <Copy size={12} />}
    </button>
  )
}
