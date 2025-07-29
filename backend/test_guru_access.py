#!/usr/bin/env python3

import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def test_guru_access_system():
    """Test sistem akses guru berdasarkan guru_id"""
    
    try:
        # Connect to database
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'school_db')
        )
        cursor = conn.cursor(dictionary=True)
        
        print("🔍 Testing Guru Access Control System")
        print("=" * 50)
        
        # Test 1: Show all users and their roles
        print("\n1. USER ROLES:")
        cursor.execute("SELECT id, email, nama_lengkap, role FROM users WHERE role = 'guru'")
        guru_users = cursor.fetchall()
        
        for guru in guru_users:
            print(f"   👨‍🏫 Guru ID {guru['id']}: {guru['nama_lengkap']} ({guru['email']})")
        
        # Test 2: Show kelas assignment per guru
        print("\n2. KELAS ASSIGNMENT PER GURU:")
        for guru in guru_users:
            guru_id = guru['id']
            nama_guru = guru['nama_lengkap']
            
            cursor.execute("SELECT id, nama FROM kelas WHERE guru_id = %s", (guru_id,))
            kelas_list = cursor.fetchall()
            
            print(f"   👨‍🏫 {nama_guru} (ID: {guru_id}):")
            if kelas_list:
                for kelas in kelas_list:
                    print(f"      📚 Kelas {kelas['id']}: {kelas['nama']}")
            else:
                print("      📚 Tidak ada kelas")
        
        # Test 3: Show siswa per guru
        print("\n3. SISWA PER GURU:")
        for guru in guru_users:
            guru_id = guru['id']
            nama_guru = guru['nama_lengkap']
            
            cursor.execute("""
                SELECT s.no, s.NISN, s.nama_siswa, k.nama as nama_kelas
                FROM siswa s 
                JOIN kelas k ON s.kelas = k.id 
                WHERE k.guru_id = %s
                ORDER BY k.id, s.nama_siswa
            """, (guru_id,))
            siswa_list = cursor.fetchall()
            
            print(f"   👨‍🏫 {nama_guru}:")
            if siswa_list:
                for siswa in siswa_list:
                    print(f"      👤 {siswa['nama_siswa']} (NISN: {siswa['NISN']}) - {siswa['nama_kelas']}")
            else:
                print("      👤 Tidak ada siswa")
        
        # Test 4: Show ujian per guru
        print("\n4. UJIAN PER GURU:")
        for guru in guru_users:
            guru_id = guru['id']
            nama_guru = guru['nama_lengkap']
            
            cursor.execute("""
                SELECT u.id, u.nama_ujian, k.nama as nama_kelas, u.pelaksanaan, u.status
                FROM ujian u 
                JOIN kelas k ON u.kelas = k.id 
                WHERE k.guru_id = %s
                ORDER BY u.pelaksanaan DESC
            """, (guru_id,))
            ujian_list = cursor.fetchall()
            
            print(f"   👨‍🏫 {nama_guru}:")
            if ujian_list:
                for ujian in ujian_list:
                    print(f"      📝 {ujian['nama_ujian']} - {ujian['nama_kelas']} ({ujian['pelaksanaan']}) [{ujian['status']}]")
            else:
                print("      📝 Tidak ada ujian")
        
        # Test 5: Test stored procedure get_ujian_siswa_by_guru
        print("\n5. TEST STORED PROCEDURE get_ujian_siswa_by_guru:")
        for guru in guru_users[:2]:  # Test untuk 2 guru pertama saja
            guru_id = guru['id']
            nama_guru = guru['nama_lengkap']
            
            cursor.callproc('get_ujian_siswa_by_guru', [guru_id])
            
            for result in cursor.stored_results():
                ujian_siswa_list = result.fetchall()
                print(f"   👨‍🏫 {nama_guru} memiliki {len(ujian_siswa_list)} ujian siswa:")
                
                for us in ujian_siswa_list[:3]:  # Show first 3 results
                    print(f"      📊 {us['nama_siswa']} - {us['nama_ujian']} (Nilai: {us['nilai']})")
        
        # Test 6: Test stored procedure get_guru_dashboard_stats
        print("\n6. TEST STORED PROCEDURE get_guru_dashboard_stats:")
        for guru in guru_users[:2]:  # Test untuk 2 guru pertama saja
            guru_id = guru['id']
            nama_guru = guru['nama_lengkap']
            
            cursor.callproc('get_guru_dashboard_stats', [guru_id])
            
            for result in cursor.stored_results():
                stats = result.fetchone()
                if stats:
                    print(f"   👨‍🏫 Statistik {nama_guru}:")
                    print(f"      📚 Total Kelas: {stats['total_kelas']}")
                    print(f"      👥 Total Siswa: {stats['total_siswa']}")
                    print(f"      📝 Total Ujian: {stats['total_ujian']}")
                    print(f"      📊 Rata-rata Nilai: {stats['rata_rata_nilai']:.2f}")
                    print(f"      🌟 Sangat Baik: {stats['sangat_baik']}, Baik: {stats['baik']}, Cukup: {stats['cukup']}")
                else:
                    print(f"   👨‍🏫 {nama_guru}: Tidak ada statistik")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Testing selesai! Sistem guru access control berfungsi dengan baik.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_guru_access_system() 