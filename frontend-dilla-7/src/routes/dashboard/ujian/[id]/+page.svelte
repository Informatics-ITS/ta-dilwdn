<script lang="ts">
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'
  import { page } from '$app/stores'
  import { getAllSoal, createSoal } from '$lib/api/soal'
  import { getUjianById } from '$lib/api/ujian'
  import { solveMathProblemText } from '$lib/api/solve'
  import type { Ujian } from '$lib/types/ujian'
  import type { Soal, SoalForm } from '$lib/types/soal'

  let ujianId: number
  let ujian: Ujian | null = null
  let questions: string[] = ['']
  let existingSoalTexts: Set<string> = new Set()
  let isSubmitting = false

  // Get Data
  async function getData() {
    ujian = await getUjianById(ujianId)

    const allSoal: Soal[] = await getAllSoal()
    const soalUjianIni = allSoal.filter((soal) => soal.ujian === ujianId)

    if (soalUjianIni.length > 0) {
      questions = soalUjianIni.map((s) => s.soal)
      existingSoalTexts = new Set(questions)
    }
  }

  onMount(async () => {
    const unsubscribe = page.subscribe(($page) => {
      ujianId = Number($page.params.id)
    })

    await getData()
    unsubscribe()
  })

  // Question
  function addQuestion() {
    questions = [...questions, '']
  }
  function updateQuestion(index: number, value: string) {
    questions[index] = value
  }

  // Create
  async function submit() {
    isSubmitting = true

    for (const question of questions) {
      const trimmed = question.trim()

      // Skip jika soal ini sudah ada
      if (!trimmed || existingSoalTexts.has(trimmed)) continue

      const resText = await solveMathProblemText({ text_input: trimmed })

      const soalData: SoalForm = {
        soal: trimmed,
        ujian: ujianId,
        json_result: resText
      }

      try {
        await createSoal(soalData)
      } catch (err) {
        console.error('Gagal membuat soal:', err)
      }
    }

    isSubmitting = false
    goto(`/dashboard/ujian/${ujianId}/jawaban`)
  }
</script>

<div class="py-8 px-6">
  <!-- Loading Overlay -->
  {#if isSubmitting}
    <div class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
      <div class="bg-white p-8 rounded-xl shadow-xl text-center max-w-md">
        <svg class="animate-spin mx-auto h-12 w-12 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <h3 class="mt-4 text-lg font-medium text-gray-900">Memproses Soal</h3>
        <p class="mt-2 text-sm text-gray-500">Harap tunggu, soal sedang diproses...</p>
      </div>
    </div>
  {/if}

  <!-- Header -->
  <div class="flex justify-between items-center mb-16">
    <h1 class="text-2xl font-semibold mb-4">{ujian?.nama_ujian}</h1>

    <!-- Step Indicator -->
    <div class="flex items-center space-x-6">
      <div class="flex items-center space-x-2">
        <div class="w-6 h-6 rounded-full bg-primary text-white text-sm flex items-center justify-center">1</div>
        <span class="text-primary font-semibold">Buat Soal</span>
      </div>
      <div class="h-px w-6 bg-gray-300"></div>
      <div class="flex items-center space-x-2 text-gray-400">
        <div class="w-6 h-6 rounded-full border border-gray-300 text-sm flex items-center justify-center">2</div>
        <span>Jawaban Acuan</span>
      </div>
    </div>
  </div>

  <!-- Form Section -->
  <h2 class="text-center text-xl font-semibold text-primary mb-6">Masukkan Soal Cerita Matematika</h2>

  <!-- Questions -->
  <div class="bg-white p-6 rounded-xl shadow-md mx-auto">
    {#each questions as question, i}
      <div class="mb-5">
        <label for="question" class="block text-sm font-medium mb-2">Nomor {i + 1}</label>
        <textarea
          rows="1"
          id="question"
          bind:value={questions[i]}
          on:input={(e) => updateQuestion(i, (e.target as HTMLTextAreaElement).value)}
          class="w-full h-12 border border-gray-300 rounded-xl px-4 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary flex items-center justify-center"
        ></textarea>
      </div>
    {/each}

    <!-- Add -->
    <button type="button" on:click={addQuestion} class="text-primary text-sm font-medium flex items-center hover:underline">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
      </svg>
      Tambah Soal
    </button>
  </div>

  <!-- Submit -->
  <div class="mt-8 text-right">
    <button
      on:click={submit}
      disabled={isSubmitting}
      class="bg-primary hover:bg-hover text-white px-6 py-2 rounded-2xl shadow-md transition duration-150 disabled:opacity-70 disabled:cursor-not-allowed"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 inline-block mr-2 -mt-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-6h13v6m-3-3h-7" />
      </svg>
      Proses
    </button>
  </div>
</div>
