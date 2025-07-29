<script lang="ts">
	import ComparisonAnalysis from '$lib/components/ComparisonAnalysis.svelte';
	import ComparisonSummary from '$lib/components/ComparisonSummary.svelte';
	import ComparisonRecommendations from '$lib/components/ComparisonRecommendations.svelte';

	// Sample data berdasarkan format yang diberikan user
	const sampleComparisonData = {
		student_answer: "7-3=4",
		ai_analysis: {
			angka_dalam_soal: "7,3",
			jawaban: "4",
			operator: "Pengurangan",
			soal_cerita: "7-3=4"
		},
		comparison: {
			status: "incorrect",
			deskripsi_analisis: "Siswa belum menjawab dengan benar semua aspek soal. operan 1 salah, operan 2 salah, operator salah, jawaban salah",
			nilai: 0,
			parameter_salah: ["operator", "operan_1", "operan_2", "jawaban"],
			koreksi: [
				"Operator yang benar adalah Pengurangan",
				"Operan 1 yang benar adalah 7",
				"Operan 2 yang benar adalah 3",
				"Jawaban yang benar adalah 4"
			]
		}
	};

	// Sample data untuk comparison yang benar
	const correctComparisonData = {
		student_answer: "5+3=8",
		ai_analysis: {
			angka_dalam_soal: "5,3",
			jawaban: "8",
			operator: "Penjumlahan",
			soal_cerita: "5+3=8"
		},
		comparison: {
			status: "correct",
			deskripsi_analisis: "Siswa telah menjawab dengan benar semua aspek soal",
			nilai: 3,
			parameter_salah: [],
			koreksi: []
		}
	};

	// Sample data untuk comparison sebagian benar
	const partialComparisonData = {
		student_answer: "6+4=9",
		ai_analysis: {
			angka_dalam_soal: "6,4",
			jawaban: "10",
			operator: "Penjumlahan",
			soal_cerita: "6+4=10"
		},
		comparison: {
			status: "incorrect",
			deskripsi_analisis: "Siswa telah menjawab dengan benar pada aspek operator, angka_dalam_soal",
			nilai: 2,
			parameter_salah: ["jawaban"],
			koreksi: ["Jawaban yang benar adalah 10"]
		}
	};

	// Sample summary data
	const summaryData = {
		total_jawaban_analyzed: 150,
		average_score: 78.5,
		nilai_tertinggi: 100,
		nilai_terendah: 45,
		persentase_kelulusan: 82.3,
		common_mistakes: {
			operator_salah: 25,
			operan_1_salah: 18,
			operan_2_salah: 22,
			jawaban_salah: 35
		},
		skill_analysis: {
			operator_mastery: 83.3,
			calculation_accuracy: 73.3,
			problem_solving: 76.7
		}
	};

	// Sample recommendations data
	const recommendationsData = [
		{
			type: 'operator_improvement',
			priority: 'high',
			message: 'Siswa perlu meningkatkan pemahaman tentang operator matematika (penjumlahan, pengurangan, perkalian, pembagian)',
			suggestions: [
				'Latihan soal cerita dengan berbagai jenis operator',
				'Pembelajaran visual tentang makna setiap operator',
				'Game interaktif untuk mengenali operator'
			]
		},
		{
			type: 'calculation_improvement',
			priority: 'high',
			message: 'Siswa perlu meningkatkan kemampuan mengidentifikasi angka dalam soal',
			suggestions: [
				'Latihan membaca soal cerita dengan teliti',
				'Teknik menggarisbawahi angka penting dalam soal',
				'Latihan soal dengan variasi penulisan angka'
			]
		},
		{
			type: 'problem_solving_improvement',
			priority: 'medium',
			message: 'Siswa perlu meningkatkan kemampuan menghitung hasil akhir',
			suggestions: [
				'Latihan operasi hitung dasar',
				'Penggunaan alat bantu hitung',
				'Verifikasi hasil dengan cara berbeda'
			]
		},
		{
			type: 'positive_reinforcement',
			priority: 'low',
			message: 'Siswa menunjukkan pemahaman yang baik tentang operator matematika',
			suggestions: [
				'Lanjutkan dengan soal yang lebih menantang',
				'Berikan peran sebagai tutor sebaya'
			]
		}
	];

	let selectedTab = 'individual';
	const tabs = [
		{ id: 'individual', label: 'Analisis Individual', icon: '🔍' },
		{ id: 'summary', label: 'Ringkasan Statistik', icon: '📊' },
		{ id: 'recommendations', label: 'Rekomendasi', icon: '💡' }
	];
</script>

