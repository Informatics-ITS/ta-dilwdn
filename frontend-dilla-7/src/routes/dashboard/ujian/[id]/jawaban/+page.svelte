<script lang="ts">
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'
  import { page } from '$app/stores'
  import { getAllSoal, updateSoal } from '$lib/api/soal';
  import { getUjianById } from '$lib/api/ujian';
  import type { Soal, JsonResult } from '$lib/types/soal';
  import type { Ujian } from '$lib/types/ujian';

  let ujianId: number | null = Number($page.params.id)
  let soalList: Soal[] = [];
  let ujian: Ujian | null = null;
  let isLoading = true;
  let isSaving = false;

  // Get Data
  onMount(async () => {
    try {
      const allSoal = await getAllSoal();
      ujian = await getUjianById(ujianId);

      soalList = allSoal.filter(soal => soal.ujian === ujianId);
    } catch (err) {
      console.error(err);
    } finally {
      isLoading = false;
    }
  });

  // Operator mapping with type safety
  const operatorMap = {
    '-': 'Pengurangan',
    'x': 'Perkalian',
    ':': 'Pembagian',
    '+': 'Penjumlahan'
  } as const;

  type OperatorKey = keyof typeof operatorMap;

  // Format answer
  function formatJawaban(data: JsonResult) {
    const [a, b] = data.angka_dalam_soal.split(',');
    const operator = data.operator === 'Pengurangan' ? '-' : 
                    data.operator === 'Perkalian' ? 'x' : 
                    data.operator === 'Pembagian' ? ':' : 
                    data.operator === 'Penjumlahan' ? '+' : 'Operator tidak diketahui';
    return `${a} ${operator} ${b} = ${data.jawaban}`;
  }

  // Parse answer with type safety
  function parseJawaban(text: string): JsonResult {
    const parts = text.split(' ');
    const operatorChar = parts[1] as OperatorKey;
    
    return {
      angka_dalam_soal: `${parts[0]},${parts[2]}`,
      operator: operatorMap[operatorChar],
      jawaban: parts[4],
      soal_cerita: soalList.find(s => formatJawaban(s.json_result!) === text)?.soal || ''
    };
  }

  // Update answer
  function updateAnswer(index: number, value: string) {
    if (soalList[index]) {
      soalList[index].json_result = parseJawaban(value);
      soalList = [...soalList]; // trigger reactivity
    }
  }

  // Save all answers
  async function saveAnswers() {
    if (!soalList.every(s => s.json_result)) return;
    
    isSaving = true;
    try {
      for (const soal of soalList) {
        if (soal && soal.json_result) {
          await updateSoal(soal.id, soal);
        }
      }

      goto(`/dashboard/ujian`)
    } catch (err) {
      console.error('Gagal menyimpan kunci jawaban:', err);
      alert('Gagal menyimpan kunci jawaban');
    } finally {
      isSaving = false;
    }
  }
</script>

<div class="p-4">
  <!-- Header -->
  <div class="flex justify-between items-center mb-16">
    <h1 class="text-2xl font-semibold mb-4">{ujian?.nama_ujian}</h1>

    <!-- Step Indicator -->
    <div class="flex items-center space-x-6">
      <div class="flex items-center space-x-2 text-gray-400">
        <div class="w-6 h-6 rounded-full border border-gray-300 text-sm flex items-center justify-center">1</div>
        <span>Buat Soal</span>
      </div>
      <div class="h-px w-6 bg-gray-300"></div>
      <div class="flex items-center space-x-2">
        <div class="w-6 h-6 rounded-full bg-primary text-white text-sm flex items-center justify-center">2</div>
        <span class="text-primary font-semibold">Jawaban Acuan</span>
      </div>
    </div>
  </div>

  <!-- Form Section -->
  <h2 class="text-center text-xl font-semibold text-primary mb-6">Kunci Jawaban Ujian</h2>

  {#if isLoading}
    <div class="flex justify-center items-center h-64">
      <svg class="animate-spin h-12 w-12 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>
  {:else}
    <div class="bg-white rounded-xl shadow p-6 max-h-[70vh] overflow-y-auto">
      {#each soalList as soal, index}
        <div class="mb-2 pb-4 last:mb-0">
          <h3 class="font-semibold mb-2">Nomor {index + 1}</h3>
          <div class="bg-columntable p-2 rounded-lg border border-black text-sm mb-2">
            {soal.soal}
          </div>

          <div class="my-2">Kunci Jawaban :</div>
          <input
            type="text"
            value={soal.json_result ? formatJawaban(soal.json_result) : ''}
            on:input={(e) => updateAnswer(index, (e.target as HTMLInputElement).value)}
            class="w-full p-2 bg-gray-50 rounded-md focus:ring-2 focus:ring-primary focus:outline-none"
          />
        </div>
      {/each}
    </div>

    <div class="flex justify-end mt-8">
      <button 
        on:click={saveAnswers}
        disabled={isSaving || !soalList.every(s => s.json_result)}
        class="bg-purple-600 text-white px-8 py-2 rounded-lg hover:bg-purple-700 transition disabled:opacity-70 disabled:cursor-not-allowed flex items-center"
      >
        {#if isSaving}
          <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Menyimpan...
        {:else}
          Simpan
        {/if}
      </button>
    </div>
  {/if}
</div>