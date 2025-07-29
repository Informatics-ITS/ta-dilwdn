<script lang="ts">
  import '/src/css/app.css'
  import { BarChart2, Menu, Users, FileText, LogOut, Search } from 'lucide-svelte'
  import { page } from '$app/stores'
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'

  let sidebarOpen = false
  let currentPath = ''
  $: currentPath = $page.url.pathname

  function getTitle(path: string) {
    if (path === '/siswa') return 'Kelas'
    if (path.startsWith('/siswa/nilai')) return 'Nilai'
    return 'Dashboard'
  }

  // onMount(() => {
  //   const user = localStorage.getItem('user')
  //   if (!user) goto('/login')
  // })

  function handleLogout() {
    localStorage.removeItem('user')
    goto('/login')
  }
</script>

<div class="flex h-screen bg-[#f9f9f9] text-gray-900">
  <!-- Sidebar -->
  <aside
    class={`fixed lg:static top-0 left-0 z-30 h-full w-64 bg-white border-r border-gray-300 shadow-md transform transition-transform duration-300 ease-in-out
      ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 flex flex-col px-4 pb-6`}
  >
    <!-- Logo -->
    <div class="flex items-center justify-between mt-6 mb-4 lg:justify-center">
      <div class="flex items-center">
        <img src="/logo.png" alt="MathGrade" class="w-8 mr-2" />
        <h1 class="text-primary font-bold text-lg font-aclonica">MathGrade</h1>
      </div>
      <button class="lg:hidden p-2 text-gray-500" on:click={() => (sidebarOpen = false)} aria-label="Close sidebar">✕</button>
    </div>

    <!-- Menu -->
    <nav class="flex flex-col gap-4">
      <a
        href="/siswa"
        class={`flex items-center gap-3 px-3 py-2 font-semibold rounded-full ${
          currentPath === '/siswa' || (currentPath.startsWith('/siswa/') && !currentPath.startsWith('/siswa/nilai')) ? 'bg-primary text-white' : 'hover:bg-purple-100'
        }`}
      >
        <Menu class="w-5 h-5" />
        Kelas
      </a>

      <a href="/siswa/nilai" class={`flex items-center gap-3 px-3 py-2 font-semibold rounded-full ${currentPath.startsWith('/siswa/nilai') ? 'bg-primary text-white' : 'hover:bg-purple-100'}`}>
        <Users class="w-5 h-5" />
        Nilai
      </a>
    </nav>

    <!-- Logout -->
    <button on:click={handleLogout} class="mt-auto text-red-600 flex items-center gap-2 hover:underline">
      <LogOut class="w-5 h-5" />
      Logout
    </button>
  </aside>

  <!-- Main Content -->
  <div class="flex-1 flex flex-col">
    <!-- Navbar -->
    <header class="flex justify-between items-center px-4 md:px-6 py-4 bg-white border-b border-gray-300 shadow-md">
      <!-- Toggle Sidebar -->
      <button class="lg:hidden text-gray-600 focus:outline-none" on:click={() => (sidebarOpen = true)} aria-label="Open sidebar">
        <Menu class="w-6 h-6" />
      </button>

      <h2 class="text-purple-700 font-semibold text-lg">{getTitle(currentPath)}</h2>

      <div class="flex items-center space-x-4">
        <div class="relative w-40">
          <Search class="absolute left-2 top-1/2 -translate-y-1/2 w-4 h-4 text-primary" />
          <input
            type="text"
            placeholder="Search..."
            class="w-full pl-10 pr-4 py-1 rounded-full border border-gray-300 text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        <button aria-label="Notifications" class="text-gray-400 hover:text-gray-700">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round">
            <path d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 00-5-5.917V4a2 2 0 10-4 0v1.083A6 6 0 004 11v3.159c0 .538-.214 1.055-.595 1.436L2 17h5m8 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
        </button>
        <img src="/Ellipse 15.png" alt="User Avatar" class="w-8 h-8 rounded-full" />
      </div>
    </header>

    <!-- Page Content -->
    <main class="p-4 md:p-6 overflow-y-auto flex-1">
      <slot />
    </main>
  </div>
</div>
