<script lang="ts">
  import { createEventDispatcher } from 'svelte'
  import { createKelas, updateKelas } from '$lib/api/kelas'
  import type { Kelas } from '$lib/types/kelas'

  export let show = false
  export let isEdit = false
  export let data: Kelas = { id: 0, nama: '' }

  const dispatch = createEventDispatcher()

  let id = 0
  let nama = ''

  $: if (isEdit && data) {
    id = data.id
    nama = data.nama
  } else if (!isEdit && data) {
    id = data.id
    nama = ''
  }

  async function handleSubmit() {
    if (isEdit) {
      await updateKelas(id, { nama })
    } else {
      await createKelas({ id, nama })
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
    <div class="bg-white p-3 rounded-lg w-full max-w-md shadow-xl">
      <h2 class="text-xl font-semibold mb-4">{isEdit ? 'Edit Kelas' : 'Tambah Kelas'}</h2>

      <form on:submit|preventDefault={handleSubmit} class="space-y-4">
        <div>
          <label for="nama" class="block text-sm font-medium text-gray-900">Nama Kelas</label>
          <input
            type="text"
            id="nama"
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary block w-full p-2.5"
            placeholder="Kelax XI IPA 1"
            bind:value={nama}
            required
          />
        </div>

        <div class="flex justify-end gap-2">
          <button
            type="button"
            on:click={close}
            class="text-gray-900 bg-white border border-gray-300 focus:outline-none hover:bg-gray-100 focus:ring-4 focus:ring-gray-100 font-medium rounded-lg text-sm px-5 py-2.5"
          >
            Batal
          </button>
          <button type="submit" class="text-white bg-primary hover:bg-hover focus:ring-4 focus:ring-secondary font-medium rounded-lg text-sm px-5 py-2.5 focus:outline-none">
            {isEdit ? 'Edit' : 'Simpan'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}
