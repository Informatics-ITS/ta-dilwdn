<script lang="ts">
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'
  import { page } from '$app/stores'
  import { getAllSoal } from '$lib/api/soal'
  import { getUjianById } from '$lib/api/ujian'
  import { getAllUser } from '$lib/api/user'
  import { solveMathProblemText, compareAnswer, analyzeAnswer } from '$lib/api/solve'
  import { createJawabanSiswa } from '$lib/api/jawaban-siswa'
  import { createLaporan } from '$lib/api/laporan'
  import type { Soal } from '$lib/types/soal'
  import type { Ujian } from '$lib/types/ujian'
  import type { JawabanSiswaForm } from '$lib/types/jawaban-siswa'

  let ujianId: number | null = Number($page.params.ujian)
  let soalList: Soal[] = []
  let ujian: Ujian | null = null
  let isLoading = true
  let isSubmitting = false
  let error: string | null = null
  let answers: Record<number, string> = {} // { soalId: answer }
  let analysisResults: Record<number, any> = {} // Store analysis results
  let showConfirmationDialog = false
  let unansweredCount = 0

  // Safely get student ID from localStorage
  let siswaId: number | null = null
  let siswaNisn: string = ''
  const userData = typeof localStorage !== 'undefined' ? localStorage.getItem('user') : null
  if (userData) {
    try {
      const user = JSON.parse(userData)
      siswaId = user?.id || null
    } catch (e) {
      console.error('Failed to parse user data', e)
    }
  }

  onMount(async () => {
    try {
      if (!ujianId) throw new Error('Ujian ID tidak valid')

      // Get all students to find NISN
      const allUser = await getAllUser()
      const currentUser = allUser.find((u) => u.id == siswaId)
      if (currentUser) {
        siswaNisn = currentUser.email
      }

      const allSoal = await getAllSoal()
      ujian = await getUjianById(ujianId)

      soalList = allSoal.filter((soal) => soal.ujian == ujianId)

      // Initialize answers object
      soalList.forEach((soal) => {
        answers[soal.id] = ''
      })
    } catch (err) {
      error = 'Gagal memuat soal'
      console.error(err)
    } finally {
      isLoading = false
    }
  })

  function formatTanggal(tanggal: string | Date): string {
    const options: Intl.DateTimeFormatOptions = {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    }
    return new Date(tanggal).toLocaleDateString('id-ID', options)
  }

  function updateAnswer(soalId: number, value: string) {
    answers[soalId] = value
    answers = { ...answers } // Trigger reactivity
  }
  function confirmSubmit() {
    unansweredCount = soalList.length - Object.values(answers).filter(a => a.trim() !== '').length
    showConfirmationDialog = true
  }

  async function submitAnswers() {
    showConfirmationDialog = false
    if (!siswaId || !ujianId) {
      error = 'Siswa atau ujian tidak teridentifikasi'
      return
    }

    isSubmitting = true
    error = null
    let allAnalysisTexts: string[] = []
    let correctAnswers = 0
    let totalAnswered = 0

    try {
      // Process each answer
      for (const soal of soalList) {
        const studentAnswer = answers[soal.id]
        if (!studentAnswer || !soal.json_result) continue

        totalAnswered++

        // Step 1: Analyze student's answer with AI
        const res = await solveMathProblemText({ text_input: studentAnswer })

        // Step 2: Compare with correct answer
        const comparison = await compareAnswer({
          ai_answer: soal.json_result,
          student_answer: res
        })

        // Count correct answers
        if (comparison.status === 'correct') {
          correctAnswers++
        }

        // Store analysis result
        analysisResults[soal.id] = comparison

        // Prepare data for createJawabanSiswa
        const jawabanData: JawabanSiswaForm = {
          nisn: siswaNisn,
          soal: soal.id,
          status: comparison.status,
          json_result: {
            student_answer: studentAnswer,
            ai_analysis: res,
            comparison: {
              status: comparison.status,
              nilai: comparison.nilai
            }
          }
        }
        console.log(jawabanData)

        // Step 3: Save student answer
        await createJawabanSiswa(jawabanData)

        // Collect analysis text for each question
        allAnalysisTexts.push(`Soal ${soalList.indexOf(soal) + 1}: ${comparison.deskripsi_analisis}`)
      }

      // Step 4: Analyze all answers together and create laporan
      if (totalAnswered > 0) {
        const analysisText = allAnalysisTexts.join(', ')
        const overallAnalysis = await analyzeAnswer({ text: analysisText })

        // Calculate score (percentage)
        const nilai = Math.round((correctAnswers / totalAnswered) * 100)

        // Determine label based on score
        let label_nilai = ''
        if (nilai < 70) label_nilai = 'Kurang'
        else if (nilai <= 80) label_nilai = 'Cukup'
        else if (nilai <= 90) label_nilai = 'Baik'
        else label_nilai = 'Sangat Baik'

        // Create laporan
        const laporanData = {
          ujian: ujianId,
          nisn: siswaNisn,
          nilai: nilai,
          label_nilai: label_nilai,
          deskripsi_analisis: overallAnalysis.analisis_pedagogik || 'Siswa menjawab dengan baik'
        }

        const resLaporan = await createLaporan(laporanData)

        goto(`/siswa/nilai`)
      } else {
        alert('Tidak ada jawaban yang disubmit!')
      }
    } catch (err) {
      error = 'Gagal menyimpan jawaban'
      console.error(err)
    } finally {
      isSubmitting = false
    }
  }

  function handleInput(event: Event, soalId: number) {
    const target = event.target as HTMLInputElement
    if (target) {
      updateAnswer(soalId, target.value)
    }
  }
