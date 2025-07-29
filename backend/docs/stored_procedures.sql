DROP PROCEDURE IF EXISTS total_siswa;
DROP PROCEDURE IF EXISTS total_kelas;
DROP PROCEDURE IF EXISTS total_ujian;
DROP PROCEDURE IF EXISTS get_capaian;

DELIMITER //

CREATE PROCEDURE total_siswa()
BEGIN
    SELECT COUNT(*) as total FROM siswa;
END //

CREATE PROCEDURE total_kelas()
BEGIN
    SELECT COUNT(*) as total FROM kelas;
END //

CREATE PROCEDURE total_ujian()
BEGIN
    SELECT COUNT(*) as total FROM ujian;
END //

CREATE PROCEDURE get_capaian()
BEGIN
    SELECT 
        COUNT(CASE WHEN label_nilai = 'lulus' THEN 1 END) as lulus,
        COUNT(CASE WHEN label_nilai = 'tidak lulus' THEN 1 END) as tidak_lulus,
        COUNT(*) as total,
        ROUND((COUNT(CASE WHEN label_nilai = 'lulus' THEN 1 END) / COUNT(*)) * 100) as persentase_lulus
    FROM ujian_siswa
    WHERE label_nilai IS NOT NULL;
END //

DELIMITER ; 