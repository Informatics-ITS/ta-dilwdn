<script lang="ts">
  import { Search, ChevronsLeft, ChevronLeft, ChevronRight, ChevronsRight } from 'lucide-svelte'
  import { page } from '$app/stores'
  import { getAllUjian } from '$lib/api/ujian'
  import { getAllKelas } from '$lib/api/kelas'
  import type { Ujian } from '$lib/types/ujian'
  import type { Kelas } from '$lib/types/kelas'
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'

  let ujianList: Ujian[] = []
  let kelasList: Kelas[] = []
  let selectedKelasId: number | null = Number($page.params.id)
  let searchTerm = ''

  // Get data
  async function getData() {
    ujianList = await getAllUjian()
    kelasList = await getAllKelas()
  }
  onMount(getData)

  // Status Color
  const statusMap = [
    { label: 'belum', bg: 'bg-red-300', text: 'text-red-800' },
    { label: 'proses', bg: 'bg-green-300', text: 'text-green-800' },
    { label: 'selesai', bg: 'bg-blue-300', text: 'text-blue-800' }
  ]
  function getStatusItem(label: string) {
    return statusMap.find((s) => s.label == label)
  }

  // Pagination
  let currentPage = 1
  const itemsPerPage = 10
  function goToPage(page: number) {
    if (page < 1 || page > totalPages) return
    currentPage = page
  }
  $: filteredList = ujianList.filter((item) => item.nama_ujian.toLowerCase().includes(searchTerm.toLowerCase())).filter((item) => (selectedKelasId ? item.kelas === selectedKelasId : true))
  $: totalItems = filteredList.length
  $: totalPages = Math.ceil(totalItems / itemsPerPage)
  $: startItem = (currentPage - 1) * itemsPerPage + 1
  $: endItem = Math.min(currentPage * itemsPerPage, totalItems)
  $: paginatedRows = filteredList.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)
  $: getNamaKelas = kelasList.find((k) => k.id === Number($page.params.id))?.nama || '-'
</script>

<div class="p-4">
  <!-- Header Area -->
  <div class="text-center">
    <div class="text-2xl font-bold">Ujian Matematika</div>
    <p class="text-lg text-gray-600 mt-1">{getNamaKelas}</p>
  </div>

  <!-- Search -->
  <div class="flex justify-end mb-5 mt-4">
    <div class="relative">
      <Search class="absolute left-2 top-1/2 -translate-y-1/2 w-4 h-4 text-primary" />
      <input
        type="text"
        bind:value={searchTerm}
        placeholder="Search..."
        class="pl-10 pr-4 py-2 rounded-full border border-gray-300 text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary"
      />
    </div>
  </div>

  <!-- Table -->
  <div class="overflow-auto shadow-lg">
    <table class="w-full border-collapse overflow-hidden">
      <thead class="bg-secondary text-dark text-left text-sm">
        <tr>
          <th class="px-4 py-3">No</th>
          <th class="px-4 py-3">Nama Ujian</th>
          <th class="px-4 py-3 text-center">Kelas</th>
          <th class="px-4 py-3 text-center">pelaksanaan</th>
          <th class="px-4 py-3 text-center">Status</th>
        </tr>
      </thead>
      <tbody>
        {#each paginatedRows as row, i}
          <tr on:click={() => goto(`/siswa/${row.kelas}/${row.id}`)} class={i % 2 === 0 ? 'bg-white px-4 py-3 cursor-pointer' : 'bg-columntable px-4 py-3 cursor-pointer'}>
            <td class="px-4 py-3 text-sm">{(currentPage - 1) * itemsPerPage + i + 1}</td>
            <td class="px-4 py-3 text-sm">{row.nama_ujian}</td>
            <td class="px-4 py-3 text-sm text-center">{getNamaKelas}</td>
            <td class="px-4 py-3 text-sm text-center">{row.pelaksanaan}</td>
            <td class="px-4 py-3 text-sm text-center">
              {#if getStatusItem(row.status)}
                <span class={`px-4 py-2 rounded-lg text-xs font-semibold ${getStatusItem(row.status)!.bg} ${getStatusItem(row.status)!.text}`}>
                  {getStatusItem(row.status)!.label}
                </span>
              {:else}
                <span class="px-4 py-2 rounded-lg text-xs font-semibold bg-gray-200 text-gray-800">Status Tidak Dikenal</span>
              {/if}
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>

  <!-- Pagination -->
  <div class="flex justify-between items-center mt-4">
    <!-- Info Pagination -->
    <p class="text-sm text-gray-700">
      Tampilkan {startItem} - {endItem} dari {totalPages} halaman
    </p>

    <!-- Pagination Controls -->
    <div class="flex items-center gap-1 text-white text-sm">
      <button on:click={() => goToPage(1)} class="bg-primary hover:bg-hover p-1 rounded">
        <ChevronsLeft class="w-4 h-4" />
      </button>
      <button on:click={() => goToPage(currentPage - 1)} class="bg-primary hover:bg-hover p-1 rounded">
        <ChevronLeft class="w-4 h-4" />
      </button>

      <span class="px-2 text-black">
        {currentPage} dari {totalPages}
      </span>

      <button on:click={() => goToPage(currentPage + 1)} class="bg-primary hover:bg-hover p-1 rounded">
        <ChevronRight class="w-4 h-4" />
      </button>
      <button on:click={() => goToPage(totalPages)} class="bg-primary hover:bg-hover p-1 rounded">
        <ChevronsRight class="w-4 h-4" />
      </button>
    </div>
  </div>
</div>
