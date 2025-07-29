<script lang="ts">
  import { ChevronDown, ChevronUp } from 'lucide-svelte'
  import { onMount } from 'svelte'
  import { page } from '$app/stores'
  import { getKelasById } from '$lib/api/kelas'
  import { getAllSiswa } from '$lib/api/siswa'
  import { getAllUjian } from '$lib/api/ujian'
  import { getAllLaporan } from '$lib/api/laporan'
  import { getAllSoal } from '$lib/api/soal'
  import { getAllJawabanSiswa } from '$lib/api/jawaban-siswa'
  import type { Siswa } from '$lib/types/siswa'
  import type { Ujian } from '$lib/types/ujian'
  import type { Laporan } from '$lib/types/laporan'
  import type { Soal } from '$lib/types/soal'
  import type { JawabanSiswa } from '$lib/types/jawaban-siswa'
  import BarChart from '$lib/components/BarChart.svelte'
  import PieChart from '$lib/components/PieChart.svelte'
  import LineChart from '$lib/components/LineChart.svelte'

  let kelasId: number
  let siswaList: Siswa[] = []
  let ujianList: Ujian[] = []
  let laporanList: Laporan[] = []
  let soalList: Soal[] = []
  let jawabanSiswaList: JawabanSiswa[] = []
  let loading = true

  // Nilai Siswa
  let allNilaiSiswa: { name: string; threePointers: number; ujianId: number }[] = []
  let showNilaiSiswaFilter = false
  let sortOrder: 'desc' | 'asc' = 'desc'
  let selectedNilaiUjianId: number | null = null

  // Capaian
  let showCapaianFilter = false
  let selectedCapaianUjianId: number | null = null
  const passingGrade = 70

  // Kesalahan Terbanyak
  let selectedKesalahanUjianId: number | null = null
  let showKesalahanFilter = false

  onMount(async () => {
    const unsubscribe = page.subscribe(($page) => {
      kelasId = Number($page.params.id)
    })

    const [kelas, semuaSiswa, semuaUjian, semuaLaporan, semuaSoal, semuaJawaban] = await Promise.all([
      getKelasById(kelasId),
      getAllSiswa(),
      getAllUjian(),
      getAllLaporan(),
      getAllSoal(),
      getAllJawabanSiswa()
    ])

    siswaList = semuaSiswa.filter((s) => s.kelas === kelas.id)
    ujianList = semuaUjian
    laporanList = semuaLaporan.filter((l) => siswaList.some((s) => s.no === l.siswa))
    soalList = semuaSoal
    jawabanSiswaList = semuaJawaban

    // Nilai Siswa
    allNilaiSiswa = laporanList.map((l) => ({
      name: siswaList.find((s) => s.no === l.siswa)?.nama_siswa ?? 'Tidak diketahui',
      threePointers: l.nilai,
      ujianId: l.ujian
    }))

    // Kesalahan Terbanyak
    if (ujianList.length > 0) {
      selectedKesalahanUjianId = ujianList[0].id
    }

    loading = false
    unsubscribe()
  })

  // Nilai Siswa
  function handleSortChange() {
    sortOrder = sortOrder === 'desc' ? 'asc' : 'desc'
  }

  function handleNilaiSiswaFilter(id: number | null) {
    selectedNilaiUjianId = id
    showNilaiSiswaFilter = false
  }

  $: filteredNilaiSiswa = allNilaiSiswa
    .filter((n) => selectedNilaiUjianId === null || n.ujianId === selectedNilaiUjianId)
    .sort((a, b) => (sortOrder === 'desc' ? b.threePointers - a.threePointers : a.threePointers - b.threePointers))

  // Capaian
  function handleCapaianFilter(id: number | null) {
    selectedCapaianUjianId = id
    showCapaianFilter = false
  }

  $: filteredCapaian = (() => {
    const filtered = laporanList.filter((l) => selectedCapaianUjianId === null || l.ujian === selectedCapaianUjianId)
    const lulus = filtered.filter((l) => l.nilai >= passingGrade).length
    const tidakLulus = filtered.length - lulus
    return [
      { name: 'Lulus', value: lulus },
      { name: 'Tidak Lulus', value: tidakLulus }
    ]
  })()

  // Kesalahan Terbanyak
  function handleKesalahanFilter(id: number) {
    selectedKesalahanUjianId = id
    showKesalahanFilter = false
  }

  $: filteredKesalahan = (() => {
    const hasil: { nomor: string; totalKesalahan: number }[] = []
    const soalFiltered = soalList.filter((s) => s.ujian === selectedKesalahanUjianId)

    soalFiltered.forEach((soal, index) => {
      const jawabanSiswa = jawabanSiswaList.filter((j) => j.soal === soal.id)
      let salah = 0
      jawabanSiswa.forEach((j) => {
        if (soal.json_result?.jawaban !== j.json_result?.jawaban) salah++
      })
      hasil.push({ nomor: `Nomor ${index + 1}`, totalKesalahan: salah })
    })

    return hasil
  })()
