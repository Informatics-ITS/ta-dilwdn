<script lang="ts">
  import { ChevronDown, Search, FileDown, FileText, FileSpreadsheet, Plus, Edit, Trash2, ChevronsLeft, ChevronLeft, ChevronRight, ChevronsRight } from 'lucide-svelte'
  import { getAllUjian, deleteUjian } from '$lib/api/ujian'
  import { getAllKelas } from '$lib/api/kelas'
  import type { Ujian } from '$lib/types/ujian'
  import type { Kelas } from '$lib/types/kelas'
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'
  import UjianModal from '$lib/components/UjianModal.svelte'
  import ConfirmDeleteModal from '$lib/components/ConfirmDeleteModal.svelte'

  let ujianList: Ujian[] = []
  let kelasList: Kelas[] = []
  let selectedKelasId: number | null = null
  let searchTerm = ''
  let showFilterMenu = false
  let showModal = false
  let isEdit = false
  let showDeleteModal = false
  let deleteId: number | null = null
  let selectedData: Ujian = { id: 0, nama_ujian: '', kelas: 0, pelaksanaan: '', status: '' }

  // Get data
  async function getData() {
    ujianList = await getAllUjian()
    kelasList = await getAllKelas()
  }
  onMount(getData)

  function getNamaKelas(id: number): string {
    return kelasList.find((k) => k.id === id)?.nama || '-'
  }

  // Create
  function getNewId() {
    if (ujianList.length === 0) return 1
    return Math.max(...ujianList.map((k) => k.id)) + 1
  }
  function openCreate() {
    isEdit = false
    selectedData = { id: getNewId(), nama_ujian: '', kelas: 0, pelaksanaan: '', status: '' }
    showModal = true
  }

  // Edit
  function openEdit(ujian: Ujian) {
    isEdit = true
    selectedData = ujian
    showModal = true
  }

  // Delete
  function openDelete(id: number) {
    deleteId = id
    showDeleteModal = true
  }
  async function confirmDelete() {
    if (deleteId !== null) {
      await deleteUjian(deleteId)
      await getData()
      deleteId = null
    }
  }

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
</script>

<!-- Modal -->
<UjianModal bind:show={showModal} {isEdit} data={selectedData} on:refresh={getData} />
<ConfirmDeleteModal bind:show={showDeleteModal} on:confirm={confirmDelete} on:cancel={() => (showDeleteModal = false)} />

<div class="p-4">
  <!-- Header Area -->
  <div class="flex flex-col gap-2 mb-4">
    <div class="flex justify-between items-center">
      <div class="text-2xl font-bold">Ujian Matematika</div>

      <!-- Create -->
      <button on:click={openCreate} class="bg-primary hover:bg-hover text-white px-6 py-3 rounded-lg text-sm flex items-center gap-1">
        <Plus class="w-4 h-4" />
        Tambah Ujian
      </button>
    </div>

    <div class="flex justify-between items-center mt-10">
      <!-- Filter -->
      <div class="relative">
        <button class="bg-primary hover:bg-hover text-white px-5 py-2 rounded-lg flex items-center gap-2" on:click={() => (showFilterMenu = !showFilterMenu)} type="button">
          {selectedKelasId === null ? 'Semua Ujian' : getNamaKelas(selectedKelasId)}
          <ChevronDown class="w-4 h-4" />
        </button>

        {#if showFilterMenu}
          <div class="absolute z-10 mt-2 bg-white border rounded shadow-md w-64 max-h-60 overflow-y-auto">
            <button
              type="button"
              class="w-full text-left p-2 hover:bg-purple-100 cursor-pointer"
              on:click={() => {
                selectedKelasId = null
                showFilterMenu = false
              }}
            >
              Semua Ujian
            </button>

            {#each kelasList as kelas}
              <button
                type="button"
                class="w-full text-left p-2 hover:bg-purple-100 cursor-pointer"
                on:click={() => {
                  selectedKelasId = kelas.id
                  showFilterMenu = false
                }}
              >
                {kelas.nama}
              </button>
            {/each}
          </div>
        {/if}
      </div>

      <!-- Search -->
      <div class="relative">
        <Search class="absolute left-2 top-1/2 -translate-y-1/2 w-4 h-4 text-primary" />
        <input
          type="text"
          bind:value={searchTerm}
          placeholder="Search..."
          class="w-full pl-10 pr-4 py-2 rounded-full border border-gray-300 text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary"
        />
      </div>
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
          <th class="px-4 py-3 text-center">Aksi</th>
        </tr>
      </thead>
      <tbody>
        {#each paginatedRows as row, i}
          <tr on:click={() => goto(`ujian/${row.id}`)} class={i % 2 === 0 ? 'bg-white px-4 py-3 cursor-pointer' : 'bg-columntable px-4 py-3 cursor-pointer'}>
            <td class="px-4 py-3 text-sm">{(currentPage - 1) * itemsPerPage + i + 1}</td>
            <td class="px-4 py-3 text-sm">{row.nama_ujian}</td>
            <td class="px-4 py-3 text-sm text-center">{getNamaKelas(row.kelas)}</td>
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
            <td class="px-4 py-3 text-center space-x-2">
              <!-- Edit -->
              <button on:click|stopPropagation={() => openEdit(row)} class="inline-flex items-center justify-center rounded-full hover:bg-blue-100 text-blue-600" aria-label="Detail">
                <Edit class="w-4 h-4" />
              </button>

              <!-- Delete -->
              <button on:click|stopPropagation={() => openDelete(row.id)} class="inline-flex items-center justify-center rounded-full hover:bg-red-100 text-red-600" aria-label="Hapus">
                <Trash2 class="w-4 h-4" />
              </button>
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
