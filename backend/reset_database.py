import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import subprocess
import sqlalchemy

# Load environment variables
load_dotenv()

def add_nilai_column_if_not_exists(engine):
    with engine.connect() as conn:
        # Cek apakah kolom sudah ada
        result = conn.execute("PRAGMA table_info(jawaban_siswa)") if engine.dialect.name == 'sqlite' else conn.execute("SHOW COLUMNS FROM jawaban_siswa")
        columns = [row[1] if engine.dialect.name == 'sqlite' else row[0] for row in result]
        if 'nilai' not in columns:
            try:
                conn.execute("ALTER TABLE jawaban_siswa ADD COLUMN nilai INTEGER DEFAULT 0")
                print("Kolom 'nilai' berhasil ditambahkan ke jawaban_siswa.")
            except Exception as e:
                print(f"Gagal menambah kolom nilai: {e}")
        else:
            print("Kolom 'nilai' sudah ada di jawaban_siswa.")

def reset_database():
    try:
        host = os.getenv('DB_HOST', 'localhost')
        user = os.getenv('DB_USER', 'root')
        password = os.getenv('DB_PASSWORD', '')
        database = os.getenv('DB_NAME', 'school_db')

        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )

        if connection.is_connected():
            cursor = connection.cursor()
            # Drop database if exists
            cursor.execute(f"DROP DATABASE IF EXISTS {database}")
            print(f"Database '{database}' dropped successfully (if existed)")

            # Create database
            cursor.execute(f"CREATE DATABASE {database}")
            print(f"Database '{database}' created successfully")

            # Use the new database
            cursor.execute(f"USE {database}")

            # --- Table creation (copy from create_database.py, plus migration columns) ---
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(120) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    nama_lengkap VARCHAR(100) NOT NULL,
                    jenis_kelamin VARCHAR(10) NOT NULL,
                    role VARCHAR(20) DEFAULT 'admin'
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kelas (
                    id INT PRIMARY KEY,
                    nama VARCHAR(50) NOT NULL,
                    guru_id INT NOT NULL,
                    FOREIGN KEY (guru_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS siswa (
                    no INT AUTO_INCREMENT PRIMARY KEY,
                    NISN VARCHAR(20) UNIQUE NOT NULL,
                    nama_siswa VARCHAR(100) NOT NULL,
                    kelas INT NOT NULL,
                    user_id INT UNIQUE NOT NULL,
                    FOREIGN KEY (kelas) REFERENCES kelas(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ujian (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nama_ujian VARCHAR(100) NOT NULL,
                    kelas INT NOT NULL,
                    pelaksanaan DATE NOT NULL,
                    status VARCHAR(10) NOT NULL,
                    FOREIGN KEY (kelas) REFERENCES kelas(id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ujian_siswa (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ujian INT NOT NULL,
                    siswa INT NOT NULL,
                    nilai INT,
                    label_nilai VARCHAR(20),
                    deskripsi_analisis TEXT,
                    FOREIGN KEY (ujian) REFERENCES ujian(id),
                    FOREIGN KEY (siswa) REFERENCES siswa(no),
                    UNIQUE KEY unique_ujian_siswa (ujian, siswa)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS soal (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    soal VARCHAR(255) NOT NULL,
                    ujian INT NOT NULL,
                    json_result JSON NOT NULL,
                    FOREIGN KEY (ujian) REFERENCES ujian(id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jawaban_siswa (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nisn VARCHAR(20) NOT NULL,
                    soal INT NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    json_result JSON NULL,
                    FOREIGN KEY (nisn) REFERENCES siswa(NISN) ON DELETE CASCADE,
                    FOREIGN KEY (soal) REFERENCES soal(id) ON DELETE CASCADE
                )
            """)
            print("All tables created successfully (with latest structure)")

            # --- Create Stored Procedures ---
            print("Creating stored procedures...")
            
            # Drop existing procedure if exists
            cursor.execute("DROP PROCEDURE IF EXISTS get_ujian_siswa_detail")
            
            # Create new stored procedure
            procedure_sql = """
            CREATE PROCEDURE get_ujian_siswa_detail(IN input_ujian_siswa_id INT)
            BEGIN
                SELECT 
                    -- Kolom dari tabel ujian_siswa
                    us.id AS ujian_siswa_id,
                    us.ujian AS ujian_siswa_ujian_id,
                    us.siswa AS ujian_siswa_siswa_no,
                    us.nilai,
                    us.label_nilai,
                    us.deskripsi_analisis,
                    
                    -- Kolom dari tabel jawaban_siswa  
                    js.id AS jawaban_siswa_id,
                    js.nisn,
                    js.soal AS jawaban_siswa_soal_id,
                    js.status AS jawaban_status,
                    js.json_result AS jawaban_json_result,
                    
                    -- Kolom dari tabel ujian
                    u.id AS ujian_id,
                    u.nama_ujian,
                    u.kelas AS ujian_kelas_id,
                    u.pelaksanaan,
                    u.status AS ujian_status,
                    
                    -- Kolom dari tabel soal
                    s.id AS soal_id,
                    s.soal AS soal_text,
                    s.ujian AS soal_ujian_id,
                    s.json_result AS soal_json_result,
                    
                    -- Kolom tambahan dari siswa
                    siswa_tbl.nama_siswa,
                    siswa_tbl.NISN AS siswa_nisn,
                    siswa_tbl.kelas AS siswa_kelas_id

                FROM ujian_siswa us
                INNER JOIN ujian u ON us.ujian = u.id
                INNER JOIN soal s ON u.id = s.ujian  
                INNER JOIN jawaban_siswa js ON s.id = js.soal
                INNER JOIN siswa siswa_tbl ON us.siswa = siswa_tbl.no AND js.nisn = siswa_tbl.NISN
                
                WHERE us.id = input_ujian_siswa_id
                
                ORDER BY s.id, js.id;
            END
            """
            
            cursor.execute(procedure_sql)
            print("Stored procedure 'get_ujian_siswa_detail' created successfully")

            # Create additional useful procedures
            cursor.execute("DROP PROCEDURE IF EXISTS get_ujian_siswa_summary")
            
            summary_procedure_sql = """
            CREATE PROCEDURE get_ujian_siswa_summary(IN input_ujian_siswa_id INT)
            BEGIN
                SELECT 
                    us.id AS ujian_siswa_id,
                    us.nilai,
                    us.label_nilai,
                    us.deskripsi_analisis,
                    u.nama_ujian,
                    u.pelaksanaan,
                    siswa_tbl.nama_siswa,
                    siswa_tbl.NISN,
                    COUNT(s.id) AS total_soal,
                    COUNT(js.id) AS total_jawaban,
                    SUM(CASE WHEN js.status = 'correct' THEN 1 ELSE 0 END) AS jawaban_benar,
                    SUM(CASE WHEN js.status = 'incorrect' THEN 1 ELSE 0 END) AS jawaban_salah,
                    SUM(CASE WHEN js.json_result IS NOT NULL AND JSON_EXTRACT(js.json_result, '$.comparison') IS NOT NULL THEN 1 ELSE 0 END) AS analyzed_answers,
                    COALESCE(AVG(CAST(JSON_EXTRACT(js.json_result, '$.comparison.nilai') AS DECIMAL(3,2))), 0) AS avg_comparison_score
                    
                FROM ujian_siswa us
                INNER JOIN ujian u ON us.ujian = u.id
                INNER JOIN siswa siswa_tbl ON us.siswa = siswa_tbl.no
                LEFT JOIN soal s ON u.id = s.ujian  
                LEFT JOIN jawaban_siswa js ON s.id = js.soal AND js.nisn = siswa_tbl.NISN
                
                WHERE us.id = input_ujian_siswa_id
                
                GROUP BY us.id, us.nilai, us.label_nilai, us.deskripsi_analisis, 
                         u.nama_ujian, u.pelaksanaan, siswa_tbl.nama_siswa, siswa_tbl.NISN;
            END
            """
            
            cursor.execute(summary_procedure_sql)
            print("Stored procedure 'get_ujian_siswa_summary' created successfully")

            # Create procedure for comparison analysis
            cursor.execute("DROP PROCEDURE IF EXISTS get_ujian_siswa_comparison_analysis")
            
            comparison_procedure_sql = """
            CREATE PROCEDURE get_ujian_siswa_comparison_analysis(IN input_ujian_siswa_id INT)
            BEGIN
                SELECT 
                    us.id AS ujian_siswa_id,
                    us.nilai,
                    us.label_nilai,
                    u.nama_ujian,
                    siswa_tbl.nama_siswa,
                    siswa_tbl.NISN,
                    s.id AS soal_id,
                    s.soal AS soal_text,
                    s.json_result AS correct_answer,
                    js.id AS jawaban_siswa_id,
                    js.status AS jawaban_status,
                    js.json_result AS student_answer,
                    
                    -- Extract comparison data from JSON
                    JSON_EXTRACT(js.json_result, '$.comparison.status') AS comparison_status,
                    JSON_EXTRACT(js.json_result, '$.comparison.nilai') AS comparison_score,
                    JSON_EXTRACT(js.json_result, '$.comparison.deskripsi_analisis') AS comparison_analysis,
                    JSON_EXTRACT(js.json_result, '$.comparison.parameter_salah') AS wrong_parameters,
                    JSON_EXTRACT(js.json_result, '$.comparison.koreksi') AS corrections
                    
                FROM ujian_siswa us
                INNER JOIN ujian u ON us.ujian = u.id
                INNER JOIN siswa siswa_tbl ON us.siswa = siswa_tbl.no
                INNER JOIN soal s ON u.id = s.ujian  
                INNER JOIN jawaban_siswa js ON s.id = js.soal AND js.nisn = siswa_tbl.NISN
                
                WHERE us.id = input_ujian_siswa_id
                  AND js.json_result IS NOT NULL 
                  AND JSON_EXTRACT(js.json_result, '$.comparison') IS NOT NULL
                
                ORDER BY s.id;
            END
            """
            
            cursor.execute(comparison_procedure_sql)
            print("Stored procedure 'get_ujian_siswa_comparison_analysis' created successfully")

            # Create stored procedure untuk mendapatkan list ujian siswa berdasarkan guru_id
            cursor.execute("DROP PROCEDURE IF EXISTS get_ujian_siswa_by_guru")
            
            ujian_siswa_by_guru_sql = """
            CREATE PROCEDURE get_ujian_siswa_by_guru(IN input_guru_id INT)
            BEGIN
                SELECT 
                    us.id AS ujian_siswa_id,
                    us.ujian AS ujian_id,
                    us.siswa AS siswa_no,
                    us.nilai,
                    us.label_nilai,
                    us.deskripsi_analisis,
                    
                    -- Info siswa
                    siswa_tbl.nama_siswa,
                    siswa_tbl.NISN AS siswa_nisn,
                    
                    -- Info ujian
                    u.nama_ujian,
                    u.pelaksanaan,
                    u.status AS ujian_status,
                    
                    -- Info kelas
                    k.id AS kelas_id,
                    k.nama AS nama_kelas,
                    k.guru_id

                FROM ujian_siswa us
                INNER JOIN ujian u ON us.ujian = u.id
                INNER JOIN kelas k ON u.kelas = k.id
                INNER JOIN siswa siswa_tbl ON us.siswa = siswa_tbl.no
                
                WHERE k.guru_id = input_guru_id
                
                ORDER BY u.pelaksanaan DESC, us.id;
            END
            """
            
            cursor.execute(ujian_siswa_by_guru_sql)
            print("Stored procedure 'get_ujian_siswa_by_guru' created successfully")

            # Create stored procedure untuk mendapatkan statistik kelas berdasarkan guru_id
            cursor.execute("DROP PROCEDURE IF EXISTS get_guru_dashboard_stats")
            
            guru_dashboard_stats_sql = """
            CREATE PROCEDURE get_guru_dashboard_stats(IN input_guru_id INT)
            BEGIN
                SELECT 
                    COUNT(DISTINCT k.id) AS total_kelas,
                    COUNT(DISTINCT s.no) AS total_siswa,
                    COUNT(DISTINCT u.id) AS total_ujian,
                    COUNT(DISTINCT us.id) AS total_ujian_siswa,
                    
                    -- Statistik nilai
                    COALESCE(AVG(us.nilai), 0) AS rata_rata_nilai,
                    COALESCE(MIN(us.nilai), 0) AS nilai_minimum,
                    COALESCE(MAX(us.nilai), 0) AS nilai_maksimum,
                    
                    -- Distribusi label nilai
                    SUM(CASE WHEN us.label_nilai = 'Sangat Baik' THEN 1 ELSE 0 END) AS sangat_baik,
                    SUM(CASE WHEN us.label_nilai = 'Baik' THEN 1 ELSE 0 END) AS baik,
                    SUM(CASE WHEN us.label_nilai = 'Cukup' THEN 1 ELSE 0 END) AS cukup,
                    SUM(CASE WHEN us.label_nilai = 'Kurang' THEN 1 ELSE 0 END) AS kurang

                FROM kelas k
                LEFT JOIN siswa s ON k.id = s.kelas
                LEFT JOIN ujian u ON k.id = u.kelas
                LEFT JOIN ujian_siswa us ON u.id = us.ujian AND s.no = us.siswa
                
                WHERE k.guru_id = input_guru_id;
            END
            """
            
            cursor.execute(guru_dashboard_stats_sql)
            print("Stored procedure 'get_guru_dashboard_stats' created successfully")

            print("All stored procedures created successfully!")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

if __name__ == '__main__':
    reset_database()
    # Jalankan create_procedures.py setelah reset database
    try:
        subprocess.run(['python', 'create_procedures.py'], check=True)
    except Exception as e:
        print(f"Error running create_procedures.py: {e}")