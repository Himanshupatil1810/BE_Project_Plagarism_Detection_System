import { createContext, useContext, useState } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('chainguard_user')) }
    catch { return null }
  })

  const login = (userData, token) => {
    setUser(userData)
    localStorage.setItem('chainguard_user', JSON.stringify(userData))
    localStorage.setItem('chainguard_token', token)
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('chainguard_user')
    localStorage.removeItem('chainguard_token')
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
