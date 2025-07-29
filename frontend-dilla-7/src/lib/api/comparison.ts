import { api } from '$lib/config/axios';
import type { AxiosResponse } from 'axios';

// Types for comparison analysis
export interface ComparisonData {
	student_answer: string;
	ai_analysis: {
		angka_dalam_soal: string;
		jawaban: string;
		operator: string;
		soal_cerita: string;
	};
	comparison: {
		status: 'correct' | 'incorrect';
		deskripsi_analisis: string;
		nilai: number;
		parameter_salah: string[];
		koreksi: string[];
	};
}

export interface SummaryData {
	total_jawaban_analyzed: number;
	average_score?: number;
	nilai_tertinggi?: number;
	nilai_terendah?: number;
	persentase_kelulusan?: number;
	common_mistakes: {
		operator_salah: number;
		operan_1_salah: number;
		operan_2_salah: number;
		jawaban_salah: number;
	};
	skill_analysis: {
		operator_mastery: number;
		calculation_accuracy: number;
		problem_solving: number;
	};
}

export interface RecommendationData {
	type: string;
	priority: 'high' | 'medium' | 'low';
	message: string;
	suggestions: string[];
}

export interface UjianDetailReport {
	ujian_info: {
		id: number;
		nama_ujian: string;
		kelas_id: number;
		kelas_nama: string;
		pelaksanaan: string;
		status: string;
		total_soal: number;
	};
	students_performance: Array<{
		siswa_info: {
			no: number;
			nisn: string;
			nama_siswa: string;
		};
		exam_taken: boolean;
		nilai: number | null;
		label_nilai: string | null;
		deskripsi_analisis: string | null;
		jawaban_detail: Array<{
			soal_id: number;
			soal_text: string;
			correct_answer: any;
			student_answer: any;
			status: string;
			has_comparison: boolean;
			comparison_analysis: any;
		}>;
	}>;
	soal_analysis: Array<{
		soal_id: number;
		soal_text: string;
		correct_answer: any;
		total_jawaban: number;
		jawaban_benar: number;
		jawaban_salah: number;
		tidak_dijawab: number;
		tingkat_kesulitan: string;
		common_mistakes: {
			operator_salah: number;
			operan_1_salah: number;
			operan_2_salah: number;
			jawaban_salah: number;
		};
		comparison_analysis_available: number;
	}>;
	summary: SummaryData & {
		total_siswa: number;
		siswa_sudah_ujian: number;
		siswa_belum_ujian: number;
		total_jawaban_benar: number;
		total_jawaban_salah: number;
	};
}

export interface SiswaComparisonReport {
	siswa_info: {
		no: number;
		nisn: string;
		nama_siswa: string;
		kelas_id: number;
		kelas_nama: string;
	};
	exam_history: Array<{
		ujian_info: {
			id: number;
			nama_ujian: string;
			pelaksanaan: string;
		};
		nilai: number;
		label_nilai: string;
		deskripsi_analisis: string;
		jawaban_detail: any[];
		exam_analysis: {
			total_soal: number;
			jawaban_benar: number;
			jawaban_salah: number;
			operator_correct: number;
			calculation_correct: number;
			final_answer_correct: number;
		};
	}>;
	overall_performance: {
		total_ujian: number;
		rata_rata_nilai: number;
		nilai_tertinggi: number;
		nilai_terendah: number;
		total_jawaban_analyzed: number;
		skill_progress: {
			operator_mastery: Array<{ ujian_id: number; nama_ujian: string; percentage: number }>;
			calculation_accuracy: Array<{ ujian_id: number; nama_ujian: string; percentage: number }>;
			problem_solving: Array<{ ujian_id: number; nama_ujian: string; percentage: number }>;
		};
		common_mistakes: {
			operator_salah: number;
			operan_1_salah: number;
			operan_2_salah: number;
			jawaban_salah: number;
		};
	};
	recommendations: RecommendationData[];
}

