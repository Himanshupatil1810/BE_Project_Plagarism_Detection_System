import { createContext, useContext, useState } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      // Prefer the user object saved by the auth-server integration (includes user_id)
      const stored = localStorage.getItem('user') || localStorage.getItem('chainguard_user')
      return stored ? JSON.parse(stored) : null
    }
    catch { return null }
  })

  const login = (userData, token) => {
    // Ensure we always have user_id available from the auth-server response
    const normalizedUser = {
      ...userData,
      user_id: userData.user_id || userData.id || userData._id,
    }

    setUser(normalizedUser)
    localStorage.setItem('chainguard_user', JSON.stringify(normalizedUser))
    localStorage.setItem('chainguard_token', token)
    // Keep compatibility with authService.js which stores `user` and `token`
    localStorage.setItem('user', JSON.stringify(normalizedUser))
    localStorage.setItem('token', token)
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
