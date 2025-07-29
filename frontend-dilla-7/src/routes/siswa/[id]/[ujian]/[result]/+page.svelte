<script lang="ts">
  import { onMount } from 'svelte'
  import { page } from '$app/stores'
  import { getLaporanById } from '$lib/api/laporan'
  import type { Laporan } from '$lib/types/laporan'

  let laporan: Laporan | null = null
  let isLoading = true
  let error: string | null = null
  let currentDateTime = ''

  onMount(async () => {
    try {
      // Get result ID from route params
      const resultId = Number($page.params.result)
      if (!resultId) throw new Error('ID hasil tidak valid')

      // Fetch laporan data
      laporan = await getLaporanById(resultId)

      // Set current date and time
      const now = new Date()
      currentDateTime = formatDateTime(now)
    } catch (err) {
      error = 'Gagal memuat hasil ujian'
      console.error(err)
    } finally {
      isLoading = false
    }
  })

  function formatDateTime(date: Date): string {
    const options: Intl.DateTimeFormatOptions = {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }
    return date.toLocaleDateString('id-ID', options)
  }

  function getNilaiLabel(nilai: number): string {
    if (nilai < 70) return 'Kurang'
    if (nilai <= 80) return 'Cukup'
    if (nilai <= 90) return 'Baik'
    return 'Sangat Baik'
  }
</script>

<div class="p-4 max-w-2xl mx-auto">
  <!-- Loading State -->
  {#if isLoading}
    <div class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500 mx-auto"></div>
      <p class="mt-4 text-gray-600">Memuat hasil ujian...</p>
    </div>

  <!-- Error State -->
  {:else if error}
    <div class="text-center py-12">
      <div class="text-red-500 text-lg font-medium">{error}</div>
      <p class="mt-2 text-gray-600">Silakan coba lagi nanti</p>
    </div>

  <!-- Success State -->
  {:else if laporan}
    <!-- Header Area -->
    <div class="text-center mb-8">
      <h1 class="text-2xl font-bold text-purple-700">Ujian Telah Diselesaikan!</h1>
      <p class="text-lg text-gray-600 mt-2">
        Terima kasih telah mengerjakan ujian. Berikut adalah hasil penilaian Anda.
      </p>
    </div>

    <!-- Results Table -->
    <div class="bg-white rounded-lg shadow-md overflow-hidden mb-6">
      <table class="w-full">
        <tbody>
          <tr class="border-b border-gray-200">
            <td class="px-6 py-4 font-medium text-gray-700">Selesai</td>
            <td class="px-6 py-4 text-right font-semibold">
              {laporan.nilai} dari 100
              <span class="ml-2 text-sm font-normal text-gray-500">
                ({getNilaiLabel(laporan.nilai)})
              </span>
            </td>
          </tr>
          <tr>
            <td class="px-6 py-4 font-medium text-gray-700">Dikirim</td>
            <td class="px-6 py-4 text-right text-gray-600">{currentDateTime}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Analysis Section -->
    <div class="bg-white rounded-lg shadow-md p-6">
      <h2 class="text-lg font-semibold text-purple-700 mb-3">Analisis Hasil</h2>
      <div class="bg-blue-50 rounded-lg p-4 text-sm text-gray-700">
        {laporan.deskripsi_analisis || 'Tidak ada analisis tambahan.'}
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="mt-8 flex justify-center space-x-4">
      <a
        href="/dashboard"
        class="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-lg transition"
      >
        Kembali ke Dashboard
      </a>
      <a
        href="/ujian"
        class="bg-white hover:bg-gray-100 text-purple-600 border border-purple-600 px-6 py-2 rounded-lg transition"
      >
        Lihat Ujian Lain
      </a>
    </div>

  <!-- No Data State -->
  {:else}
    <div class="text-center py-12">
      <p class="text-gray-600">Data hasil ujian tidak ditemukan</p>
    </div>
  {/if}
</div>