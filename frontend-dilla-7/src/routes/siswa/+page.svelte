<script lang="ts">
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'
  import { getAllKelas } from '$lib/api/kelas'
  import type { Kelas } from '$lib/types/kelas'

  let isLoading = true
  let error: string | null = null

  onMount(async () => {
    try {
      // Get user data
      const userData = localStorage.getItem('user')
      if (!userData) {
        goto('/login')
        return
      }

      const user = JSON.parse(userData)
      
      // Get siswa's kelas
      const kelasList = await getAllKelas()
      
      if (kelasList.length > 0) {
        // Redirect to siswa's kelas page
        goto(`/siswa/${kelasList[0].id}`)
      } else {
        error = 'Anda belum terdaftar di kelas manapun'
      }
    } catch (err) {
      console.error('Error:', err)
      error = 'Gagal memuat data kelas'
    } finally {
      isLoading = false
    }
  })
</script>

<div class="min-h-screen bg-gray-50 flex items-center justify-center">
  {#if isLoading}
    <div class="text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500 mx-auto"></div>
      <p class="mt-4 text-gray-600">Memuat data siswa...</p>
    </div>
  {:else if error}
    <div class="text-center">
      <div class="text-red-500 text-lg font-medium">{error}</div>
      <p class="mt-2 text-gray-600">Silakan hubungi guru Anda</p>
      <button 
        on:click={() => goto('/login')} 
        class="mt-4 bg-purple-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600"
      >
        Kembali ke Login
      </button>
    </div>
  {/if}
</div> 