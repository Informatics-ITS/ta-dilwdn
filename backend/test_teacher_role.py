#!/usr/bin/env python3
"""
Script untuk testing role guru
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_teacher_login():
    """Test login guru"""
    print("🔐 Testing Teacher Login...")
    
    login_data = {
        "email": "guru@sekolah.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/api/teacher/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Login berhasil!")
        print(f"   Teacher: {data['teacher']['nama_lengkap']}")
        print(f"   Role: {data['teacher']['role']}")
        return True
    else:
        print(f"❌ Login gagal: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_create_kelas():
    """Test membuat kelas"""
    print("\n🏫 Testing Create Kelas...")
    
    # Login first
    login_data = {"email": "guru@sekolah.com", "password": "password123"}
    login_response = requests.post(f"{BASE_URL}/api/teacher/login", json=login_data)
    
    if login_response.status_code != 200:
        print("❌ Login gagal untuk test kelas")
        return False
    
    # Create kelas
    kelas_data = {
        "id": 1,
        "nama": "Kelas X IPA 1"
    }
    
    response = requests.post(f"{BASE_URL}/api/teacher/kelas", json=kelas_data)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Kelas berhasil dibuat!")
        print(f"   ID: {data['kelas']['id']}")
        print(f"   Nama: {data['kelas']['nama']}")
        return True
    else:
        print(f"❌ Gagal membuat kelas: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_create_siswa():
    """Test membuat siswa"""
    print("\n👨‍🎓 Testing Create Siswa...")
    
    # Login first
    login_data = {"email": "guru@sekolah.com", "password": "password123"}
    login_response = requests.post(f"{BASE_URL}/api/teacher/login", json=login_data)
    
    if login_response.status_code != 200:
        print("❌ Login gagal untuk test siswa")
        return False
    
    # Create siswa
    siswa_data = {
        "NISN": "1234567890",
        "nama_siswa": "John Doe",
        "kelas": 1
    }
    
    response = requests.post(f"{BASE_URL}/api/teacher/siswa", json=siswa_data)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Siswa berhasil dibuat!")
        print(f"   NISN: {data['siswa']['NISN']}")
        print(f"   Nama: {data['siswa']['nama_siswa']}")
        print(f"   Kelas: {data['siswa']['kelas']}")
        print("   Password default: NISN (1234567890)")
        return True
    else:
        print(f"❌ Gagal membuat siswa: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_dashboard():
    """Test dashboard guru"""
    print("\n📊 Testing Teacher Dashboard...")
    
    # Login first
    login_data = {"email": "guru@sekolah.com", "password": "password123"}
    login_response = requests.post(f"{BASE_URL}/api/teacher/login", json=login_data)
    
    if login_response.status_code != 200:
        print("❌ Login gagal untuk test dashboard")
        return False
    
    response = requests.get(f"{BASE_URL}/api/teacher/dashboard")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Dashboard berhasil diakses!")
        print(f"   Total Kelas: {data['statistics']['total_kelas']}")
        print(f"   Total Siswa: {data['statistics']['total_siswa']}")
        print(f"   Total Ujian: {data['statistics']['total_ujian']}")
        
        if data['kelas']:
            print("   Daftar Kelas:")
            for kelas in data['kelas']:
                print(f"     - {kelas['nama']} ({kelas['total_siswa']} siswa)")
        
        return True
    else:
        print(f"❌ Gagal mengakses dashboard: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_student_login():
    """Test login siswa dengan password default NISN"""
    print("\n👨‍🎓 Testing Student Login...")
    
    login_data = {
        "nisn": "1234567890",
        "password": "1234567890"  # Default password = NISN
    }
    
    response = requests.post(f"{BASE_URL}/api/student/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Siswa berhasil login!")
        print(f"   NISN: {data['siswa']['NISN']}")
        print(f"   Nama: {data['siswa']['nama_siswa']}")
        print(f"   Kelas: {data['siswa']['kelas']}")
        return True
    else:
        print(f"❌ Login siswa gagal: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def main():
    print("🚀 School Management System - Teacher Role Testing")
    print("=" * 60)
    
    # Test teacher login
    if not test_teacher_login():
        print("❌ Test teacher login gagal, berhenti testing")
        return
    
    # Test create kelas
    test_create_kelas()
    
    # Test create siswa
    test_create_siswa()
    
    # Test dashboard
    test_dashboard()
    
    # Test student login
    test_student_login()
    
    print("\n" + "=" * 60)
    print("✅ Testing selesai!")
    print("\n📝 Catatan:")
    print("- Guru dapat login dengan email dan password")
    print("- Siswa dapat login dengan NISN dan password NISN")
    print("- Password default siswa adalah NISN")
    print("- Semua endpoint guru memerlukan role 'guru'")

if __name__ == "__main__":
    main() 