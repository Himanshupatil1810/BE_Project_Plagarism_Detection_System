import { useState } from 'react'
import { Shield, Mail, Lock, User, ArrowRight } from 'lucide-react'
import { useAuth } from '../context/AuthContext.jsx'
import { authService } from '../api/authService.js'

export default function Login() {
  const { login } = useAuth()
  const [mode, setMode]     = useState('login')   // 'login' | 'signup'
  const [form, setForm]     = useState({ name: '', email: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError]   = useState('')

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }))

  const submit = async () => {
    if (!form.email || !form.password) { setError('Please fill in all fields.'); return }
    if (mode === 'signup' && !form.name) { setError('Please enter your name.'); return }
    setError(''); setLoading(true)
    try {
      const res =
        mode === 'login'
          ? await authService.login(form.email, form.password)
          : await authService.signup(form.email, form.password, form.name)
      login(res.user, res.token)
    } catch (err) {
      setError(err.message)
    }
    setLoading(false)
  }

  const onKey = (e) => { if (e.key === 'Enter') submit() }
  const switchMode = () => { setMode((m) => (m === 'login' ? 'signup' : 'login')); setError('') }

  return (
    <div
      className="min-h-screen flex items-center justify-center relative overflow-hidden"
      style={{ background: 'var(--bg)' }}
    >
      {/* Background orbs */}
      <div
        className="auth-orb"
        style={{ width: 500, height: 500, background: '#34d399', top: -200, left: -100 }}
      />
      <div
        className="auth-orb"
        style={{ width: 400, height: 400, background: '#0891b2', bottom: -150, right: -100 }}
      />

      <div
        className="relative z-10 w-full mx-4 fade-in"
        style={{
          maxWidth: 400,
          background: 'var(--bg2)',
          border: '1px solid var(--border2)',
          borderRadius: 20,
          padding: '40px',
        }}
      >
        {/* Logo */}
        <div className="flex items-center justify-center gap-3 mb-8">
          <div
            className="flex items-center justify-center rounded-xl"
            style={{ width: 40, height: 40, background: 'linear-gradient(135deg,#34d399,#0891b2)' }}
          >
            <Shield size={20} color="#0f1117" />
          </div>
          <div>
            <div className="font-syne font-extrabold text-app" style={{ fontSize: 20, lineHeight: 1 }}>
              ChainGuard
            </div>
            <div className="font-jetbrains text-app3 uppercase mt-0.5" style={{ fontSize: 10, letterSpacing: 1 }}>
              AI Plagiarism Detection
            </div>
          </div>
        </div>

        <h2 className="font-syne font-extrabold text-app text-center mb-1.5" style={{ fontSize: 24 }}>
          {mode === 'login' ? 'Welcome back' : 'Create account'}
        </h2>
        <p className="text-app2 text-center text-sm mb-7">
          {mode === 'login'
            ? 'Sign in to your account to continue'
            : 'Start detecting plagiarism with blockchain verification'}
        </p>

        {/* Name (signup only) */}
        {mode === 'signup' && (
          <div className="mb-4">
            <label className="block text-app2 font-semibold mb-1.5" style={{ fontSize: 13 }}>
              Full Name
            </label>
            <div className="relative">
              <User size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-app3 pointer-events-none" />
              <input
                className="form-input has-icon"
                placeholder="John Doe"
                value={form.name}
                onChange={set('name')}
                onKeyDown={onKey}
              />
            </div>
          </div>
        )}

        {/* Email */}
        <div className="mb-4">
          <label className="block text-app2 font-semibold mb-1.5" style={{ fontSize: 13 }}>
            Email
          </label>
          <div className="relative">
            <Mail size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-app3 pointer-events-none" />
            <input
              className="form-input has-icon"
              type="email"
              placeholder="you@example.com"
              value={form.email}
              onChange={set('email')}
              onKeyDown={onKey}
            />
          </div>
        </div>

        {/* Password */}
        <div className="mb-5">
          <label className="block text-app2 font-semibold mb-1.5" style={{ fontSize: 13 }}>
            Password
          </label>
          <div className="relative">
            <Lock size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-app3 pointer-events-none" />
            <input
              className="form-input has-icon"
              type="password"
              placeholder="••••••••"
              value={form.password}
              onChange={set('password')}
              onKeyDown={onKey}
            />
          </div>
        </div>

        {/* Error */}
        {error && (
          <div
            className="mb-4 text-danger rounded-lg px-3 py-2.5 text-sm"
            style={{ background: 'var(--danger-dim)' }}
          >
            {error}
          </div>
        )}

        {/* Submit */}
        <button
          className="btn btn-primary w-full"
          onClick={submit}
          disabled={loading}
        >
          {loading ? (
            <div className="spinner" />
          ) : (
            <>
              {mode === 'login' ? 'Sign In' : 'Create Account'}
              <ArrowRight size={16} />
            </>
          )}
        </button>

        {/* Switch */}
        <p className="text-center text-app2 mt-5 text-sm">
          {mode === 'login' ? "Don't have an account? " : 'Already have an account? '}
          <button
            onClick={switchMode}
            className="text-accent font-semibold"
            style={{ background: 'none', border: 'none', cursor: 'pointer' }}
          >
            {mode === 'login' ? 'Sign up' : 'Sign in'}
          </button>
        </p>
      </div>
    </div>
  )
}
