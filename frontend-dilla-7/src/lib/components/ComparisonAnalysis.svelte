<script lang="ts">
	export let comparisonData: any = null;
	export let showStudentAnswer: boolean = true;
	export let showCorrectAnswer: boolean = true;
	export let compact: boolean = false;

	// Helper function to get status color
	function getStatusColor(status: string): string {
		switch (status) {
			case 'correct':
				return 'text-green-600 bg-green-50 border-green-200';
			case 'incorrect':
				return 'text-red-600 bg-red-50 border-red-200';
			default:
				return 'text-gray-600 bg-gray-50 border-gray-200';
		}
	}

	// Helper function to get parameter error color
	function getParameterColor(parameter: string): string {
		switch (parameter) {
			case 'operator':
				return 'bg-purple-100 text-purple-800';
			case 'operan_1':
			case 'operan_2':
				return 'bg-blue-100 text-blue-800';
			case 'jawaban':
				return 'bg-orange-100 text-orange-800';
			default:
				return 'bg-gray-100 text-gray-800';
		}
	}

	// Helper function to get score color
	function getScoreColor(score: number): string {
		if (score === 3) return 'text-green-600';
		if (score === 2) return 'text-yellow-600';
		if (score === 1) return 'text-orange-600';
		return 'text-red-600';
	}

	// Helper function to format parameter name
	function formatParameterName(parameter: string): string {
		switch (parameter) {
			case 'operator':
				return 'Operator';
			case 'operan_1':
				return 'Angka Pertama';
			case 'operan_2':
				return 'Angka Kedua';
			case 'jawaban':
				return 'Jawaban Akhir';
			default:
				return parameter;
		}
	}
</script>

{#if comparisonData && comparisonData.comparison}
	<div class="comparison-analysis {compact ? 'compact' : ''} bg-white rounded-lg border shadow-sm">
		<!-- Header Status -->
		<div class="p-4 border-b">
			<div class="flex items-center justify-between">
				<div class="flex items-center space-x-3">
					<div class="flex items-center space-x-2">
						<div
							class="px-3 py-1 rounded-full text-sm font-medium border {getStatusColor(
								comparisonData.comparison.status
							)}"
						>
							{comparisonData.comparison.status === 'correct' ? '✓ Benar' : '✗ Salah'}
						</div>
						<div class="text-lg font-semibold {getScoreColor(comparisonData.comparison.nilai)}">
							Skor: {comparisonData.comparison.nilai}/3
						</div>
					</div>
				</div>
				<div class="text-sm text-gray-500">
					{comparisonData.comparison.nilai === 3
						? '🎉 Sempurna!'
						: comparisonData.comparison.nilai === 2
						? '👍 Baik'
						: comparisonData.comparison.nilai === 1
						? '📚 Perlu Latihan'
						: '🔄 Perlu Bimbingan'}
				</div>
			</div>
		</div>

		<!-- Analysis Description -->
		<div class="p-4 bg-gray-50">
			<p class="text-sm text-gray-700 leading-relaxed">
				<span class="font-medium">Analisis:</span>
				{comparisonData.comparison.deskripsi_analisis}
			</p>
		</div>

		<!-- Answer Comparison -->
		{#if showStudentAnswer || showCorrectAnswer}
			<div class="p-4 space-y-4">
				{#if showStudentAnswer}
					<div class="answer-section">
						<h4 class="text-sm font-medium text-gray-700 mb-2">📝 Jawaban Siswa:</h4>
						<div class="bg-blue-50 p-3 rounded-lg border border-blue-200">
							<p class="text-blue-800 font-mono">{comparisonData.student_answer || 'Tidak dijawab'}</p>
						</div>
					</div>
				{/if}

				{#if showCorrectAnswer && comparisonData.ai_analysis}
					<div class="answer-section">
						<h4 class="text-sm font-medium text-gray-700 mb-2">✅ Jawaban Benar:</h4>
						<div class="bg-green-50 p-3 rounded-lg border border-green-200">
							<div class="grid grid-cols-2 gap-4 text-sm">
								<div>
									<span class="text-gray-600">Operator:</span>
									<span class="ml-2 text-green-800 font-medium"
										>{comparisonData.ai_analysis.operator}</span
									>
								</div>
								<div>
									<span class="text-gray-600">Angka:</span>
									<span class="ml-2 text-green-800 font-medium"
										>{comparisonData.ai_analysis.angka_dalam_soal}</span
									>
								</div>
								<div class="col-span-2">
									<span class="text-gray-600">Jawaban:</span>
									<span class="ml-2 text-green-800 font-medium text-lg"
										>{comparisonData.ai_analysis.jawaban}</span
									>
								</div>
							</div>
						</div>
					</div>
				{/if}
			</div>
		{/if}

		<!-- Error Analysis -->
		{#if comparisonData.comparison.parameter_salah && comparisonData.comparison.parameter_salah.length > 0}
			<div class="p-4 border-t">
				<h4 class="text-sm font-medium text-gray-700 mb-3">🔍 Parameter yang Salah:</h4>
				<div class="flex flex-wrap gap-2">
					{#each comparisonData.comparison.parameter_salah as parameter}
						<span class="px-3 py-1 rounded-full text-xs font-medium {getParameterColor(parameter)}">
							{formatParameterName(parameter)}
						</span>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Corrections -->
		{#if comparisonData.comparison.koreksi && comparisonData.comparison.koreksi.length > 0}
			<div class="p-4 border-t bg-yellow-50">
				<h4 class="text-sm font-medium text-yellow-800 mb-3">💡 Saran Perbaikan:</h4>
				<ul class="space-y-2">
					{#each comparisonData.comparison.koreksi as koreksi}
						<li class="flex items-start space-x-2 text-sm text-yellow-700">
							<span class="text-yellow-500 mt-0.5">•</span>
							<span>{koreksi}</span>
						</li>
					{/each}
				</ul>
			</div>
		{/if}

		<!-- Progress Bar -->
		{#if !compact}
			<div class="p-4 border-t">
				<div class="flex items-center justify-between text-sm text-gray-600 mb-2">
					<span>Tingkat Penguasaan</span>
					<span>{Math.round((comparisonData.comparison.nilai / 3) * 100)}%</span>
				</div>
				<div class="w-full bg-gray-200 rounded-full h-2">
					<div
						class="h-2 rounded-full transition-all duration-300 {comparisonData.comparison.nilai === 3
							? 'bg-green-500'
							: comparisonData.comparison.nilai === 2
							? 'bg-yellow-500'
							: comparisonData.comparison.nilai === 1
							? 'bg-orange-500'
							: 'bg-red-500'}"
						style="width: {(comparisonData.comparison.nilai / 3) * 100}%"
					></div>
				</div>
			</div>
		{/if}
	</div>
{:else}
	<div class="comparison-analysis bg-gray-50 rounded-lg border border-dashed border-gray-300 p-6">
		<div class="text-center text-gray-500">
			<div class="text-2xl mb-2">📊</div>
			<p class="text-sm">Analisis comparison belum tersedia</p>
			<p class="text-xs text-gray-400 mt-1">Data akan muncul setelah jawaban dianalisis</p>
		</div>
	</div>
{/if}

<style>
	.comparison-analysis.compact {
		@apply text-sm;
	}

	.comparison-analysis.compact .answer-section {
		@apply space-y-2;
	}

	.comparison-analysis.compact .bg-blue-50,
	.comparison-analysis.compact .bg-green-50 {
		@apply p-2;
	}

	.answer-section {
		@apply transition-all duration-200;
	}

	.answer-section:hover {
		@apply transform scale-[1.01];
	}
</style> 