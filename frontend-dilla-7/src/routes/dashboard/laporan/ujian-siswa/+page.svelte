<script lang="ts">
  import { onMount } from 'svelte';
  import { Search, FileText, User, Calendar, Award } from 'lucide-svelte';
  import { api } from '$lib/config/axios';

  interface UjianSiswaListItem {
    id: number;
    ujian_id: number;
    siswa_no: number;
    nilai: number;
    label_nilai: string;
    deskripsi_analisis: string;
    nama_siswa: string;
    nisn: string;
    nama_ujian: string;
    pelaksanaan: string;
    status: string;
  }

  let ujianSiswaList: UjianSiswaListItem[] = [];
  let filteredList: UjianSiswaListItem[] = [];
  let loading = true;
  let error = '';
  let searchTerm = '';
  let selectedStatus = '';
  let selectedUjian = '';

  // Pagination
  let currentPage = 1;
  let itemsPerPage = 10;
  
  $: totalPages = Math.ceil(filteredList.length / itemsPerPage);
  $: startIndex = (currentPage - 1) * itemsPerPage;
  $: endIndex = startIndex + itemsPerPage;
  $: paginatedList = filteredList.slice(startIndex, endIndex);

  // Filter data based on search and filters
  $: {
    filteredList = ujianSiswaList.filter(item => {
      const matchesSearch = searchTerm === '' || 
        item.nama_siswa.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.nama_ujian.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.nisn.includes(searchTerm);
      
      const matchesStatus = selectedStatus === '' || item.status === selectedStatus;
      const matchesUjian = selectedUjian === '' || item.nama_ujian === selectedUjian;
      
      return matchesSearch && matchesStatus && matchesUjian;
    });
    
    // Reset to first page when filters change
    currentPage = 1;
  }

  // Get unique values for filters
  $: uniqueStatuses = [...new Set(ujianSiswaList.map(item => item.status))];
  $: uniqueUjians = [...new Set(ujianSiswaList.map(item => item.nama_ujian))];

  async function loadData() {
    try {
      loading = true;
      error = '';
      
      const response = await api.get('/api/teacher/ujian-siswa/list');
      ujianSiswaList = response.data;
      
    } catch (err: any) {
      error = err.response?.data?.error || 'Terjadi kesalahan saat memuat data';
      console.error('Error loading ujian siswa list:', err);
    } finally {
      loading = false;
    }
  }

  function goToPage(page: number) {
    if (page >= 1 && page <= totalPages) {
      currentPage = page;
    }
  }

  function getStatusColor(status: string) {
    switch (status?.toLowerCase()) {
      case 'aktif': return 'bg-green-100 text-green-800';
      case 'selesai': return 'bg-blue-100 text-blue-800';
      case 'ditutup': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  }

  function getNilaiColor(nilai: number) {
    if (nilai >= 80) return 'text-green-600 font-bold';
    if (nilai >= 70) return 'text-blue-600 font-bold';
    if (nilai >= 60) return 'text-yellow-600 font-bold';
    return 'text-red-600 font-bold';
  }

  onMount(loadData);
</script>

<svelte:head>
  <title>Daftar Ujian Siswa - Dilla</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 p-6">
  <div class="max-w-7xl mx-auto">
    
    <!-- Header -->
    <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center space-x-3">
          <div class="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
            <FileText class="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Daftar Ujian Siswa</h1>
            <p class="text-gray-600">Pilih ujian siswa untuk melihat analisis detail</p>
          </div>
        </div>
        
        <div class="text-right">
          <div class="bg-blue-50 p-4 rounded-lg">
            <div class="text-sm text-blue-600">Total Ujian Siswa</div>
            <div class="text-2xl font-bold text-blue-800">{ujianSiswaList.length}</div>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- Search -->
        <div class="relative">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input 
            type="text" 
            bind:value={searchTerm}
            placeholder="Cari nama siswa, ujian, atau NISN..."
            class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <!-- Status Filter -->
        <select 
          bind:value={selectedStatus}
          class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">Semua Status</option>
          {#each uniqueStatuses as status}
            <option value={status}>{status}</option>
          {/each}
        </select>

        <!-- Ujian Filter -->
        <select 
          bind:value={selectedUjian}
          class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">Semua Ujian</option>
          {#each uniqueUjians as ujian}
            <option value={ujian}>{ujian}</option>
          {/each}
        </select>

        <!-- Results Count -->
        <div class="flex items-center justify-end">
          <span class="text-sm text-gray-600">
            Menampilkan {filteredList.length} dari {ujianSiswaList.length} data
          </span>
        </div>
      </div>
    </div>

    {#if loading}
      <div class="flex items-center justify-center min-h-96">
        <div class="text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p class="text-gray-600">Memuat data ujian siswa...</p>
        </div>
      </div>
    
    {:else if error}
      <div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <div class="text-red-600 text-xl mb-2">⚠️</div>
        <h3 class="text-lg font-medium text-red-800 mb-2">Error</h3>
        <p class="text-red-700 mb-4">{error}</p>
        <button 
          on:click={loadData}
          class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
        >
          Coba Lagi
        </button>
      </div>
    
    {:else}
      <!-- Table -->
      <div class="bg-white rounded-xl shadow-sm overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50 border-b border-gray-200">
              <tr>
                <th class="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">No</th>
                <th class="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Siswa</th>
                <th class="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ujian</th>
                <th class="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tanggal</th>
                <th class="px-6 py-4 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Nilai</th>
                <th class="px-6 py-4 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th class="px-6 py-4 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Aksi</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              {#each paginatedList as item, index}
                <tr class="hover:bg-gray-50 transition-colors">
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {startIndex + index + 1}
                  </td>
                  
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <User class="w-5 h-5 text-blue-600" />
                      </div>
                      <div class="ml-3">
                        <div class="text-sm font-medium text-gray-900">{item.nama_siswa}</div>
                        <div class="text-sm text-gray-500">NISN: {item.nisn}</div>
                      </div>
                    </div>
                  </td>
                  
                  <td class="px-6 py-4">
                    <div class="text-sm font-medium text-gray-900">{item.nama_ujian}</div>
                    <div class="text-sm text-gray-500 line-clamp-2">{item.deskripsi_analisis}</div>
                  </td>
                  
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center text-sm text-gray-900">
                      <Calendar class="w-4 h-4 mr-2 text-gray-400" />
                      {new Date(item.pelaksanaan).toLocaleDateString('id-ID')}
                    </div>
                  </td>
                  
                  <td class="px-6 py-4 whitespace-nowrap text-center">
                    <div class="flex items-center justify-center">
                      <Award class="w-4 h-4 mr-1 text-gray-400" />
                      <span class="{getNilaiColor(item.nilai)}">{item.nilai}</span>
                    </div>
                    <div class="text-xs text-gray-500">{item.label_nilai}</div>
                  </td>
                  
                  <td class="px-6 py-4 whitespace-nowrap text-center">
                    <span class="px-2 py-1 text-xs font-medium rounded-full {getStatusColor(item.status)}">
                      {item.status}
                    </span>
                  </td>
                  
                  <td class="px-6 py-4 whitespace-nowrap text-center">
                    <a 
                      href={`/dashboard/laporan/ujian-siswa/${item.id}`}
                      class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 transition-colors inline-flex items-center space-x-2"
                    >
                      <FileText class="w-4 h-4" />
                      <span>Analisis Detail</span>
                    </a>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        {#if totalPages > 1}
          <div class="bg-gray-50 px-6 py-4 flex items-center justify-between border-t border-gray-200">
            <div class="text-sm text-gray-700">
              Menampilkan {startIndex + 1} - {Math.min(endIndex, filteredList.length)} dari {filteredList.length} data
            </div>
            
            <div class="flex items-center space-x-2">
              <button 
                on:click={() => goToPage(currentPage - 1)}
                disabled={currentPage === 1}
                class="px-3 py-1 border border-gray-300 rounded-md text-sm bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Sebelumnya
              </button>
              
              {#each Array(Math.min(5, totalPages)) as _, i}
                {@const page = i + 1}
                <button 
                  on:click={() => goToPage(page)}
                  class="px-3 py-1 border rounded-md text-sm {currentPage === page 
                    ? 'bg-blue-600 text-white border-blue-600' 
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}"
                >
                  {page}
                </button>
              {/each}
              
              <button 
                on:click={() => goToPage(currentPage + 1)}
                disabled={currentPage === totalPages}
                class="px-3 py-1 border border-gray-300 rounded-md text-sm bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Selanjutnya
              </button>
            </div>
          </div>
        {/if}
      </div>
    {/if}
  </div>
</div>

<style>
  .line-clamp-2 {
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }
</style> 