<script lang="ts">
  import { createEventDispatcher } from 'svelte'
  import { createSiswa, updateSiswa } from '$lib/api/siswa'
  import type { Siswa } from '$lib/types/siswa'

  export let show = false
  export let isEdit = false
  export let data: Siswa = { no: 0, nama_siswa: '', kelas: 0, NISN: '', password: '' }

  const dispatch = createEventDispatcher()

  let no = 0
  let nama_siswa = ''
  let kelas = 0
  let NISN = ''
  let password = ''

  $: if (isEdit && data) {
    no = data.no
    nama_siswa = data.nama_siswa
    kelas = data.kelas
    NISN = data.NISN
    password = data.password
  } else if (!isEdit && data) {
    no = data.no
    nama_siswa = ''
    kelas = data.kelas
    NISN = ''
    password = ''
  }

  async function handleSubmit() {
    if (isEdit) {
      await updateSiswa(no, { nama_siswa, kelas, NISN, password })
    } else {
      await createSiswa({ nama_siswa, kelas, NISN, password })
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
      <h2 class="text-xl font-semibold mb-4">{isEdit ? 'Edit Siswa' : 'Tambah Siswa'}</h2>

      <form on:submit|preventDefault={handleSubmit} class="space-y-4">
        <!-- NISN -->
        <div>
          <label for="NISN" class="block text-sm font-medium text-gray-900">NISN</label>
          <input
            type="text"
            id="NISN"
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary block w-full p-2.5"
            placeholder="2690375184"
            bind:value={NISN}
            required
          />
        </div>

        <!-- Nama Siswa -->
        <div>
          <label for="nama_siswa" class="block text-sm font-medium text-gray-900">Nama Siswa</label>
          <input
            type="text"
            id="nama_siswa"
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary block w-full p-2.5"
            placeholder="Prillia Sintya Bella"
            bind:value={nama_siswa}
            required
          />
        </div>

        <!-- Password -->
        <!-- <div>
          <label for="password" class="block text-sm font-medium text-gray-900">Password</label>
          <input
            type="password"
            id="password"
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary block w-full p-2.5"
            placeholder="Prillia Sintya Bella"
            bind:value={password}
            required
          />
        </div> -->

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
