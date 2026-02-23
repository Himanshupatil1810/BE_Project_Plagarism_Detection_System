// Simulates a Node.js / Express + SQLite auth backend using localStorage.
// Replace these functions with real fetch/axios calls to your auth server.

const DB_KEY = 'integrichain_auth_db'

const getDB = () => {
  try { return JSON.parse(localStorage.getItem(DB_KEY) || '[]') }
  catch { return [] }
}
const saveDB = (users) => localStorage.setItem(DB_KEY, JSON.stringify(users))

const fakeJwt = (payload) => btoa(JSON.stringify({ ...payload, exp: Date.now() + 86_400_000 }))

export const authService = {
  signup: async (email, password, name) => {
    const users = getDB()
    if (users.find((u) => u.email === email)) {
      throw new Error('An account with this email already exists.')
    }
    const user = {
      id: `user_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
      email,
      name,
      passwordHash: btoa(password),
      createdAt: new Date().toISOString(),
    }
    users.push(user)
    saveDB(users)
    const token = fakeJwt({ id: user.id, email, name })
    return { token, user: { id: user.id, email, name } }
  },

  login: async (email, password) => {
    const users = getDB()
    const user = users.find(
      (u) => u.email === email && u.passwordHash === btoa(password)
    )
    if (!user) throw new Error('Invalid email or password.')
    const token = fakeJwt({ id: user.id, email: user.email, name: user.name })
    return { token, user: { id: user.id, email: user.email, name: user.name } }
  },
}
