<script lang="ts">
  import { MoreVertical, Edit, Trash2 } from 'lucide-svelte'
  import { getAllKelas, deleteKelas } from '$lib/api/kelas'
  import { getAllSiswa } from '$lib/api/siswa'
  import type { Kelas } from '$lib/types/kelas'
  import type { Siswa } from '$lib/types/siswa'
  import { onMount } from 'svelte'
  import KelasModal from '$lib/components/KelasModal.svelte'
  import ConfirmDeleteModal from '$lib/components/ConfirmDeleteModal.svelte'

  let kelasList: Kelas[] = []
  let siswaList: Siswa[] = []
  let showModal = false
  let isEdit = false
  let showDeleteModal = false
  let kelasColors: Record<number, { border: string; text: string; bg: string }> = {}
  let deleteId: number | null = null
  let selectedData: Kelas = { id: 0, nama: '' }

  // Color
  const warnaOptions = [
    { border: 'border-red-500', text: 'text-red-500', bg: 'bg-red-500' },
    { border: 'border-green-500', text: 'text-green-500', bg: 'bg-green-500' },
    { border: 'border-blue-500', text: 'text-blue-500', bg: 'bg-blue-500' },
    { border: 'border-purple-500', text: 'text-purple-500', bg: 'bg-purple-500' },
    { border: 'border-pink-500', text: 'text-pink-500', bg: 'bg-pink-500' }
  ]
  function getRandomWarna() {
    return warnaOptions[Math.floor(Math.random() * warnaOptions.length)]
  }
  function getColorForKelas(id: number) {
    if (!kelasColors[id]) {
      kelasColors[id] = getRandomWarna()
    }
    return kelasColors[id]
  }

  // Get data
  async function getData() {
    const [kelas, siswa] = await Promise.all([getAllKelas(), getAllSiswa()])
    kelasList = kelas
    siswaList = siswa
  }
  onMount(getData)

  // Siswa
  function getJumlahSiswa(kelasId: number) {
    return siswaList.filter((s) => s.kelas === kelasId).length
  }

  // Create
  function getNewId() {
    if (kelasList.length === 0) return 1
    return Math.max(...kelasList.map((k) => k.id)) + 1
  }
  function openCreate() {
    isEdit = false
    selectedData = { id: getNewId(), nama: '' }
    showModal = true
  }

  // Edit
  function openEdit(kelas: Kelas) {
    isEdit = true
    selectedData = kelas
    showModal = true
  }

  // Delete
  function openDelete(id: number) {
    deleteId = id
    showDeleteModal = true
  }
  async function confirmDelete() {
    if (deleteId !== null) {
      await deleteKelas(deleteId)
      await getData()
      deleteId = null
    }
  }

  // Menu
  let menuIndex: number | null = null
  function toggleMenu(index: number) {
    menuIndex = menuIndex === index ? null : index
  }
</script>

<!-- Modal -->
<KelasModal bind:show={showModal} {isEdit} data={selectedData} on:refresh={getData} />
<ConfirmDeleteModal bind:show={showDeleteModal} on:confirm={confirmDelete} on:cancel={() => (showDeleteModal = false)} />

<div class="min-h-screen bg-gray-50 p-6">
  <!-- Header -->
  <div class="text-center mb-10">
    <h1 class="text-2xl font-bold text-gray-800">Manajemen Kelas dan Siswa</h1>
    <p class="text-sm text-gray-600 mt-1">
      Akses seluruh kelas yang Anda ampu dan
      <br />
      pantau perkembangan siswanya
    </p>
  </div>

  <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
    {#each kelasList as kelas, index}
      <div class="bg-white rounded-xl shadow-sm relative overflow-hidden border border-gray-200">
        <!-- Menu -->
        <div class="absolute top-3 right-3 text-gray-500 z-20">
          <button on:click={() => toggleMenu(index)} class="hover:text-gray-800">
            <MoreVertical size="20" />
          </button>

          {#if menuIndex === index}
            <div class="absolute right-0 mt-2 w-28 bg-white border rounded-md shadow-lg z-10">
              <!-- Delete -->
              <button on:click={() => openDelete(kelas.id)} class="flex items-center px-3 py-2 w-full text-sm hover:bg-gray-100 text-red-600">
                <Trash2 size="16" class="mr-2" /> Hapus
              </button>

              <!-- Edit -->
              <button on:click={() => openEdit(kelas)} class="flex items-center px-3 py-2 w-full text-sm hover:bg-gray-100 text-blue-600">
                <Edit size="16" class="mr-2" /> Edit
              </button>
            </div>
          {/if}
        </div>

        <div class="px-8 pt-4 pb-2 flex items-center justify-between">
          <!-- Nama -->
          <p class="font-medium text-gray-800 text-base">{kelas.nama}</p>

          <!-- Badge siswa -->
          <div class={`rounded-full w-20 h-20 my-1 flex flex-col items-center justify-center text-xs font-medium border ${getColorForKelas(kelas.id).border} ${getColorForKelas(kelas.id).text}`}>
            <div class="text-lg leading-none">{getJumlahSiswa(kelas.id)}</div>
            <div class="mt-0.5">siswa</div>
          </div>
        </div>

        <!-- Selanjutnya -->
        <a href={`kelas/${kelas.id}`}>
          <div class={`${getColorForKelas(kelas.id).bg} w-full text-white text-sm px-4 py-2 rounded-b-xl text-right cursor-pointer transition`}>Selanjutnya &nbsp; &gt;</div>
        </a>
      </div>
    {/each}

    <!-- Create -->
    <button
      type="button"
      on:click={openCreate}
      class="border-2 border-dashed border-purple-400 rounded-xl p-6 flex flex-col items-center justify-center text-purple-600 hover:bg-purple-50 cursor-pointer"
    >
      <div class="text-2xl">➕</div>
      <p class="mt-2 text-sm font-semibold">Tambah Kelas</p>
    </button>
  </div>
</div>
