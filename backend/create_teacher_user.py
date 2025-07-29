#!/usr/bin/env python3
"""
Script untuk membuat user guru contoh
"""

import os
import sys
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User

# Load environment variables
load_dotenv()

def create_teacher_user():
    """Membuat user guru contoh"""
    
    with app.app_context():
        # Check if teacher user already exists
        existing_teacher = User.query.filter_by(email='guru@sekolah.com').first()
        if existing_teacher:
            print("User guru sudah ada!")
            print(f"Email: {existing_teacher.email}")
            print(f"Nama: {existing_teacher.nama_lengkap}")
            print(f"Role: {existing_teacher.role}")
            return
        
        # Create teacher user
        teacher = User(
            email='guru@sekolah.com',
            password=generate_password_hash('password123'),
            nama_lengkap='Guru Matematika',
            jenis_kelamin='laki-laki',
            role='guru'
        )
        
        try:
            db.session.add(teacher)
            db.session.commit()
            print("✅ User guru berhasil dibuat!")
            print(f"Email: {teacher.email}")
            print(f"Password: password123")
            print(f"Nama: {teacher.nama_lengkap}")
            print(f"Role: {teacher.role}")
            print("\nAnda dapat login menggunakan:")
            print("POST /api/teacher/login")
            print("Body: {\"email\": \"guru@sekolah.com\", \"password\": \"password123\"}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error membuat user guru: {str(e)}")

def create_admin_user():
    """Membuat user admin contoh"""
    
    with app.app_context():
        # Check if admin user already exists
        existing_admin = User.query.filter_by(email='admin@sekolah.com').first()
        if existing_admin:
            print("User admin sudah ada!")
            print(f"Email: {existing_admin.email}")
            print(f"Nama: {existing_admin.nama_lengkap}")
            print(f"Role: {existing_admin.role}")
            return
        
        # Create admin user
        admin = User(
            email='admin@sekolah.com',
            password=generate_password_hash('admin123'),
            nama_lengkap='Administrator',
            jenis_kelamin='laki-laki',
            role='admin'
        )
        
        try:
            db.session.add(admin)
            db.session.commit()
            print("✅ User admin berhasil dibuat!")
            print(f"Email: {admin.email}")
            print(f"Password: admin123")
            print(f"Nama: {admin.nama_lengkap}")
            print(f"Role: {admin.role}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error membuat user admin: {str(e)}")

def list_users():
    """Menampilkan semua user"""
    
    with app.app_context():
        users = User.query.all()
        if not users:
            print("Tidak ada user yang ditemukan.")
            return
        
        print("📋 Daftar User:")
        print("-" * 50)
        for user in users:
            print(f"ID: {user.id}")
            print(f"Email: {user.email}")
            print(f"Nama: {user.nama_lengkap}")
            print(f"Role: {user.role}")
            print(f"Jenis Kelamin: {user.jenis_kelamin}")
            print("-" * 50)

if __name__ == "__main__":
    print("🚀 School Management System - User Creation Script")
    print("=" * 60)
    
    # Create teacher user
    print("\n1. Membuat User Guru...")
    create_teacher_user()
    
    # Create admin user
    print("\n2. Membuat User Admin...")
    create_admin_user()
    
    # List all users
    print("\n3. Daftar Semua User...")
    list_users()
    
    print("\n✅ Script selesai!")
    print("\n📝 Catatan:")
    print("- User guru dapat login di /api/teacher/login")
    print("- User admin dapat menggunakan endpoint /api/users")
    print("- Siswa dapat login di /api/student/login dengan NISN dan password NISN") 