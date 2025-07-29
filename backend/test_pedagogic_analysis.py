#!/usr/bin/env python3
"""
Script untuk testing analisis pedagogik menggunakan Gemini 2.0 Flash
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:5000"

def test_pedagogic_analysis_status():
    """Test status analisis pedagogik"""
    print("🔍 Testing Pedagogic Analysis Status...")
    
    response = requests.get(f"{BASE_URL}/api/pedagogic/status")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Status analisis pedagogik:")
        print(f"   Available: {data['available']}")
        print(f"   Model: {data['model']}")
        print(f"   Message: {data['message']}")
        return data['available']
    else:
        print(f"❌ Gagal mendapatkan status: {response.status_code}")
        return False

def test_teacher_login():
    """Test login guru"""
    print("\n🔐 Testing Teacher Login...")
    
    login_data = {
        "email": "guru@sekolah.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/api/teacher/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Login guru berhasil!")
        print(f"   Teacher: {data['teacher']['nama_lengkap']}")
        print(f"   Role: {data['teacher']['role']}")
        return True
    else:
        print(f"❌ Login gagal: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_create_sample_data():
    """Membuat data sample untuk testing"""
    print("\n📝 Creating Sample Data...")
    
    # Login first
    login_data = {"email": "guru@sekolah.com", "password": "password123"}
    login_response = requests.post(f"{BASE_URL}/api/teacher/login", json=login_data)
    
    if login_response.status_code != 200:
        print("❌ Login gagal untuk membuat data sample")
        return False
    
    # Create kelas
    kelas_data = {"id": 1, "nama": "Kelas X IPA 1"}
    kelas_response = requests.post(f"{BASE_URL}/api/teacher/kelas", json=kelas_data)
    
    if kelas_response.status_code != 200:
        print("❌ Gagal membuat kelas")
        return False
    
    # Create siswa
    siswa_data = {
        "NISN": "1234567890",
        "nama_siswa": "John Doe",
        "kelas": 1
    }
    siswa_response = requests.post(f"{BASE_URL}/api/teacher/siswa", json=siswa_data)
    
    if siswa_response.status_code != 200:
        print("❌ Gagal membuat siswa")
        return False
    
    print("✅ Data sample berhasil dibuat!")
    return True

def test_analyze_student_answer():
    """Test analisis jawaban siswa"""
    print("\n🧠 Testing Student Answer Analysis...")
    
    # Login first
    login_data = {"email": "guru@sekolah.com", "password": "password123"}
    login_response = requests.post(f"{BASE_URL}/api/teacher/login", json=login_data)
    
    if login_response.status_code != 200:
        print("❌ Login gagal untuk analisis")
        return False
    
    # Sample data untuk testing
    analysis_data = {
        "soal_id": 1,  # Assuming soal exists
        "jawaban_siswa_id": 1  # Assuming jawaban exists
    }
    
    response = requests.post(f"{BASE_URL}/api/pedagogic/analyze-answer", json=analysis_data)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Analisis jawaban siswa berhasil!")
        print(f"   Status: {data['status']}")
        if data['status'] == 'success':
            analysis = data['analisis_pedagogik']
            print(f"   Model: {data['model_used']}")
            print(f"   Analisis Kognitif: {analysis['analisis_kognitif']['kesimpulan_kognitif'][:100]}...")
            print(f"   Rekomendasi: {analysis['rekomendasi_pembelajaran']['strategi_pembelajaran'][:100]}...")
        return True
    elif response.status_code == 503:
        print("⚠️  Analisis pedagogik tidak tersedia (perlu install google-generativeai)")
        return False
    else:
        print(f"❌ Gagal analisis: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_analyze_class_performance():
    """Test analisis performa kelas"""
    print("\n📊 Testing Class Performance Analysis...")
    
    # Login first
    login_data = {"email": "guru@sekolah.com", "password": "password123"}
    login_response = requests.post(f"{BASE_URL}/api/teacher/login", json=login_data)
    
    if login_response.status_code != 200:
        print("❌ Login gagal untuk analisis kelas")
        return False
    
    response = requests.get(f"{BASE_URL}/api/pedagogic/analyze-class/1")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Analisis performa kelas berhasil!")
        print(f"   Status: {data['status']}")
        if data['status'] == 'success':
            print(f"   Total Siswa: {data['statistik_kelas']['total_siswa']}")
            print(f"   Nilai Tinggi: {data['statistik_kelas']['nilai_tinggi']}")
            print(f"   Model: {data['model_used']}")
        return True
    elif response.status_code == 503:
        print("⚠️  Analisis pedagogik tidak tersedia (perlu install google-generativeai)")
        return False
    else:
        print(f"❌ Gagal analisis kelas: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_analyze_student_patterns():
    """Test analisis pola pembelajaran siswa"""
    print("\n📈 Testing Student Learning Patterns Analysis...")
    
    # Login first
    login_data = {"email": "guru@sekolah.com", "password": "password123"}
    login_response = requests.post(f"{BASE_URL}/api/teacher/login", json=login_data)
    
    if login_response.status_code != 200:
        print("❌ Login gagal untuk analisis pola")
        return False
    
    response = requests.get(f"{BASE_URL}/api/pedagogic/analyze-student/1")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Analisis pola pembelajaran berhasil!")
        print(f"   Status: {data['status']}")
        if data['status'] == 'success':
            print(f"   Model: {data['model_used']}")
        return True
    elif response.status_code == 503:
        print("⚠️  Analisis pedagogik tidak tersedia (perlu install google-generativeai)")
        return False
    else:
        print(f"❌ Gagal analisis pola: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def main():
    print("🚀 School Management System - Pedagogic Analysis Testing")
    print("=" * 70)
    
    # Test status
    status_available = test_pedagogic_analysis_status()
    
    if not status_available:
        print("\n⚠️  Analisis pedagogik tidak tersedia!")
        print("   Untuk mengaktifkan, install package google-generativeai:")
        print("   pip install google-generativeai==0.3.2")
        print("   Dan set environment variable GEMINI_API_KEY")
        return
    
    # Test login
    if not test_teacher_login():
        print("❌ Login gagal, berhenti testing")
        return
    
    # Create sample data
    test_create_sample_data()
    
    # Test analisis pedagogik
    test_analyze_student_answer()
    test_analyze_class_performance()
    test_analyze_student_patterns()
    
    print("\n" + "=" * 70)
    print("✅ Testing selesai!")
    print("\n📝 Catatan:")
    print("- Analisis pedagogik menggunakan Gemini 2.0 Flash")
    print("- Semua endpoint memerlukan role guru")
    print("- Hasil analisis disimpan di database")
    print("- Analisis mencakup aspek kognitif, kesalahan, dan rekomendasi")

if __name__ == "__main__":
    main() 