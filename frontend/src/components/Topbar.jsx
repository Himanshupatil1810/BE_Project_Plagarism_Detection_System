import { Menu, Sun, Moon, Search } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useTheme } from '../context/ThemeContext.jsx'
import { useAuth } from '../context/AuthContext.jsx'

const PAGE_TITLES = {
  '/':        'Dashboard',
  '/history': 'Report History',
  '/verify':  'Verification Portal',
  '/results': 'Analysis Results',
}

export default function Topbar({ onMenuClick, pathname }) {
  const { theme, toggle } = useTheme()
  const { user } = useAuth()
  const navigate = useNavigate()
  const title = PAGE_TITLES[pathname] || 'ChainGuard'

  return (
    <div className="topbar">
      <div className="flex items-center gap-3">
        <button className="icon-btn lg:hidden" onClick={onMenuClick}>
          <Menu size={17} />
        </button>
        <h1 className="font-syne font-bold text-app" style={{ fontSize: 18 }}>
          {title}
        </h1>
      </div>

      <div className="flex items-center gap-2">
        <button className="icon-btn" onClick={() => navigate('/verify')} title="Verify a report">
          <Search size={16} />
        </button>
        <button className="icon-btn" onClick={toggle} title="Toggle theme">
          {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
        </button>
        <div
          className="flex items-center justify-center rounded-full font-syne font-bold ml-1"
          style={{
            width: 32, height: 32, fontSize: 13, color: '#0f1117',
            background: 'linear-gradient(135deg, #34d399, #0891b2)',
            flexShrink: 0,
          }}
        >
          {(user?.name || user?.email || '?')[0].toUpperCase()}
        </div>
      </div>
    </div>
  )
}
