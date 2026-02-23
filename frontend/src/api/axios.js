import axios from 'axios'

const axiosInstance = axios.create({
  baseURL: 'http://localhost:5000',
  timeout: 30000,
})

export default axiosInstance
