import { redirect } from '@sveltejs/kit'

export function load() {
  if (typeof localStorage !== 'undefined') {
    const user = localStorage.getItem('user')
    if (!user) {
      throw redirect(302, '/login')
    }

    try {
      const userData = JSON.parse(user)
      // Only allow siswa to access siswa pages
      if (userData.role !== 'siswa') {
        // Redirect guru/admin to dashboard which has proper design
        throw redirect(302, '/dashboard')
      }
    } catch (error) {
      // If parsing fails, redirect to login
      localStorage.removeItem('user')
      throw redirect(302, '/login')
    }
  }
}
