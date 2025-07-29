#!/usr/bin/env python3

import mysql.connector
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'school_db')
    )

def test_stored_procedure():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # First, let's check if we have any ujian_siswa data
        cursor.execute("SELECT COUNT(*) as count FROM ujian_siswa")
        count_result = cursor.fetchone()
        print(f"Total ujian_siswa records: {count_result['count']}")
        
        if count_result['count'] == 0:
            print("No ujian_siswa data found. Creating sample data...")
            
            # Create sample data for testing
            # Insert sample kelas
            cursor.execute("INSERT IGNORE INTO kelas (id, nama) VALUES (1, 'Kelas 7A')")
            
            # Insert sample user 
            cursor.execute("""
                INSERT IGNORE INTO users (id, email, password, nama_lengkap, jenis_kelamin, role) 
                VALUES (1, 'siswa1@test.com', 'password', 'Test Siswa', 'Laki-laki', 'siswa')
            """)
            
            # Insert sample siswa
            cursor.execute("""
                INSERT IGNORE INTO siswa (no, NISN, nama_siswa, kelas, user_id) 
                VALUES (1, '1234567890', 'Test Siswa', 1, 1)
            """)
            
            # Insert sample ujian
            cursor.execute("""
                INSERT IGNORE INTO ujian (id, nama_ujian, kelas, pelaksanaan, status) 
                VALUES (1, 'Test Ujian Matematika', 1, '2024-01-15', 'aktif')
            """)
            
            # Insert sample ujian_siswa
            cursor.execute("""
                INSERT IGNORE INTO ujian_siswa (id, ujian, siswa, nilai, label_nilai, deskripsi_analisis) 
                VALUES (1, 1, 1, 85, 'Baik', 'Test deskripsi analisis')
            """)
            
            # Insert sample soal
            cursor.execute("""
                INSERT IGNORE INTO soal (id, soal, ujian, json_result) 
                VALUES (1, '5 + 3 = ?', 1, '{"angka_dalam_soal": "5,3", "operator": "Penjumlahan", "jawaban": "8"}')
            """)
            
            # Insert sample jawaban_siswa
            cursor.execute("""
                INSERT IGNORE INTO jawaban_siswa (id, nisn, soal, status, json_result) 
                VALUES (1, '1234567890', 1, 'correct', 
                '{"student_answer": "5+3=8", "ai_analysis": {"angka_dalam_soal": "5,3", "operator": "Penjumlahan", "jawaban": "8"}, "comparison": {"status": "correct", "nilai": 3, "deskripsi_analisis": "Jawaban benar"}}')
            """)
            
            conn.commit()
            print("Sample data created successfully!")
        
        # Test the stored procedure
        print("\nTesting stored procedure with ujian_siswa_id = 1...")
        
        cursor.callproc('get_ujian_siswa_detail', [1])
        
        results = []
        for result in cursor.stored_results():
            data = result.fetchall()
            results.extend(data)
        
        print(f"Retrieved {len(results)} records")
        
        if results:
            print("\nFirst record structure:")
            for key, value in results[0].items():
                value_type = type(value).__name__
                if isinstance(value, (bytes, bytearray)):
                    try:
                        decoded = value.decode('utf-8')
                        print(f"  {key}: {value_type} -> {decoded[:100]}...")
                    except:
                        print(f"  {key}: {value_type} (binary data, length: {len(value)})")
                else:
                    print(f"  {key}: {value_type} -> {value}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_stored_procedure() 