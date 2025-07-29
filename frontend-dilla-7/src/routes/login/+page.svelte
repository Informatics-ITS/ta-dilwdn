<script lang="ts">
  import { Eye, EyeOff, Mail, Lock, User, BookOpen } from 'lucide-svelte'
  import { goto } from '$app/navigation'
  import { login } from '$lib/api/auth'
  import type { Auth } from '$lib/types/auth'

  // Login state
  let loginType: 'guru' | 'siswa' = 'guru'
  let email = ''
  let password = ''
  let remember = false
  let showPassword = false
  let errorMessage = ''
  let isLoading = false

  async function handleLogin(event: Event) {
    event.preventDefault()
    errorMessage = ''
    isLoading = true

    try {
      // Prepare login data based on user type
      let loginData: any = {}
      
      if (loginType === 'guru') {
        loginData = {
          email,
          password
        }
      } else {
        loginData = {
          nisn: email, // Use email field for NISN
          password
        }
      }

      const response = await login(loginData)

      // Store user data
      localStorage.setItem('user', JSON.stringify(response.user))
      localStorage.setItem('id', response.user.id)

      // Role-based redirect to pages with proper design
      if (response.user.role === 'guru' || response.user.role === 'admin') {
        goto('/dashboard') // Dashboard has complete design
      } else if (response.user.role === 'siswa') {
        goto('/siswa') // Will auto-redirect to siswa/[id] which has design
      } else {
        // Fallback - redirect to login page with error
        errorMessage = 'Role tidak dikenali'
        localStorage.clear()
      }
    } catch (error) {
      console.error('Login error:', error)
      errorMessage = loginType === 'guru' ? 'Email atau password salah' : 'NISN atau password salah'
    } finally {
      isLoading = false
    }
  }
</script>

<div class="min-h-screen flex items-center justify-center bg-registrasi bg-cover bg-center bg-black">
  <!-- Header -->
  <div class="text-center absolute top-20 text-white px-4">
    <h1 class="text-4xl font-bold mb-4">Login</h1>
    <p class="text-lg">
      Selamat datang! Silakan pilih jenis login
      <br />
      <span class="font-semibold">untuk melanjutkan</span>
    </p>
  </div>

  <div class="bg-pink-100 p-8 rounded-xl shadow-md w-full max-w-md mt-20">
    <!-- Login Type Toggle -->
    <div class="flex mb-6 bg-gray-200 p-1 rounded-xl">
      <button class={`flex-1 py-2 rounded-xl transition ${loginType === 'guru' ? 'bg-purple-500 text-white' : 'text-gray-700'}`} on:click={() => (loginType = 'guru')}>
        <div class="flex items-center justify-center gap-2">
          <User size="18" />
          <span>Guru</span>
        </div>
      </button>
      <button class={`flex-1 py-2 rounded-xl transition ${loginType === 'siswa' ? 'bg-purple-500 text-white' : 'text-gray-700'}`} on:click={() => (loginType = 'siswa')}>
        <div class="flex items-center justify-center gap-2">
          <BookOpen size="18" />
          <span>Siswa</span>
        </div>
      </button>
    </div>

    <form class="space-y-4" on:submit|preventDefault={handleLogin}>
      <div class="block text-left font-semibold text-gray-700">
        {loginType === 'guru' ? 'Akun Guru' : 'Akun Siswa'}
      </div>

      <!-- Email/NISN Field -->
      <div class="relative">
        <span class="absolute left-3 top-2.5 text-gray-400">
          {#if loginType === 'guru'}
            <Mail size="20" />
          {:else}
            <User size="20" />
          {/if}
        </span>

        <input type="text" bind:value={email} placeholder="Email" class="w-full rounded-2xl pl-10 pr-4 py-2 border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-400" />
      </div>

      <!-- Password -->
      <div class="relative">
        <span class="absolute left-3 top-2.5 text-gray-400">
          <Lock size="20" />
        </span>
        <input
          type={showPassword ? 'text' : 'password'}
          bind:value={password}
          placeholder="Kata Sandi"
          class="w-full rounded-2xl pl-10 pr-10 py-2 border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-400"
        />
        <button type="button" class="absolute right-3 top-2.5 text-gray-500 hover:text-primary" on:click={() => (showPassword = !showPassword)}>
          {#if showPassword}
            <Eye size="20" />
          {:else}
            <EyeOff size="20" />
          {/if}
        </button>
      </div>

      <!-- Forgot Password -->
      <div class="flex justify-between items-center">
        <div class="text-left">
          <a href="/forgot-password" class="text-sm text-primary hover:underline">Lupa kata sandi?</a>
        </div>

        <!-- Error Message -->
        {#if errorMessage}
          <p class="text-sm text-red-600">{errorMessage}</p>
        {/if}
      </div>

      <div class="flex justify-between items-center">
        <!-- Remember Me -->
        <label class="flex items-center space-x-2 text-sm">
          <input type="checkbox" bind:checked={remember} />
          <span>Ingat Saya</span>
        </label>

        <!-- Submit -->
        <button type="submit" disabled={isLoading} class="bg-purple-500 text-white py-2 px-6 rounded-2xl hover:bg-primary transition text-sm">Masuk</button>
      </div>

      <!-- Register -->
      <p class="text-sm text-center mt-4">
        Belum mempunyai akun?
        <a href="/register" class="text-sm text-primary hover:underline">Daftar di sini</a>
      </p>
    </form>
  </div>
</div>