// API Functions
export const comparisonApi = {
	// Analyze individual jawaban
	analyzeJawaban: async (jawabanId: number): Promise<any> => {
		const response: AxiosResponse = await api.post(`/api/teacher/jawaban-siswa/${jawabanId}/analyze`);
		return response.data;
	},

	// Analyze all answers in ujian
	analyzeAllAnswers: async (ujianId: number): Promise<any> => {
		const response: AxiosResponse = await api.post(`/api/teacher/ujian/${ujianId}/analyze-all-answers`);
		return response.data;
	},

	// Get comparison detail for specific jawaban
	getJawabanComparison: async (jawabanId: number): Promise<any> => {
		const response: AxiosResponse = await api.get(`/api/teacher/jawaban-siswa/${jawabanId}/comparison`);
		return response.data;
	},

	// Get ujian detail report
	getUjianDetailReport: async (ujianId: number): Promise<UjianDetailReport> => {
		const response: AxiosResponse<UjianDetailReport> = await api.get(`/api/teacher/ujian/${ujianId}/detail-report`);
		return response.data;
	},

	// Get ujian comparison report
	getUjianComparisonReport: async (ujianId: number): Promise<any> => {
		const response: AxiosResponse = await api.get(`/api/teacher/ujian/${ujianId}/comparison-report`);
		return response.data;
	},

	// Get kelas comparison summary
	getKelasComparisonSummary: async (kelasId: number): Promise<any> => {
		const response: AxiosResponse = await api.get(`/api/teacher/kelas/${kelasId}/comparison-summary`);
		return response.data;
	},

	// Get siswa comparison report
	getSiswaComparisonReport: async (siswaNo: number): Promise<SiswaComparisonReport> => {
		const response: AxiosResponse<SiswaComparisonReport> = await api.get(`/api/teacher/siswa/${siswaNo}/comparison-report`);
		return response.data;
	}
};

// Helper functions for processing data
export const comparisonHelpers = {
	// Calculate overall skill percentage
	calculateOverallSkill: (skillProgress: Array<{ percentage: number }>): number => {
		if (skillProgress.length === 0) return 0;
		const total = skillProgress.reduce((sum, item) => sum + item.percentage, 0);
		return Math.round(total / skillProgress.length);
	},

	// Get skill level based on percentage
	getSkillLevel: (percentage: number): { level: string; color: string; icon: string } => {
		if (percentage >= 90) return { level: 'Sangat Baik', color: 'green', icon: '🏆' };
		if (percentage >= 80) return { level: 'Baik', color: 'blue', icon: '👍' };
		if (percentage >= 70) return { level: 'Cukup', color: 'yellow', icon: '📚' };
		if (percentage >= 60) return { level: 'Kurang', color: 'orange', icon: '🔄' };
		return { level: 'Perlu Bimbingan', color: 'red', icon: '🆘' };
	},

	// Filter recommendations by priority
	filterRecommendationsByPriority: (recommendations: RecommendationData[], priority: 'high' | 'medium' | 'low'): RecommendationData[] => {
		return recommendations.filter(rec => rec.priority === priority);
	},

	// Format comparison data for display
	formatComparisonData: (rawData: any): ComparisonData | null => {
		if (!rawData || !rawData.comparison) return null;
		
		return {
			student_answer: rawData.student_answer || 'Tidak dijawab',
			ai_analysis: rawData.ai_analysis || {
				angka_dalam_soal: '',
				jawaban: '',
				operator: '',
				soal_cerita: ''
			},
			comparison: {
				status: rawData.comparison.status || 'incorrect',
				deskripsi_analisis: rawData.comparison.deskripsi_analisis || '',
				nilai: rawData.comparison.nilai || 0,
				parameter_salah: rawData.comparison.parameter_salah || [],
				koreksi: rawData.comparison.koreksi || []
			}
		};
	},

	// Calculate mistake percentage
	calculateMistakePercentage: (mistakeCount: number, totalAnalyzed: number): number => {
		if (totalAnalyzed === 0) return 0;
		return Math.round((mistakeCount / totalAnalyzed) * 100);
	}
}; 