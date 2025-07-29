<script lang="ts">
	export let summaryData: any = null;
	export let title: string = 'Ringkasan Analisis';
	export let showDetails: boolean = true;

	// Helper function to calculate percentage
	function calculatePercentage(value: number, total: number): number {
		if (total === 0) return 0;
		return Math.round((value / total) * 100);
	}

	// Helper function to get skill level color and text
	function getSkillLevel(percentage: number): { color: string; text: string; icon: string } {
		if (percentage >= 90) return { color: 'text-green-600 bg-green-50', text: 'Sangat Baik', icon: '🏆' };
		if (percentage >= 80) return { color: 'text-blue-600 bg-blue-50', text: 'Baik', icon: '👍' };
		if (percentage >= 70) return { color: 'text-yellow-600 bg-yellow-50', text: 'Cukup', icon: '📚' };
		if (percentage >= 60) return { color: 'text-orange-600 bg-orange-50', text: 'Kurang', icon: '🔄' };
		return { color: 'text-red-600 bg-red-50', text: 'Perlu Bimbingan', icon: '🆘' };
	}

	// Calculate derived statistics
	$: totalAnalyzed = summaryData?.total_jawaban_analyzed || 0;
	$: commonMistakes = summaryData?.common_mistakes || {};
	$: skillAnalysis = summaryData?.skill_analysis || {};

	// Calculate error rates
	$: operatorErrorRate = totalAnalyzed > 0 ? calculatePercentage(commonMistakes.operator_salah || 0, totalAnalyzed) : 0;
	$: calculationErrorRate = totalAnalyzed > 0 ? calculatePercentage((commonMistakes.operan_1_salah || 0) + (commonMistakes.operan_2_salah || 0), totalAnalyzed) : 0;
	$: answerErrorRate = totalAnalyzed > 0 ? calculatePercentage(commonMistakes.jawaban_salah || 0, totalAnalyzed) : 0;

	// Skill levels
	$: operatorSkill = getSkillLevel(skillAnalysis.operator_mastery || 0);
	$: calculationSkill = getSkillLevel(skillAnalysis.calculation_accuracy || 0);
	$: problemSolvingSkill = getSkillLevel(skillAnalysis.problem_solving || 0);
</script>

