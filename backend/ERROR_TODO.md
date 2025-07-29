[x] POST /api/siswa
Error: Cannot add or update a child row: a foreign key constraint fails (school_db.siswa, CONSTRAINT siswa_ibfk_1 FOREIGN KEY (kelas) REFERENCES kelas (id))
Penyebab: Data kelas yang diinput tidak ada di tabel kelas.
[ ] POST /api/ujian
Error: Cannot add or update a child row: a foreign key constraint fails (school_db.ujian, CONSTRAINT ujian_ibfk_1 FOREIGN KEY (kelas) REFERENCES kelas (id))
Penyebab: Data kelas yang diinput tidak ada di tabel kelas.
[ ] POST /api/soal
Error: Cannot add or update a child row: a foreign key constraint fails (school_db.soal, CONSTRAINT soal_ibfk_1 FOREIGN KEY (ujian) REFERENCES ujian (id))
Penyebab: Data ujian yang diinput tidak ada di tabel ujian.
[ ] GET /api/statistics/total-siswa
Error: NameError: name 'get_db_connection' is not defined
Penyebab: Fungsi get_db_connection tidak didefinisikan di app.py.
[ ] GET /api/statistics/total-kelas
Error: NameError: name 'get_db_connection' is not defined
Penyebab: Fungsi get_db_connection tidak didefinisikan di app.py.
[ ] GET /api/statistics/total-ujian
Error: NameError: name 'get_db_connection' is not defined
Penyebab: Fungsi get_db_connection tidak didefinisikan di app.py.
[ ] POST /api/teacher/login
Error: 401 Unauthorized
Penyebab: Email/password salah atau data user guru tidak ada di database.
[ ] POST /api/student/login
Error: 401 Unauthorized
Penyebab: NISN/password salah atau data siswa tidak ada di database.
Catatan:
Untuk error foreign key, pastikan data referensi (kelas, ujian) sudah ada sebelum insert data yang terkait.
Untuk error get_db_connection, tambahkan atau perbaiki fungsi tersebut di app.py.
Untuk error login, pastikan data user/siswa sudah ada dan password benar.
Jika ingin solusi detail untuk tiap error, silakan pilih salah satu dari daftar di atas!