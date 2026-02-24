import axios from 'axios'

// const axiosInstance = axios.create({
//   baseURL: 'http://localhost:5000',
//   timeout: 30000,
// })

// export default axiosInstance
// Instance for the Plagiarism Analysis Backend (Flask)
// Use timeout: 0 to disable axios-side timeout; the browser/Flask will control limits.
const analysisApi = axios.create({
  baseURL: 'http://localhost:5000',
  timeout: 0,
});

// Instance for the User Authentication Backend (Node.js + MongoDB)
const authApi = axios.create({
  baseURL: 'http://localhost:5001', // Your new Auth Server port
  timeout: 10000,
});

// Add a request interceptor to include the JWT token automatically for Auth calls
authApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export { analysisApi, authApi };