{#if summaryData && totalAnalyzed > 0}
	<div class="comparison-summary bg-white rounded-lg border shadow-sm">
		<!-- Header -->
		<div class="p-4 border-b bg-gradient-to-r from-blue-50 to-indigo-50">
			<h3 class="text-lg font-semibold text-gray-800 flex items-center space-x-2">
				<span class="text-blue-600">📊</span>
				<span>{title}</span>
			</h3>
			<p class="text-sm text-gray-600 mt-1">
				Berdasarkan {totalAnalyzed.toLocaleString()} jawaban yang dianalisis
			</p>
		</div>

		<!-- Skill Analysis -->
		<div class="p-4 space-y-4">
			<h4 class="text-md font-medium text-gray-700 mb-3">🎯 Penguasaan Keterampilan</h4>
			
			<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
				<!-- Operator Mastery -->
				<div class="skill-card p-4 rounded-lg border {operatorSkill.color}">
					<div class="flex items-center justify-between mb-2">
						<span class="text-sm font-medium">Pengenalan Operator</span>
						<span class="text-lg">{operatorSkill.icon}</span>
					</div>
					<div class="text-2xl font-bold mb-1">
						{skillAnalysis.operator_mastery?.toFixed(1) || 0}%
					</div>
					<div class="text-xs opacity-75">{operatorSkill.text}</div>
					<div class="mt-2 w-full bg-white bg-opacity-50 rounded-full h-2">
						<div
							class="h-2 rounded-full bg-current opacity-60"
							style="width: {skillAnalysis.operator_mastery || 0}%"
						></div>
					</div>
				</div>

				<!-- Calculation Accuracy -->
				<div class="skill-card p-4 rounded-lg border {calculationSkill.color}">
					<div class="flex items-center justify-between mb-2">
						<span class="text-sm font-medium">Identifikasi Angka</span>
						<span class="text-lg">{calculationSkill.icon}</span>
					</div>
					<div class="text-2xl font-bold mb-1">
						{skillAnalysis.calculation_accuracy?.toFixed(1) || 0}%
					</div>
					<div class="text-xs opacity-75">{calculationSkill.text}</div>
					<div class="mt-2 w-full bg-white bg-opacity-50 rounded-full h-2">
						<div
							class="h-2 rounded-full bg-current opacity-60"
							style="width: {skillAnalysis.calculation_accuracy || 0}%"
						></div>
					</div>
				</div>

				<!-- Problem Solving -->
				<div class="skill-card p-4 rounded-lg border {problemSolvingSkill.color}">
					<div class="flex items-center justify-between mb-2">
						<span class="text-sm font-medium">Pemecahan Masalah</span>
						<span class="text-lg">{problemSolvingSkill.icon}</span>
					</div>
					<div class="text-2xl font-bold mb-1">
						{skillAnalysis.problem_solving?.toFixed(1) || 0}%
					</div>
					<div class="text-xs opacity-75">{problemSolvingSkill.text}</div>
					<div class="mt-2 w-full bg-white bg-opacity-50 rounded-full h-2">
						<div
							class="h-2 rounded-full bg-current opacity-60"
							style="width: {skillAnalysis.problem_solving || 0}%"
						></div>
					</div>
				</div>
			</div>
		</div>

		{#if showDetails}
			<!-- Common Mistakes -->
			<div class="p-4 border-t">
				<h4 class="text-md font-medium text-gray-700 mb-3">⚠️ Kesalahan Umum</h4>
				
				<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
					<div class="mistake-card p-3 bg-purple-50 rounded-lg border border-purple-200">
						<div class="text-center">
							<div class="text-2xl font-bold text-purple-600">
								{commonMistakes.operator_salah || 0}
							</div>
							<div class="text-xs text-purple-700 mt-1">Operator Salah</div>
							<div class="text-xs text-purple-600 font-medium">
								{operatorErrorRate}% dari total
							</div>
						</div>
					</div>

					<div class="mistake-card p-3 bg-blue-50 rounded-lg border border-blue-200">
						<div class="text-center">
							<div class="text-2xl font-bold text-blue-600">
								{(commonMistakes.operan_1_salah || 0) + (commonMistakes.operan_2_salah || 0)}
							</div>
							<div class="text-xs text-blue-700 mt-1">Angka Salah</div>
							<div class="text-xs text-blue-600 font-medium">
								{calculationErrorRate}% dari total
							</div>
						</div>
					</div>

					<div class="mistake-card p-3 bg-orange-50 rounded-lg border border-orange-200">
						<div class="text-center">
							<div class="text-2xl font-bold text-orange-600">
								{commonMistakes.jawaban_salah || 0}
							</div>
							<div class="text-xs text-orange-700 mt-1">Jawaban Salah</div>
							<div class="text-xs text-orange-600 font-medium">
								{answerErrorRate}% dari total
							</div>
						</div>
					</div>

					<div class="mistake-card p-3 bg-green-50 rounded-lg border border-green-200">
						<div class="text-center">
							<div class="text-2xl font-bold text-green-600">
								{totalAnalyzed - (commonMistakes.operator_salah || 0) - ((commonMistakes.operan_1_salah || 0) + (commonMistakes.operan_2_salah || 0)) - (commonMistakes.jawaban_salah || 0)}
							</div>
							<div class="text-xs text-green-700 mt-1">Jawaban Benar</div>
							<div class="text-xs text-green-600 font-medium">
								{100 - operatorErrorRate - calculationErrorRate - answerErrorRate}% dari total
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Additional Statistics -->
			{#if summaryData.average_score !== undefined}
				<div class="p-4 border-t bg-gray-50">
					<div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
						<div>
							<div class="text-2xl font-bold text-blue-600">
								{summaryData.average_score?.toFixed(1) || 0}
							</div>
							<div class="text-xs text-gray-600">Rata-rata Nilai</div>
						</div>
						
						{#if summaryData.nilai_tertinggi !== undefined}
							<div>
								<div class="text-2xl font-bold text-green-600">
									{summaryData.nilai_tertinggi || 0}
								</div>
								<div class="text-xs text-gray-600">Nilai Tertinggi</div>
							</div>
						{/if}
						
						{#if summaryData.nilai_terendah !== undefined}
							<div>
								<div class="text-2xl font-bold text-red-600">
									{summaryData.nilai_terendah || 0}
								</div>
								<div class="text-xs text-gray-600">Nilai Terendah</div>
							</div>
						{/if}
						
						{#if summaryData.persentase_kelulusan !== undefined}
							<div>
								<div class="text-2xl font-bold text-purple-600">
									{summaryData.persentase_kelulusan?.toFixed(1) || 0}%
								</div>
								<div class="text-xs text-gray-600">Tingkat Kelulusan</div>
							</div>
						{/if}
					</div>
				</div>
			{/if}
		{/if}
	</div>
{:else}
	<div class="comparison-summary bg-gray-50 rounded-lg border border-dashed border-gray-300 p-6">
		<div class="text-center text-gray-500">
			<div class="text-3xl mb-2">📈</div>
			<p class="text-sm font-medium">Belum Ada Data Analisis</p>
			<p class="text-xs text-gray-400 mt-1">
				Ringkasan akan muncul setelah ada jawaban yang dianalisis
			</p>
		</div>
	</div>
{/if}

<style>
	.skill-card {
		@apply transition-all duration-200;
	}

	.skill-card:hover {
		@apply transform scale-105 shadow-md;
	}

	.mistake-card {
		@apply transition-all duration-200;
	}

	.mistake-card:hover {
		@apply transform scale-105 shadow-sm;
	}
</style> 