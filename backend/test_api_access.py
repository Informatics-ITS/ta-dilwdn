#!/usr/bin/env python3

import requests
import json

BASE_URL = "http://localhost:5000"

def test_guru_api_access():
    """Test akses API guru untuk memastikan hanya melihat data kelas mereka"""
    
    print("🔧 Testing Guru API Access Control")
    print("=" * 50)
    
    # Test login untuk setiap guru
    gurus = [
        {"email": "guru@school.com", "password": "guru123", "nama": "Guru Matematika"},
        {"email": "guru2@school.com", "password": "guru123", "nama": "Guru Fisika"},
        {"email": "guru3@school.com", "password": "guru123", "nama": "Guru Kimia"}
    ]
    
    for guru in gurus:
        print(f"\n👨‍🏫 Testing login untuk {guru['nama']} ({guru['email']})")
        
        # Login
        login_data = {
            "email": guru["email"],
            "password": guru["password"]
        }
        
        session = requests.Session()
        
        try:
            # Test login
            login_response = session.post(f"{BASE_URL}/api/login", json=login_data)
            if login_response.status_code == 200:
                print(f"   ✅ Login berhasil untuk {guru['nama']}")
                
                # Test endpoint /api/kelas
                kelas_response = session.get(f"{BASE_URL}/api/kelas")
                if kelas_response.status_code == 200:
                    kelas_data = kelas_response.json()
                    print(f"   📚 Kelas yang terlihat: {len(kelas_data)} kelas")
                    for kelas in kelas_data:
                        print(f"      - {kelas['nama']} (ID: {kelas['id']}, Guru ID: {kelas.get('guru_id', 'N/A')})")
                else:
                    print(f"   ❌ Error getting kelas: {kelas_response.status_code}")
                
                # Test endpoint /api/teacher/kelas
                teacher_kelas_response = session.get(f"{BASE_URL}/api/teacher/kelas")
                if teacher_kelas_response.status_code == 200:
                    teacher_kelas_data = teacher_kelas_response.json()
                    print(f"   👨‍🏫 Teacher kelas: {len(teacher_kelas_data)} kelas")
                    for kelas in teacher_kelas_data:
                        print(f"      - {kelas['nama']} (ID: {kelas['id']}, Siswa: {kelas['total_siswa']})")
                else:
                    print(f"   ❌ Error getting teacher kelas: {teacher_kelas_response.status_code}")
                
                # Test endpoint /api/ujian
                ujian_response = session.get(f"{BASE_URL}/api/ujian")
                if ujian_response.status_code == 200:
                    ujian_data = ujian_response.json()
                    print(f"   📝 Ujian yang terlihat: {len(ujian_data)} ujian")
                    for ujian in ujian_data:
                        print(f"      - {ujian['nama_ujian']} (Kelas: {ujian['kelas']})")
                else:
                    print(f"   ❌ Error getting ujian: {ujian_response.status_code}")
                
                # Test dashboard
                dashboard_response = session.get(f"{BASE_URL}/api/teacher/dashboard")
                if dashboard_response.status_code == 200:
                    dashboard_data = dashboard_response.json()
                    stats = dashboard_data.get('statistics', {})
                    print(f"   📊 Dashboard stats:")
                    print(f"      - Total Kelas: {stats.get('total_kelas', 0)}")
                    print(f"      - Total Siswa: {stats.get('total_siswa', 0)}")
                    print(f"      - Total Ujian: {stats.get('total_ujian', 0)}")
                else:
                    print(f"   ❌ Error getting dashboard: {dashboard_response.status_code}")
                
                # Logout
                logout_response = session.post(f"{BASE_URL}/api/teacher/logout")
                if logout_response.status_code == 200:
                    print(f"   🚪 Logout berhasil untuk {guru['nama']}")
                else:
                    print(f"   ❌ Error logout: {logout_response.status_code}")
                    
            else:
                print(f"   ❌ Login gagal untuk {guru['nama']}: {login_response.status_code}")
                if login_response.status_code == 401:
                    print(f"      Response: {login_response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Tidak bisa koneksi ke server. Pastikan Flask app berjalan di {BASE_URL}")
            break
        except Exception as e:
            print(f"   ❌ Error testing {guru['nama']}: {e}")
    
    print(f"\n✅ Testing selesai!")
    print(f"\n💡 Catatan:")
    print(f"   - Pastikan Flask app berjalan dengan: python app.py")
    print(f"   - Setiap guru seharusnya hanya melihat kelas mereka sendiri")
    print(f"   - Guru Matematika: Kelas 1, 4, 99")
    print(f"   - Guru Fisika: Kelas 2") 
    print(f"   - Guru Kimia: Kelas 3")

if __name__ == '__main__':
    test_guru_api_access() 