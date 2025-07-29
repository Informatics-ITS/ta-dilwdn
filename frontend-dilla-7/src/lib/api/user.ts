import { api } from '$lib/config/axios'
import type { User, Register } from '$lib/types/user'

export async function getAllUser(): Promise<User[]> {
  const res = await api.get('/api/users')
  return res.data
}

export async function register(data: Register) {
  const res = await api.post('/api/users', data)
  return res.data
}
