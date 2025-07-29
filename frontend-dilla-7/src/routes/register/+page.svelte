<script lang="ts">
  import { Eye, EyeOff } from 'lucide-svelte'
  import { register } from '$lib/api/user'
  import type { Register } from '$lib/types/user'

  let name = ''
  let email = ''
  let gender = ''
  let password = ''
  let confirmPassword = ''
  let showPassword = false
  let showConfirm = false
  let errorMessage = ''
  let successMessage = ''

  async function handleSubmit(event: Event) {
    event.preventDefault()
    errorMessage = ''
    successMessage = ''

    if (!name || !email || !gender || !password || !confirmPassword) {
      errorMessage = 'Semua kolom wajib diisi'
      return
    }

    if (password !== confirmPassword) {
      errorMessage = 'Konfirmasi password tidak sesuai'
      return
    }

    const data: Register = {
      nama_lengkap: name,
      email,
      jenis_kelamin: gender,
      password,
      role: "guru"
    }

    try {
      await register(data)
      successMessage = 'Registrasi berhasil, Silahkan'
      name = email = gender = password = confirmPassword = ''
    } catch (err) {
      errorMessage = 'Registrasi gagal. Coba lagi.'
      console.error(err)
    }
  }
</script>

<div class="min-h-screen flex items-center justify-center bg-registrasi bg-cover bg-center bg-black">
  <div class="bg-pink-100 rounded-2xl shadow-lg p-8 w-full max-w-xl">
    <!-- Title -->
    <div class="mb-6 text-center">
      <h1 class="text-3xl font-bold text-gray-700">Masukkan</h1>
      <p class="text-3xl font-bold text-gray-700">Data Registrasi</p>
    </div>

    <!-- Snk -->
    <p class="text-sm text-gray-600 mb-6">
      Kami membutuhkan bantuan Anda untuk memberikan beberapa informasi dasar untuk pembuatan akun Anda. Berikut ini adalah
      <span class="text-blue-600 underline cursor-pointer">syarat dan ketentuan</span>
      kami.
    </p>

    <form class="space-y-4" on:submit|preventDefault={handleSubmit}>
      <!-- Name -->
      <div>
        <label class="block text-sm font-medium text-gray-700" for="name">Nama Lengkap</label>
        <input id="name" type="text" bind:value={name} placeholder="John" class="w-full px-4 py-2 rounded-2xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500" />
      </div>

      <!-- Email -->
      <div>
        <label class="block text-sm font-medium text-gray-700" for="email">Email</label>
        <input
          id="email"
          type="email"
          bind:value={email}
          placeholder="johnsmith@gmail.com"
          class="w-full px-4 py-2 rounded-2xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500"
        />
      </div>

      <!-- Gender -->
      <div>
        <label class="block text-sm font-medium text-gray-700" for="gender">Jenis Kelamin</label>
        <select id="gender" bind:value={gender} class="w-full px-4 py-2 rounded-2xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500">
          <option value="">Pilih</option>
          <option value="Laki-laki">Laki-laki</option>
          <option value="Perempuan">Perempuan</option>
        </select>
      </div>

      <div class="flex gap-2">
        <!-- Password -->
        <div class="w-full relative">
          <label class="block text-sm font-medium text-gray-700" for="password">Kata Sandi</label>
          <input
            id="password"
            bind:value={password}
            type={showPassword ? 'text' : 'password'}
            class="w-full px-4 py-2 pr-10 rounded-2xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          <button type="button" on:click={() => (showPassword = !showPassword)} class="absolute right-3 top-[30px] text-gray-500">
            {#if showPassword}
              <EyeOff size="20" />
            {:else}
              <Eye size="20" />
            {/if}
          </button>
        </div>

        <!-- Confirm Password -->
        <div class="w-full relative">
          <label class="block text-sm font-medium text-gray-700" for="confirm">Konfirmasi Kata Sandi</label>
          <input
            id="confirm"
            bind:value={confirmPassword}
            type={showConfirm ? 'text' : 'password'}
            class="w-full px-4 py-2 pr-10 rounded-2xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          <button type="button" on:click={() => (showConfirm = !showConfirm)} class="absolute right-3 top-[30px] text-gray-500">
            {#if showConfirm}
              <EyeOff size="20" />
            {:else}
              <Eye size="20" />
            {/if}
          </button>
        </div>
      </div>

      {#if errorMessage}
        <p class="text-red-600 text-sm">{errorMessage}</p>
      {/if}
      {#if successMessage}
        <p class="text-green-600 text-sm">
          {successMessage}
          <a href="/login" class="text-sm text-primary hover:underline">Login di sini</a>
        </p>
      {/if}

      <!-- Submit -->
      <div class="text-end pt-2">
        <button type="submit" class="bg-primary hover:bg-hover text-white font-semibold py-2 px-6 rounded-2xl">Registrasi</button>
      </div>
    </form>
  </div>
</div>
