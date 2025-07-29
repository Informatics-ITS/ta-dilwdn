import { redirect } from '@sveltejs/kit'

export function load() {
  if (typeof localStorage !== 'undefined') {
    const user = localStorage.getItem('user')
    if (!user) {
      throw redirect(302, '/login')
    }

    try {
      const userData = JSON.parse(user)
      // Only allow guru or admin to access dashboard
      if (userData.role !== 'guru' && userData.role !== 'admin') {
        // Redirect siswa to their proper page with design
        throw redirect(302, '/siswa')
      }
    } catch (error) {
      // If parsing fails, redirect to login
      localStorage.removeItem('user')
      throw redirect(302, '/login')
    }
  }
}
