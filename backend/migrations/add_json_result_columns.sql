-- Add json_result column to Soal table
ALTER TABLE Soal
ADD COLUMN json_result JSON NOT NULL;

-- Add json_result column to Jawaban_Siswa table (nullable)
ALTER TABLE Jawaban_Siswa
ADD COLUMN json_result JSON NULL; 

-- Hapus kolom password dari tabel siswa
ALTER TABLE siswa DROP COLUMN password;
-- Tambahkan kolom user_id ke tabel siswa
ALTER TABLE siswa ADD COLUMN user_id INT UNIQUE NOT NULL;
ALTER TABLE siswa ADD CONSTRAINT fk_siswa_user FOREIGN KEY (user_id) REFERENCES users(id); 