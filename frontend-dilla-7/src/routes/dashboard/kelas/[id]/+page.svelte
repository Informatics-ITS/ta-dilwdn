<script lang="ts">
  import { Search, Plus, Edit, Trash2, ChevronsLeft, ChevronLeft, ChevronRight, ChevronsRight } from 'lucide-svelte'
  import { page } from '$app/stores'
  import { getAllSiswa, uploadSiswa, deleteSiswa } from '$lib/api/siswa'
  import { getKelasById } from '$lib/api/kelas'
  import type { Siswa, SiswaUpload } from '$lib/types/siswa'
  import type { Kelas } from '$lib/types/kelas'
  import { onMount } from 'svelte'
  import SiswaModal from '$lib/components/SiswaModal.svelte'
  import ConfirmDeleteModal from '$lib/components/ConfirmDeleteModal.svelte'

  let siswaList: Siswa[] = []
  let kelas: Kelas | null = null
  let kelasId: number
  let searchTerm = ''
  let showModal = false
  let isEdit = false
  let showDeleteModal = false
  let deleteId: number | null = null
  let selectedData: Siswa = { no: 0, nama_siswa: '', kelas: 0, NISN: '', password: '' }
  let fileInput: HTMLInputElement
  let isUploading = false
  let uploadMessage = ''

  // Get data
  async function getData() {
    const allSiswa = await getAllSiswa()
    siswaList = allSiswa.filter((s) => s.kelas === kelasId)

    kelas = await getKelasById(kelasId)
  }
  onMount(async () => {
    const unsubscribe = page.subscribe(($page) => {
      kelasId = Number($page.params.id)
    })

    await getData()
    unsubscribe()
  })

  // Create
  function getNewId() {
    if (siswaList.length === 0) return 1
    return Math.max(...siswaList.map((k) => k.no)) + 1
  }
  function openCreate() {
    isEdit = false
    selectedData = { no: getNewId(), nama_siswa: '', kelas: kelasId, NISN: '', password: '' }
    showModal = true
  }

  // Upload
  function handleUpload() {
    fileInput?.click()
  }

  async function handleFileSelected(event: Event) {
    const target = event.target as HTMLInputElement
    const file = target.files?.[0]
    if (!file) return

    isUploading = true
    uploadMessage = ''

    try {
      // Create object matching SiswaUpload type
      const uploadData: SiswaUpload = {
        file: file // Assuming SiswaUpload expects a File object
      }

      await uploadSiswa(uploadData)
      uploadMessage = '✅ Upload berhasil!'
      await getData() // Refresh data siswa
    } catch (error) {
      console.error(error)
      uploadMessage = '❌ Upload gagal!'
    } finally {
      isUploading = false
      target.value = '' // Reset file input
    }
  }

  // Edit
  function openEdit(siswa: Siswa) {
    isEdit = true
    selectedData = siswa
    showModal = true
  }

  // Delete
  function openDelete(no: number) {
    deleteId = no
    showDeleteModal = true
  }
  async function confirmDelete() {
    if (deleteId !== null) {
      await deleteSiswa(deleteId)
      await getData()
      deleteId = null
    }
  }

  // Pagination
  let currentPage = 1
  const itemsPerPage = 10
  function goToPage(page: number) {
    if (page < 1 || page > totalPages) return
    currentPage = page
  }
  $: filteredList = siswaList.filter((item) => item.nama_siswa.toLowerCase().includes(searchTerm.toLowerCase()))
  $: totalItems = filteredList.length
  $: totalPages = Math.ceil(totalItems / itemsPerPage)
  $: startItem = (currentPage - 1) * itemsPerPage + 1
  $: endItem = Math.min(currentPage * itemsPerPage, totalItems)
  $: paginatedRows = filteredList.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)
</script>

<!-- Modal -->
<SiswaModal bind:show={showModal} {isEdit} data={selectedData} on:refresh={getData} />
<ConfirmDeleteModal bind:show={showDeleteModal} on:confirm={confirmDelete} on:cancel={() => (showDeleteModal = false)} />

<div class="p-4">
  <!-- Header Area -->
  <div class="flex flex-col gap-2 mb-4">
    <div class="text-2xl font-bold">Data Siswa {kelas ? kelas.nama : 'Memuat...'}</div>

    <div class="flex justify-between items-center mt-10">
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

      <div class="flex justify-center gap-4">
        <!-- Upload -->
        <button on:click={handleUpload} class="bg-primary hover:bg-hover text-white px-6 py-3 rounded-lg text-sm flex items-center gap-1 disabled:opacity-50" disabled={isUploading}>
          <Plus class="w-4 h-4" />
          {#if isUploading}
            Uploading...
          {:else}
            Upload Excel
          {/if}
        </button>
        <input type="file" accept=".xlsx, .xls" bind:this={fileInput} on:change={handleFileSelected} class="hidden" />

        <!-- Create -->
        <button on:click={openCreate} class="bg-primary hover:bg-hover text-white px-6 py-3 rounded-lg text-sm flex items-center gap-1">
          <Plus class="w-4 h-4" />
          Tambah Siswa
        </button>
      </div>
    </div>
  </div>

  {#if uploadMessage}
    <div class="text-sm mt-2 {uploadMessage.includes('berhasil') ? 'text-green-600' : 'text-red-600'}">
      {uploadMessage}
    </div>
  {/if}

  <!-- Table -->
  <div class="overflow-auto shadow-lg">
    <table class="w-full border-collapse overflow-hidden">
      <thead class="bg-secondary text-dark text-left text-sm">
        <tr>
          <th class="px-4 py-3">No</th>
          <th class="px-4 py-3">Nama Siswa</th>
          <th class="px-4 py-3 text-center">NISN</th>
          <th class="px-4 py-3 text-center">Password</th>
          <th class="px-4 py-3 text-center">Aksi</th>
        </tr>
      </thead>
      <tbody>
        {#each paginatedRows as row, i}
          <tr class={i % 2 === 0 ? 'bg-white' : 'bg-columntable'}>
            <td class="px-4 py-3 text-sm">{(currentPage - 1) * itemsPerPage + i + 1}</td>
            <td class="px-4 py-3 text-sm">{row.nama_siswa}</td>
            <td class="px-4 py-3 text-sm text-center">{row.NISN}</td>
            <td class="px-4 py-3 text-sm text-center">{row.NISN}</td>
            <td class="px-4 py-3 text-center space-x-2">
              <!-- Edit -->
              <button on:click={() => openEdit(row)} class="inline-flex items-center justify-center rounded-full hover:bg-blue-100 text-blue-600" aria-label="Detail">
                <Edit class="w-4 h-4" />
              </button>

              <!-- Delete -->
              <button on:click={() => openDelete(row.no)} class="inline-flex items-center justify-center rounded-full hover:bg-red-100 text-red-600" aria-label="Hapus">
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