</script>

<div class="p-4">
  {#if isLoading}
    <div class="text-center py-8">Memuat soal...</div>
  {:else if error}
    <div class="text-red-500 text-center py-8">{error}</div>
  {:else if soalList.length === 0}
    <div class="text-center py-8">Tidak ada soal ditemukan</div>
  {:else}
    <h1 class="text-2xl font-bold">{ujian?.nama_ujian || 'Ujian'}</h1>
    <p class="mb-8">tanggal {formatTanggal(ujian?.pelaksanaan || new Date())}</p>

    <div class="mb-8">
      <h2 class="text-xl font-semibold text-center text-primary mb-4">Kerjakan dengan baik</h2>
    </div>

    <div class="bg-white rounded-xl shadow p-6 max-h-[70vh] overflow-y-auto">
      {#each soalList as soal, index}
        <div class="mb-6 pb-4 border-b border-gray-200 last:border-b-0">
          <h3 class="font-semibold mb-2">Nomor {index + 1}</h3>
          <div class="bg-columntable p-3 rounded-lg border border-black text-sm mb-2">
            {soal.soal}
          </div>

          <input
            type="text"
            bind:value={answers[soal.id]}
            on:input={(e) => handleInput(e, soal.id)}
            placeholder="Jawaban Anda"
            class="w-full border-b border-gray-400 focus:outline-none focus:border-black text-sm placeholder-gray-500 py-3"
          />
        </div>
      {/each}
    </div>

    <div class="flex justify-end mt-8">
      <button
        on:click={confirmSubmit}
      disabled={isSubmitting || Object.values(answers).every((a) => !a)}
        class="bg-purple-600 text-white px-6 py-2 rounded-md hover:bg-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
      >
        {#if isSubmitting}
          <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Menyimpan...
        {:else}
          Submit
        {/if}
      </button>
    </div>
  {/if}

  <!-- Confirmation Dialog -->
     {#if showConfirmationDialog}

    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-secondary rounded-xl p-6 max-w-md w-full mx-4 text-center">
        <h3 class="text-md font-semibold mb-4">Apakah Anda yakin ingin mengumpulkan jawaban sekarang? </h3>
        <p class="text-sm mb-4">
          Setelah dikumpulkan, Anda tidak dapat mengubah jawaban. Pastikan semua soal telah dijawab dengan benar.
        </p>
        <div class="flex justify-center space-x-4">
          <button
            on:click={() => showConfirmationDialog = false}
            class="bg-white text-red px-4 py-2 rounded-md hover:bg-gray-50 transition"
          >
            Batal
          </button>
          <button
            on:click={submitAnswers}
            class="bg-white text-green px-4 py-2 rounded-md hover:bg-purple-700 transition"
          >
            Kumpulkan
          </button>
        </div>
      </div>
    </div>
      {/if}

</div>
