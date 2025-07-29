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
  import * as XLSX from 'xlsx'
  import jsPDF from 'jspdf'
  import autoTable from 'jspdf-autotable'

  let laporanList: Laporan[] = []
  let siswaList: Siswa[] = []

  let ujianList: Ujian[] = []
  let kelasList: Kelas[] = []

  let selectedUjianId: number | null = null
  let selectedKelasId: number | null = null
  let searchTerm = ''
  let showFilterMenu: 'kelas' | 'ujian' | null = null

  // Get data
  async function getData() {
    const [laporan, siswa, ujian, kelas] = await Promise.all([getAllLaporan(), getAllSiswa(), getAllUjian(), getAllKelas()])

    siswaList = siswa
    ujianList = ujian
    kelasList = kelas

    laporanList = laporan.map((lap) => {
      const siswaData = siswa.find((s) => s.no === lap.siswa)
      const kelasData = kelas.find((k) => k.id === siswaData?.kelas)
      const ujianData = ujian.find((u) => u.id === lap.ujian)

      return {
        ...lap,
        nama_siswa: siswaData?.nama_siswa ?? 'Tidak ditemukan',
        nama_ujian: ujianData?.nama_ujian ?? 'Tidak ditemukan',
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

  // Export
  function exportCSV() {
    const header = ['No', 'Nama Siswa', 'Deskripsi Analisis', 'Nilai']
    const rows = laporanList.map((lap, i) => [i + 1, lap.nama_siswa, lap.deskripsi_analisis, lap.nilai])
    const csvContent = 'data:text/csv;charset=utf-8,' + [header, ...rows].map((e) => e.join(',')).join('\n')
    const encodedUri = encodeURI(csvContent)
    const link = document.createElement('a')
    link.setAttribute('href', encodedUri)
    link.setAttribute('download', 'laporan.csv')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  function exportPDF() {
    const doc = new jsPDF()
    doc.text('Laporan Nilai', 14, 10)
    autoTable(doc, {
      head: [['No', 'Nama Siswa', 'Deskripsi Analisis', 'Nilai']],
      body: laporanList.map((lap, i) => [i + 1, lap.nama_siswa, lap.deskripsi_analisis, lap.nilai])
    })
    doc.save('laporan.pdf')
  }

  function exportExcel() {
    const worksheet = XLSX.utils.json_to_sheet(
      laporanList.map((lap, i) => ({
        No: i + 1,
        Nama: lap.nama_siswa,
        Deskripsi: lap.deskripsi_analisis,
        Nilai: lap.nilai
      }))
    )
    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Laporan')
    XLSX.writeFile(workbook, 'laporan.xlsx')
  }

  let showExportMenu = false
  let exportOptions = [
    { label: 'Comma Separated Values (.csv)', icon: FileDown },
    { label: 'PDF (.pdf)', icon: FileText },
    { label: 'Microsoft Excel (.xlsx)', icon: FileSpreadsheet }
  ]
  function handleExport(label: string) {
    showExportMenu = false
    if (label.includes('.csv')) {
      exportCSV()
    } else if (label.includes('.pdf')) {
      exportPDF()
    } else if (label.includes('.xlsx')) {
      exportExcel()
    }
  }

  // --- Dynamic text formatting for recommendationText ---
  let recommendationText = `Menerapkan algoritma perhitungan yang sesuai untuk soal tersebut. **Rekomendasi Pembelajaran:** Guru perlu melakukan asesmen lebih lanjut untuk mengidentifikasi secara spesifik kesulitan yang dialami siswa pada Soal 3. Beberapa kemungkinan penyebab kesulitan antara lain: * **Kesulitan Memahami Soal:**`

  function formatText(text: string): string {
    // 1. Replace '**text**' with '<strong>text</strong>'
    let formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')

    // 2. Process for bullet points and paragraphs
    const lines = formatted.split('\n')
    let inList = false
    let resultHtml = []

    lines.forEach((line) => {
      if (line.trim().startsWith('* ')) {
        if (!inList) {
          resultHtml.push('<ul>')
          inList = true
        }
        resultHtml.push(`<li>${line.trim().substring(2).trim()}</li>`)
      } else {
        if (inList) {
          resultHtml.push('</ul>')
          inList = false
        }
        if (line.trim().length > 0) {
          // Wrap non-list, non-empty lines in paragraphs
          resultHtml.push(`<p>${line.trim()}</p>`)
        }
      }
    })

    if (inList) {
      resultHtml.push('</ul>')
    }

    return resultHtml.join('\n')
  }

  $: formattedRecommendationHtml = formatText(recommendationText)
  // --- End Dynamic text formatting ---
</script>

<div class="p-4">
  <div class="mb-8">
    <div class="prose">
      {@html formattedRecommendationHtml}
    </div>
  </div>
  ---

  <div class="flex flex-col gap-2 mb-4">
    <div class="flex justify-end items-center">
      <div class="flex gap-2">
        <div class="relative">
          <button
            class="bg-primary hover:bg-hover text-white px-4 py-2 rounded-full text-sm flex items-center gap-1"
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

        <div class="relative">
          <button
            class="bg-primary hover:bg-hover text-white px-4 py-2 rounded-full text-sm flex items-center gap-1"
            on:click={() => (showFilterMenu = showFilterMenu === 'ujian' ? null : 'ujian')}
            type="button"
          >
            {selectedUjianId === null ? 'Semua Ujian' : (ujianList.find((u) => u.id === selectedUjianId)?.nama_ujian ?? 'Tidak Dikenal')}
            <ChevronDown class="w-4 h-4" />
          </button>

          {#if showFilterMenu === 'ujian'}
            <div class="absolute z-10 mt-2 bg-white border rounded shadow-md w-64 max-h-60 overflow-y-auto">
              <button
                class="w-full text-left p-2 hover:bg-purple-100"
                on:click={() => {
                  selectedUjianId = null
                  showFilterMenu = null
                }}
              >
                Semua Ujian
              </button>
              {#each ujianList as ujian}
                <button
                  class="w-full text-left p-2 hover:bg-purple-100"
                  on:click={() => {
                    selectedUjianId = ujian.id
                    showFilterMenu = null
                  }}
                >
                  {ujian.nama_ujian}
                </button>
              {/each}
            </div>
          {/if}
        </div>
      </div>
    </div>

    <div class="flex justify-between items-center mt-10">
      <div class="relative">
        <button class="bg-primary hover:bg-hover text-white px-4 py-4 rounded-2xl flex items-center gap-2" on:click={() => (showExportMenu = !showExportMenu)}>
          <FileDown class="w-4 h-4" />
          Download
          <ChevronDown class="w-4 h-4" />
        </button>

        {#if showExportMenu}
          <div class="absolute z-10 mt-2 bg-white border rounded shadow-md w-64">
            {#each exportOptions as option}
              <button class="w-full flex items-center gap-2 p-2 hover:bg-purple-100 cursor-pointer" on:click={() => handleExport(option.label)}>
                <svelte:component this={option.icon} class="w-4 h-4 text-primary" />
                <span class="text-left">{option.label}</span>
              </button>
            {/each}
          </div>
        {/if}
      </div>

      <div class="relative">
        <Search class="absolute left-2 top-1/2 -translate-y-1/2 w-4 h-4 text-primary" />
        <input type="text" bind:value={searchTerm} placeholder="Search..." class="pl-8 pr-3 py-2 rounded-lg bg-pink-100 text-sm text-purple-800 placeholder-purple-400 focus:outline-none" />
      </div>
    </div>
  </div>

  <div class="overflow-auto shadow-lg">
    <table class="w-full border-collapse overflow-hidden">
      <thead class="bg-secondary text-dark text-left text-sm">
        <tr>
          <th class="px-4 py-3">No</th>
          <th class="px-4 py-3">Nama</th>
          <th class="px-4 py-3">Deskripsi Analisis</th>
          <th class="px-4 py-3 text-center">Nilai</th>
          <th class="px-4 py-3 text-center">Aksi</th>
        </tr>
      </thead>
      <tbody>
        {#each paginatedRows as row, i}
          <tr class={i % 2 === 0 ? 'bg-white' : 'bg-columntable'}>
            <td class="px-4 py-3 text-sm">{(currentPage - 1) * itemsPerPage + i + 1}</td>
            <td class="px-4 py-3 text-sm">{row.nama_siswa}</td>
            <td class="px-4 py-3 text-sm">
              <pre
                class="whitespace-pre-wrap break-words overflow-hidden max-h-20 text-ellipsis cursor-pointer"
                on:click={(e) => e.currentTarget.classList.toggle('max-h-20')}>{row.deskripsi_analisis}</pre>
            </td>
            <td class="px-4 py-3 text-center font-bold">{row.nilai}</td>
            <td class="px-4 py-3 text-center">
              <div class="flex justify-center space-x-2">
                <a href={`/dashboard/laporan/${row.id}`} class="text-dark underline text-sm hover:text-hover">Detail</a>
              </div>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>

  <div class="flex justify-between items-center mt-4">
    <p class="text-sm text-gray-700">
      Tampilkan {startItem} - {endItem} dari {totalPages} halaman
    </p>

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

<style>
  /* Styling for the recommendation text section */
  .prose ul {
    list-style-type: disc; /* Ensures actual bullet points */
    padding-left: 1.5em;
  }

  .prose strong {
    font-weight: bold;
  }

  .prose p {
    margin-bottom: 0.5em; /* Add some spacing between paragraphs for the formatted text */
  }

  /* You might need to adjust these colors/styles based on your Tailwind config */
  .bg-primary {
    background-color: #6a0dad; /* Example purple color */
  }
  .hover\:bg-hover:hover {
    background-color: #8a2be2; /* Lighter purple on hover */
  }
  .bg-secondary {
    background-color: #e0b0ff; /* Example lighter purple for table header */
  }
  .text-dark {
    color: #333; /* Example dark text color */
  }
  .bg-pink-100 {
    background-color: #fce4ec; /* Example light pink for search input */
  }
  .text-purple-800 {
    color: #4a148c; /* Example dark purple text for search input */
  }
  .placeholder-purple-400::placeholder {
    color: #9c27b0; /* Example purple placeholder text */
  }
  .bg-columntable {
    background-color: #f7f7f7; /* Example light grey for alternating rows */
  }
  .hover\:text-hover:hover {
    color: #8a2be2; /* Lighter purple on hover for links */
  }
</style>
