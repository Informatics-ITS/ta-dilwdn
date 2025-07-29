from flask import Flask
from models import db, User, Kelas, Siswa, Ujian, UjianSiswa, Soal, JawabanSiswa
from datetime import datetime
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', '')}@{os.getenv('DB_HOST', 'localhost')}/{os.getenv('DB_NAME', 'school_db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def seed_database():
    with app.app_context():
        # Clear existing data
        JawabanSiswa.query.delete()
        UjianSiswa.query.delete()
        Soal.query.delete()
        Ujian.query.delete()
        Siswa.query.delete()
        Kelas.query.delete()
        User.query.delete()
        db.session.commit()

        # Create users (untuk semua test)
        users = [
            User(
                email='admin@school.com',
                password=generate_password_hash('admin123'),
                nama_lengkap='Administrator',
                jenis_kelamin='laki-laki',
                role='admin'
            ),
            User(
                email='guru@school.com',
                password=generate_password_hash('guru123'),
                nama_lengkap='Guru Matematika',
                jenis_kelamin='perempuan',
                role='guru'
            ),
            User(
                email='guru2@school.com',
                password=generate_password_hash('guru123'),
                nama_lengkap='Guru Fisika',
                jenis_kelamin='laki-laki',
                role='guru'
            ),
            User(
                email='guru3@school.com',
                password=generate_password_hash('guru123'),
                nama_lengkap='Guru Kimia',
                jenis_kelamin='perempuan',
                role='guru'
            ),
            User(
                email='user_test@example.com',
                password=generate_password_hash('password123'),
                nama_lengkap='John Doe',
                jenis_kelamin='laki-laki',
                role='admin'
            )
        ]
        db.session.add_all(users)
        db.session.commit()

        # Create classes (untuk semua test) - assign ke guru yang berbeda
        # users[1] = Guru Matematika, users[2] = Guru Fisika, users[3] = Guru Kimia
        classes = [
            Kelas(id=1, nama='Kelas X IPA 1', guru_id=users[1].id),  # Guru Matematika
            Kelas(id=2, nama='Kelas X IPA 2', guru_id=users[2].id),  # Guru Fisika  
            Kelas(id=3, nama='Kelas XI IPA 1', guru_id=users[3].id), # Guru Kimia
            Kelas(id=4, nama='Kelas XI IPA 2', guru_id=users[1].id), # Guru Matematika lagi
            Kelas(id=99, nama='Kelas Test', guru_id=users[1].id)     # Test class untuk Guru Matematika
        ]
        db.session.add_all(classes)
        db.session.commit()

        # Create students (untuk semua test)
        siswa_users = [
            User(
                email='1234567890',
                password=generate_password_hash('1234567890'),
                nama_lengkap='Budi Santoso',
                jenis_kelamin='laki-laki',
                role='siswa'
            ),
            User(
                email='9999999999',
                password=generate_password_hash('9999999999'),
                nama_lengkap='Test Siswa',
                jenis_kelamin='laki-laki',
                role='siswa'
            )
        ]
        db.session.add_all(siswa_users)
        db.session.commit()

        # Tambahkan siswa lain untuk kelas berbeda
        siswa_users_additional = [
            User(
                email='1111111111',
                password=generate_password_hash('1111111111'),
                nama_lengkap='Siti Aminah',
                jenis_kelamin='perempuan',
                role='siswa'
            ),
            User(
                email='2222222222',
                password=generate_password_hash('2222222222'),
                nama_lengkap='Ahmad Fauzi',
                jenis_kelamin='laki-laki',
                role='siswa'
            ),
            User(
                email='3333333333',
                password=generate_password_hash('3333333333'),
                nama_lengkap='Rina Sari',
                jenis_kelamin='perempuan',
                role='siswa'
            )
        ]
        db.session.add_all(siswa_users_additional)
        db.session.commit()

        students = [
            # Siswa di kelas Guru Matematika (kelas 1 & 4)
            Siswa(NISN='1234567890', nama_siswa='Budi Santoso', kelas=1, user_id=siswa_users[0].id),
            Siswa(NISN='9999999999', nama_siswa='Test Siswa', kelas=1, user_id=siswa_users[1].id),
            Siswa(NISN='1111111111', nama_siswa='Siti Aminah', kelas=4, user_id=siswa_users_additional[0].id),
            
            # Siswa di kelas Guru Fisika (kelas 2)
            Siswa(NISN='2222222222', nama_siswa='Ahmad Fauzi', kelas=2, user_id=siswa_users_additional[1].id),
            
            # Siswa di kelas Guru Kimia (kelas 3)
            Siswa(NISN='3333333333', nama_siswa='Rina Sari', kelas=3, user_id=siswa_users_additional[2].id)
        ]
        db.session.add_all(students)
        db.session.commit()

        # Create exams (untuk semua test) - buat ujian untuk masing-masing kelas
        exams = [
            # Ujian untuk kelas Guru Matematika
            Ujian(
                nama_ujian='Ujian Matematika Dasar',
                kelas=1,
                pelaksanaan=datetime.strptime('2024-12-01', '%Y-%m-%d').date(),
                status='aktif'
            ),
            Ujian(
                nama_ujian='Ujian Matematika Lanjutan',
                kelas=4,
                pelaksanaan=datetime.strptime('2024-12-05', '%Y-%m-%d').date(),
                status='aktif'
            ),
            # Ujian untuk kelas Guru Fisika
            Ujian(
                nama_ujian='Ujian Fisika Dasar',
                kelas=2,
                pelaksanaan=datetime.strptime('2024-12-10', '%Y-%m-%d').date(),
                status='aktif'
            ),
            # Ujian untuk kelas Guru Kimia
            Ujian(
                nama_ujian='Ujian Kimia Organik',
                kelas=3,
                pelaksanaan=datetime.strptime('2024-12-15', '%Y-%m-%d').date(),
                status='aktif'
            ),
            # Test ujian
            Ujian(
                nama_ujian='Ujian Test',
                kelas=99,
                pelaksanaan=datetime.strptime('2024-12-01', '%Y-%m-%d').date(),
                status='aktif'
            )
        ]
        db.session.add_all(exams)
        db.session.commit()

        # Create questions (untuk semua test) - buat soal untuk setiap ujian
        questions = [
            # Soal untuk Ujian Matematika Dasar (ujian_id=1)
            Soal(
                soal='2+2=..',
                ujian=1,
                json_result={"operator": "Penjumlahan", "angka_dalam_soal": "2,2", "jawaban": "4"}
            ),
            Soal(
                soal='5-3=..',
                ujian=1,
                json_result={"operator": "Pengurangan", "angka_dalam_soal": "5,3", "jawaban": "2"}
            ),
            
            # Soal untuk Ujian Matematika Lanjutan (ujian_id=2)
            Soal(
                soal='7×8=..',
                ujian=2,
                json_result={"operator": "Perkalian", "angka_dalam_soal": "7,8", "jawaban": "56"}
            ),
            
            # Soal untuk Ujian Fisika Dasar (ujian_id=3)
            Soal(
                soal='F = m × a, jika m=5kg dan a=2m/s², maka F=..N',
                ujian=3,
                json_result={"tipe": "Fisika", "konsep": "Hukum Newton II", "jawaban": "10"}
            ),
            
            # Soal untuk Ujian Kimia Organik (ujian_id=4)
            Soal(
                soal='Rumus molekul metana adalah..',
                ujian=4,
                json_result={"tipe": "Kimia", "konsep": "Hidrokarbon", "jawaban": "CH4"}
            ),
            
            # Soal untuk Ujian Test (ujian_id=5)
            Soal(
                soal='Test question: 1+1=..',
                ujian=5,
                json_result={"operator": "Penjumlahan", "angka_dalam_soal": "1,1", "jawaban": "2"}
            )
        ]
        db.session.add_all(questions)
        db.session.commit()

        # Create UjianSiswa records (menghubungkan siswa dengan ujian mereka)
        ujian_siswa_records = [
            # Siswa di kelas 1 ikut Ujian Matematika Dasar
            UjianSiswa(ujian=1, siswa=students[0].no, nilai=100, label_nilai='Sangat Baik', 
                      deskripsi_analisis='Siswa sangat memahami konsep dasar matematika'),
            UjianSiswa(ujian=1, siswa=students[1].no, nilai=85, label_nilai='Baik',
                      deskripsi_analisis='Siswa cukup memahami konsep dasar matematika'),
            
            # Siswa di kelas 4 ikut Ujian Matematika Lanjutan  
            UjianSiswa(ujian=2, siswa=students[2].no, nilai=90, label_nilai='Sangat Baik',
                      deskripsi_analisis='Siswa memahami dengan baik konsep matematika lanjutan'),
            
            # Siswa di kelas 2 ikut Ujian Fisika Dasar
            UjianSiswa(ujian=3, siswa=students[3].no, nilai=75, label_nilai='Cukup',
                      deskripsi_analisis='Siswa perlu meningkatkan pemahaman konsep fisika'),
            
            # Siswa di kelas 3 ikut Ujian Kimia Organik
            UjianSiswa(ujian=4, siswa=students[4].no, nilai=95, label_nilai='Sangat Baik',
                      deskripsi_analisis='Siswa sangat memahami konsep kimia organik'),
        ]
        db.session.add_all(ujian_siswa_records)
        db.session.commit()

        # Create answers (jawaban_siswa) for testing foreign key - buat jawaban untuk berbagai siswa dan soal
        answers = [
            # Jawaban untuk Ujian Matematika Dasar (questions[0] dan questions[1])
            JawabanSiswa(
                nisn=students[0].NISN,  # Budi Santoso
                soal=questions[0].id,   # 2+2=..
                status='correct',
                json_result={
                    "student_answer": "4",
                    "ai_analysis": {"operator": "Penjumlahan", "angka_dalam_soal": "2,2", "jawaban": "4"},
                    "comparison": {"status": "correct", "nilai": 3}
                },
                nilai=0 # Tambahkan nilai=0
            ),
            JawabanSiswa(
                nisn=students[0].NISN,  # Budi Santoso
                soal=questions[1].id,   # 5-3=..
                status='correct',
                json_result={
                    "student_answer": "2",
                    "ai_analysis": {"operator": "Pengurangan", "angka_dalam_soal": "5,3", "jawaban": "2"},
                    "comparison": {"status": "correct", "nilai": 3}
                },
                nilai=0 # Tambahkan nilai=0
            ),
            JawabanSiswa(
                nisn=students[1].NISN,  # Test Siswa
                soal=questions[0].id,   # 2+2=..
                status='correct',
                json_result={
                    "student_answer": "4",
                    "ai_analysis": {"operator": "Penjumlahan", "angka_dalam_soal": "2,2", "jawaban": "4"},
                    "comparison": {"status": "correct", "nilai": 3}
                },
                nilai=0 # Tambahkan nilai=0
            ),
            JawabanSiswa(
                nisn=students[1].NISN,  # Test Siswa
                soal=questions[1].id,   # 5-3=..
                status='incorrect',
                json_result={
                    "student_answer": "3",
                    "ai_analysis": {"operator": "Pengurangan", "angka_dalam_soal": "5,3", "jawaban": "2"},
                    "comparison": {"status": "incorrect", "nilai": 1}
                },
                nilai=0 # Tambahkan nilai=0
            ),
            
            # Jawaban untuk Ujian Matematika Lanjutan
            JawabanSiswa(
                nisn=students[2].NISN,  # Siti Aminah
                soal=questions[2].id,   # 7×8=..
                status='correct',
                json_result={
                    "student_answer": "56",
                    "ai_analysis": {"operator": "Perkalian", "angka_dalam_soal": "7,8", "jawaban": "56"},
                    "comparison": {"status": "correct", "nilai": 3}
                },
                nilai=0 # Tambahkan nilai=0
            ),
            
            # Jawaban untuk Ujian Fisika Dasar
            JawabanSiswa(
                nisn=students[3].NISN,  # Ahmad Fauzi
                soal=questions[3].id,   # F = m × a
                status='correct',
                json_result={
                    "student_answer": "10",
                    "ai_analysis": {"tipe": "Fisika", "konsep": "Hukum Newton II", "jawaban": "10"},
                    "comparison": {"status": "correct", "nilai": 3}
                },
                nilai=0 # Tambahkan nilai=0
            ),
            
            # Jawaban untuk Ujian Kimia Organik
            JawabanSiswa(
                nisn=students[4].NISN,  # Rina Sari
                soal=questions[4].id,   # Metana
                status='correct',
                json_result={
                    "student_answer": "CH4",
                    "ai_analysis": {"tipe": "Kimia", "konsep": "Hidrokarbon", "jawaban": "CH4"},
                    "comparison": {"status": "correct", "nilai": 3}
                },
                nilai=0 # Tambahkan nilai=0
            )
        ]
        db.session.add_all(answers)
        db.session.commit()

        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database() 