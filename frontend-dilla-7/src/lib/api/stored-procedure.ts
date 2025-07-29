import { api } from '$lib/config/axios';

// Types for stored procedure responses
export interface UjianSiswaDetailData {
  ujian_siswa_id: number;
  ujian_siswa_ujian_id: number;
  ujian_siswa_siswa_no: number;
  nilai: number;
  label_nilai: string;
  deskripsi_analisis: string;
  
  jawaban_siswa_id: number;
  nisn: string;
  jawaban_siswa_soal_id: number;
  jawaban_status: string;
  jawaban_json_result: any;
  
  ujian_id: number;
  nama_ujian: string;
  ujian_kelas_id: number;
  pelaksanaan: string;
  ujian_status: string;
  
  soal_id: number;
  soal_text: string;
  soal_ujian_id: number;
  soal_json_result: any;
  
  nama_siswa: string;
  siswa_nisn: string;
  siswa_kelas_id: number;
}

export interface UjianSiswaDetailResponse {
  ujian_siswa_id: number;
  total_records: number;
  data: UjianSiswaDetailData[];
}

export interface UjianSiswaSummaryData {
  ujian_siswa_id: number;
  nilai: number;
  label_nilai: string;
  deskripsi_analisis: string;
  nama_ujian: string;
  pelaksanaan: string;
  nama_siswa: string;
  NISN: string;
  total_soal: number;
  total_jawaban: number;
  jawaban_benar: number;
  jawaban_salah: number;
  analyzed_answers: number;
  avg_comparison_score: number;
}

export interface UjianSiswaComparisonData {
  ujian_siswa_id: number;
  nilai: number;
  label_nilai: string;
  nama_ujian: string;
  nama_siswa: string;
  NISN: string;
  soal_id: number;
  soal_text: string;
  correct_answer: any;
  jawaban_siswa_id: number;
  jawaban_status: string;
  student_answer: any;
  comparison_status: string;
  comparison_score: number;
  comparison_analysis: string;
  wrong_parameters: any;
  corrections: any;
}

export interface UjianSiswaComparisonResponse {
  ujian_siswa_id: number;
  total_analyzed: number;
  data: UjianSiswaComparisonData[];
}

// API functions
export const getUjianSiswaDetail = async (ujianSiswaId: number): Promise<UjianSiswaDetailResponse> => {
  try {
    const response = await api.get(`/api/teacher/ujian-siswa/${ujianSiswaId}/detail`);
    return response.data;
  } catch (error: any) {
    console.error('Error fetching ujian siswa detail:', error);
    throw new Error(error.response?.data?.error || 'Failed to fetch ujian siswa detail');
  }
};

export const getUjianSiswaSummary = async (ujianSiswaId: number): Promise<UjianSiswaSummaryData> => {
  try {
    const response = await api.get(`/api/teacher/ujian-siswa/${ujianSiswaId}/summary`);
    return response.data;
  } catch (error: any) {
    console.error('Error fetching ujian siswa summary:', error);
    throw new Error(error.response?.data?.error || 'Failed to fetch ujian siswa summary');
  }
};

export const getUjianSiswaComparisonAnalysis = async (ujianSiswaId: number): Promise<UjianSiswaComparisonResponse> => {
  try {
    const response = await api.get(`/api/teacher/ujian-siswa/${ujianSiswaId}/comparison-analysis`);
    return response.data;
  } catch (error: any) {
    console.error('Error fetching ujian siswa comparison analysis:', error);
    throw new Error(error.response?.data?.error || 'Failed to fetch ujian siswa comparison analysis');
  }
};

// Helper functions to process jawaban_json_result
export const parseJawabanJsonResult = (jsonResult: any) => {
  if (!jsonResult) return null;
  
  try {
    if (typeof jsonResult === 'string') {
      return JSON.parse(jsonResult);
    }
    return jsonResult;
  } catch (error) {
    console.error('Error parsing jawaban_json_result:', error);
    return null;
  }
};

export const extractComparisonFromJawabanResult = (jawabanJsonResult: any) => {
  const parsed = parseJawabanJsonResult(jawabanJsonResult);
  return parsed?.comparison || null;
};

export const extractStudentAnswerFromJawabanResult = (jawabanJsonResult: any) => {
  const parsed = parseJawabanJsonResult(jawabanJsonResult);
  return {
    student_answer: parsed?.student_answer || '',
    ai_analysis: parsed?.ai_analysis || {},
    comparison: parsed?.comparison || {}
  };
};

export const formatMathAnswer = (data: any) => {
  if (!data || !data.angka_dalam_soal) return '-';
  
  try {
    const numbers = data.angka_dalam_soal.split(',');
    if (numbers.length !== 2) return data.jawaban || '-';
    
    const [a, b] = numbers;
    let operator = '+';
    
    if (data.operator) {
      switch (data.operator.toLowerCase()) {
        case 'pengurangan':
        case 'kurang':
        case 'minus':
          operator = '-';
          break;
        case 'perkalian':
        case 'kali':
          operator = '×';
          break;
        case 'pembagian':
        case 'bagi':
          operator = '÷';
          break;
        default:
          operator = '+';
      }
    }
    
    return `${a} ${operator} ${b} = ${data.jawaban || '?'}`;
  } catch (error) {
    return data.jawaban || '-';
  }
}; 