#!/usr/bin/env python3
"""
Script untuk menambahkan kolom role ke tabel users yang sudah ada
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def add_role_column():
    try:
        # Get database configuration from environment variables or use defaults
        host = os.getenv('DB_HOST', 'localhost')
        user = os.getenv('DB_USER', 'root')
        password = os.getenv('DB_PASSWORD', '')
        database = os.getenv('DB_NAME', 'school_db')

        # Connect to MySQL server
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            cursor = connection.cursor()
            
            # Check if role column exists
            cursor.execute("SHOW COLUMNS FROM users LIKE 'role'")
            result = cursor.fetchone()
            
            if result:
                print("✅ Kolom 'role' sudah ada di tabel users")
            else:
                # Add role column
                cursor.execute("""
                    ALTER TABLE users 
                    ADD COLUMN role VARCHAR(20) DEFAULT 'admin' AFTER jenis_kelamin
                """)
                print("✅ Kolom 'role' berhasil ditambahkan ke tabel users")
            
            # Check if password column exists in siswa table
            cursor.execute("SHOW COLUMNS FROM siswa LIKE 'password'")
            result = cursor.fetchone()
            
            if result:
                print("✅ Kolom 'password' sudah ada di tabel siswa")
            else:
                # Add password column to siswa table
                cursor.execute("""
                    ALTER TABLE siswa 
                    ADD COLUMN password VARCHAR(255) NOT NULL DEFAULT 'default_password' AFTER kelas
                """)
                print("✅ Kolom 'password' berhasil ditambahkan ke tabel siswa")
            
            # Check if json_result column exists in soal table
            cursor.execute("SHOW COLUMNS FROM soal LIKE 'json_result'")
            result = cursor.fetchone()
            
            if result:
                print("✅ Kolom 'json_result' sudah ada di tabel soal")
            else:
                # Add json_result column to soal table
                cursor.execute("""
                    ALTER TABLE soal 
                    ADD COLUMN json_result JSON AFTER soal
                """)
                print("✅ Kolom 'json_result' berhasil ditambahkan ke tabel soal")
            
            # Check if json_result column exists in jawaban_siswa table
            cursor.execute("SHOW COLUMNS FROM jawaban_siswa LIKE 'json_result'")
            result = cursor.fetchone()
            
            if result:
                print("✅ Kolom 'json_result' sudah ada di tabel jawaban_siswa")
            else:
                # Add json_result column to jawaban_siswa table
                cursor.execute("""
                    ALTER TABLE jawaban_siswa 
                    ADD COLUMN json_result JSON AFTER status
                """)
                print("✅ Kolom 'json_result' berhasil ditambahkan ke tabel jawaban_siswa")
            
            connection.commit()
            print("\n✅ Semua kolom berhasil diperbarui!")

    except Error as e:
        print(f"❌ Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    print("🚀 School Management System - Database Migration Script")
    print("=" * 60)
    add_role_column() 