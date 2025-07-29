<script lang="ts">
  import { getAllKelas } from '$lib/api/kelas'
  import { getAllSiswa } from '$lib/api/siswa'
  import type { Kelas } from '$lib/types/kelas'
  import type { Siswa } from '$lib/types/siswa'
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'

  let kelasList: Kelas[] = []
  let siswaList: Siswa[] = []
  let kelasColors: Record<number, { border: string; text: string; bg: string }> = {}

  // Color
  const warnaOptions = [
    { border: 'border-red-500', text: 'text-red-500', bg: 'bg-red-500' },
    { border: 'border-green-500', text: 'text-green-500', bg: 'bg-green-500' },
    { border: 'border-blue-500', text: 'text-blue-500', bg: 'bg-blue-500' },
    { border: 'border-purple-500', text: 'text-purple-500', bg: 'bg-purple-500' },
    { border: 'border-pink-500', text: 'text-pink-500', bg: 'bg-pink-500' }
  ]
  function getRandomWarna() {
    return warnaOptions[Math.floor(Math.random() * warnaOptions.length)]
  }
  function getColorForKelas(id: number) {
    if (!kelasColors[id]) {
      kelasColors[id] = getRandomWarna()
    }
    return kelasColors[id]
  }

  // Get data
  async function getData() {
    const [kelas, siswa] = await Promise.all([getAllKelas(), getAllSiswa()])
    kelasList = kelas
    siswaList = siswa
  }
  onMount(getData)

  // Siswa
  function getJumlahSiswa(kelasId: number) {
    return siswaList.filter((s) => s.kelas === kelasId).length
  }
</script>

<div class="min-h-screen bg-gray-50 p-6">
  <!-- Header -->
  <div class="text-center mb-10">
    <h1 class="text-2xl font-bold text-gray-800">Pilih Kelas</h1>
    <p class="text-sm text-gray-600 mt-1">Pilih kelas yang ingin kamu analisis</p>
  </div>

  <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3 gap-10 max-w-6xl mx-auto">
    {#each kelasList as kelas}
      <button class={`cursor-pointer bg-white rounded-xl shadow-sm relative overflow-hidden border ${getColorForKelas(kelas.id).border}`} on:click={() => goto(`/dashboard/analisis/${kelas.id}`)}>
        <div class="px-8 py-4 flex items-center justify-between">
          <!-- Nama -->
          <p class={`font-medium text-base ${getColorForKelas(kelas.id).text}`}>{kelas.nama}</p>

          <!-- Badge siswa -->
          <div class={`rounded-full w-20 h-20 my-1 flex flex-col items-center justify-center text-xs font-medium border ${getColorForKelas(kelas.id).border} ${getColorForKelas(kelas.id).text}`}>
            <div class="text-lg leading-none">{getJumlahSiswa(kelas.id)}</div>
            <div class="mt-0.5">siswa</div>
          </div>
        </div>
      </button>
    {/each}
  </div>
</div>
