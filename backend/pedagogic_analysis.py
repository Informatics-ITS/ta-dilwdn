#!/usr/bin/env python3
"""
Modul Analisis Pedagogik menggunakan Gemini 2.0 Flash
"""

import google.generativeai as genai
import os
import json
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PedagogicAnalyzer:
    """Kelas untuk analisis pedagogik menggunakan Gemini 2.0 Flash"""
    
    def __init__(self):
        """Inisialisasi Gemini AI"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY tidak ditemukan di environment variables")
        
        genai.configure(api_key=api_key)
        
        # Menggunakan model Gemini 2.0 Flash
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # System prompt untuk analisis pedagogik
        self.system_prompt = """
        Anda adalah seorang ahli pedagogik dan psikologi pendidikan yang berpengalaman dalam menganalisis hasil belajar siswa. 
        Tugas Anda adalah memberikan analisis mendalam tentang:
        
        1. **Analisis Kemampuan Kognitif**: Menilai tingkat pemahaman, aplikasi, dan analisis siswa
        2. **Analisis Kesalahan**: Mengidentifikasi pola kesalahan dan penyebabnya
        3. **Rekomendasi Pembelajaran**: Memberikan saran untuk perbaikan dan pengembangan
        4. **Analisis Pedagogik**: Menilai aspek pedagogik dari jawaban siswa
        5. **Strategi Remedial**: Memberikan strategi pembelajaran remedial yang tepat
        
        Berikan analisis yang:
        - Objektif dan berdasarkan data
        - Konstruktif dan mendukung perkembangan siswa
        - Spesifik dan dapat ditindaklanjuti
        - Menggunakan bahasa yang mudah dipahami
        """
    
    def analyze_student_answer(self, soal_data: Dict, jawaban_siswa: Dict, hasil_analisis: Dict) -> Dict[str, Any]:
        """
        Menganalisis jawaban siswa secara pedagogik
        
        Args:
            soal_data: Data soal yang dijawab
            jawaban_siswa: Jawaban yang diberikan siswa
            hasil_analisis: Hasil analisis teknis (operator, angka, jawaban)
        
        Returns:
            Dict berisi analisis pedagogik lengkap
        """
        
        # Menyusun prompt untuk analisis
        prompt = f"""
        {self.system_prompt}
        
        **DATA SOAL:**
        - Soal: {soal_data.get('soal', 'Tidak tersedia')}
        - Jenis Operasi: {hasil_analisis.get('operator', 'Tidak diketahui')}
        - Angka dalam Soal: {hasil_analisis.get('angka_dalam_soal', 'Tidak diketahui')}
        - Jawaban Benar: {hasil_analisis.get('jawaban', 'Tidak diketahui')}
        
        **JAWABAN SISWA:**
        - Operator yang Dikenali: {jawaban_siswa.get('operator', 'Tidak diketahui')}
        - Angka yang Dikenali: {jawaban_siswa.get('angka_dalam_soal', 'Tidak diketahui')}
        - Jawaban Siswa: {jawaban_siswa.get('jawaban', 'Tidak diketahui')}
        
        **HASIL ANALISIS TEKNIS:**
        - Status: {hasil_analisis.get('status', 'Tidak diketahui')}
        - Nilai: {hasil_analisis.get('nilai', 0)}/3
        - Parameter yang Benar: {', '.join(hasil_analisis.get('correct_parameters', []))}
        - Parameter yang Salah: {', '.join(hasil_analisis.get('wrong_parameters', []))}
        
        Berikan analisis pedagogik yang mendalam dalam format JSON dengan struktur berikut:
        {{
            "analisis_kognitif": {{
                "tingkat_pemahaman": "string",
                "kemampuan_aplikasi": "string",
                "kemampuan_analisis": "string",
                "kesimpulan_kognitif": "string"
            }},
            "analisis_kesalahan": {{
                "jenis_kesalahan": "string",
                "penyebab_kesalahan": "string",
                "pola_kesalahan": "string",
                "kesimpulan_kesalahan": "string"
            }},
            "rekomendasi_pembelajaran": {{
                "strategi_pembelajaran": "string",
                "materi_penguatan": "string",
                "metode_remedial": "string",
                "alat_bantu": "string"
            }},
            "analisis_pedagogik": {{
                "aspek_pedagogik": "string",
                "pendekatan_pembelajaran": "string",
                "evaluasi_formatif": "string",
                "kesimpulan_pedagogik": "string"
            }},
            "strategi_remedial": {{
                "jenis_remedial": "string",
                "durasi_remedial": "string",
                "metode_evaluasi": "string",
                "target_pencapaian": "string"
            }},
            "ringkasan_analisis": "string"
        }}
        
        Pastikan analisis Anda:
        1. Berdasarkan data yang diberikan
        2. Menggunakan terminologi pedagogik yang tepat
        3. Memberikan rekomendasi yang praktis dan dapat diterapkan
        4. Mempertimbangkan aspek psikologis dan kognitif siswa
        5. Menggunakan bahasa yang konstruktif dan mendukung
        """
        
        try:
            # Generate response dari Gemini
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            analysis_result = json.loads(response.text)
            
            return {
                "status": "success",
                "analisis_pedagogik": analysis_result,
                "model_used": "gemini-2.0-flash-exp",
                "timestamp": self._get_timestamp()
            }
            
        except json.JSONDecodeError as e:
            # Jika response bukan JSON valid, coba parse manual
            return self._parse_text_response(response.text)
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Gagal melakukan analisis pedagogik"
            }
    
    def analyze_class_performance(self, data_kelas: List[Dict]) -> Dict[str, Any]:
        """
        Menganalisis performa kelas secara keseluruhan
        
        Args:
            data_kelas: List data siswa dalam kelas dengan hasil ujian
        
        Returns:
            Dict berisi analisis performa kelas
        """
        
        # Menyusun statistik kelas
        total_siswa = len(data_kelas)
        nilai_tinggi = 0
        nilai_rendah = 0
        nilai_menengah = 0
        
        for siswa in data_kelas:
            nilai = siswa.get('nilai', 0)
            if nilai >= 80:
                nilai_tinggi += 1
            elif nilai >= 60:
                nilai_menengah += 1
            else:
                nilai_rendah += 1
        
        prompt = f"""
        {self.system_prompt}
        
        **DATA PERFORMA KELAS:**
        - Total Siswa: {total_siswa}
        - Siswa dengan Nilai Tinggi (≥80): {nilai_tinggi}
        - Siswa dengan Nilai Menengah (60-79): {nilai_menengah}
        - Siswa dengan Nilai Rendah (<60): {nilai_rendah}
        
        **DETAIL SISWA:**
        {json.dumps(data_kelas, indent=2, ensure_ascii=False)}
        
        Berikan analisis pedagogik untuk performa kelas ini dalam format JSON:
        {{
            "analisis_performa_kelas": {{
                "distribusi_nilai": "string",
                "kekuatan_kelas": "string",
                "kelemahan_kelas": "string",
                "trend_pembelajaran": "string"
            }},
            "rekomendasi_pembelajaran_kelas": {{
                "strategi_umum": "string",
                "pembelajaran_diferensiasi": "string",
                "pengelompokan_siswa": "string",
                "evaluasi_kelas": "string"
            }},
            "analisis_pedagogik_kelas": {{
                "pendekatan_pembelajaran": "string",
                "metode_evaluasi": "string",
                "intervensi_pedagogik": "string",
                "kesimpulan_kelas": "string"
            }},
            "rencana_pengembangan": {{
                "target_peningkatkan": "string",
                "strategi_intervensi": "string",
                "timeline": "string",
                "indikator_keberhasilan": "string"
            }}
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            analysis_result = json.loads(response.text)
            
            return {
                "status": "success",
                "analisis_kelas": analysis_result,
                "statistik_kelas": {
                    "total_siswa": total_siswa,
                    "nilai_tinggi": nilai_tinggi,
                    "nilai_menengah": nilai_menengah,
                    "nilai_rendah": nilai_rendah,
                    "persentase_tinggi": round((nilai_tinggi/total_siswa)*100, 2) if total_siswa > 0 else 0,
                    "persentase_menengah": round((nilai_menengah/total_siswa)*100, 2) if total_siswa > 0 else 0,
                    "persentase_rendah": round((nilai_rendah/total_siswa)*100, 2) if total_siswa > 0 else 0
                },
                "model_used": "gemini-2.0-flash-exp",
                "timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Gagal melakukan analisis performa kelas"
            }
    
    def analyze_learning_patterns(self, data_siswa: List[Dict]) -> Dict[str, Any]:
        """
        Menganalisis pola pembelajaran siswa
        
        Args:
            data_siswa: List data ujian siswa dalam beberapa periode
        
        Returns:
            Dict berisi analisis pola pembelajaran
        """
        
        prompt = f"""
        {self.system_prompt}
        
        **DATA POLA PEMBELAJARAN SISWA:**
        {json.dumps(data_siswa, indent=2, ensure_ascii=False)}
        
        Berikan analisis pola pembelajaran dalam format JSON:
        {{
            "analisis_pola_pembelajaran": {{
                "trend_perkembangan": "string",
                "konsistensi_pembelajaran": "string",
                "area_perbaikan": "string",
                "potensi_pengembangan": "string"
            }},
            "rekomendasi_pembelajaran_individu": {{
                "strategi_personal": "string",
                "metode_pembelajaran": "string",
                "alat_bantu": "string",
                "evaluasi_berkelanjutan": "string"
            }},
            "analisis_pedagogik_individu": {{
                "gaya_belajar": "string",
                "motivasi_pembelajaran": "string",
                "hambatan_pembelajaran": "string",
                "kesimpulan_individu": "string"
            }}
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            analysis_result = json.loads(response.text)
            
            return {
                "status": "success",
                "analisis_pola": analysis_result,
                "model_used": "gemini-2.0-flash-exp",
                "timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Gagal melakukan analisis pola pembelajaran"
            }
    
    def analyze_text(self, text: str) -> str:
        """
        Analisis pedagogik untuk teks bebas (analisis narasi atau jawaban esai)
        Args:
            text: Teks yang akan dianalisis
        Returns:
            String hasil analisis pedagogik
        """
        prompt = f"""
    Anda adalah seorang ahli pedagogik dan psikologi pendidikan yang berpengalaman dalam menganalisis hasil belajar siswa sekolah dasar.

    Kompetensi analisis:
    1. Siswa mampu mengenali operand 1
    2. Siswa mampu mengenali operand 2
    3. Siswa mampu mengenali operator (penjumlahan, pengurangan, perkalian, atau pembagian)
    4. Siswa mampu mengoperasikan
    a. (penjumlahan atau pengurangan) bilangan cacah (hingga 20, hingga 100, hingga 1000)
    b. (perkalian atau pembagian) bilangan cacah hingga 100

    Teks berikut adalah hasil jawaban atau narasi siswa:
    \"{text}\"

    Buatlah analisis pedagogik dalam bentuk narasi paragraf (bukan JSON), yang menjelaskan kemampuan siswa berdasarkan kompetensi di atas, serta berikan saran atau rekomendasi pembelajaran jika diperlukan. Gunakan bahasa yang jelas, singkat, dan mudah dipahami guru.
    """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Gagal melakukan analisis pedagogik pada teks: {str(e)}"
    
    def _parse_text_response(self, text_response: str) -> Dict[str, Any]:
        """Parse response text jika JSON parsing gagal"""
        return {
            "status": "success",
            "analisis_pedagogik": {
                "analisis_kognitif": {
                    "tingkat_pemahaman": "Analisis berdasarkan response AI",
                    "kemampuan_aplikasi": "Dianalisis dari pola jawaban",
                    "kemampuan_analisis": "Dievaluasi dari ketepatan",
                    "kesimpulan_kognitif": "Berdasarkan hasil analisis AI"
                },
                "analisis_kesalahan": {
                    "jenis_kesalahan": "Dianalisis dari parameter yang salah",
                    "penyebab_kesalahan": "Berdasarkan pola kesalahan",
                    "pola_kesalahan": "Ditemukan dari analisis berulang",
                    "kesimpulan_kesalahan": "Berdasarkan analisis AI"
                },
                "rekomendasi_pembelajaran": {
                    "strategi_pembelajaran": "Disesuaikan dengan kebutuhan",
                    "materi_penguatan": "Berdasarkan area lemah",
                    "metode_remedial": "Strategi perbaikan yang tepat",
                    "alat_bantu": "Sesuai dengan kebutuhan pembelajaran"
                },
                "analisis_pedagogik": {
                    "aspek_pedagogik": "Dianalisis secara komprehensif",
                    "pendekatan_pembelajaran": "Disesuaikan dengan karakteristik",
                    "evaluasi_formatif": "Berbasis data dan observasi",
                    "kesimpulan_pedagogik": "Berdasarkan analisis mendalam"
                },
                "strategi_remedial": {
                    "jenis_remedial": "Disesuaikan dengan kesalahan",
                    "durasi_remedial": "Berdasarkan tingkat kesulitan",
                    "metode_evaluasi": "Evaluasi berkelanjutan",
                    "target_pencapaian": "Target yang realistis dan terukur"
                },
                "ringkasan_analisis": text_response[:500] + "..." if len(text_response) > 500 else text_response
            },
            "model_used": "gemini-2.0-flash-exp",
            "timestamp": self._get_timestamp(),
            "note": "Response di-parse manual karena format JSON tidak valid"
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

# Singleton instance
_pedagogic_analyzer = None

def get_pedagogic_analyzer() -> PedagogicAnalyzer:
    """Get singleton instance of PedagogicAnalyzer"""
    global _pedagogic_analyzer
    if _pedagogic_analyzer is None:
        _pedagogic_analyzer = PedagogicAnalyzer()
    return _pedagogic_analyzer 