import { createContext, useContext, useEffect, useState } from 'react'

const ThemeContext = createContext(null)

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(
    () => localStorage.getItem('chainguard_theme') || 'dark'
  )

  useEffect(() => {
    const root = document.documentElement
    if (theme === 'light') {
      root.classList.add('theme-light')
    } else {
      root.classList.remove('theme-light')
    }
    localStorage.setItem('chainguard_theme', theme)
  }, [theme])

  const toggle = () => setTheme((t) => (t === 'dark' ? 'light' : 'dark'))

  return (
    <ThemeContext.Provider value={{ theme, toggle }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => useContext(ThemeContext)
