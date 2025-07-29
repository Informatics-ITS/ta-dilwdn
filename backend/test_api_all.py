import pytest
import requests
import json
import uuid

BASE_URL = "http://localhost:5000"

# Dummy credentials (harus sesuai seed)
ADMIN_EMAIL = "admin@school.com"
ADMIN_PASSWORD = "admin123"
GURU_EMAIL = "guru@school.com"
GURU_PASSWORD = "guru123"
SISWA_NISN = "1234567890"
SISWA_PASSWORD = "1234567890"

@pytest.fixture(scope="session")
def session_guru():
    s = requests.Session()
    resp = s.post(f"{BASE_URL}/api/teacher/login", json={"email": GURU_EMAIL, "password": GURU_PASSWORD})
    assert resp.status_code == 200
    return s

@pytest.fixture(scope="session")
def session_siswa():
    s = requests.Session()
    resp = s.post(f"{BASE_URL}/api/student/login", json={"nisn": SISWA_NISN, "password": SISWA_PASSWORD})
    assert resp.status_code == 200
    return s

# --- USERS ---
def test_get_all_users():
    resp = requests.get(f"{BASE_URL}/api/users")
    assert resp.status_code == 200

def test_create_user():
    # Gunakan email unik setiap test
    email = f"user_test_{uuid.uuid4().hex[:8]}@example.com"
    data = {
        "email": email,
        "password": "password123",
        "nama_lengkap": "John Doe",
        "jenis_kelamin": "laki-laki",
        "role": "admin"
    }
    resp = requests.post(f"{BASE_URL}/api/users", json=data)
    assert resp.status_code in [200, 201]
    # Clean up
    # Cari user by email
    users = requests.get(f"{BASE_URL}/api/users").json()
    user_id = None
    for u in users:
        if u["email"] == email:
            user_id = u["id"]
    if user_id:
        requests.delete(f"{BASE_URL}/api/users/{user_id}")

# --- SISWA ---
def test_get_all_siswa():
    resp = requests.get(f"{BASE_URL}/api/siswa")
    assert resp.status_code == 200

def test_create_siswa():
    nisn = f"99999{uuid.uuid4().hex[:5]}"
    data = {"NISN": nisn, "nama_siswa": "Test Siswa", "kelas": 1}
    resp = requests.post(f"{BASE_URL}/api/siswa", json=data)
    assert resp.status_code in [200, 201, 400]  # 400 jika NISN sudah ada
    # Clean up
    siswa_list = requests.get(f"{BASE_URL}/api/siswa").json()
    for s in siswa_list:
        if s["NISN"] == nisn:
            requests.delete(f"{BASE_URL}/api/siswa/{s['no']}")

# --- KELAS ---
def test_get_all_kelas():
    resp = requests.get(f"{BASE_URL}/api/kelas")
    assert resp.status_code == 200

def test_create_kelas():
    kelas_id = int(str(uuid.uuid4().int)[:2]) + 10  # id unik
    data = {"id": kelas_id, "nama": f"Kelas Test {kelas_id}"}
    resp = requests.post(f"{BASE_URL}/api/kelas", json=data)
    assert resp.status_code in [200, 201, 400]  # 400 jika id sudah ada
    # Clean up
    requests.delete(f"{BASE_URL}/api/kelas/{kelas_id}")

# --- UJIAN ---
def test_get_all_ujian():
    resp = requests.get(f"{BASE_URL}/api/ujian")
    assert resp.status_code == 200

def test_create_ujian():
    data = {"nama_ujian": f"Ujian Test {uuid.uuid4().hex[:5]}", "kelas": 1, "pelaksanaan": "2024-12-01", "status": "aktif"}
    resp = requests.post(f"{BASE_URL}/api/ujian", json=data)
    assert resp.status_code in [200, 201]
    # Clean up
    ujian_id = None
    for u in requests.get(f"{BASE_URL}/api/ujian").json():
        if u["nama_ujian"] == data["nama_ujian"]:
            ujian_id = u["id"]
    if ujian_id:
        requests.delete(f"{BASE_URL}/api/ujian/{ujian_id}")

# --- SOAL ---
def test_get_all_soal():
    resp = requests.get(f"{BASE_URL}/api/soal")
    assert resp.status_code == 200

def test_create_soal():
    soal_text = f"{uuid.uuid4().hex[:5]}+{uuid.uuid4().hex[:2]}=.."
    data = {
        "soal": soal_text,
        "ujian": 1,
        "json_result": {"operator": "Penjumlahan", "angka_dalam_soal": "2,2", "jawaban": "4"}
    }
    resp = requests.post(f"{BASE_URL}/api/soal", json=data)
    assert resp.status_code in [200, 201]
    # Clean up
    soal_id = None
    for s in requests.get(f"{BASE_URL}/api/soal").json():
        if s["soal"] == soal_text:
            soal_id = s["id"]
    if soal_id:
        requests.delete(f"{BASE_URL}/api/soal/{soal_id}")

# --- STATISTICS ---
def test_get_total_siswa():
    resp = requests.get(f"{BASE_URL}/api/statistics/total-siswa")
    assert resp.status_code == 200

def test_get_total_kelas():
    resp = requests.get(f"{BASE_URL}/api/statistics/total-kelas")
    assert resp.status_code == 200

def test_get_total_ujian():
    resp = requests.get(f"{BASE_URL}/api/statistics/total-ujian")
    assert resp.status_code == 200

# --- MATH SOLVER ---
def test_solve_text():
    data = {"text_input": "Budi memiliki 5 apel dan membeli 3 apel lagi. Berapa total apel yang dimiliki Budi?"}
    resp = requests.post(f"{BASE_URL}/api/solve_text", json=data)
    assert resp.status_code == 200

def test_compare_answer():
    data = {
        "ai_answer": {"operator": "Penjumlahan", "angka_dalam_soal": "5,3", "jawaban": "8"},
        "student_answer": {"operator": "Penjumlahan", "angka_dalam_soal": "5,3", "jawaban": "8"}
    }
    resp = requests.post(f"{BASE_URL}/api/compare_answer", json=data)
    assert resp.status_code == 200

# --- PEDAGOGIC ---
def test_pedagogic_status():
    resp = requests.get(f"{BASE_URL}/api/pedagogic/status")
    assert resp.status_code == 200

# --- AUTH & SESSION ENDPOINTS (GURU/SISWA) ---
def test_teacher_profile(session_guru):
    resp = session_guru.get(f"{BASE_URL}/api/teacher/profile")
    assert resp.status_code == 200

def test_teacher_dashboard(session_guru):
    resp = session_guru.get(f"{BASE_URL}/api/teacher/dashboard")
    assert resp.status_code == 200

def test_student_profile(session_siswa):
    resp = session_siswa.get(f"{BASE_URL}/api/student/profile")
    assert resp.status_code == 200

def test_student_exams(session_siswa):
    resp = session_siswa.get(f"{BASE_URL}/api/student/exams")
    assert resp.status_code == 200

# Untuk endpoint yang butuh file upload, gunakan requests dengan files={...} 