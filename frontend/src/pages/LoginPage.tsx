import { useState, useMemo } from 'react';
import { useAuth } from '../lib/auth';
import { useNavigate } from 'react-router-dom';
import { LogIn, UserPlus, Mail, Lock, User, Sparkles, Mic, FileText, Zap, Check, X } from 'lucide-react';
import './LoginPage.css';

function PasswordStrength({ password }: { password: string }) {
  const checks = useMemo(() => [
    { label: 'At least 8 characters', test: password.length >= 8 },
    { label: 'Uppercase letter', test: /[A-Z]/.test(password) },
    { label: 'Lowercase letter', test: /[a-z]/.test(password) },
    { label: 'Number', test: /\d/.test(password) },
    { label: 'Special character', test: /[!@#$%^&*(),.?":{}|<>]/.test(password) },
  ], [password]);

  const passed = checks.filter(c => c.test).length;
  const strength = passed <= 1 ? 'weak' : passed <= 3 ? 'fair' : passed <= 4 ? 'good' : 'strong';

  if (!password) return null;

  return (
    <div className="password-strength animate-fade-in">
      <div className="strength-bars">
        {[1, 2, 3, 4, 5].map(i => (
          <div key={i} className={`strength-bar ${i <= passed ? `strength-${strength}` : ''}`} />
        ))}
      </div>
      <span className={`strength-label strength-label-${strength}`}>
        {strength.charAt(0).toUpperCase() + strength.slice(1)}
      </span>
      <ul className="strength-checklist">
        {checks.map((check, i) => (
          <li key={i} className={check.test ? 'check-pass' : 'check-fail'}>
            {check.test ? <Check size={12} /> : <X size={12} />}
            {check.label}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [errorList, setErrorList] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setErrorList([]);
    setLoading(true);
    try {
      if (isLogin) {
        await login(email, password);
      } else {
        await register(email, username, password);
      }
      navigate('/');
    } catch (err: any) {
      const data = err.response?.data || {};
      const detail = data.detail;
      const message = data.message;

      if (message?.password_errors && Array.isArray(message.password_errors)) {
        setErrorList(message.password_errors);
      } else if (typeof message === 'string') {
        setError(message);
      } else if (typeof detail === 'string') {
        setError(detail);
      } else if (detail?.password_errors && Array.isArray(detail.password_errors)) {
        setErrorList(detail.password_errors);
      } else if (Array.isArray(detail)) {
        // Pydantic validation errors
        setErrorList(detail.map((d: any) => d.msg || JSON.stringify(d)));
      } else {
        setError('An error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      {/* Background decoration */}
      <div className="login-bg-orb login-bg-orb-1" />
      <div className="login-bg-orb login-bg-orb-2" />
      <div className="login-bg-orb login-bg-orb-3" />

      <div className="login-container">
        {/* Left panel — branding */}
        <div className="login-branding">
          <div className="login-branding-content">
            <div className="login-logo">
              <Sparkles size={40} />
            </div>
            <h1 className="login-brand-title">
              AI Meeting<br /><span className="gradient-text">Summarizer</span>
            </h1>
            <p className="login-brand-subtitle">
              Transform your meetings into actionable insights with AI-powered transcription and summarization.
            </p>
            <div className="login-features">
              <div className="login-feature">
                <Mic size={20} />
                <span>Audio Transcription</span>
              </div>
              <div className="login-feature">
                <FileText size={20} />
                <span>Smart Summaries</span>
              </div>
              <div className="login-feature">
                <Zap size={20} />
                <span>Action Items</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right panel — form */}
        <div className="login-form-panel">
          <div className="login-form-wrapper">
            <div className="login-form-header">
              <h2>{isLogin ? 'Welcome back' : 'Create account'}</h2>
              <p>{isLogin ? 'Sign in to your account' : 'Get started for free'}</p>
            </div>

            {error && (
              <div className="login-error">
                {error}
              </div>
            )}

            {errorList.length > 0 && (
              <div className="login-error login-error-list">
                <ul>
                  {errorList.map((msg, i) => (
                    <li key={i}>{msg}</li>
                  ))}
                </ul>
              </div>
            )}

            <form onSubmit={handleSubmit} className="login-form">
              <div className="input-group">
                <Mail size={18} className="input-icon" />
                <input
                  type="email"
                  className="input-field"
                  placeholder="Email address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                  style={{ paddingLeft: '44px' }}
                />
              </div>

              {!isLogin && (
                <div className="input-group animate-fade-in">
                  <User size={18} className="input-icon" />
                  <input
                    type="text"
                    className="input-field"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                    minLength={3}
                    pattern="[a-zA-Z0-9_-]+"
                    style={{ paddingLeft: '44px' }}
                  />
                </div>
              )}

              <div className="input-group">
                <Lock size={18} className="input-icon" />
                <input
                  type="password"
                  className="input-field"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={8}
                  style={{ paddingLeft: '44px' }}
                />
              </div>

              {/* Password strength — registration only */}
              {!isLogin && <PasswordStrength password={password} />}

              <button type="submit" className="btn-primary login-submit" disabled={loading}>
                {loading ? (
                  <span className="spinner" style={{ width: 20, height: 20, borderWidth: 2 }} />
                ) : isLogin ? (
                  <><LogIn size={18} /> Sign In</>
                ) : (
                  <><UserPlus size={18} /> Create Account</>
                )}
              </button>
            </form>

            <div className="login-switch">
              <span>{isLogin ? "Don't have an account?" : 'Already have an account?'}</span>
              <button
                type="button"
                className="btn-ghost"
                onClick={() => { setIsLogin(!isLogin); setError(''); setErrorList([]); }}
              >
                {isLogin ? 'Sign up' : 'Sign in'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
