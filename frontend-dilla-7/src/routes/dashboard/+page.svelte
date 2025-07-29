<script lang="ts">
  import { Gauge, Users, LayoutGrid } from 'lucide-svelte'
  import Calendar from '$lib/components/Calendar.svelte'
  import guruImage from '$lib/assets/amico.png'
  import type { User } from '$lib/types/user'
  import { onMount } from 'svelte'
  import { writable } from 'svelte/store'

  import { getAllSiswa } from '$lib/api/siswa'
  import { getAllKelas } from '$lib/api/kelas'
  import { getAllUjian } from '$lib/api/ujian'
  import { getAllLaporan } from '$lib/api/laporan'

  const user = writable<User>({
    id: 0,
    nama_lengkap: '',
    email: '',
    jenis_kelamin: '',
    password: ''
  })

  const totalSiswa = writable(0)
  const totalKelas = writable(0)
  const totalUjian = writable(0)

  const nilaiSiswa = writable<any[]>([])
  const penilaianTerkini = writable<any[]>([])
  const progresPenilaian = writable<any[]>([])

  onMount(async () => {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        user.set(JSON.parse(storedUser))
      } catch (e) {
        console.error('Gagal parse data user dari localStorage', e)
      }
    }

    const siswa = await getAllSiswa()
    const kelas = await getAllKelas()
    const ujian = await getAllUjian()
    const laporan = await getAllLaporan()

    totalSiswa.set(siswa.length)
    totalKelas.set(kelas.length)
    totalUjian.set(ujian.length)

    const warnaWarna = ['bg-red-500', 'bg-green-500', 'bg-blue-500', 'bg-yellow-500', 'bg-purple-500', 'bg-pink-500', 'bg-indigo-500', 'bg-teal-500']
    const hasil = laporan.map((l) => ({
      name: siswa.find((s) => s.no === l.siswa)?.nama_siswa ?? 'Tidak diketahui',
      score: l.nilai,
      color: warnaWarna[Math.floor(Math.random() * warnaWarna.length)]
    }))
    hasil.sort((a, b) => b.score - a.score)
    nilaiSiswa.set(hasil)

    penilaianTerkini.set(
      laporan.slice(0, 3).map((l: any) => ({
        title: l.nama || 'Ulangan Harian',
        kelas: l.kelas?.nama || '-',
        type: l.tipe || 'penjumlahan',
        date: l.tanggal || '3 Mei 2025',
        status: 'Selesai'
      }))
    )

    progresPenilaian.set(
      ujian.slice(0, 3).map((u: any, idx: number) => ({
        label: 'UH',
        title: u.nama,
        date: u.tanggal,
        count: `${Math.floor(Math.random() * 20) + 10}/30`,
        bgColor: ['bg-blue-100', 'bg-yellow-100', 'bg-red-100'][idx % 3],
        textColor: ['text-blue-700', 'text-yellow-700', 'text-red-700'][idx % 3]
      }))
    )
  })

  const penilaian = [
    { title: 'Ulangan Harian 4', kelas: '1B', type: 'penjumlahan', date: '3 Mei 2025', status: 'Selesai' },
    { title: 'Ulangan Harian 4', kelas: '1B', type: 'penjumlahan', date: '3 Mei 2025', status: 'Selesai' },
    { title: 'Ulangan Harian 4', kelas: '1B', type: 'penjumlahan', date: '3 Mei 2025', status: 'Selesai' }
  ]

  const progress = [
    {
      label: 'UH',
      title: 'Ulangan Harian 2',
      date: '9 Mei 2025',
      count: '15/30',
      bgColor: 'bg-blue-100',
      textColor: 'text-blue-700'
    },
    {
      label: 'UH',
      title: 'Ulangan Harian 2',
      date: '9 Mei 2025',
      count: '15/30',
      bgColor: 'bg-yellow-100',
      textColor: 'text-yellow-700'
    },
    {
      label: 'UH',
      title: 'Ulangan Harian 2',
      date: '9 Mei 2025',
      count: '15/30',
      bgColor: 'bg-red-100',
      textColor: 'text-red-700'
    }
  ]
</script>

