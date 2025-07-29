import { api } from '$lib/config/axios'
import type { Auth } from '$lib/types/auth'

export async function login(data: Auth | { nisn: string; password: string }) {
  const res = await api.post('/api/login', data)
  return res.data
}