</script>

<!-- UI -->
<div class="p-4 min-h-screen">
  <!-- Kesalahan Terbanyak -->
  <div class="bg-white rounded-xl shadow p-5 my-4">
    <div class="flex justify-between items-center flex-wrap">
      <div class="text-md font-bold">Kesalahan Terbanyak</div>
      <div class="relative">
        <button class="bg-primary hover:bg-hover text-white p-2 rounded-xl flex items-center text-xs" on:click={() => (showKesalahanFilter = !showKesalahanFilter)}>
          {ujianList.find((u) => u.id === selectedKesalahanUjianId)?.nama_ujian ?? 'Pilih Ujian'}
          <ChevronDown class="w-4 h-4 ml-1" />
        </button>

        {#if showKesalahanFilter}
          <div class="absolute z-10 mt-2 bg-white border rounded shadow-md w-64 max-h-60 overflow-y-auto">
            {#each ujianList as option}
              <button class="w-full text-left px-4 py-2 hover:bg-purple-100" on:click={() => handleKesalahanFilter(option.id)}>
                {option.nama_ujian}
              </button>
            {/each}
          </div>
        {/if}
      </div>
    </div>

    <LineChart {filteredKesalahan} />
  </div>

  <!-- Bar Chart & Pie Chart -->
  <div class="w-full flex flex-col lg:flex-row justify-center gap-4">
    <!-- Nilai Siswa -->
    <div class="w-full bg-white rounded-xl shadow p-5">
      <div class="flex justify-between flex-wrap items-center mb-2">
        <div class="text-md font-bold">Nilai Siswa</div>
        <div class="flex flex-wrap gap-2 mt-2 lg:mt-0">
          <button class="bg-primary hover:bg-hover text-white p-2 rounded-xl flex items-center text-xs" on:click={handleSortChange}>
            {sortOrder === 'desc' ? 'Tertinggi' : 'Terendah'}
            {#if sortOrder === 'desc'}
              <ChevronUp class="w-4 h-4 ml-1" />
            {:else}
              <ChevronDown class="w-4 h-4 ml-1" />
            {/if}
          </button>

          <div class="relative">
            <button class="bg-primary hover:bg-hover text-white p-2 rounded-xl flex items-center text-xs" on:click={() => (showNilaiSiswaFilter = !showNilaiSiswaFilter)}>
              {selectedNilaiUjianId === null ? 'Semua Ujian' : (ujianList.find((u) => u.id === selectedNilaiUjianId)?.nama_ujian ?? 'Ujian')}
              <ChevronDown class="w-4 h-4 ml-1" />
            </button>
            {#if showNilaiSiswaFilter}
              <div class="absolute z-10 mt-2 bg-white border rounded shadow-md w-64 max-h-60 overflow-y-auto">
                <button class="w-full text-left px-4 py-2 hover:bg-purple-100" on:click={() => handleNilaiSiswaFilter(null)}>Semua Ujian</button>
                {#each ujianList as option}
                  <button class="w-full text-left px-4 py-2 hover:bg-purple-100" on:click={() => handleNilaiSiswaFilter(option.id)}>
                    {option.nama_ujian}
                  </button>
                {/each}
              </div>
            {/if}
          </div>
        </div>
      </div>
      <BarChart players={filteredNilaiSiswa} />
    </div>

    <!-- Capaian -->
    <div class="w-full bg-white rounded-xl shadow p-5">
      <div class="flex justify-between flex-wrap items-center mb-2">
        <div class="text-md font-bold">Capaian</div>
        <div class="relative">
          <button class="bg-primary hover:bg-hover text-white p-2 rounded-xl flex items-center text-xs" on:click={() => (showCapaianFilter = !showCapaianFilter)}>
            {selectedCapaianUjianId === null ? 'Semua Ujian' : (ujianList.find((u) => u.id === selectedCapaianUjianId)?.nama_ujian ?? 'Ujian')}
            <ChevronDown class="w-4 h-4 ml-1" />
          </button>
          {#if showCapaianFilter}
            <div class="absolute z-10 mt-2 bg-white border rounded shadow-md w-64 max-h-60 overflow-y-auto">
              <button class="w-full text-left px-4 py-2 hover:bg-purple-100" on:click={() => handleCapaianFilter(null)}>Semua Ujian</button>
              {#each ujianList as option}
                <button class="w-full text-left px-4 py-2 hover:bg-purple-100" on:click={() => handleCapaianFilter(option.id)}>
                  {option.nama_ujian}
                </button>
              {/each}
            </div>
          {/if}
        </div>
      </div>
      <PieChart data={filteredCapaian} />
    </div>
  </div>
</div>
