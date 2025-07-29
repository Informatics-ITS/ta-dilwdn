import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_procedures():
    try:
        host = os.getenv('DB_HOST', 'localhost')
        user = os.getenv('DB_USER', 'root')
        password = os.getenv('DB_PASSWORD', '')
        database = os.getenv('DB_NAME', 'school_db')

        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Drop and create all procedures
            procedures = [
                # --- From stored_procedures.sql ---
                "DROP PROCEDURE IF EXISTS total_siswa;",
                """
                CREATE PROCEDURE total_siswa()
                BEGIN
                    SELECT COUNT(*) as total FROM siswa;
                END
                """,
                "DROP PROCEDURE IF EXISTS total_kelas;",
                """
                CREATE PROCEDURE total_kelas()
                BEGIN
                    SELECT COUNT(*) as total FROM kelas;
                END
                """,
                "DROP PROCEDURE IF EXISTS total_ujian;",
                """
                CREATE PROCEDURE total_ujian()
                BEGIN
                    SELECT COUNT(*) as total FROM ujian;
                END
                """,
                "DROP PROCEDURE IF EXISTS get_capaian;",
                """
                CREATE PROCEDURE get_capaian()
                BEGIN
                    SELECT 
                        COUNT(CASE WHEN label_nilai = 'lulus' THEN 1 END) as lulus,
                        COUNT(CASE WHEN label_nilai = 'tidak lulus' THEN 1 END) as tidak_lulus,
                        COUNT(*) as total,
                        ROUND((COUNT(CASE WHEN label_nilai = 'lulus' THEN 1 END) / COUNT(*)) * 100) as persentase_lulus
                    FROM ujian_siswa
                    WHERE label_nilai IS NOT NULL;
                END
                """,
                # --- From Get_Class_Statistics.sql ---
                "DROP PROCEDURE IF EXISTS Get_Class_Statistics;",
                """
                CREATE PROCEDURE Get_Class_Statistics()
                BEGIN
                    SELECT 
                        k.id AS class_id,
                        k.nama AS class_name,
                        COUNT(DISTINCT s.no) AS total_students,
                        COUNT(DISTINCT u.id) AS total_exams,
                        ROUND(AVG(us.nilai)) AS average_score,
                        ROUND(MIN(us.nilai)) AS minimum_score,
                        ROUND(MAX(us.nilai)) AS maximum_score,
                        COUNT(DISTINCT CASE WHEN us.label_nilai = 'Baik' THEN us.id END) AS good_scores,
                        COUNT(DISTINCT CASE WHEN us.label_nilai = 'Cukup' THEN us.id END) AS fair_scores,
                        COUNT(DISTINCT CASE WHEN us.label_nilai = 'Kurang' THEN us.id END) AS poor_scores
                    FROM 
                        Kelas k
                        LEFT JOIN Siswa s ON s.kelas = k.id
                        LEFT JOIN Ujian u ON u.kelas = k.id
                        LEFT JOIN Ujian_Siswa us ON us.ujian = u.id AND us.siswa = s.no
                    GROUP BY 
                        k.id, k.nama
                    ORDER BY 
                        k.id;
                END
                """,
                # --- Tambahan dari create_procedures.py lama ---
                "DROP PROCEDURE IF EXISTS get_nilai_siswa;",
                """
                CREATE PROCEDURE get_nilai_siswa(IN siswa_id INT)
                BEGIN
                    SELECT 
                        u.nama_ujian,
                        us.nilai,
                        us.label_nilai,
                        us.deskripsi_analisis
                    FROM ujian_siswa us
                    JOIN ujian u ON us.ujian = u.id
                    WHERE us.siswa = siswa_id;
                END
                """,
                "DROP PROCEDURE IF EXISTS get_statistik_kelas;",
                """
                CREATE PROCEDURE get_statistik_kelas(IN kelas_id INT)
                BEGIN
                    SELECT 
                        COUNT(DISTINCT us.siswa) as total_siswa,
                        ROUND(AVG(us.nilai)) as rata_rata_nilai,
                        COUNT(CASE WHEN us.label_nilai = 'lulus' THEN 1 END) as jumlah_lulus,
                        COUNT(CASE WHEN us.label_nilai = 'tidak lulus' THEN 1 END) as jumlah_tidak_lulus
                    FROM ujian_siswa us
                    JOIN siswa s ON us.siswa = s.no
                    WHERE s.kelas = kelas_id;
                END
                """
            ]

            for sql in procedures:
                try:
                    cursor.execute(sql)
                except Error as e:
                    print(f"Error executing: {sql[:40]}... -> {e}")

            connection.commit()
            print("All stored procedures created successfully")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    create_procedures()