import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database():
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
            password=password
        )

        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
            print(f"Database '{database}' created successfully or already exists")
            
            # Use the database
            cursor.execute(f"USE {database}")
            
            # Create tables
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
                    nama VARCHAR(50) NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS siswa (
                    no INT AUTO_INCREMENT PRIMARY KEY,
                    NISN VARCHAR(20) UNIQUE NOT NULL,
                    nama_siswa VARCHAR(100) NOT NULL,
                    kelas INT NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    FOREIGN KEY (kelas) REFERENCES kelas(id)
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
                    FOREIGN KEY (ujian) REFERENCES ujian(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jawaban_siswa (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    siswa INT NOT NULL,
                    soal INT NOT NULL,
                    status VARCHAR(10) NOT NULL,
                    FOREIGN KEY (siswa) REFERENCES siswa(no),
                    FOREIGN KEY (soal) REFERENCES soal(id)
                )
            """)

            print("All tables created successfully")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    create_database() 