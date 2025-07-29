-- =====================================================================
-- STORED PROCEDURES FOR UJIAN SISWA DETAIL ANALYSIS
-- =====================================================================

-- Drop existing procedures if they exist
DROP PROCEDURE IF EXISTS get_ujian_siswa_detail;
DROP PROCEDURE IF EXISTS get_ujian_siswa_summary;
DROP PROCEDURE IF EXISTS get_ujian_siswa_comparison_analysis;

-- =====================================================================
-- 1. GET UJIAN SISWA DETAIL
-- Menampilkan detail lengkap ujian siswa dengan semua jawaban
-- Input: ujian_siswa_id
-- =====================================================================

DELIMITER //

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
END //

-- =====================================================================
-- 2. GET UJIAN SISWA SUMMARY
-- Menampilkan ringkasan statistik ujian siswa
-- Input: ujian_siswa_id
-- =====================================================================

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
END //

-- =====================================================================
-- 3. GET UJIAN SISWA COMPARISON ANALYSIS
-- Menampilkan detail analisis comparison untuk ujian siswa
-- Input: ujian_siswa_id
-- =====================================================================

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
END //

DELIMITER ;

-- =====================================================================
-- USAGE EXAMPLES:
-- =====================================================================

-- 1. Get full detail for ujian_siswa_id = 1
-- CALL get_ujian_siswa_detail(1);

-- 2. Get summary for ujian_siswa_id = 1  
-- CALL get_ujian_siswa_summary(1);

-- 3. Get comparison analysis for ujian_siswa_id = 1
-- CALL get_ujian_siswa_comparison_analysis(1);

-- =====================================================================
-- NOTES:
-- =====================================================================

-- 1. Procedures menggunakan INNER JOIN untuk memastikan data konsisten
-- 2. Procedure summary menggunakan LEFT JOIN untuk menangani soal yang belum dijawab
-- 3. JSON_EXTRACT digunakan untuk mengakses data comparison di json_result
-- 4. COALESCE digunakan untuk menangani NULL values pada avg_comparison_score
-- 5. Input parameter menggunakan ujian_siswa.id sebagai filter utama 