<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte'
  import { createUjian, updateUjian } from '$lib/api/ujian'
  import { getAllKelas } from '$lib/api/kelas'
  import type { Ujian } from '$lib/types/ujian'
  import type { Kelas } from '$lib/types/kelas'

  export let show = false
  export let isEdit = false
  export let data: Ujian = { id: 0, nama_ujian: '', kelas: 0, pelaksanaan: '', status: '' }

  const dispatch = createEventDispatcher()

  let kelasList: Kelas[] = []
  let id = 0
  let nama_ujian = ''
  let kelas = 0
  let pelaksanaan = ''
  let status = ''

  $: if (isEdit && data) {
    id = data.id
    nama_ujian = data.nama_ujian
    kelas = data.kelas
    pelaksanaan = data.pelaksanaan
    status = data.status
  } else if (!isEdit && data) {
    nama_ujian = ''
    kelas = 0
    pelaksanaan = ''
    status = ''
  }

  onMount(async () => {
    kelasList = await getAllKelas()
  })

  // Status
  const statusMap = [
    { label: 'belum', bg: 'bg-red-300', text: 'text-red-800' },
    { label: 'proses', bg: 'bg-green-300', text: 'text-green-800' },
    { label: 'selesai', bg: 'bg-blue-300', text: 'text-blue-800' }
  ]
  function getStatusClass(s: string) {
    const status = statusMap.find((item) => item.label === s)
    return status ? `${status.bg} ${status.text}` : ''
  }
  function getActiveClass(s: string) {
    return status === s ? `${getStatusClass(s)} border font-semibold` : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-100'
  }
  function setStatus(s: string) {
    status = s
  }

  async function handleSubmit() {
    if (isEdit) {
      await updateUjian(id, { nama_ujian, kelas, pelaksanaan, status })
    } else {
      await createUjian({ nama_ujian, kelas, pelaksanaan, status })
    }

    dispatch('refresh')
    close()
  }

  function close() {
    show = false
    dispatch('close')
  }
</script>

{#if show}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white p-4 rounded-lg w-full max-w-md shadow-xl">
      <h2 class="text-xl font-semibold mb-4">{isEdit ? 'Edit Ujian' : 'Tambah Ujian'}</h2>

      <form on:submit|preventDefault={handleSubmit} class="space-y-4">
        <!-- Nama Ujian -->
        <div>
          <label for="nama_ujian" class="block text-sm font-medium text-gray-900">Nama Ujian</label>
          <input
            type="text"
            id="nama_ujian"
            bind:value={nama_ujian}
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary block w-full p-2.5"
            placeholder="Ujian Akhir Semester"
            required
          />
        </div>

        <!-- Kelas -->
        <div>
          <label for="kelas" class="block text-sm font-medium text-gray-900">Kelas</label>
          <select
            bind:value={kelas}
            id="kelas"
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary block w-full p-2.5"
            required
          >
            <option disabled value="0">Pilih Kelas</option>
            {#each kelasList as k}
              <option value={k.id}>{k.nama}</option>
            {/each}
          </select>
        </div>

        <!-- Pelaksanaan -->
        <div>
          <label for="pelaksanaan" class="block text-sm font-medium text-gray-900">Tanggal Pelaksanaan</label>
          <input
            type="date"
            id="pelaksanaan"
            bind:value={pelaksanaan}
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary block w-full p-2.5"
            required
          />
        </div>

        <!-- Status -->
        <div>
          <label for="status" class="block text-sm font-medium text-gray-900 mb-1">Status</label>
          <div class="flex gap-2">
            {#each ['belum', 'proses', 'selesai'] as s}
              <button type="button" id="status" class={`px-4 py-2 rounded-lg text-sm transition ${getActiveClass(s)}`} on:click={() => setStatus(s)}>
                {s.charAt(0).toUpperCase() + s.slice(1)}
              </button>
            {/each}
          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-end gap-2 pt-2">
          <button type="button" on:click={close} class="text-gray-900 bg-white border border-gray-300 hover:bg-gray-100 focus:ring-4 focus:ring-gray-100 rounded-lg text-sm px-5 py-2.5">Batal</button>
          <button type="submit" class="text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 rounded-lg text-sm px-5 py-2.5">
            {isEdit ? 'Edit' : 'Simpan'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}
