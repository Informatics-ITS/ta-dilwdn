DROP PROCEDURE IF EXISTS Get_Class_Statistics;
DELIMITER //

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
END //

DELIMITER ; 