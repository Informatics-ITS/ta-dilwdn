<script lang="ts">
  import { ChevronDown, Search, FileDown, FileText, FileSpreadsheet, ChevronsLeft, ChevronLeft, ChevronRight, ChevronsRight } from 'lucide-svelte'
  import { getAllLaporan } from '$lib/api/laporan'
  import { getAllSiswa } from '$lib/api/siswa'
  import { getAllUjian } from '$lib/api/ujian'
  import { getAllKelas } from '$lib/api/kelas'
  import type { Laporan } from '$lib/types/laporan'
  import type { Siswa } from '$lib/types/siswa'
  import type { Ujian } from '$lib/types/ujian'
  import type { Kelas } from '$lib/types/kelas'
  import { onMount } from 'svelte'
  import type { User } from '$lib/types/user'
  import { writable } from 'svelte/store'

  let laporanList: Laporan[] = []
  let siswaList: Siswa[] = []
  const user = writable<User>({
    id: 0,
    nama_lengkap: '',
    email: '',
    jenis_kelamin: '',
    password: ''
  })

  let currentUserEmail = ''; // Store the email separately

  let ujianList: Ujian[] = []
  let kelasList: Kelas[] = []

  let selectedUjianId: number | null = null
  let selectedKelasId: number | null = null
  let searchTerm = ''
  let showFilterMenu: 'kelas' | 'ujian' | null = null

  // Get data
  async function getData() {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        user.set(parsedUser);
        currentUserEmail = parsedUser.email; // Store the email
      } catch (e) {
        console.error('Gagal parse data user dari localStorage', e)
      }
    }

    const [laporan, siswa, ujian, kelas] = await Promise.all([getAllLaporan(), getAllSiswa(), getAllUjian(), getAllKelas()])

    siswaList = siswa
    ujianList = ujian
    kelasList = kelas
    
    // Find the current student based on email (assuming email is NISN)
    const currentSiswa = siswa.find((s) => s.NISN === currentUserEmail)

    // Filter laporanList to only show reports for the current student
    laporanList = laporan
      .filter(lap => currentSiswa ? lap.siswa === currentSiswa.no : false)
      .map((lap) => {
        const siswaData = siswa.find((s) => s.no === lap.siswa)
        const kelasData = kelas.find((k) => k.id === siswaData?.kelas)
        const ujianData = ujian.find((u) => u.id === lap.ujian)

        return {
          ...lap,
          nama_siswa: siswaData?.nama_siswa ?? 'Tidak ditemukan',
          nama_ujian: ujianData?.nama_ujian ?? 'Tidak ditemukan',
          nama_kelas: kelasData?.nama ?? '-',
          pelaksanaan: ujianData?.pelaksanaan ?? '-',
          kelas_id: kelasData?.id ?? 0,
          nama: kelasData?.nama ?? 'Tidak ditemukan'
        }
      })
  }
  onMount(getData)

  // Pagination
  let currentPage = 1
  const itemsPerPage = 10
  function goToPage(page: number) {
    if (page < 1 || page > totalPages) return
    currentPage = page
  }
  $: filteredList = laporanList
    .filter((item) => item.deskripsi_analisis.toLowerCase().includes(searchTerm.toLowerCase()) || item.nama_siswa.toLowerCase().includes(searchTerm.toLowerCase()))
    .filter((item) => (selectedUjianId ? item.ujian === selectedUjianId : true))
    .filter((item) => (selectedKelasId ? item.kelas_id === selectedKelasId : true))
  $: totalItems = filteredList.length
  $: totalPages = Math.ceil(totalItems / itemsPerPage)
  $: startItem = (currentPage - 1) * itemsPerPage + 1
  $: endItem = Math.min(currentPage * itemsPerPage, totalItems)
  $: paginatedRows = filteredList.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)

  // Date Format
  function formatTanggal(tanggal?: string | Date | null): string {
    if (!tanggal) return '-';
    
    const options: Intl.DateTimeFormatOptions = {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    };
    
    try {
      const date = new Date(tanggal);
      return isNaN(date.getTime()) ? '-' : date.toLocaleDateString('id-ID', options);
    } catch {
      return '-';
    }
  }
</script>

<div class="p-4">
  <div class="flex flex-col gap-2 mb-4">
    <!-- Header Area -->
    <div class="text-center">
      <div class="text-2xl font-bold">Ujian Matematika</div>
    </div>

    <div class="flex justify-between items-center mt-10">
      <!-- Filter Kelas -->
      <div class="relative">
        <button
          class="bg-primary hover:bg-hover text-white px-4 py-2 rounded-lg text-sm flex items-center gap-1"
          on:click={() => (showFilterMenu = showFilterMenu === 'kelas' ? null : 'kelas')}
          type="button"
        >
          {selectedKelasId === null ? 'Semua Kelas' : (kelasList.find((k) => k.id === selectedKelasId)?.nama ?? 'Tidak Dikenal')}
          <ChevronDown class="w-4 h-4" />
        </button>

        {#if showFilterMenu === 'kelas'}
          <div class="absolute z-10 mt-2 bg-white border rounded shadow-md w-64 max-h-60 overflow-y-auto">
            <button
              class="w-full text-left p-2 hover:bg-purple-100"
              on:click={() => {
                selectedKelasId = null
                showFilterMenu = null
              }}
            >
              Semua Kelas
            </button>
            {#each kelasList as kelas}
              <button
                class="w-full text-left p-2 hover:bg-purple-100"
                on:click={() => {
                  selectedKelasId = kelas.id
                  showFilterMenu = null
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
          class="pl-10 pr-4 py-2 rounded-full border border-gray-300 text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary"
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
          <th class="px-4 py-3">Nama</th>
          <th class="px-4 py-3 text-center">Kelas</th>
          <th class="px-4 py-3 text-center">Pelaksanaaan</th>
          <th class="px-4 py-3 text-center">Nilai</th>
        </tr>
      </thead>
      <tbody>
        {#each paginatedRows as row, i}
          <tr class={i % 2 === 0 ? 'bg-white' : 'bg-columntable'}>
            <td class="px-4 py-3 text-sm">{(currentPage - 1) * itemsPerPage + i + 1}</td>
            <td class="px-4 py-3 text-sm">{row.nama_ujian}</td>
            <td class="px-4 py-3 text-sm text-center">{row.nama_kelas}</td>
            <td class="px-4 py-3 text-sm text-center">{formatTanggal(row.pelaksanaan)}</td>
            <td class="px-4 py-3 text-center font-bold">{row.nilai}</td>
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
