import { useNavigate, useLocation } from 'react-router-dom'
import { BarChart2, Clock, Shield, FileText, LogOut, ChevronRight } from 'lucide-react'
import { useAuth } from '../context/AuthContext.jsx'

const NAV = [
  { path: '/',        label: 'Dashboard',        Icon: BarChart2 },
  { path: '/history', label: 'Report History',   Icon: Clock     },
  { path: '/verify',  label: 'Verify Document',  Icon: Shield    },
]

export default function Sidebar({ isOpen, onClose }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const { pathname } = useLocation()

  const go = (path) => { navigate(path); onClose?.() }

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-90 lg:hidden"
          style={{ background: 'rgba(0,0,0,0.5)', zIndex: 90 }}
          onClick={onClose}
        />
      )}

      <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
        {/* Logo */}
        <div
          className="flex items-center gap-2.5 px-5 py-6"
          style={{ borderBottom: '1px solid var(--border)' }}
        >
          <div
            className="flex items-center justify-center rounded-xl flex-shrink-0"
            style={{
              width: 34, height: 34,
              background: 'linear-gradient(135deg, #34d399, #0891b2)',
            }}
          >
            <Shield size={16} color="#0f1117" />
          </div>
          <div>
            <div className="font-syne font-bold text-app leading-none" style={{ fontSize: 16 }}>
              IntegriChain
            </div>
            <div
              className="font-jetbrains text-app3 uppercase mt-0.5"
              style={{ fontSize: 10, letterSpacing: '1px' }}
            >
              Plagiarism AI
            </div>
          </div>
        </div>

        {/* Nav */}
        <div className="flex-1 overflow-y-auto px-3 py-4">
          <div
            className="font-jetbrains text-app3 uppercase px-2 mb-2"
            style={{ fontSize: 10, letterSpacing: '1.2px' }}
          >
            Navigation
          </div>
          {NAV.map(({ path, label, Icon }) => (
            <button
              key={path}
              className={`nav-item ${pathname === path ? 'active' : ''}`}
              onClick={() => go(path)}
            >
              <Icon size={15} className="flex-shrink-0" />
              {label}
            </button>
          ))}

          <div
            className="font-jetbrains text-app3 uppercase px-2 mb-2 mt-5"
            style={{ fontSize: 10, letterSpacing: '1.2px' }}
          >
            Tools
          </div>
          <button
            className={`nav-item ${pathname === '/results' ? 'active' : ''}`}
            onClick={() => go('/results')}
          >
            <FileText size={15} className="flex-shrink-0" />
            Latest Result
            <ChevronRight size={13} className="ml-auto" />
          </button>
        </div>

        {/* User footer */}
        <div
          className="px-4 py-4"
          style={{ borderTop: '1px solid var(--border)' }}
        >
          <div className="flex items-center gap-2.5">
            <div
              className="flex items-center justify-center rounded-full flex-shrink-0 font-syne font-bold"
              style={{
                width: 32, height: 32, fontSize: 13, color: '#0f1117',
                background: 'linear-gradient(135deg, #34d399, #0891b2)',
              }}
            >
              {(user?.name || user?.email || '?')[0].toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <div className="font-semibold text-app truncate" style={{ fontSize: 13 }}>
                {user?.name || 'User'}
              </div>
              <div className="text-app3 truncate" style={{ fontSize: 11 }}>
                {user?.email}
              </div>
            </div>
            <button
              onClick={logout}
              className="flex items-center justify-center rounded-lg p-1.5 transition-colors"
              title="Sign out"
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text3)' }}
              onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--danger)'; e.currentTarget.style.background = 'var(--danger-dim)' }}
              onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--text3)'; e.currentTarget.style.background = 'none' }}
            >
              <LogOut size={15} />
            </button>
          </div>
        </div>
      </aside>
    </>
  )
}
