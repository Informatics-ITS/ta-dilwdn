<script>
  const steps = [
    { number: 1, title: 'Membuat Kelas' },
    { number: 2, title: 'Membuat Ujian' },
    { number: 3, title: 'Pindai jawaban' },
    { number: 4, title: 'Analisis Jawaban' },
    { number: 5, title: 'Lihat Hasil Analisis' },
    { number: 6, title: 'Unduh Analisis' }
  ]
</script>

<!-- Hero Section -->
<section class="bg-pink-100 min-h-screen flex flex-col items-center justify-start px-6">
  <!-- Navbar -->
  <nav class="relative w-full max-w-6xl flex items-center justify-center py-6">
    <!-- Navigasi utama di tengah -->
    <ul class="absolute left-1/2 transform -translate-x-1/2 flex gap-6 lg:text-lg md:text-lg sm:text-sm text-black font-medium">
      <li><a class="font-bold" href="/">Home</a></li>
      <li><a href="/">Kelas</a></li>
      <li><a href="/">Ujian</a></li>
      <li><a href="/">Analisis</a></li>
    </ul>

    <!-- Login dan Register di pojok kanan -->
    <div class="ml-auto flex items-center gap-2">
      <a href="/login" class="lg:text-lg md:text-lg sm:text-sm text-gray-700">Login</a>
      <a href="/register" class="bg-primary text-white lg:text-lg md:text-lg sm:text-sm px-4 py-1 rounded-full">Sign In</a>
    </div>
  </nav>

  <!-- Hero Content -->
  <div class="max-w-6xl grid md:grid-cols-2 items-center py-12 gap-8 w-full">
    <div>
      <h1 class="text-4xl md:text-5xl font-extrabold text-black leading-tight mb-4">Penilaian Jawaban Soal Cerita Matematika Lebih Cepat dan Mudah</h1>
      <p class="text-gray-700 text-lg">Unggah jawaban siswa, dapatkan penilaian instan, dan berikan umpan balik yang membangun</p>
    </div>
    <div class="flex justify-center">
      <img src="/src/lib/assets/image.png" alt="Ilustrasi bentuk 3D yang menunjukkan penilaian soal matematika" class="w-full max-w-md object-contain" />
    </div>
  </div>
</section>

<!-- Steps Section -->
<section class="bg-white py-16 px-6">
  <div class="max-w-5xl mx-auto text-center">
    <h2 class="text-2xl font-bold text-purple-600 mb-2">Cara Penggunaan</h2>
    <p class="text-gray-600 mb-10 max-w-xl mx-auto">Ikuti panduan sederhana ini untuk menilai jawaban soal cerita dengan cepat, akurat, dan adil</p>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-10">
      {#each steps as step}
        <div class="flex flex-col items-center text-center">
          <div class="w-24 h-24 bg-gray-300 rounded-full flex items-center justify-center relative mb-4">
            <span class="absolute -bottom-2 -right-2 bg-black text-white text-sm rounded-full w-6 h-6 flex items-center justify-center">
              {step.number}
            </span>
          </div>
          <h3 class="text-lg font-bold mb-1">{step.title}</h3>
          <p class="text-sm text-gray-600">buat kelas untuk memudahkan pengelompokan nilai dengan memasukkan id kelas, nama kelas, dan nama-nama siswa yang ada</p>
        </div>
      {/each}
    </div>
  </div>
</section>
