// // Simulates a Node.js / Express + SQLite auth backend using localStorage.
// // Replace these functions with real fetch/axios calls to your auth server.

// const DB_KEY = 'integrichain_auth_db'

// const getDB = () => {
//   try { return JSON.parse(localStorage.getItem(DB_KEY) || '[]') }
//   catch { return [] }
// }
// const saveDB = (users) => localStorage.setItem(DB_KEY, JSON.stringify(users))

// const fakeJwt = (payload) => btoa(JSON.stringify({ ...payload, exp: Date.now() + 86_400_000 }))

// export const authService = {
//   signup: async (email, password, name) => {
//     const users = getDB()
//     if (users.find((u) => u.email === email)) {
//       throw new Error('An account with this email already exists.')
//     }
//     const user = {
//       id: `user_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
//       email,
//       name,
//       passwordHash: btoa(password),
//       createdAt: new Date().toISOString(),
//     }
//     users.push(user)
//     saveDB(users)
//     const token = fakeJwt({ id: user.id, email, name })
//     return { token, user: { id: user.id, email, name } }
//   },

//   login: async (email, password) => {
//     const users = getDB()
//     const user = users.find(
//       (u) => u.email === email && u.passwordHash === btoa(password)
//     )
//     if (!user) throw new Error('Invalid email or password.')
//     const token = fakeJwt({ id: user.id, email: user.email, name: user.name })
//     return { token, user: { id: user.id, email: user.email, name: user.name } }
//   },
// }
// CHANGE: Specifically import the authApi instance configured for port 5001
import { authApi } from './axios'; 

export const authService = {
  signup: async (email, password, name) => {
    try {
      // CHANGE: Use authApi instead of generic axios
      const response = await authApi.post('/api/auth/signup', {
        name,
        email,
        password
      });

      if (response.data.token) {
        localStorage.setItem('token', response.data.token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }

      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Signup failed. Please try again.');
    }
  },

  login: async (email, password) => {
    try {
      // CHANGE: Use authApi instead of generic axios
      const response = await authApi.post('/api/auth/login', {
        email,
        password
      });

      if (response.data.token) {
        localStorage.setItem('token', response.data.token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }

      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Invalid email or password.');
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  getCurrentUserId: () => {
    const user = JSON.parse(localStorage.getItem('user'));
    // This user_id was generated in MongoDB and is sent to Flask for tracking
    return user ? user.user_id : null;
  }
};