<svelte:head>
	<title>Demo Analisis Comparison - Dilla</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 p-6">
	<div class="max-w-7xl mx-auto">
		<!-- Header -->
		<div class="mb-8">
			<div class="flex items-center space-x-3 mb-4">
				<div class="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
					<span class="text-white text-xl">📊</span>
				</div>
				<div>
					<h1 class="text-3xl font-bold text-gray-900">Demo Analisis Comparison</h1>
					<p class="text-gray-600">Komponen frontend untuk menampilkan hasil analisis jawaban siswa</p>
				</div>
			</div>
			
			<!-- Navigation Tabs -->
			<div class="flex space-x-1 bg-gray-200 p-1 rounded-lg w-fit">
				{#each tabs as tab}
					<button
						class="px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 flex items-center space-x-2 {selectedTab === tab.id
							? 'bg-white text-blue-600 shadow-sm'
							: 'text-gray-600 hover:text-gray-900'}"
						on:click={() => selectedTab = tab.id}
					>
						<span>{tab.icon}</span>
						<span>{tab.label}</span>
					</button>
				{/each}
			</div>
		</div>

		<!-- Content -->
		{#if selectedTab === 'individual'}
			<div class="space-y-8">
				<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
					<!-- Analisis Jawaban Salah -->
					<div>
						<h2 class="text-xl font-semibold text-gray-800 mb-4 flex items-center space-x-2">
							<span class="text-red-500">❌</span>
							<span>Contoh Jawaban Salah</span>
						</h2>
						<ComparisonAnalysis 
							comparisonData={sampleComparisonData}
							showStudentAnswer={true}
							showCorrectAnswer={true}
							compact={false}
						/>
					</div>

					<!-- Analisis Jawaban Benar -->
					<div>
						<h2 class="text-xl font-semibold text-gray-800 mb-4 flex items-center space-x-2">
							<span class="text-green-500">✅</span>
							<span>Contoh Jawaban Benar</span>
						</h2>
						<ComparisonAnalysis 
							comparisonData={correctComparisonData}
							showStudentAnswer={true}
							showCorrectAnswer={true}
							compact={false}
						/>
					</div>
				</div>

				<!-- Analisis Jawaban Sebagian Benar -->
				<div class="max-w-2xl mx-auto">
					<h2 class="text-xl font-semibold text-gray-800 mb-4 flex items-center space-x-2">
						<span class="text-yellow-500">⚠️</span>
						<span>Contoh Jawaban Sebagian Benar</span>
					</h2>
					<ComparisonAnalysis 
						comparisonData={partialComparisonData}
						showStudentAnswer={true}
						showCorrectAnswer={true}
						compact={false}
					/>
				</div>

				<!-- Compact Version -->
				<div class="bg-white p-6 rounded-lg border">
					<h2 class="text-xl font-semibold text-gray-800 mb-4 flex items-center space-x-2">
						<span>📱</span>
						<span>Versi Compact</span>
					</h2>
					<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
						<ComparisonAnalysis 
							comparisonData={sampleComparisonData}
							showStudentAnswer={false}
							showCorrectAnswer={false}
							compact={true}
						/>
						<ComparisonAnalysis 
							comparisonData={correctComparisonData}
							showStudentAnswer={false}
							showCorrectAnswer={false}
							compact={true}
						/>
						<ComparisonAnalysis 
							comparisonData={partialComparisonData}
							showStudentAnswer={false}
							showCorrectAnswer={false}
							compact={true}
						/>
					</div>
				</div>
			</div>

		{:else if selectedTab === 'summary'}
			<div class="space-y-8">
				<ComparisonSummary 
					summaryData={summaryData}
					title="Ringkasan Analisis Kelas"
					showDetails={true}
				/>

				<!-- Summary tanpa detail -->
				<div class="max-w-4xl mx-auto">
					<h2 class="text-xl font-semibold text-gray-800 mb-4">Versi Ringkas</h2>
					<ComparisonSummary 
						summaryData={summaryData}
						title="Ringkasan Singkat"
						showDetails={false}
					/>
				</div>
			</div>

		{:else if selectedTab === 'recommendations'}
			<div class="space-y-8">
				<ComparisonRecommendations 
					recommendations={recommendationsData}
					title="Rekomendasi Pembelajaran Individual"
					showPriority={true}
				/>

				<!-- Recommendations tanpa priority -->
				<div class="max-w-4xl mx-auto">
					<h2 class="text-xl font-semibold text-gray-800 mb-4">Versi Tanpa Priority</h2>
					<ComparisonRecommendations 
						recommendations={recommendationsData.slice(0, 2)}
						title="Rekomendasi Utama"
						showPriority={false}
					/>
				</div>
			</div>
		{/if}

		<!-- Data Structure Info -->
		<div class="mt-12 bg-white p-6 rounded-lg border">
			<h2 class="text-xl font-semibold text-gray-800 mb-4 flex items-center space-x-2">
				<span>📋</span>
				<span>Format Data JSON</span>
			</h2>
			<div class="space-y-4">
				<div>
					<h3 class="text-sm font-medium text-gray-700 mb-2">Comparison Data Structure:</h3>
					<pre class="bg-gray-100 p-4 rounded-lg text-xs overflow-x-auto"><code>{JSON.stringify(sampleComparisonData, null, 2)}</code></pre>
				</div>
				
				<div>
					<h3 class="text-sm font-medium text-gray-700 mb-2">Summary Data Structure:</h3>
					<pre class="bg-gray-100 p-4 rounded-lg text-xs overflow-x-auto"><code>{JSON.stringify(summaryData, null, 2)}</code></pre>
				</div>
			</div>
		</div>
	</div>
</div>

<style>
	pre {
		font-family: 'Fira Code', 'Monaco', 'Cascadia Code', 'Roboto Mono', monospace;
	}
</style> 