<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
  <!-- Left content -->
  <div class="lg:col-span-2 space-y-6">
    <!-- Header -->
    <section class="bg-[#F1CEFF] rounded-xl flex flex-col md:flex-row justify-between items-center px-6 py-4 gap-4 shadow-sm">
      <div class="text-center md:text-left">
        <h1 class="text-lg md:text-2xl font-bold text-primary">Selamat Datang Ibu Guru {$user.nama_lengkap}!!</h1>
        <p class="text-sm md:text-base text-gray-700 mt-1">Mari memahami cara berpikir siswa lewat setiap baris jawaban mereka</p>
      </div>
      <img src={guruImage} alt="Guru Dilla" class="w-24 md:w-36 lg:w-32 object-contain" />
    </section>

    <!-- Stat boxes -->
    <section class="grid grid-cols-2 sm:grid-cols-3 gap-4">
      <div class="bg-green-100 rounded-3xl p-4 text-center">
        <Users class="mx-auto text-green-700" />
        <p class="text-xl font-bold my-2">{$totalSiswa}</p>
        <p class="text-xs font-semibold">Total Siswa</p>
      </div>
      <div class="bg-blue-100 rounded-3xl p-4 text-center">
        <LayoutGrid class="mx-auto text-blue-700" />
        <p class="text-xl font-bold my-2">{$totalKelas}</p>
        <p class="text-xs font-semibold">Total Kelas</p>
      </div>
      <div class="bg-purple-100 rounded-3xl p-4 text-center col-span-2 sm:col-span-1">
        <Gauge class="mx-auto text-purple-700" />
        <p class="text-xl font-bold my-2">{$totalUjian}</p>
        <p class="text-xs font-semibold">Total Ujian</p>
      </div>
    </section>

    <!-- Nilai & Capaian -->
    <section class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="md:col-span-2 bg-white rounded-3xl p-6 space-y-3">
        <div class="flex justify-between items-center">
          <h3 class="font-semibold">Nilai siswa</h3>
          <a href="/dashboard/laporan" class="text-purple-600 text-sm hover:underline">Lihat Semua</a>
        </div>
        <ul class="space-y-3">
          {#each $nilaiSiswa as s}
            <li class="flex flex-col sm:flex-row items-start sm:items-center sm:space-x-4 text-sm font-medium">
              <div class="w-full sm:w-1/3 truncate">{s.name}</div>
              <div class="w-full sm:w-1/2 h-2 rounded-full bg-gray-200 overflow-hidden my-1 sm:my-0">
                <div class={`${s.color} h-2 rounded-full`} style="width: {s.score}%"></div>
              </div>
              <div class="w-full sm:w-1/6 text-right">{s.score}</div>
            </li>
          {/each}
        </ul>
      </div>

      <div class="bg-white rounded-3xl p-6">
        <h3 class="font-semibold">Capaian</h3>
        <div class="flex justify-center items-center my-4">
          <div class="relative w-28 h-28 sm:w-32 sm:h-32">
            <svg viewBox="0 0 36 36" class="w-full h-full">
              <path
                class="text-gray-200"
                stroke="currentColor"
                stroke-width="3.8"
                fill="none"
                d="M18 2.0845
                   a 15.9155 15.9155 0 0 1 0 31.831
                   a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <path
                class="text-purple-600"
                stroke="currentColor"
                stroke-width="3.8"
                stroke-dasharray="95, 100"
                stroke-linecap="round"
                fill="none"
                d="M18 2.0845
                   a 15.9155 15.9155 0 0 1 0 31.831"
              />
            </svg>
            <div class="absolute inset-0 flex flex-col justify-center items-center font-semibold text-purple-700 text-lg">
              <span>95%</span>
              <span class="text-sm text-gray-500">Lulus</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Penilaian -->
    <div class="flex justify-between items-center">
      <h3 class="font-semibold">Penilaian Terkini</h3>
      <a href="/dashboard/ujian" class="text-purple-600 text-sm hover:underline flex items-center gap-1">
        Lihat Semua <span>→</span>
      </a>
    </div>

    <div class="space-y-2">
      {#each penilaian as p}
        <div class="bg-white rounded-xl px-4 py-3 flex flex-col md:flex-row md:items-center md:justify-between text-sm gap-2">
          <div class="flex flex-wrap md:flex-nowrap gap-4 md:gap-6">
            <span class="w-24">{p.title}</span>
            <span class="w-10">{p.kelas}</span>
            <span class="w-32">{p.type}</span>
            <span class="w-32">{p.date}</span>
          </div>
          <span class="px-3 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-700">
            {p.status}
          </span>
        </div>
      {/each}
    </div>
  </div>

  <!-- Right sidebar -->
  <div class="space-y-6">
    <Calendar />

    <div class="py-2">
      <h3 class="font-semibold my-1">Progres Penilaian</h3>
      <ul class="space-y-2">
        {#each progress as p}
          <li class="relative px-3 py-4 rounded-3xl bg-white">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <span class={`font-bold px-3 py-2 rounded-full text-xs ${p.bgColor} ${p.textColor}`}>
                  {p.label}
                </span>
                <div>
                  <p class="font-semibold">{p.title}</p>
                  <p class="text-xs text-gray-500">{p.date}</p>
                </div>
              </div>
            </div>
            <span class="absolute bottom-3 right-3 text-sm text-gray-700">
              {p.count} siswa
            </span>
          </li>
        {/each}
      </ul>
    </div>

    <div class="bg-gradient-to-t from-purple-700 to-purple-500 rounded-2xl p-4 flex flex-col sm:flex-row items-center gap-4 text-white">
      <img src="/Ellipse 15.png" alt="Avatar" class="w-14 h-14 rounded-full bg-white p-1" />
      <div class="text-center sm:text-left">
        <p class="font-semibold">{$user.nama_lengkap}</p>
        <p class="text-sm">{$user.email}</p>
      </div>
    </div>
  </div>
</div>
