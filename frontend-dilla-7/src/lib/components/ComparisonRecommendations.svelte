<script lang="ts">
	export let recommendations: any[] = [];
	export let title: string = 'Rekomendasi Pembelajaran';
	export let showPriority: boolean = true;

	// Helper function to get priority color and icon
	function getPriorityStyle(priority: string): { color: string; icon: string; text: string } {
		switch (priority) {
			case 'high':
				return { color: 'border-red-200 bg-red-50 text-red-800', icon: '🚨', text: 'Prioritas Tinggi' };
			case 'medium':
				return { color: 'border-yellow-200 bg-yellow-50 text-yellow-800', icon: '⚠️', text: 'Prioritas Sedang' };
			case 'low':
				return { color: 'border-green-200 bg-green-50 text-green-800', icon: '💡', text: 'Saran' };
			default:
				return { color: 'border-gray-200 bg-gray-50 text-gray-800', icon: '📝', text: 'Informasi' };
		}
	}

	// Helper function to get recommendation type icon
	function getTypeIcon(type: string): string {
		switch (type) {
			case 'operator_improvement':
				return '🔢';
			case 'calculation_improvement':
				return '🧮';
			case 'problem_solving_improvement':
				return '🧩';
			case 'positive_reinforcement':
				return '🌟';
			default:
				return '📚';
		}
	}

	// Sort recommendations by priority
	$: sortedRecommendations = recommendations.sort((a, b) => {
		const priorityOrder = { high: 3, medium: 2, low: 1 };
		return (priorityOrder[b.priority] || 0) - (priorityOrder[a.priority] || 0);
	});
</script>

{#if recommendations && recommendations.length > 0}
	<div class="comparison-recommendations bg-white rounded-lg border shadow-sm">
		<!-- Header -->
		<div class="p-4 border-b bg-gradient-to-r from-purple-50 to-pink-50">
			<h3 class="text-lg font-semibold text-gray-800 flex items-center space-x-2">
				<span class="text-purple-600">💡</span>
				<span>{title}</span>
			</h3>
			<p class="text-sm text-gray-600 mt-1">
				{recommendations.length} rekomendasi berdasarkan analisis pembelajaran
			</p>
		</div>

		<!-- Recommendations List -->
		<div class="p-4 space-y-4">
			{#each sortedRecommendations as recommendation, index}
				{@const priorityStyle = getPriorityStyle(recommendation.priority)}
				{@const typeIcon = getTypeIcon(recommendation.type)}
				
				<div class="recommendation-card border rounded-lg {priorityStyle.color} transition-all duration-200 hover:shadow-md">
					<!-- Recommendation Header -->
					<div class="p-4 border-b border-current border-opacity-20">
						<div class="flex items-start justify-between">
							<div class="flex items-start space-x-3">
								<div class="text-2xl">{typeIcon}</div>
								<div class="flex-1">
									<div class="flex items-center space-x-2 mb-1">
										{#if showPriority}
											<span class="inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium border">
												<span>{priorityStyle.icon}</span>
												<span>{priorityStyle.text}</span>
											</span>
										{/if}
									</div>
									<p class="text-sm font-medium leading-relaxed">
										{recommendation.message}
									</p>
								</div>
							</div>
						</div>
					</div>

					<!-- Suggestions -->
					{#if recommendation.suggestions && recommendation.suggestions.length > 0}
						<div class="p-4">
							<h5 class="text-sm font-medium mb-3 flex items-center space-x-2">
								<span>🎯</span>
								<span>Langkah-langkah yang Disarankan:</span>
							</h5>
							<ul class="space-y-2">
								{#each recommendation.suggestions as suggestion, suggestionIndex}
									<li class="flex items-start space-x-3 text-sm">
										<span class="inline-flex items-center justify-center w-5 h-5 bg-white bg-opacity-70 rounded-full text-xs font-medium mt-0.5">
											{suggestionIndex + 1}
										</span>
										<span class="flex-1 leading-relaxed">{suggestion}</span>
									</li>
								{/each}
							</ul>
						</div>
					{/if}

					<!-- Action Buttons -->
					<div class="p-4 border-t border-current border-opacity-20 bg-white bg-opacity-30">
						<div class="flex items-center justify-between">
							<div class="text-xs opacity-75">
								Rekomendasi #{index + 1}
							</div>
							<div class="flex space-x-2">
								<button class="px-3 py-1 bg-white bg-opacity-70 hover:bg-opacity-90 rounded text-xs font-medium transition-all duration-200">
									📋 Catat
								</button>
								<button class="px-3 py-1 bg-white bg-opacity-70 hover:bg-opacity-90 rounded text-xs font-medium transition-all duration-200">
									✅ Tandai Selesai
								</button>
							</div>
						</div>
					</div>
				</div>
			{/each}
		</div>

			<!-- Summary Footer -->
	{#if recommendations.length > 0}
		{@const highPriority = recommendations.filter(r => r.priority === 'high').length}
		{@const mediumPriority = recommendations.filter(r => r.priority === 'medium').length}
		{@const lowPriority = recommendations.filter(r => r.priority === 'low').length}
		<div class="p-4 border-t bg-gray-50">
				
				<div class="flex items-center justify-between text-sm">
					<div class="flex items-center space-x-4">
						{#if highPriority > 0}
							<span class="flex items-center space-x-1 text-red-600">
								<span>🚨</span>
								<span>{highPriority} Prioritas Tinggi</span>
							</span>
						{/if}
						{#if mediumPriority > 0}
							<span class="flex items-center space-x-1 text-yellow-600">
								<span>⚠️</span>
								<span>{mediumPriority} Prioritas Sedang</span>
							</span>
						{/if}
						{#if lowPriority > 0}
							<span class="flex items-center space-x-1 text-green-600">
								<span>💡</span>
								<span>{lowPriority} Saran</span>
							</span>
						{/if}
					</div>
					<div class="text-gray-500">
						Total: {recommendations.length} rekomendasi
					</div>
				</div>
			</div>
		{/if}
	</div>
{:else}
	<div class="comparison-recommendations bg-gray-50 rounded-lg border border-dashed border-gray-300 p-6">
		<div class="text-center text-gray-500">
			<div class="text-3xl mb-2">🎯</div>
			<p class="text-sm font-medium">Belum Ada Rekomendasi</p>
			<p class="text-xs text-gray-400 mt-1">
				Rekomendasi akan muncul berdasarkan hasil analisis pembelajaran
			</p>
		</div>
	</div>
{/if}

<style>
	.recommendation-card {
		@apply transition-all duration-200;
	}

	.recommendation-card:hover {
		@apply transform scale-[1.02];
	}

	.recommendation-card button:hover {
		@apply transform scale-105;
	}
</style> 