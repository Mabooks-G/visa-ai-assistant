import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { LogIn, Mail, Lock, Eye, EyeOff, AlertCircle } from 'lucide-react'
import { login } from '/src/lib/api'

export default function Login() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.message || 'Invalid email or password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-xl bg-primary shadow-lg">
            <span className="font-heading text-2xl font-bold text-on-primary">V</span>
          </div>
          <h1 className="font-heading text-3xl font-bold text-foreground">Visa AI Assistant</h1>
          <p className="mt-2 text-secondary">Sign in to manage your visa applications</p>
        </div>

        {/* Form */}
        <form onSubmit={handleLogin} className="rounded-xl border border-border bg-white p-6 shadow-md">
          {error && (
            <div className="mb-4 flex items-start gap-3 rounded-lg bg-destructive/10 p-3 text-sm text-destructive">
              <AlertCircle size={18} className="mt-0.5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="mb-4">
            <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-foreground">
              Email
            </label>
            <div className="relative">
              <Mail size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary" />
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
                className="w-full rounded-lg border border-border bg-background py-2.5 pl-10 pr-3 text-sm text-foreground placeholder:text-secondary focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/20 transition-all"
              />
            </div>
          </div>

          <div className="mb-6">
            <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-foreground">
              Password
            </label>
            <div className="relative">
              <Lock size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary" />
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
                className="w-full rounded-lg border border-border bg-background py-2.5 pl-10 pr-10 text-sm text-foreground placeholder:text-secondary focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/20 transition-all"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-secondary hover:text-foreground cursor-pointer"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-accent py-2.5 text-sm font-semibold text-white transition-all duration-150 hover:bg-accent/90 active:scale-[0.97] disabled:opacity-60 cursor-pointer"
          >
            {loading ? (
              <div className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />
            ) : (
              <>
                <LogIn size={18} />
                Sign In
              </>
            )}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-secondary">
          Don't have an account?{' '}
          <Link to="/register" className="font-medium text-accent hover:text-accent/80 transition-colors">
            Create one
          </Link>
        </p>
      </div>
    </div>
  )
}