import axios from 'axios'

const url = 'http://localhost:5000'
const api = axios.create({ 
  baseURL: url,
  withCredentials: true  // Enable credentials for session cookies
})

// Token
let token: string | null = null
if (typeof window !== 'undefined') {
  token = localStorage.getItem('token')
}

// Headers
const headers = token ? { Authorization: `Bearer ${token}` } : {}

const headersImage = token
  ? {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'multipart/form-data'
    }
  : { 'Content-Type': 'multipart/form-data' }

// Cookie
axios.defaults.withCredentials = true

export { axios, api, url, token, headers, headersImage }
