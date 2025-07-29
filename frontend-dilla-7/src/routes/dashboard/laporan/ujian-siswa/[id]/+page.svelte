<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { browser } from '$app/environment';
  import type { PageData } from './$types';
  import { 
    getUjianSiswaDetail, 
    getUjianSiswaSummary, 
    getUjianSiswaComparisonAnalysis,
    extractStudentAnswerFromJawabanResult,
    formatMathAnswer,
    type UjianSiswaDetailResponse,
    type UjianSiswaSummaryData,
    type UjianSiswaComparisonResponse
  } from '$lib/api/stored-procedure';
  import ComparisonAnalysis from '$lib/components/ComparisonAnalysis.svelte';
  import ComparisonSummary from '$lib/components/ComparisonSummary.svelte';
  import ComparisonRecommendations from '$lib/components/ComparisonRecommendations.svelte';

  export let data: PageData;

  // Data variables
  let ujianSiswaId: number = data.ujianSiswaId || 0;
  let detailData: UjianSiswaDetailResponse | null = null;
  let summaryData: UjianSiswaSummaryData | null = null;
  let comparisonData: UjianSiswaComparisonResponse | null = null;
  let loading = true;
  let error = '';
  let selectedTab = 'detail';

  // Tabs configuration
  const tabs = [
    { id: 'detail', label: 'Detail Jawaban', icon: '📋' },
    { id: 'comparison', label: 'Analisis Comparison', icon: '🔍' },
    { id: 'summary', label: 'Ringkasan', icon: '📊' },
    { id: 'recommendations', label: 'Rekomendasi', icon: '💡' }
  ];

  // Processed data for components (only calculate after mount to avoid SSR issues)
  let processedSummary: any = null;
  let recommendations: any[] = [];

  // Update processed data when summaryData changes
  $: if (summaryData && browser) {
    processedSummary = {
      total_jawaban_analyzed: summaryData.analyzed_answers,
      average_score: summaryData.avg_comparison_score,
      nilai_tertinggi: summaryData.nilai,
      nilai_terendah: summaryData.nilai,
      persentase_kelulusan: (summaryData.jawaban_benar / summaryData.total_soal) * 100,
      common_mistakes: {
        operator_salah: 0,
        operan_1_salah: 0,
        operan_2_salah: 0,
        jawaban_salah: summaryData.jawaban_salah
      },
      skill_analysis: {
        operator_mastery: (summaryData.jawaban_benar / summaryData.total_soal) * 100,
        calculation_accuracy: (summaryData.jawaban_benar / summaryData.total_soal) * 100,
        problem_solving: summaryData.avg_comparison_score * 33.33
      }
    };
    recommendations = generateRecommendations(summaryData);
  }

  function generateRecommendations(summary: UjianSiswaSummaryData) {
    const accuracy = (summary.jawaban_benar / summary.total_soal) * 100;
    const recs = [];

    if (accuracy < 60) {
      recs.push({
        type: 'urgent_improvement',
        priority: 'high',
        message: 'Siswa memerlukan perhatian khusus dalam pemahaman dasar matematika',
        suggestions: [
          'Remedial pembelajaran dengan pendekatan individual',
          'Latihan soal dasar secara bertahap',
          'Konsultasi dengan orang tua untuk pembelajaran di rumah'
        ]
      });
    } else if (accuracy < 75) {
      recs.push({
        type: 'skill_improvement',
        priority: 'medium',
        message: 'Siswa perlu meningkatkan kemampuan pemecahan masalah matematika',
        suggestions: [
          'Latihan soal cerita dengan variasi tingkat kesulitan',
          'Pembelajaran kelompok untuk diskusi strategi',
          'Praktik operasi hitung secara rutin'
        ]
      });
    } else if (accuracy < 90) {
      recs.push({
        type: 'enhancement',
        priority: 'low',
        message: 'Siswa sudah memiliki pemahaman yang baik, tingkatkan ke level yang lebih menantang',
        suggestions: [
          'Berikan soal dengan tingkat kesulitan lebih tinggi',
          'Latihan olimpiade matematika tingkat dasar',
          'Menjadi tutor sebaya untuk teman sekelas'
        ]
      });
    } else {
      recs.push({
        type: 'excellence',
        priority: 'low',
        message: 'Siswa menunjukkan kemampuan matematika yang sangat baik',
        suggestions: [
          'Ikuti kompetisi matematika',
          'Bergabung dengan program akselerasi',
          'Mengembangkan proyek matematika kreatif'
        ]
      });
    }

    return recs;
  }

  async function loadData() {
    try {
      loading = true;
      error = '';
      
      // Load all data in parallel
      const [detail, summary, comparison] = await Promise.all([
        getUjianSiswaDetail(ujianSiswaId),
        getUjianSiswaSummary(ujianSiswaId),
        getUjianSiswaComparisonAnalysis(ujianSiswaId)
      ]);

      detailData = detail;
      summaryData = summary;
      comparisonData = comparison;
      
    } catch (err: any) {
      error = err.message || 'Terjadi kesalahan saat memuat data';
      console.error('Error loading ujian siswa data:', err);
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    if (!browser) return;
    
    if (!ujianSiswaId || isNaN(ujianSiswaId)) {
      error = 'ID ujian siswa tidak valid';
      loading = false;
      return;
    }

    loadData();
  });

  function getStatusColor(status: string) {
    switch (status?.toLowerCase()) {
      case 'correct': return 'text-green-600 bg-green-100';
      case 'incorrect': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  }

  function getComparisonIcon(status: string) {
    switch (status?.toLowerCase()) {
      case 'correct': return '✅';
      case 'incorrect': return '❌';
      default: return '❓';
    }
  }
</script>

<svelte:head>
  <title>Laporan Ujian Siswa #{ujianSiswaId} - Dilla</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 p-6">
  <div class="max-w-7xl mx-auto">
    
    {#if !browser}
      <div class="flex items-center justify-center min-h-96">
        <div class="text-center">
          <div class="animate-pulse rounded-full h-12 w-12 bg-gray-300 mx-auto mb-4"></div>
          <p class="text-gray-600">Loading...</p>
        </div>
      </div>
    {:else if loading}
      <div class="flex items-center justify-center min-h-96">
        <div class="text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p class="text-gray-600">Memuat data laporan...</p>
        </div>
      </div>
    
    {:else if error}
      <div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <div class="text-red-600 text-xl mb-2">⚠️</div>
        <h3 class="text-lg font-medium text-red-800 mb-2">Error</h3>
        <p class="text-red-700 mb-4">{error}</p>
        <button 
          on:click={() => goto('/dashboard/laporan')}
          class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
        >
          Kembali ke Laporan
        </button>
      </div>
    
    {:else if summaryData}
      <!-- Header Section -->
      <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
        <div class="flex justify-between items-start mb-6">
          <div>
            <div class="flex items-center space-x-3 mb-2">
              <div class="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
                <span class="text-white text-xl">📊</span>
              </div>
              <div>
                <h1 class="text-2xl font-bold text-gray-900">{summaryData.nama_ujian}</h1>
                <p class="text-gray-600">Laporan Ujian Siswa</p>
              </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
              <div class="bg-blue-50 p-4 rounded-lg">
                <div class="text-sm text-blue-600 font-medium">Nama Siswa</div>
                <div class="text-lg font-semibold text-blue-800">{summaryData.nama_siswa}</div>
                <div class="text-sm text-blue-600">NISN: {summaryData.NISN}</div>
              </div>
              
              <div class="bg-green-50 p-4 rounded-lg">
                <div class="text-sm text-green-600 font-medium">Nilai Ujian</div>
                <div class="text-2xl font-bold text-green-800">{summaryData.nilai}</div>
                <div class="text-sm text-green-600">{summaryData.label_nilai}</div>
              </div>
              
              <div class="bg-purple-50 p-4 rounded-lg">
                <div class="text-sm text-purple-600 font-medium">Tanggal Pelaksanaan</div>
                <div class="text-lg font-semibold text-purple-800">
                  {new Date(summaryData.pelaksanaan).toLocaleDateString('id-ID')}
                </div>
              </div>
            </div>
          </div>

          <!-- Quick Stats -->
          <div class="text-right">
            <div class="bg-gray-50 p-4 rounded-lg">
              <div class="text-sm text-gray-600">Statistik Cepat</div>
              <div class="space-y-1 mt-2">
                <div class="text-sm">
                  <span class="text-green-600 font-medium">{summaryData.jawaban_benar}</span>
                  <span class="text-gray-500"> / </span>
                  <span class="text-gray-600">{summaryData.total_soal}</span>
                  <span class="text-gray-500"> benar</span>
                </div>
                <div class="text-sm">
                  <span class="text-blue-600 font-medium">{summaryData.analyzed_answers}</span>
                  <span class="text-gray-500"> dianalisis</span>
                </div>
                <div class="text-sm">
                  <span class="text-purple-600 font-medium">{summaryData.avg_comparison_score.toFixed(1)}</span>
                  <span class="text-gray-500"> rata-rata</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Navigation Tabs -->
        <div class="flex space-x-1 bg-gray-100 p-1 rounded-lg w-fit">
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

      <!-- Content Sections -->
      {#if selectedTab === 'detail' && detailData}
        <div class="space-y-4">
          <h2 class="text-xl font-semibold text-gray-800 flex items-center space-x-2">
            <span>📋</span>
            <span>Detail Jawaban Siswa</span>
            <span class="text-sm text-gray-500">({detailData.total_records} jawaban)</span>
          </h2>
          
          <div class="grid gap-4">
                         {#each detailData.data as item, index}
               {@const studentAnswerData = (() => {
                 try {
                   return extractStudentAnswerFromJawabanResult(item.jawaban_json_result);
                 } catch (e) {
                   return { student_answer: '', ai_analysis: {}, comparison: {} };
                 }
               })()}
               {@const correctAnswerFormatted = (() => {
                 try {
                   return formatMathAnswer(item.soal_json_result);
                 } catch (e) {
                   return '-';
                 }
               })()}
               {@const studentAnswerFormatted = (() => {
                 try {
                   return formatMathAnswer(studentAnswerData.ai_analysis);
                 } catch (e) {
                   return '-';
                 }
               })()}
              
              <div class="bg-white rounded-lg shadow-sm border">
                <div class="p-4 border-b bg-gray-50">
                  <div class="flex justify-between items-center">
                    <div class="flex items-center space-x-3">
                      <div class="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">
                        {index + 1}
                      </div>
                      <h3 class="font-medium text-gray-900">Soal #{item.soal_id}</h3>
                      <span class="px-2 py-1 rounded-full text-xs font-medium {getStatusColor(item.jawaban_status)}">
                        {getComparisonIcon(item.jawaban_status)} {item.jawaban_status}
                      </span>
                    </div>
                    
                    <div class="text-sm text-gray-500">
                      ID Jawaban: {item.jawaban_siswa_id}
                    </div>
                  </div>
                </div>
                
                <div class="p-4">
                  <div class="mb-4">
                    <div class="text-sm text-gray-600 mb-1">Soal:</div>
                    <div class="font-medium text-gray-900">{item.soal_text}</div>
                  </div>
                  
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div class="bg-green-50 p-3 rounded-lg">
                      <div class="text-sm text-green-600 font-medium mb-1">Jawaban Benar:</div>
                      <div class="font-mono text-green-800">{correctAnswerFormatted}</div>
                    </div>
                    
                    <div class="bg-blue-50 p-3 rounded-lg">
                      <div class="text-sm text-blue-600 font-medium mb-1">Jawaban Siswa:</div>
                      <div class="font-mono text-blue-800">{studentAnswerFormatted}</div>
                    </div>
                  </div>
                  
                                     {#if browser && studentAnswerData.comparison && Object.keys(studentAnswerData.comparison).length > 0}
                     <div class="border-t pt-4">
                       <ComparisonAnalysis 
                         comparisonData={studentAnswerData}
                         showStudentAnswer={false}
                         showCorrectAnswer={false}
                         compact={true}
                       />
                     </div>
                   {/if}
                </div>
              </div>
            {/each}
          </div>
        </div>

      {:else if selectedTab === 'comparison' && comparisonData}
        <div class="space-y-6">
          <h2 class="text-xl font-semibold text-gray-800 flex items-center space-x-2">
            <span>🔍</span>
            <span>Analisis Comparison Detail</span>
            <span class="text-sm text-gray-500">({comparisonData.total_analyzed} dianalisis)</span>
          </h2>
          
          <div class="grid gap-6">
            {#each comparisonData.data as item}
                             {@const comparisonForComponent = (() => {
                 try {
                   return {
                     student_answer: formatMathAnswer(JSON.parse(item.student_answer || '{}')),
                     ai_analysis: JSON.parse(item.correct_answer || '{}'),
                     comparison: {
                       status: item.comparison_status,
                       nilai: item.comparison_score,
                       deskripsi_analisis: item.comparison_analysis,
                       parameter_salah: JSON.parse(item.wrong_parameters || '[]'),
                       koreksi: JSON.parse(item.corrections || '[]')
                     }
                   };
                 } catch (e) {
                   return {
                     student_answer: '',
                     ai_analysis: {},
                     comparison: {
                       status: 'unknown',
                       nilai: 0,
                       deskripsi_analisis: 'Error parsing data',
                       parameter_salah: [],
                       koreksi: []
                     }
                   };
                 }
               })()}
              
              <div class="bg-white rounded-lg shadow-sm border p-6">
                <div class="flex justify-between items-center mb-4">
                  <h3 class="text-lg font-medium text-gray-900">Soal #{item.soal_id}</h3>
                  <div class="text-sm text-gray-500">
                    Score: {item.comparison_score}/3
                  </div>
                </div>
                
                <div class="mb-4">
                  <div class="text-sm text-gray-600 mb-1">Soal:</div>
                  <div class="font-medium text-gray-900 mb-3">{item.soal_text}</div>
                </div>
                
                                 {#if browser}
                   <ComparisonAnalysis 
                     comparisonData={comparisonForComponent}
                     showStudentAnswer={true}
                     showCorrectAnswer={true}
                     compact={false}
                   />
                 {:else}
                   <div class="text-center py-4 text-gray-500">Loading analysis...</div>
                 {/if}
              </div>
            {/each}
          </div>
        </div>

      {:else if selectedTab === 'summary' && processedSummary && browser}
        <div class="space-y-6">
          <ComparisonSummary 
            summaryData={processedSummary}
            title="Ringkasan Analisis Ujian"
            showDetails={true}
          />
        </div>

      {:else if selectedTab === 'recommendations' && browser}
        <div class="space-y-6">
          <ComparisonRecommendations 
            recommendations={recommendations}
            title="Rekomendasi Pembelajaran untuk {summaryData?.nama_siswa || 'Siswa'}"
            showPriority={true}
          />
        </div>
      
      {:else if !browser}
        <div class="text-center py-12">
          <div class="animate-pulse">
            <div class="h-4 bg-gray-300 rounded w-3/4 mx-auto mb-2"></div>
            <div class="h-4 bg-gray-300 rounded w-1/2 mx-auto"></div>
          </div>
        </div>
      {/if}

      <!-- Back Button -->
      <div class="mt-8 flex justify-between items-center">
        <button 
          on:click={() => goto('/dashboard/laporan')}
          class="bg-gray-600 text-white px-6 py-2 rounded-lg hover:bg-gray-700 transition-colors flex items-center space-x-2"
        >
          <span>←</span>
          <span>Kembali ke Daftar Laporan</span>
        </button>
        
        <div class="text-sm text-gray-500">
          Ujian Siswa ID: {ujianSiswaId}
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .font-mono {
    font-family: 'Fira Code', 'Monaco', 'Cascadia Code', 'Roboto Mono', monospace;
  }
</style> 