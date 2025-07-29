<script lang="ts">
  import { onMount } from 'svelte'
  import { page } from '$app/stores'
  import { getLaporanById } from '$lib/api/laporan'
  import { getAllSoal } from '$lib/api/soal'
  import { getAllUjian } from '$lib/api/ujian'
  import { getAllSiswa } from '$lib/api/siswa'
  import { getAllJawabanSiswa } from '$lib/api/jawaban-siswa'
  import { compareAnswer } from '$lib/api/solve'
  import type { Soal } from '$lib/types/soal'
  import type { Ujian } from '$lib/types/ujian'
  import type { Siswa } from '$lib/types/siswa'
  import type { JawabanSiswa } from '$lib/types/jawaban-siswa'
  import type { Laporan } from '$lib/types/laporan'
  import type { JsonResult } from '$lib/types/solve'

  type AnalisisItem = {
    nomor: number
    analisis: string
    kunci: string
    jawaban: string
    benar: boolean
  }

  let hasil: Laporan | null = null
  let soalList: Soal[] = []
  let ujianList: Ujian[] = []
  let siswaList: Siswa[] = []
  let jawabanList: JawabanSiswa[] = []
  let analisis: AnalisisItem[] = []
  const laporanId = Number($page.params.id)

  // Format jawaban based on different question types
  function formatJawaban(data: any | undefined | null): string {
    if (!data) return '-'
    
    try {
      // For math questions
      if (data.angka_dalam_soal && data.operator) {
        const [a, b] = data.angka_dalam_soal.split(',')
        const operator = 
          data.operator === 'Pengurangan' ? '-' :
          data.operator === 'Penjumlahan' ? '+' :
          data.operator === 'Perkalian' ? '×' :
          data.operator === 'Pembagian' ? '÷' : data.operator
        return `${a} ${operator} ${b} = ${data.jawaban || '?'}`
      }
      // For science questions
      else if (data.konsep && data.tipe) {
        return `${data.tipe}: ${data.jawaban} (${data.konsep})`
      }
      // Fallback
      return data.jawaban || '-'
    } catch (e) {
      return '-'
    }
  }

  onMount(async () => {
    try {
      soalList = await getAllSoal()
      ujianList = await getAllUjian()
      siswaList = await getAllSiswa()
      jawabanList = await getAllJawabanSiswa()

      const laporan = await getLaporanById(laporanId)
      const siswa = siswaList.find((s) => s.no === laporan?.siswa)
      const ujian = ujianList.find((u) => u.id === laporan?.ujian)

      if (laporan) {
        hasil = {
          ...laporan,
          nama_siswa: siswa ? siswa.nama_siswa : 'Tidak ditemukan',
          nama_ujian: ujian ? ujian.nama_ujian : 'Tidak ditemukan'
        }

        const soalFiltered = soalList.filter((soal) => soal.ujian === hasil?.ujian)
        analisis = await Promise.all(
          soalFiltered.map(async (soal, index): Promise<AnalisisItem> => {
            const siswaNisn = siswaList.find((s) => s.no === hasil?.siswa)
            const jawaban = jawabanList.find((j) => j.soal === soal.id && j.nisn === siswaNisn?.NISN)
            
            const kunci = formatJawaban(soal?.json_result)
            const jawabanSiswa = formatJawaban(jawaban?.json_result?.ai_analysis)
            
            // Determine correctness based on status field
            const benar = kunci === jawabanSiswa

            const defaultJsonResult: JsonResult = {
              angka_dalam_soal: '',
              jawaban: '',
              operator: '',
              soal_cerita: ''
            }
            
            const compare = await compareAnswer({
              ai_answer: soal?.json_result ?? defaultJsonResult,
              student_answer: jawaban?.json_result?.ai_analysis ?? defaultJsonResult
            })

            return {
              nomor: index + 1,
              analisis: compare.deskripsi_analisis || 'Tidak ada analisis.',
              kunci,
              jawaban: jawabanSiswa,
              benar
            }
          })
        )
      }
    } catch (error) {
      console.error('Error loading data:', error)
    }
  })
</script>

<div>
  <!-- Header -->
  <div class="flex justify-between items-center mb-16">
    <div>
      <div class="text-2xl font-semibold">{hasil?.nama_ujian}</div>
      <div class="text-xl mb-4">{hasil?.nama_siswa}</div>
    </div>

    <!-- Step Indicator -->
    <div class="flex items-center space-x-6">
      <div class="flex items-center space-x-2 text-gray-400">
        <div class="w-6 h-6 rounded-full border border-gray-300 text-sm flex items-center justify-center">1</div>
        <span>Buat Soal</span>
      </div>
      <div class="h-px w-6 bg-gray-300"></div>
      <div class="flex items-center space-x-2 text-gray-400">
        <div class="w-6 h-6 rounded-full border border-gray-300 text-sm flex items-center justify-center">2</div>
        <span>Jawaban Siswa</span>
      </div>
      <div class="h-px w-6 bg-gray-300"></div>
      <div class="flex items-center space-x-2">
        <div class="w-6 h-6 rounded-full bg-primary text-white text-sm flex items-center justify-center">3</div>
        <span class="text-primary font-semibold">Hasil</span>
      </div>
    </div>
  </div>

  <!-- Nilai -->
  <div class="flex justify-center">
    <div class="bg-primary text-white text-4xl font-bold rounded-2xl w-48 h-24 flex items-center justify-center">
      {hasil?.nilai}
    </div>
  </div>

  <!-- List Soal dan Analisis -->
  <div class="p-8 bg-white rounded-2xl shadow-md -mt-12">
    {#if analisis.length === 0}
      <div class="text-center py-8">Tidak ada data analisis yang tersedia.</div>
    {:else}
      {#each analisis as item}
        <div class="my-4">
          <h2 class="font-semibold">
            Nomor {item.nomor}
            {#if item.benar}
              <span class="text-green-600 text-lg">✔</span>
            {:else}
              <span class="text-red-600 text-lg">❌</span>
            {/if}
          </h2>
          <div class={`rounded-xl p-5 ${item.benar ? 'bg-green-100' : 'bg-red-100'}`}>
            <p class="mb-3 text-sm">{item.analisis}</p>
            <div class="space-y-1 text-sm">
              <div>
                <div class="font-bold">Kunci Jawaban:</div>
                {item.kunci}
              </div>
              <div>
                <div class="font-bold">Jawaban Siswa:</div>
                {item.jawaban}
              </div>
            </div>
          </div>
        </div>
      {/each}

      <div class="flex justify-end">
        <a href={`/dashboard/ujian/${hasil?.ujian}/jawaban`} class="bg-primary hover:bg-hover text-white px-6 py-2 rounded-lg text-sm gap-1">Selesai</a>
      </div>
    {/if}
  </div>
</div>