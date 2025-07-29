from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, User, Kelas, Siswa, Ujian, UjianSiswa, Soal, JawabanSiswa
from datetime import datetime
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from flask import Flask, render_template, flash, request, jsonify, session
from wtforms import StringField, validators, FileField
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
import numpy as np
from anytree import Node, RenderTree
import string
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import joblib
from PIL import Image
import pytesseract
import os
import re
import base64
from io import BytesIO
import pandas as pd
import jwt
from functools import wraps
import json
import time


GEMINI_SLEEP_SECONDS = 25

# Import pedagogic analysis module
try:
    from pedagogic_analysis import get_pedagogic_analyzer
    import google.generativeai as genai
    PEDAGOGIC_ANALYSIS_AVAILABLE = True
except ImportError:
    PEDAGOGIC_ANALYSIS_AVAILABLE = False
    print("Warning: Pedagogic analysis module not available. Install google-generativeai package.")

# Tesseract command path
tesseract_path = r'E:\Program Files\Tesseract-OCR\tesseract.exe'
if not os.path.exists(tesseract_path):
    tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

pytesseract.pytesseract.tesseract_cmd = tesseract_path

# Load environment variables
load_dotenv()

app = Flask(__name__)

# CORS configuration to support credentials/sessions
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', '')}@{os.getenv('DB_HOST', 'localhost')}/{os.getenv('DB_NAME', 'school_db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['WTF_CSRF_ENABLED'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key-here'

# Session configuration
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

# Load CNN model and tokenizer (DISABLED - using simple algorithm instead)
model = load_model("cnn_model.h5")
tokenizer = joblib.load("tokenizer.pkl")
print("Using simple math extraction algorithm instead of CNN model")

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'school_db')
    )

def serialize_stored_procedure_result(data):
    """
    Convert stored procedure results to JSON-serializable format
    """
    import decimal
    
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            result[key] = serialize_stored_procedure_result(value)
        return result
    elif isinstance(data, list):
        return [serialize_stored_procedure_result(item) for item in data]
    elif isinstance(data, (bytes, bytearray)):
        try:
            # Try to decode as UTF-8 string first
            decoded = data.decode('utf-8')
            # Try to parse as JSON if it looks like JSON
            if decoded.strip().startswith(('{', '[')):
                try:
                    return json.loads(decoded)
                except json.JSONDecodeError:
                    return decoded
            return decoded
        except UnicodeDecodeError:
            # If can't decode as UTF-8, return as string representation
            return str(data)
    elif isinstance(data, datetime):
        return data.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(data, decimal.Decimal):
        return float(data)
    elif hasattr(data, 'isoformat'):  # Handle date objects
        return data.isoformat()
    elif data is None:
        return None
    else:
        try:
            # Try to JSON serialize the object to check if it's serializable
            json.dumps(data)
            return data
        except (TypeError, ValueError):
            # If not serializable, convert to string
            return str(data)

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Login required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(f"student_required decorator: session = {dict(session)}")
        print(f"user_id in session: {'user_id' in session}")
        print(f"role in session: {session.get('role')}")
        
        if 'user_id' not in session:
            print("Error: user_id not in session")
            return jsonify({'error': 'Login required'}), 401
        if 'role' not in session or session['role'] != 'siswa':
            print(f"Error: role check failed. Role: {session.get('role')}")
            return jsonify({'error': 'Student access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Login required'}), 401
        if 'role' not in session or session['role'] != 'guru':
            return jsonify({'error': 'Teacher access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Teacher Authentication routes
@app.route('/api/teacher/logout', methods=['POST'])
@login_required
def teacher_logout():
    session.clear()
    return jsonify({'message': 'Logout successful'})

@app.route('/api/teacher/profile', methods=['GET'])
@teacher_required
def get_teacher_profile():
    user = User.query.get(session['user_id'])
    return jsonify({
        'id': user.id,
        'email': user.email,
        'nama_lengkap': user.nama_lengkap,
        'jenis_kelamin': user.jenis_kelamin,
        'role': user.role
    })

# Teacher Management routes
@app.route('/api/teacher/kelas', methods=['GET'])
@teacher_required
def teacher_get_kelas():
    # Filter kelas berdasarkan guru_id yang sedang login
    guru_id = session['user_id']
    kelas = Kelas.query.filter_by(guru_id=guru_id).all()
    return jsonify([{
        'id': k.id,
        'nama': k.nama,
        'guru_id': k.guru_id,
        'total_siswa': len(k.siswa)
    } for k in kelas])

@app.route('/api/teacher/kelas', methods=['POST'])
@teacher_required
def teacher_create_kelas():
    data = request.get_json()
    
    # Check if kelas with this ID already exists
    existing_kelas = Kelas.query.filter_by(id=data['id']).first()
    if existing_kelas:
        return jsonify({'error': 'Kelas with this ID already exists'}), 400
    
    # Assign guru_id dari session user yang sedang login
    guru_id = session['user_id']
    kelas = Kelas(id=data['id'], nama=data['nama'], guru_id=guru_id)
    db.session.add(kelas)
    db.session.commit()
    
    return jsonify({
        'message': 'Kelas created successfully',
        'kelas': {
            'id': kelas.id,
            'nama': kelas.nama,
            'guru_id': kelas.guru_id
        }
    })

@app.route('/api/teacher/kelas/<int:id>', methods=['PUT'])
@teacher_required
def teacher_update_kelas(id):
    # Pastikan kelas yang diupdate adalah milik guru yang sedang login
    guru_id = session['user_id']
    kelas = Kelas.query.filter_by(id=id, guru_id=guru_id).first()
    
    if not kelas:
        return jsonify({'error': 'Kelas not found or access denied'}), 404
    
    data = request.get_json()
    
    if 'nama' in data:
        kelas.nama = data['nama']
    
    db.session.commit()
    return jsonify({
        'message': 'Kelas updated successfully',
        'kelas': {
            'id': kelas.id,
            'nama': kelas.nama,
            'guru_id': kelas.guru_id
        }
    })

@app.route('/api/teacher/kelas/<int:id>', methods=['DELETE'])
@teacher_required
def teacher_delete_kelas(id):
    # Pastikan kelas yang dihapus adalah milik guru yang sedang login
    guru_id = session['user_id']
    kelas = Kelas.query.filter_by(id=id, guru_id=guru_id).first()
    
    if not kelas:
        return jsonify({'error': 'Kelas not found or access denied'}), 404
    
    # Check if there are students in this class
    if kelas.siswa:
        return jsonify({'error': 'Cannot delete kelas with existing students'}), 400
    
    # Check if there are exams for this class
    if kelas.ujian:
        return jsonify({'error': 'Cannot delete kelas with existing exams'}), 400
    
    db.session.delete(kelas)
    db.session.commit()
    return jsonify({'message': 'Kelas deleted successfully'})

@app.route('/api/teacher/kelas/<int:kelas_id>/siswa', methods=['GET'])
@teacher_required
def teacher_get_siswa_by_kelas(kelas_id):
    # Pastikan kelas yang diakses adalah milik guru yang sedang login
    guru_id = session['user_id']
    kelas = Kelas.query.filter_by(id=kelas_id, guru_id=guru_id).first()
    
    if not kelas:
        return jsonify({'error': 'Kelas not found or access denied'}), 404
    
    siswa_list = Siswa.query.filter_by(kelas=kelas_id).all()
    return jsonify([{
        'no': s.no,
        'NISN': s.NISN,
        'nama_siswa': s.nama_siswa,
        'kelas': s.kelas
    } for s in siswa_list])


@app.route('/api/teacher/siswa', methods=['POST'])
@teacher_required
def teacher_create_siswa():
    data = request.get_json()
    # Check if NISN already exists
    existing_siswa = Siswa.query.filter_by(NISN=data['NISN']).first()
    if existing_siswa:
        return jsonify({'error': 'Student with this NISN already exists'}), 400
    
    # Check if kelas exists dan pastikan milik guru yang sedang login
    guru_id = session['user_id']
    kelas = Kelas.query.filter_by(id=data['kelas'], guru_id=guru_id).first()
    if not kelas:
        return jsonify({'error': 'Kelas not found or access denied'}), 404
    # Create user for siswa
    existing_user = User.query.filter_by(email=data['NISN']).first()
    if existing_user:
        return jsonify({'error': 'User with this NISN already exists'}), 400
    user = User(
        email=data['NISN'],
        password=generate_password_hash(data['NISN']),
        nama_lengkap=data['nama_siswa'],
        jenis_kelamin=data.get('jenis_kelamin', 'laki-laki'),
        role='siswa'
    )
    db.session.add(user)
    db.session.commit()
    # Create siswa with user_id
    siswa = Siswa(
        NISN=data['NISN'],
        nama_siswa=data['nama_siswa'],
        kelas=data['kelas'],
        user_id=user.id
    )
    db.session.add(siswa)
    db.session.commit()
    return jsonify({
        'message': 'Student created successfully',
        'siswa': {
            'no': siswa.no,
            'NISN': siswa.NISN,
            'nama_siswa': siswa.nama_siswa,
            'kelas': siswa.kelas
        }
    })

@app.route('/api/teacher/siswa/bulk', methods=['POST'])
@teacher_required
def teacher_create_siswa_bulk():
    data = request.get_json()
    siswa_list = data.get('siswa_list', [])
    
    if not siswa_list:
        return jsonify({'error': 'No students provided'}), 400
    
    created_siswa = []
    errors = []
    
    for siswa_data in siswa_list:
        try:
            nisn = siswa_data['NISN']
            nama_siswa = siswa_data['nama_siswa']
            kelas_id = siswa_data['kelas']
            jenis_kelamin = siswa_data.get('jenis_kelamin', 'laki-laki')
            
            # Check if NISN already exists in siswa table
            existing_siswa = Siswa.query.filter_by(NISN=nisn).first()
            if existing_siswa:
                errors.append(f"NISN {nisn} already exists")
                continue
            
            # Check if user with this NISN already exists
            existing_user = User.query.filter_by(email=nisn).first()
            if existing_user:
                errors.append(f"User with NISN {nisn} already exists")
                continue
            
            # Check if kelas exists
            kelas = Kelas.query.get(kelas_id)
            if not kelas:
                errors.append(f"Kelas {kelas_id} not found for NISN {nisn}")
                continue
            
            # Create user first
            user = User(
                email=nisn,
                password=generate_password_hash(nisn),  # Default password is NISN
                nama_lengkap=nama_siswa,
                jenis_kelamin=jenis_kelamin,
                role='siswa'
            )
            db.session.add(user)
            db.session.flush()  # Get user.id without committing
            
            # Create siswa with user_id
            siswa = Siswa(
                NISN=nisn,
                nama_siswa=nama_siswa,
                kelas=kelas_id,
                user_id=user.id
            )
            db.session.add(siswa)
            
            created_siswa.append({
                'NISN': nisn,
                'nama_siswa': nama_siswa,
                'kelas': kelas_id,
                'user_id': user.id
            })
            
        except Exception as e:
            errors.append(f"Error creating student {siswa_data.get('NISN', 'Unknown')}: {str(e)}")
    
    try:
        db.session.commit()
        return jsonify({
            'message': f'Successfully created {len(created_siswa)} students',
            'created_siswa': created_siswa,
            'errors': errors
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/teacher/siswa/<int:no>', methods=['PUT'])
@teacher_required
def teacher_update_siswa(no):
    # Pastikan siswa berada di kelas yang dimiliki guru yang sedang login
    guru_id = session['user_id']
    siswa = Siswa.query.join(Kelas).filter(
        Siswa.no == no,
        Kelas.guru_id == guru_id
    ).first()
    
    if not siswa:
        return jsonify({'error': 'Student not found or access denied'}), 404
    
    data = request.get_json()
    
    if 'nama_siswa' in data:
        siswa.nama_siswa = data['nama_siswa']
    if 'kelas' in data:
        # Check if kelas exists dan milik guru yang sama
        kelas = Kelas.query.filter_by(id=data['kelas'], guru_id=guru_id).first()
        if not kelas:
            return jsonify({'error': 'Kelas not found or access denied'}), 404
        siswa.kelas = data['kelas']
    if 'password' in data:
        siswa.password = generate_password_hash(data['password'])
    
    db.session.commit()
    return jsonify({
        'message': 'Student updated successfully',
        'siswa': {
            'no': siswa.no,
            'NISN': siswa.NISN,
            'nama_siswa': siswa.nama_siswa,
            'kelas': siswa.kelas
        }
    })

@app.route('/api/teacher/siswa/<int:no>', methods=['DELETE'])
@teacher_required
def teacher_delete_siswa(no):
    # Pastikan siswa berada di kelas yang dimiliki guru yang sedang login
    guru_id = session['user_id']
    siswa = Siswa.query.join(Kelas).filter(
        Siswa.no == no,
        Kelas.guru_id == guru_id
    ).first()
    
    if not siswa:
        return jsonify({'error': 'Student not found or access denied'}), 404
    
    # Check if student has exam results
    if siswa.ujian_siswa:
        return jsonify({'error': 'Cannot delete student with existing exam results'}), 400
    
    # Check if student has answers
    if siswa.jawaban:
        return jsonify({'error': 'Cannot delete student with existing answers'}), 400
    
    db.session.delete(siswa)
    db.session.commit()
    return jsonify({'message': 'Student deleted successfully'})

@app.route('/api/teacher/siswa/excel', methods=['POST'])
@teacher_required
def teacher_import_siswa_excel():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.xlsx'):
        return jsonify({'error': 'Please upload an Excel file (.xlsx)'}), 400
    
    try:
        # Read Excel file
        df = pd.read_excel(file)
        
        # Validate required columns
        required_columns = ['NISN', 'nama_siswa', 'kelas']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({'error': f'Missing required columns: {missing_columns}'}), 400

        print(df)
        
        created_siswa = []
        errors = []
        guru_id = session['user_id']
        
        for index, row in df.iterrows():
            try:
                nisn = str(row['NISN']).strip() if not pd.isnull(row['NISN']) else ''
                nama_siswa = str(row['nama_siswa']).strip() if not pd.isnull(row['nama_siswa']) else ''
                kelas_id = row['kelas']
                try:
                    kelas_id = int(kelas_id)
                except Exception:
                    kelas_id = None
                jenis_kelamin = str(row.get('jenis_kelamin', 'laki-laki')).strip() if not pd.isnull(row.get('jenis_kelamin', 'laki-laki')) else 'laki-laki'
                
                # Validasi data wajib
                if not nisn or not nama_siswa or not kelas_id:
                    errors.append(f"Row {index + 2}: Data tidak lengkap (NISN, nama_siswa, kelas wajib diisi)")
                    continue
                
                # Check if NISN already exists in siswa table
                existing_siswa = Siswa.query.filter_by(NISN=nisn).first()
                if existing_siswa:
                    errors.append(f"Row {index + 2}: NISN {nisn} already exists")
                    continue
                
                # Check if user with this NISN already exists
                existing_user = User.query.filter_by(email=nisn).first()
                if existing_user:
                    errors.append(f"Row {index + 2}: User with NISN {nisn} already exists")
                    continue
                
                # Check if kelas exists dan milik guru yang sedang login
                kelas_obj = Kelas.query.filter_by(id=kelas_id, guru_id=guru_id).first()
                if not kelas_obj:
                    errors.append(f"Row {index + 2}: Kelas {kelas_id} not found or not owned by this teacher")
                    continue
                
                # Create user first
                user = User(
                    email=nisn,
                    password=generate_password_hash(nisn),  # Default password is NISN
                    nama_lengkap=nama_siswa,
                    jenis_kelamin=jenis_kelamin,
                    role='siswa'
                )
                db.session.add(user)
                db.session.flush()  # Get user.id without committing
                
                # Create siswa with user_id
                siswa = Siswa(
                    NISN=nisn,
                    nama_siswa=nama_siswa,
                    kelas=kelas_id,
                    user_id=user.id
                )
                db.session.add(siswa)
                
                created_siswa.append({
                    'NISN': nisn,
                    'nama_siswa': nama_siswa,
                    'kelas': kelas_id,
                    'user_id': user.id
                })
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                errors.append(f"Row {index + 2}: Error processing data - {str(e)}")
        try:
            db.session.commit()
        except Exception as e:
            import traceback
            traceback.print_exc()
            db.session.rollback()
            errors.append(f"Database commit error: {str(e)}")
        
        return jsonify({
            'message': f'Successfully imported {len(created_siswa)} students',
            'created_siswa': created_siswa,
            'errors': errors
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': f'Error processing Excel file: {str(e)}'}), 500

@app.route('/api/teacher/dashboard', methods=['GET'])
@teacher_required
def teacher_dashboard():
    # Get statistics for teacher dashboard - hanya untuk kelas guru yang sedang login
    guru_id = session['user_id']
    
    # Hitung statistik hanya untuk kelas guru ini
    guru_kelas = Kelas.query.filter_by(guru_id=guru_id).all()
    total_kelas = len(guru_kelas)
    
    # Hitung total siswa di semua kelas guru ini
    total_siswa = 0
    for kelas in guru_kelas:
        total_siswa += len(kelas.siswa)
    
    # Hitung total ujian di semua kelas guru ini
    kelas_ids = [k.id for k in guru_kelas]
    total_ujian = Ujian.query.filter(Ujian.kelas.in_(kelas_ids)).count() if kelas_ids else 0
    
    # Get kelas with student count - hanya kelas guru ini
    kelas_with_count = []
    for kelas in guru_kelas:
        kelas_with_count.append({
            'id': kelas.id,
            'nama': kelas.nama,
            'guru_id': kelas.guru_id,
            'total_siswa': len(kelas.siswa)
        })
    
    return jsonify({
        'statistics': {
            'total_kelas': total_kelas,
            'total_siswa': total_siswa,
            'total_ujian': total_ujian
        },
        'kelas': kelas_with_count
    })

# Endpoint untuk laporan detail ujian dengan analisis comparison
@app.route('/api/teacher/ujian/<int:ujian_id>/detail-report', methods=['GET'])
@teacher_required
def get_ujian_detail_report(ujian_id):
    """
    Endpoint untuk laporan detail ujian termasuk analisis comparison
    """
    # Pastikan ujian ada di kelas yang dimiliki guru yang sedang login
    guru_id = session['user_id']
    ujian = Ujian.query.join(Kelas).filter(
        Ujian.id == ujian_id,
        Kelas.guru_id == guru_id
    ).first()
    
    if not ujian:
        return jsonify({'error': 'Ujian not found or access denied'}), 404
    
    # Get kelas info
    kelas = Kelas.query.get(ujian.kelas)
    
    # Get all soal for this ujian
    soal_list = Soal.query.filter_by(ujian=ujian_id).all()
    
    report_data = {
        'ujian_info': {
            'id': ujian.id,
            'nama_ujian': ujian.nama_ujian,
            'kelas_id': ujian.kelas,
            'kelas_nama': kelas.nama if kelas else 'Unknown',
            'pelaksanaan': ujian.pelaksanaan.isoformat() if ujian.pelaksanaan else None,
            'status': ujian.status,
            'total_soal': len(soal_list)
        },
        'students_performance': [],
        'soal_analysis': [],
        'summary': {
            'total_siswa': 0,
            'siswa_sudah_ujian': 0,
            'siswa_belum_ujian': 0,
            'rata_rata_nilai': 0,
            'nilai_tertinggi': 0,
            'nilai_terendah': 100,
            'total_jawaban_benar': 0,
            'total_jawaban_salah': 0,
            'persentase_kelulusan': 0
        }
    }
    
    # Get all students in the class
    siswa_list = Siswa.query.filter_by(kelas=ujian.kelas).all()
    report_data['summary']['total_siswa'] = len(siswa_list)
    
    nilai_list = []
    
    for siswa in siswa_list:
        # Get exam result for this student
        ujian_siswa = UjianSiswa.query.filter_by(ujian=ujian_id, siswa=siswa.no).first()
        
        student_data = {
            'siswa_info': {
                'no': siswa.no,
                'nisn': siswa.NISN,
                'nama_siswa': siswa.nama_siswa
            },
            'exam_taken': ujian_siswa is not None,
            'nilai': ujian_siswa.nilai if ujian_siswa else None,
            'label_nilai': ujian_siswa.label_nilai if ujian_siswa else None,
            'deskripsi_analisis': ujian_siswa.deskripsi_analisis if ujian_siswa else None,
            'jawaban_detail': []
        }
        
        if ujian_siswa:
            report_data['summary']['siswa_sudah_ujian'] += 1
            nilai_list.append(ujian_siswa.nilai)
            
            # Get detailed answers with comparison analysis
            for soal in soal_list:
                jawaban = JawabanSiswa.query.filter_by(nisn=siswa.NISN, soal=soal.id).first()
                
                jawaban_detail = {
                    'soal_id': soal.id,
                    'soal_text': soal.soal,
                    'correct_answer': soal.json_result,
                    'student_answer': jawaban.json_result if jawaban else None,
                    'status': jawaban.status if jawaban else 'not_answered',
                    'has_comparison': False,
                    'comparison_analysis': None
                }
                
                if jawaban and jawaban.json_result and 'comparison' in jawaban.json_result:
                    jawaban_detail['has_comparison'] = True
                    jawaban_detail['comparison_analysis'] = jawaban.json_result['comparison']
                    
                    # Count correct/incorrect answers (excellent and good = correct)
                    if jawaban.status in ['excellent', 'good']:
                        report_data['summary']['total_jawaban_benar'] += 1
                    else:
                        report_data['summary']['total_jawaban_salah'] += 1
                
                student_data['jawaban_detail'].append(jawaban_detail)
        else:
            report_data['summary']['siswa_belum_ujian'] += 1
        
        report_data['students_performance'].append(student_data)
    
    # Calculate summary statistics
    if nilai_list:
        report_data['summary']['rata_rata_nilai'] = round(sum(nilai_list) / len(nilai_list), 2)
        report_data['summary']['nilai_tertinggi'] = max(nilai_list)
        report_data['summary']['nilai_terendah'] = min(nilai_list)
        
        # Calculate passing rate (nilai >= 60)
        passing_count = len([n for n in nilai_list if n >= 60])
        report_data['summary']['persentase_kelulusan'] = round(
            (passing_count / len(nilai_list)) * 100, 2
        )
    
    # Soal analysis - performance per question
    for soal in soal_list:
        jawaban_list = JawabanSiswa.query.filter_by(soal=soal.id).all()
        
        soal_stats = {
            'soal_id': soal.id,
            'soal_text': soal.soal,
            'correct_answer': soal.json_result,
            'total_jawaban': len(jawaban_list),
            'jawaban_benar': 0,
            'jawaban_salah': 0,
            'tidak_dijawab': report_data['summary']['siswa_sudah_ujian'] - len(jawaban_list),
            'tingkat_kesulitan': 'Mudah',
            'common_mistakes': {
                'operator_salah': 0,
                'operan_1_salah': 0,
                'operan_2_salah': 0,
                'jawaban_salah': 0
            },
            'comparison_analysis_available': 0
        }
        
        for jawaban in jawaban_list:
            if jawaban.status in ['excellent', 'good']:
                soal_stats['jawaban_benar'] += 1
            else:
                soal_stats['jawaban_salah'] += 1
            
            # Analyze common mistakes from comparison data
            if jawaban.json_result and 'comparison' in jawaban.json_result:
                soal_stats['comparison_analysis_available'] += 1
                comparison = jawaban.json_result['comparison']
                
                if 'parameter_salah' in comparison:
                    for param in comparison['parameter_salah']:
                        if param in soal_stats['common_mistakes']:
                            soal_stats['common_mistakes'][param] += 1
        
        # Determine difficulty level based on correct answer percentage
        if soal_stats['total_jawaban'] > 0:
            correct_percentage = (soal_stats['jawaban_benar'] / soal_stats['total_jawaban']) * 100
            if correct_percentage >= 80:
                soal_stats['tingkat_kesulitan'] = 'Mudah'
            elif correct_percentage >= 60:
                soal_stats['tingkat_kesulitan'] = 'Sedang'
            else:
                soal_stats['tingkat_kesulitan'] = 'Sulit'
        
        report_data['soal_analysis'].append(soal_stats)
    
    return jsonify(report_data)

# Endpoint untuk laporan ringkasan kelas dengan analisis comparison
@app.route('/api/teacher/kelas/<int:kelas_id>/comparison-summary', methods=['GET'])
@teacher_required
def get_kelas_comparison_summary(kelas_id):
    """
    Endpoint untuk ringkasan analisis comparison per kelas
    """
    # Pastikan kelas yang diakses adalah milik guru yang sedang login
    guru_id = session['user_id']
    kelas = Kelas.query.filter_by(id=kelas_id, guru_id=guru_id).first()
    
    if not kelas:
        return jsonify({'error': 'Kelas not found or access denied'}), 404
    
    # Get all ujian for this kelas
    ujian_list = Ujian.query.filter_by(kelas=kelas_id).all()
    
    summary_data = {
        'kelas_info': {
            'id': kelas.id,
            'nama': kelas.nama,
            'total_siswa': len(kelas.siswa)
        },
        'ujian_summary': [],
        'overall_stats': {
            'total_ujian': len(ujian_list),
            'total_jawaban_analyzed': 0,
            'average_score': 0,
            'common_mistakes': {
                'operator_salah': 0,
                'operan_1_salah': 0,
                'operan_2_salah': 0,
                'jawaban_salah': 0
            },
            'skill_analysis': {
                'operator_mastery': 0,
                'calculation_accuracy': 0,
                'problem_solving': 0
            }
        }
    }
    
    all_scores = []
    total_analyzed = 0
    overall_mistakes = summary_data['overall_stats']['common_mistakes']
    
    for ujian in ujian_list:
        # Get exam results
        ujian_siswa_list = UjianSiswa.query.filter_by(ujian=ujian.id).all()
        
        ujian_stats = {
            'ujian_id': ujian.id,
            'nama_ujian': ujian.nama_ujian,
            'pelaksanaan': ujian.pelaksanaan.isoformat() if ujian.pelaksanaan else None,
            'total_participants': len(ujian_siswa_list),
            'average_score': 0,
            'comparison_analysis_count': 0
        }
        
        ujian_scores = []
        for us in ujian_siswa_list:
            if us.nilai is not None:
                ujian_scores.append(us.nilai)
                all_scores.append(us.nilai)
        
        if ujian_scores:
            ujian_stats['average_score'] = round(sum(ujian_scores) / len(ujian_scores), 2)
        
        # Count comparison analyses for this ujian
        soal_list = Soal.query.filter_by(ujian=ujian.id).all()
        for soal in soal_list:
            jawaban_list = JawabanSiswa.query.filter_by(soal=soal.id).all()
            for jawaban in jawaban_list:
                if jawaban.json_result and 'comparison' in jawaban.json_result:
                    ujian_stats['comparison_analysis_count'] += 1
                    total_analyzed += 1
                    
                    # Aggregate mistakes
                    comparison = jawaban.json_result['comparison']
                    if 'parameter_salah' in comparison:
                        for param in comparison['parameter_salah']:
                            if param in overall_mistakes:
                                overall_mistakes[param] += 1
        
        summary_data['ujian_summary'].append(ujian_stats)
    
    # Calculate overall statistics
    summary_data['overall_stats']['total_jawaban_analyzed'] = total_analyzed
    
    if all_scores:
        summary_data['overall_stats']['average_score'] = round(sum(all_scores) / len(all_scores), 2)
    
    # Calculate skill mastery percentages
    if total_analyzed > 0:
        # Operator mastery: correct operator / total analyzed
        operator_correct = total_analyzed - overall_mistakes['operator_salah']
        summary_data['overall_stats']['skill_analysis']['operator_mastery'] = round(
            (operator_correct / total_analyzed) * 100, 2
        )
        
        # Calculation accuracy: correct operands / total analyzed  
        operand_errors = overall_mistakes['operan_1_salah'] + overall_mistakes['operan_2_salah']
        calculation_correct = total_analyzed - operand_errors
        summary_data['overall_stats']['skill_analysis']['calculation_accuracy'] = round(
            (calculation_correct / total_analyzed) * 100, 2
        )
        
        # Problem solving: correct final answers / total analyzed
        answer_correct = total_analyzed - overall_mistakes['jawaban_salah']
        summary_data['overall_stats']['skill_analysis']['problem_solving'] = round(
            (answer_correct / total_analyzed) * 100, 2
        )
    
    return jsonify(summary_data)

# Endpoint untuk laporan individual siswa dengan analisis comparison
@app.route('/api/teacher/siswa/<int:siswa_no>/comparison-report', methods=['GET'])
@teacher_required
def get_siswa_comparison_report(siswa_no):
    """
    Endpoint untuk laporan individual siswa dengan analisis comparison
    """
    siswa = Siswa.query.get_or_404(siswa_no)
    kelas = Kelas.query.get(siswa.kelas)
    
    # Get all exam results for this student
    ujian_siswa_list = UjianSiswa.query.filter_by(siswa=siswa_no).all()
    
    report_data = {
        'siswa_info': {
            'no': siswa.no,
            'nisn': siswa.NISN,
            'nama_siswa': siswa.nama_siswa,
            'kelas_id': siswa.kelas,
            'kelas_nama': kelas.nama if kelas else 'Unknown'
        },
        'exam_history': [],
        'overall_performance': {
            'total_ujian': len(ujian_siswa_list),
            'rata_rata_nilai': 0,
            'nilai_tertinggi': 0,
            'nilai_terendah': 100,
            'total_jawaban_analyzed': 0,
            'skill_progress': {
                'operator_mastery': [],
                'calculation_accuracy': [],
                'problem_solving': []
            },
            'common_mistakes': {
                'operator_salah': 0,
                'operan_1_salah': 0,
                'operan_2_salah': 0,
                'jawaban_salah': 0
            }
        },
        'recommendations': []
    }
    
    nilai_list = []
    total_analyzed = 0
    overall_mistakes = report_data['overall_performance']['common_mistakes']
    
    for ujian_siswa in ujian_siswa_list:
        ujian = Ujian.query.get(ujian_siswa.ujian)
        if not ujian:
            continue
            
        nilai_list.append(ujian_siswa.nilai)
        
        exam_data = {
            'ujian_info': {
                'id': ujian.id,
                'nama_ujian': ujian.nama_ujian,
                'pelaksanaan': ujian.pelaksanaan.isoformat() if ujian.pelaksanaan else None
            },
            'nilai': ujian_siswa.nilai,
            'label_nilai': ujian_siswa.label_nilai,
            'deskripsi_analisis': ujian_siswa.deskripsi_analisis,
            'jawaban_detail': [],
            'exam_analysis': {
                'total_soal': 0,
                'jawaban_benar': 0,
                'jawaban_salah': 0,
                'operator_correct': 0,
                'calculation_correct': 0,
                'final_answer_correct': 0
            }
        }
        
        # Get detailed answers for this exam
        soal_list = Soal.query.filter_by(ujian=ujian.id).all()
        exam_data['exam_analysis']['total_soal'] = len(soal_list)
        
        for soal in soal_list:
            jawaban = JawabanSiswa.query.filter_by(nisn=siswa.NISN, soal=soal.id).first()
            
            jawaban_detail = {
                'soal_id': soal.id,
                'soal_text': soal.soal,
                'correct_answer': soal.json_result,
                'student_answer': jawaban.json_result if jawaban else None,
                'status': jawaban.status if jawaban else 'not_answered',
                'has_comparison': False,
                'comparison_analysis': None
            }
            
            if jawaban and jawaban.json_result and 'comparison' in jawaban.json_result:
                jawaban_detail['has_comparison'] = True
                jawaban_detail['comparison_analysis'] = jawaban.json_result['comparison']
                total_analyzed += 1
                
                comparison = jawaban.json_result['comparison']
                
                # Count skill performance
                if 'parameter_salah' in comparison:
                    for param in comparison['parameter_salah']:
                        if param in overall_mistakes:
                            overall_mistakes[param] += 1
                
                # Track individual skills for this exam
                if 'operator' not in comparison.get('parameter_salah', []):
                    exam_data['exam_analysis']['operator_correct'] += 1
                
                if 'operan_1' not in comparison.get('parameter_salah', []) and 'operan_2' not in comparison.get('parameter_salah', []):
                    exam_data['exam_analysis']['calculation_correct'] += 1
                
                if 'jawaban' not in comparison.get('parameter_salah', []):
                    exam_data['exam_analysis']['final_answer_correct'] += 1
                
                if jawaban.status in ['excellent', 'good']:
                    exam_data['exam_analysis']['jawaban_benar'] += 1
                else:
                    exam_data['exam_analysis']['jawaban_salah'] += 1
            
            exam_data['jawaban_detail'].append(jawaban_detail)
        
        # Calculate skill percentages for this exam
        if exam_data['exam_analysis']['total_soal'] > 0:
            total_soal = exam_data['exam_analysis']['total_soal']
            
            operator_pct = (exam_data['exam_analysis']['operator_correct'] / total_soal) * 100
            calculation_pct = (exam_data['exam_analysis']['calculation_correct'] / total_soal) * 100
            answer_pct = (exam_data['exam_analysis']['final_answer_correct'] / total_soal) * 100
            
            report_data['overall_performance']['skill_progress']['operator_mastery'].append({
                'ujian_id': ujian.id,
                'nama_ujian': ujian.nama_ujian,
                'percentage': round(operator_pct, 2)
            })
            
            report_data['overall_performance']['skill_progress']['calculation_accuracy'].append({
                'ujian_id': ujian.id,
                'nama_ujian': ujian.nama_ujian,
                'percentage': round(calculation_pct, 2)
            })
            
            report_data['overall_performance']['skill_progress']['problem_solving'].append({
                'ujian_id': ujian.id,
                'nama_ujian': ujian.nama_ujian,
                'percentage': round(answer_pct, 2)
            })
        
        report_data['exam_history'].append(exam_data)
    
    # Calculate overall performance statistics
    if nilai_list:
        report_data['overall_performance']['rata_rata_nilai'] = round(sum(nilai_list) / len(nilai_list), 2)
        report_data['overall_performance']['nilai_tertinggi'] = max(nilai_list)
        report_data['overall_performance']['nilai_terendah'] = min(nilai_list)
    
    report_data['overall_performance']['total_jawaban_analyzed'] = total_analyzed
    
    # Generate recommendations based on performance
    recommendations = []
    
    if total_analyzed > 0:
        operator_error_rate = (overall_mistakes['operator_salah'] / total_analyzed) * 100
        calculation_error_rate = ((overall_mistakes['operan_1_salah'] + overall_mistakes['operan_2_salah']) / total_analyzed) * 100
        answer_error_rate = (overall_mistakes['jawaban_salah'] / total_analyzed) * 100
        
        if operator_error_rate > 30:
            recommendations.append({
                'type': 'operator_improvement',
                'priority': 'high',
                'message': 'Siswa perlu meningkatkan pemahaman tentang operator matematika (penjumlahan, pengurangan, perkalian, pembagian)',
                'suggestions': [
                    'Latihan soal cerita dengan berbagai jenis operator',
                    'Pembelajaran visual tentang makna setiap operator',
                    'Game interaktif untuk mengenali operator'
                ]
            })
        
        if calculation_error_rate > 25:
            recommendations.append({
                'type': 'calculation_improvement',
                'priority': 'high',
                'message': 'Siswa perlu meningkatkan kemampuan mengidentifikasi angka dalam soal',
                'suggestions': [
                    'Latihan membaca soal cerita dengan teliti',
                    'Teknik menggarisbawahi angka penting dalam soal',
                    'Latihan soal dengan variasi penulisan angka'
                ]
            })
        
        if answer_error_rate > 20:
            recommendations.append({
                'type': 'problem_solving_improvement',
                'priority': 'medium',
                'message': 'Siswa perlu meningkatkan kemampuan menghitung hasil akhir',
                'suggestions': [
                    'Latihan operasi hitung dasar',
                    'Penggunaan alat bantu hitung',
                    'Verifikasi hasil dengan cara berbeda'
                ]
            })
        
        # Positive reinforcement for good performance
        if operator_error_rate < 10:
            recommendations.append({
                'type': 'positive_reinforcement',
                'priority': 'low',
                'message': 'Siswa menunjukkan pemahaman yang baik tentang operator matematika',
                'suggestions': [
                    'Lanjutkan dengan soal yang lebih menantang',
                    'Berikan peran sebagai tutor sebaya'
                ]
            })
    
    report_data['recommendations'] = recommendations
    
    return jsonify(report_data)

# User routes
@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'email': user.email,
        'nama_lengkap': user.nama_lengkap,
        'jenis_kelamin': user.jenis_kelamin,
        'role': user.role
    } for user in users])

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    # Cek apakah email sudah ada
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'error': f"User dengan email {data['email']} sudah terdaftar."}), 400

    user = User(
        email=data['email'],
        password=generate_password_hash(data['password']),
        nama_lengkap=data['nama_lengkap'],
        jenis_kelamin=data['jenis_kelamin'],
        role=data.get('role', 'guru')  # Default to guru if not specified
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created successfully', 'id': user.id})

@app.route('/api/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify({
        'id': user.id,
        'email': user.email,
        'nama_lengkap': user.nama_lengkap,
        'jenis_kelamin': user.jenis_kelamin,
        'role': user.role
    })

@app.route('/api/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.get_json()
    
    if 'email' in data:
        user.email = data['email']
    if 'password' in data:
        user.password = generate_password_hash(data['password'])
    if 'nama_lengkap' in data:
        user.nama_lengkap = data['nama_lengkap']
    if 'jenis_kelamin' in data:
        user.jenis_kelamin = data['jenis_kelamin']
    if 'role' in data:
        user.role = data['role']
    
    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

@app.route('/api/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})

# Student Authentication routes
@app.route('/api/student/logout', methods=['POST'])
@login_required
def student_logout():
    session.clear()
    return jsonify({'message': 'Logout successful'})

@app.route('/api/student/profile', methods=['GET'])
@student_required
def get_student_profile():
    user_id = session.get('user_id')
    
    # Get student data with JOIN
    student_data = db.session.query(User, Siswa, Kelas)\
        .join(Siswa, User.id == Siswa.user_id)\
        .join(Kelas, Siswa.kelas == Kelas.id)\
        .filter(User.id == user_id)\
        .first()
    
    if not student_data:
        return jsonify({'error': 'Student profile not found'}), 404
        
    user, siswa, kelas = student_data
    
    return jsonify({
        'user_id': user.id,
        'email': user.email,
        'nama_lengkap': user.nama_lengkap,
        'jenis_kelamin': user.jenis_kelamin,
        'role': user.role,
        'siswa_no': siswa.no,
        'NISN': siswa.NISN,
        'nama_siswa': siswa.nama_siswa,
        'kelas': {
            'id': kelas.id,
            'nama': kelas.nama
        }
    })

# Kelas routes
@app.route('/api/kelas', methods=['GET'])
def get_kelas():
    # Jika login sebagai siswa, hanya tampilkan kelas siswa tersebut
    if 'role' in session and session['role'] == 'siswa':
        kelas_id = session.get('kelas_id')
        
        if not kelas_id:
            return jsonify({'error': 'Data kelas siswa tidak ditemukan dalam session'}), 404
        
        # Get kelas by ID from session
        kelas = Kelas.query.filter_by(id=kelas_id).all()
        
        if not kelas:
            return jsonify({'error': 'Kelas tidak ditemukan'}), 404
    elif 'role' in session and session['role'] == 'guru':
        # For guru, show only their classes
        guru_id = session['user_id']
        kelas = Kelas.query.filter_by(guru_id=guru_id).all()
    else:
        # For admin, show all classes
        kelas = Kelas.query.all()
    
    return jsonify([{
        'id': k.id,
        'nama': k.nama,
        'guru_id': k.guru_id if hasattr(k, 'guru_id') else None
    } for k in kelas])

@app.route('/api/kelas', methods=['POST'])
def create_kelas():
    data = request.get_json()
    
    # Jika guru yang membuat kelas, assign guru_id
    if 'role' in session and session['role'] == 'guru':
        guru_id = session['user_id']
        kelas = Kelas(id=data['id'], nama=data['nama'], guru_id=guru_id)
    else:
        # Admin bisa membuat kelas untuk guru tertentu
        guru_id = data.get('guru_id')
        if not guru_id:
            return jsonify({'error': 'guru_id is required'}), 400
        kelas = Kelas(id=data['id'], nama=data['nama'], guru_id=guru_id)
    
    db.session.add(kelas)
    db.session.commit()
    return jsonify({
        'message': 'Kelas created successfully',
        'kelas': {
            'id': kelas.id,
            'nama': kelas.nama,
            'guru_id': kelas.guru_id
        }
    })

@app.route('/api/kelas/<int:id>', methods=['GET'])
def get_kelas_by_id(id):
    # Jika guru, pastikan hanya bisa akses kelas mereka
    if 'role' in session and session['role'] == 'guru':
        guru_id = session['user_id']
        kelas = Kelas.query.filter_by(id=id, guru_id=guru_id).first()
        if not kelas:
            return jsonify({'error': 'Kelas not found or access denied'}), 404
    else:
        kelas = Kelas.query.get_or_404(id)
    
    return jsonify({
        'id': kelas.id,
        'nama': kelas.nama,
        'guru_id': kelas.guru_id
    })

@app.route('/api/kelas/<int:id>', methods=['PUT'])
def update_kelas(id):
    # Jika guru, pastikan hanya bisa update kelas mereka
    if 'role' in session and session['role'] == 'guru':
        guru_id = session['user_id']
        kelas = Kelas.query.filter_by(id=id, guru_id=guru_id).first()
        if not kelas:
            return jsonify({'error': 'Kelas not found or access denied'}), 404
    else:
        kelas = Kelas.query.get_or_404(id)
    
    data = request.get_json()
    
    if 'nama' in data:
        kelas.nama = data['nama']
    
    db.session.commit()
    return jsonify({
        'message': 'Kelas updated successfully',
        'kelas': {
            'id': kelas.id,
            'nama': kelas.nama,
            'guru_id': kelas.guru_id
        }
    })

@app.route('/api/kelas/<int:id>', methods=['DELETE'])
def delete_kelas(id):
    # Jika guru, pastikan hanya bisa delete kelas mereka
    if 'role' in session and session['role'] == 'guru':
        guru_id = session['user_id']
        kelas = Kelas.query.filter_by(id=id, guru_id=guru_id).first()
        if not kelas:
            return jsonify({'error': 'Kelas not found or access denied'}), 404
    else:
        kelas = Kelas.query.get_or_404(id)
    
    # Check if there are students in this class
    if kelas.siswa:
        return jsonify({'error': 'Cannot delete kelas with existing students'}), 400
    
    # Check if there are exams for this class
    if kelas.ujian:
        return jsonify({'error': 'Cannot delete kelas with existing exams'}), 400
    
    db.session.delete(kelas)
    db.session.commit()
    return jsonify({'message': 'Kelas deleted successfully'})

# Siswa routes
@app.route('/api/siswa', methods=['GET'])
def get_siswa():
    siswa = Siswa.query.all()
    return jsonify([{
        'no': s.no,
        'NISN': s.NISN,
        'nama_siswa': s.nama_siswa,
        'kelas': s.kelas
    } for s in siswa])

@app.route('/api/siswa', methods=['POST'])
def create_siswa():
    data = request.get_json()
    # Validasi kelas
    kelas_id = data.get('kelas')
    kelas_obj = Kelas.query.get(kelas_id)
    if not kelas_obj:
        return jsonify({'error': f'Kelas dengan id {kelas_id} tidak ditemukan. Tambahkan kelas terlebih dahulu.'}), 400
    # Cek apakah user dengan NISN sudah ada
    existing_user = User.query.filter_by(email=data['NISN']).first()
    if existing_user:
        return jsonify({'error': 'User dengan NISN ini sudah terdaftar.'}), 400
    # Buat user baru
    user = User(
        email=data['NISN'],
        password=generate_password_hash(data['NISN']),
        nama_lengkap=data['nama_siswa'],
        jenis_kelamin=data.get('jenis_kelamin', 'laki-laki'),
        role='siswa'
    )
    db.session.add(user)
    db.session.commit()
    # Set default password as NISN dan user_id
    siswa = Siswa(
        NISN=data['NISN'],
        nama_siswa=data['nama_siswa'],
        kelas=kelas_id,
        user_id=user.id
    )
    db.session.add(siswa)
    db.session.commit()
    return jsonify({'message': 'Siswa created successfully with default password (NISN)'})

@app.route('/api/siswa/<int:no>', methods=['GET'])
def get_siswa_by_id(no):
    siswa = Siswa.query.get_or_404(no)
    return jsonify({
        'no': siswa.no,
        'NISN': siswa.NISN,
        'nama_siswa': siswa.nama_siswa,
        'kelas': siswa.kelas
    })

@app.route('/api/siswa/<int:no>', methods=['PUT'])
def update_siswa(no):
    siswa = Siswa.query.get_or_404(no)
    data = request.get_json()
    
    if 'NISN' in data:
        siswa.NISN = data['NISN']
    if 'nama_siswa' in data:
        siswa.nama_siswa = data['nama_siswa']
    if 'kelas' in data:
        siswa.kelas = data['kelas']
    
    db.session.commit()
    return jsonify({'message': 'Siswa updated successfully'})

@app.route('/api/siswa/<int:no>', methods=['DELETE'])
def delete_siswa(no):
    siswa = Siswa.query.get_or_404(no)
    db.session.delete(siswa)
    db.session.commit()
    return jsonify({'message': 'Siswa deleted successfully'})

@app.route('/api/siswa/excel', methods=['POST'])
def import_siswa_excel():
    # get guru id
    guru_id = session['user_id']

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({'error': 'File must be an Excel file (.xlsx or .xls)'}), 400
    
    try:
        # Read Excel file
        df = pd.read_excel(file)
        
        # Validate required columns
        required_columns = ['NISN', 'nama_siswa', 'kelas']
        if not all(col in df.columns for col in required_columns):
            return jsonify({'error': f'Excel file must contain columns: {", ".join(required_columns)}'}), 400
        
        # Process each row
        success_count = 0
        error_count = 0
        errors = []
        created_students = []
        
        # Get the next available ID for Kelas
        next_kelas_id = db.session.query(db.func.max(Kelas.id)).scalar() or 0
        next_kelas_id += 1
        
        for index, row in df.iterrows():
            try:
                nisn = str(row['NISN']).strip()
                nama_siswa = str(row['nama_siswa']).strip()
                kelas_nama = str(row['kelas']).strip()
                jenis_kelamin = str(row.get('jenis_kelamin', 'laki-laki')).strip()
                
                # Check if kelas exists
                kelas = Kelas.query.filter_by(nama=kelas_nama).first()
                
                # If kelas doesn't exist, create it with the next available ID
                if not kelas:
                    kelas = Kelas(id=next_kelas_id, nama=kelas_nama, guru_id=guru_id)
                    db.session.add(kelas)
                    db.session.flush()  # Get the ID without committing
                    next_kelas_id += 1
                
                # Check if student with NISN already exists in siswa table
                existing_siswa = Siswa.query.filter_by(NISN=nisn).first()
                if existing_siswa:
                    error_count += 1
                    errors.append(f"Row {index + 2}: NISN {nisn} already exists in siswa table")
                    continue
                
                # Check if user with this NISN already exists
                existing_user = User.query.filter_by(email=nisn).first()
                if existing_user:
                    error_count += 1
                    errors.append(f"Row {index + 2}: User with NISN {nisn} already exists")
                    continue
                
                # Create user first
                user = User(
                    email=nisn,
                    password=generate_password_hash(nisn),  # Default password is NISN
                    nama_lengkap=nama_siswa,
                    jenis_kelamin=jenis_kelamin,
                    role='siswa'
                )
                db.session.add(user)
                db.session.flush()  # Get user.id without committing
                
                # Create new student with user_id
                siswa = Siswa(
                    NISN=nisn,
                    nama_siswa=nama_siswa,
                    kelas=kelas.id,
                    user_id=user.id
                )
                db.session.add(siswa)
                
                success_count += 1
                created_students.append({
                    'NISN': nisn,
                    'nama_siswa': nama_siswa,
                    'kelas': kelas.id,
                    'kelas_nama': kelas_nama,
                    'user_id': user.id
                })
                
            except Exception as e:
                error_count += 1
                errors.append(f"Row {index + 2}: {str(e)}")
                continue
        
        # Commit all changes
        db.session.commit()
        
        return jsonify({
            'message': 'Import completed',
            'success_count': success_count,
            'error_count': error_count,
            'created_students': created_students,
            'errors': errors
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

# Ujian routes
@app.route('/api/ujian', methods=['GET'])
def get_ujian():
    # Jika guru, hanya tampilkan ujian dari kelas mereka
    if 'role' in session and session['role'] == 'guru':
        guru_id = session['user_id']
        ujian = Ujian.query.join(Kelas).filter(Kelas.guru_id == guru_id).all()
    else:
        ujian = Ujian.query.all()
    
    return jsonify([{
        'id': u.id,
        'nama_ujian': u.nama_ujian,
        'kelas': u.kelas,
        'pelaksanaan': u.pelaksanaan.strftime('%Y-%m-%d'),
        'status': u.status
    } for u in ujian])

@app.route('/api/ujian', methods=['POST'])
def create_ujian():
    data = request.get_json()
    
    # Jika guru, pastikan kelas yang dipilih adalah milik mereka
    if 'role' in session and session['role'] == 'guru':
        guru_id = session['user_id']
        kelas = Kelas.query.filter_by(id=data['kelas'], guru_id=guru_id).first()
        if not kelas:
            return jsonify({'error': 'Kelas not found or access denied'}), 404
    
    ujian = Ujian(
        nama_ujian=data['nama_ujian'],
        kelas=data['kelas'],
        pelaksanaan=datetime.strptime(data['pelaksanaan'], '%Y-%m-%d').date(),
        status=data['status']
    )
    db.session.add(ujian)
    db.session.commit()
    return jsonify({
        'message': 'Ujian created successfully',
        'ujian': {
            'id': ujian.id,
            'nama_ujian': ujian.nama_ujian,
            'kelas': ujian.kelas,
            'pelaksanaan': ujian.pelaksanaan.strftime('%Y-%m-%d'),
            'status': ujian.status
        }
    })

@app.route('/api/ujian/<int:id>', methods=['GET'])
def get_ujian_by_id(id):
    ujian = Ujian.query.get_or_404(id)
    return jsonify({
        'id': ujian.id,
        'nama_ujian': ujian.nama_ujian,
        'kelas': ujian.kelas,
        'pelaksanaan': ujian.pelaksanaan.strftime('%Y-%m-%d'),
        'status': ujian.status
    })

@app.route('/api/ujian/<int:id>', methods=['PUT'])
def update_ujian(id):
    ujian = Ujian.query.get_or_404(id)
    data = request.get_json()
    
    if 'nama_ujian' in data:
        ujian.nama_ujian = data['nama_ujian']
    if 'kelas' in data:
        ujian.kelas = data['kelas']
    if 'pelaksanaan' in data:
        ujian.pelaksanaan = datetime.strptime(data['pelaksanaan'], '%Y-%m-%d').date()
    if 'status' in data:
        ujian.status = data['status']
    
    db.session.commit()
    return jsonify({'message': 'Ujian updated successfully'})

@app.route('/api/ujian/<int:id>', methods=['DELETE'])
def delete_ujian(id):
    ujian = Ujian.query.get_or_404(id)
    # Delete all related JawabanSiswa for Soal in this Ujian
    for soal in ujian.soal:
        for jawaban in soal.jawaban:
            db.session.delete(jawaban)
    # Delete all related Soal
    for soal in ujian.soal:
        db.session.delete(soal)
    # Delete all related UjianSiswa
    for us in ujian.ujian_siswa:
        db.session.delete(us)
    db.session.delete(ujian)
    db.session.commit()
    return jsonify({'message': 'Ujian beserta data terkait berhasil dihapus'})

# UjianSiswa routes
@app.route('/api/ujian-siswa', methods=['GET'])
def get_ujian_siswa():
    ujian_siswa = UjianSiswa.query.all()
    return jsonify([{
        'id': us.id,
        'ujian': us.ujian,
        'siswa': us.siswa,
        'nilai': us.nilai,
        'label_nilai': us.label_nilai,
        'deskripsi_analisis': us.deskripsi_analisis
    } for us in ujian_siswa])

@app.route('/api/ujian-siswa', methods=['POST'])
def create_ujian_siswa():
    data = request.get_json()
    print(f"create_ujian_siswa - received data: {data}")

    nisn = data.get('nisn')
    ujian = data.get('ujian')
    if not nisn or not ujian:
        return jsonify({'error': 'NISN and ujian are required'}), 400

    siswa = Siswa.query.filter_by(NISN=nisn).first()
    if not siswa:
        return jsonify({'error': 'Siswa with NISN not found'}), 404

    # Ambil semua jawaban siswa untuk ujian ini
    soal_ids = [s.id for s in Soal.query.filter_by(ujian=ujian).all()]
    jawaban_list = JawabanSiswa.query.filter(JawabanSiswa.nisn==nisn, JawabanSiswa.soal.in_(soal_ids)).all()
    total_nilai = sum(jawaban.nilai or 0 for jawaban in jawaban_list)
    max_nilai = len(jawaban_list) * 4  # 4 poin per soal

    nilai_persen = int(round((total_nilai / max_nilai) * 100)) if max_nilai > 0 else 0

    print(f"create_ujian_siswa - total_nilai: {total_nilai}, max_nilai: {max_nilai}, nilai_persen: {nilai_persen}")

    ujian_siswa = UjianSiswa(
        ujian=ujian,
        siswa=siswa.no,
        nilai=nilai_persen,
        label_nilai=data.get('label_nilai'),
        deskripsi_analisis=data.get('deskripsi_analisis')
    )
    try:
        db.session.add(ujian_siswa)
        db.session.commit()
        print(f"create_ujian_siswa - successfully created ujian_siswa: {ujian_siswa.id}")
        return jsonify({'message': 'Ujian siswa created successfully'})
    except Exception as e:
        db.session.rollback()
        print(f"create_ujian_siswa - error: {str(e)}")
        return jsonify({'error': 'Failed to create ujian siswa', 'details': str(e)}), 500


@app.route('/api/ujian-siswa/<int:id>', methods=['GET'])
def get_ujian_siswa_by_id(id):
    ujian_siswa = UjianSiswa.query.get_or_404(id)
    return jsonify({
        'id': ujian_siswa.id,
        'ujian': ujian_siswa.ujian,
        'siswa': ujian_siswa.siswa,
        'nilai': ujian_siswa.nilai,
        'label_nilai': ujian_siswa.label_nilai,
        'deskripsi_analisis': ujian_siswa.deskripsi_analisis
    })

@app.route('/api/ujian-siswa/<int:id>', methods=['PUT'])
def update_ujian_siswa(id):
    ujian_siswa = UjianSiswa.query.get_or_404(id)
    data = request.get_json()
    
    if 'ujian' in data:
        ujian_siswa.ujian = data['ujian']
    if 'siswa' in data:
        ujian_siswa.siswa = data['siswa']
    if 'nilai' in data:
        ujian_siswa.nilai = data['nilai']
    if 'label_nilai' in data:
        ujian_siswa.label_nilai = data['label_nilai']
    if 'deskripsi_analisis' in data:
        ujian_siswa.deskripsi_analisis = data['deskripsi_analisis']
    
    db.session.commit()
    return jsonify({'message': 'Ujian siswa updated successfully'})

@app.route('/api/ujian-siswa/<int:id>', methods=['DELETE'])
def delete_ujian_siswa(id):
    ujian_siswa = UjianSiswa.query.get_or_404(id)
    db.session.delete(ujian_siswa)
    db.session.commit()
    return jsonify({'message': 'Ujian siswa deleted successfully'})

# Soal routes
@app.route('/api/soal', methods=['GET'])
def get_soal():
    soal = Soal.query.all()
    return jsonify([{
        'id': s.id,
        'soal': s.soal,
        'ujian': s.ujian,
        'json_result': s.json_result
    } for s in soal])

@app.route('/api/soal', methods=['POST'])
def create_soal():
    data = request.get_json()
    ujian_id = data.get('ujian')
    ujian_obj = Ujian.query.get(ujian_id)
    if not ujian_obj:
        return jsonify({'error': f'Ujian dengan id {ujian_id} tidak ditemukan. Tambahkan ujian terlebih dahulu.'}), 400

    soal = Soal(
        soal=data['soal'],
        ujian=ujian_id,
        json_result=data.get('json_result', {
            "operator": "",
            "angka_dalam_soal": "",
            "jawaban": ""
        })
    )
    db.session.add(soal)
    db.session.commit()
    return jsonify({'message': 'Soal created successfully'})

@app.route('/api/soal/<int:id>', methods=['GET'])
def get_soal_by_id(id):
    soal = Soal.query.get_or_404(id)
    return jsonify({
        'id': soal.id,
        'soal': soal.soal,
        'ujian': soal.ujian
    })

@app.route('/api/soal/<int:id>', methods=['PUT'])
def update_soal(id):
    soal = Soal.query.get_or_404(id)
    data = request.get_json()
    
    if 'soal' in data:
        soal.soal = data['soal']
    if 'ujian' in data:
        soal.ujian = data['ujian']
    if 'json_result' in data:
        soal.json_result = data['json_result']
    
    db.session.commit()
    return jsonify({'message': 'Soal updated successfully'})

@app.route('/api/soal/<int:id>', methods=['DELETE'])
def delete_soal(id):
    soal = Soal.query.get_or_404(id)
    db.session.delete(soal)
    db.session.commit()
    return jsonify({'message': 'Soal deleted successfully'})

# JawabanSiswa routes
@app.route('/api/jawaban-siswa', methods=['GET'])
def get_jawaban_siswa():
    jawaban = JawabanSiswa.query.all()
    return jsonify([{
        'id': j.id,
        'nisn': j.nisn,  # Changed from j.siswa to j.nisn
        'soal': j.soal,
        'status': j.status,
        'json_result': j.json_result
    } for j in jawaban])

@app.route('/api/jawaban-siswa', methods=['POST'])
@teacher_required
def create_jawaban_siswa():
    data = request.get_json()
    nisn = data.get('nisn')
    siswa = Siswa.query.filter_by(NISN=nisn).first()
    if not siswa:
        return jsonify({'error': 'Siswa dengan NISN tersebut tidak ditemukan'}), 404
    jawaban = JawabanSiswa(
        nisn=nisn,
        soal=data['soal'],
        status=data['status'],
        json_result=data.get('json_result')
    )
    db.session.add(jawaban)
    db.session.commit()
    return jsonify({'message': 'Jawaban siswa created successfully'})

@app.route('/api/jawaban-siswa/<int:id>', methods=['GET'])
def get_jawaban_siswa_by_id(id):
    jawaban = JawabanSiswa.query.get_or_404(id)
    return jsonify({
        'id': jawaban.id,
        'nisn': jawaban.nisn,  # Changed from jawaban.siswa to jawaban.nisn
        'soal': jawaban.soal,
        'status': jawaban.status,
        'json_result': jawaban.json_result
    })

@app.route('/api/jawaban-siswa/<int:id>', methods=['PUT'])
def update_jawaban_siswa(id):
    jawaban = JawabanSiswa.query.get_or_404(id)
    data = request.get_json()
    
    if 'nisn' in data:
        jawaban.nisn = data['nisn']  # Changed from siswa to nisn
    if 'soal' in data:
        jawaban.soal = data['soal']
    if 'status' in data:
        jawaban.status = data['status']
    if 'json_result' in data:
        jawaban.json_result = data['json_result']
    if 'nilai' in data:
        jawaban.nilai = data['nilai']
    
    db.session.commit()
    return jsonify({'message': 'Jawaban siswa updated successfully'})

@app.route('/api/jawaban-siswa/<int:id>', methods=['DELETE'])
def delete_jawaban_siswa(id):
    jawaban = JawabanSiswa.query.get_or_404(id)
    db.session.delete(jawaban)
    db.session.commit()
    return jsonify({'message': 'Jawaban siswa deleted successfully'})

# Statistics routes
@app.route('/api/statistics/total-siswa', methods=['GET'])
def get_total_siswa():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.callproc('total_siswa')
    result = next(cursor.stored_results())
    total = result.fetchone()
    cursor.close()
    conn.close()
    return jsonify(total)

@app.route('/api/statistics/total-kelas', methods=['GET'])
def get_total_kelas():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.callproc('total_kelas')
    result = next(cursor.stored_results())
    total = result.fetchone()
    cursor.close()
    conn.close()
    return jsonify(total)

@app.route('/api/statistics/total-ujian', methods=['GET'])
def get_total_ujian():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.callproc('total_ujian')
    result = next(cursor.stored_results())
    total = result.fetchone()
    cursor.close()
    conn.close()
    return jsonify(total)

@app.route('/api/statistics/capaian', methods=['GET'])
def get_capaian():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.callproc('get_capaian')
    result = next(cursor.stored_results())
    capaian = result.fetchone()
    cursor.close()
    conn.close()
    # Ensure all values are integers (no decimals)
    if capaian:
        for k in capaian:
            if capaian[k] is not None and isinstance(capaian[k], float):
                capaian[k] = int(round(capaian[k]))
    return jsonify(capaian)

@app.route('/api/statistics/kelas/<int:kelas_id>', methods=['GET'])
def get_statistik_kelas(kelas_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.callproc('get_statistik_kelas', [kelas_id])
    result = next(cursor.stored_results())
    statistik = result.fetchone()
    cursor.close()
    conn.close()
    # Ensure all values are integers (no decimals)
    if statistik:
        for k in statistik:
            if statistik[k] is not None and isinstance(statistik[k], float):
                statistik[k] = int(round(statistik[k]))
    return jsonify(statistik)

@app.route('/api/statistics/class-statistics', methods=['GET'])
def get_class_statistics():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.callproc('Get_Class_Statistics')
    result = next(cursor.stored_results())
    statistics = result.fetchall()
    cursor.close()
    conn.close()
    # Ensure all values are integers (no decimals)
    for row in statistics:
        for k in row:
            if row[k] is not None and isinstance(row[k], float):
                row[k] = int(round(row[k]))
    return jsonify(statistics)

@app.route("/api/solve", methods=['POST'])
def solve():
    # Get the JSON data from the request
    data = request.get_json()

    # Extracting base64 image data from the request
    image_data = data.get("image", None)

    if not image_data:
        return jsonify({"error": "No valid image input found."}), 400

    try:
        # Decode the base64 image data
        img_data = image_data.split(",")[1]  # Remove 'data:image/png;base64,' part
        img_bytes = base64.b64decode(img_data)

        # Open image from bytes
        img = Image.open(BytesIO(img_bytes))
        text_input = pytesseract.image_to_string(img)  # OCR to extract text
        print("OCR Text:", text_input)

    except Exception as e:
        return jsonify({"error": f"Failed to process the image: {str(e)}"}), 500

    if not text_input.strip():
        return jsonify({"error": "No text extracted from the image."}), 400

    # cleaning text_input
    text_input = text_input.replace(" ", "")
    text_input = text_input.replace(".", "")
    text_input = text_input.replace(",", "")
    text_input = text_input.replace(":", "")
    text_input = text_input.replace(";", "")
    text_input = text_input.replace("!", "")
    text_input = text_input.replace("?", "")
    text_input = text_input.replace("\n", "")
    text_input = text_input.replace("\r", "")
    text_input = text_input.replace("\t", "")
    text_input = text_input.replace("\r\n", "")
    text_input = text_input.replace("\n\r", "")

    # Extract numbers and operator using regular expressions
    numbers = re.findall(r'\d+', text_input.split("=")[0])
    operator = ''.join([i for i in text_input.split("=")[0] if not i.isdigit()])
    result = text_input.split("=")[1]
    print("Numbers extracted:", numbers)
    print("Operator extracted:", operator)

    # operator to operator_label
    operator_mapping = {
        1: "+",
        2: "-",
        3: "x",
        4: "/",
    }

    operator_label_mapping = {
        "+": "Penjumlahan",
        "-": "Pengurangan",
        "x": "Perkalian",
        "/": "Pembagian",
    }
    operator_sign = operator
    operator_label = operator_label_mapping.get(operator, "Tidak diketahui")

    # Handle numbers for calculation
    numbers = [int(num) for num in numbers]
    try:
        jawaban = int(result)
    except Exception:
        jawaban = result

    # Construct response
    response = {
        "soal_cerita": text_input,
        "operator": operator_label,
        "angka_dalam_soal": ",".join(str(x) for x in numbers),
        "jawaban": str(jawaban) if not isinstance(jawaban, int) else jawaban
    }

    return jsonify(response)

@app.route("/api/extract_student_answer", methods=['POST'])
def extract_student_answer():
    # Get the JSON data from the request
    data = request.get_json()

    # Extracting base64 image data from the request
    image_data = data.get("image", None)

    if not image_data:
        return jsonify({"error": "No valid image input found."}), 400

    try:
        # Decode the base64 image data
        img_data = image_data.split(",")[1]  # Remove 'data:image/png;base64,' part
        img_bytes = base64.b64decode(img_data)

        # Open image from bytes
        img = Image.open(BytesIO(img_bytes))
        text_input = pytesseract.image_to_string(img)  # OCR to extract text
        print("OCR Text:", text_input)

    except Exception as e:
        return jsonify({"error": f"Failed to process the image: {str(e)}"}), 500

    if not text_input.strip():
        return jsonify({"error": "No text extracted from the image."}), 400

    # Extract numbers and operator using regular expressions
    numbers = re.findall(r'\d+', text_input)
    operator = ''.join([i for i in text_input if not i.isdigit()])
    print("Numbers extracted:", numbers)
    print("Operator extracted:", operator)
    
    # operator label
    operator_mapping = {
        1: "Penjumlahan",
        2: "Pengurangan",
        3: "Perkalian",
        4: "Pembagian",
        5: "Mix"
    }
    operator_label = operator_mapping.get(kelas, "Tidak diketahui")

    # Construct response
    response = {
        "soal_cerita": text_input,
        "operator": operator_label,
        "angka_dalam_soal": ",".join(str(x) for x in numbers),
        "jawaban": str(jawaban)
    }

    return jsonify(response)

@app.route("/api/compare_answer", methods=['POST'])
def compare_answer():
    data = request.get_json()
    ai_answer = data.get("ai_answer", None)
    student_answer = data.get("student_answer", None)

    if not ai_answer or not student_answer:
        return jsonify({"error": "Missing AI answer or student answer"}), 400

    try:
        # Use the internal comparison function for consistency
        result = compare_answers_internal(ai_answer, student_answer)
        print(f"compare_answer - result: {result}; ai_answer: {ai_answer}; student_answer: {student_answer}")
        
        # Format response to match original API format
        response = {
            "status": result["status"],
            "deskripsi_analisis": result["deskripsi_analisis"],
            "koreksi": " dan ".join(result["koreksi"]) if result["koreksi"] else "Tidak ada koreksi",
            "nilai": result["nilai"],
            "nilai_maksimal": result["nilai_maksimal"],
            "persentase": result["persentase"],
            "parameter_salah": result["parameter_salah"],
            "parameter_benar": result["parameter_benar"]
        }

        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "error": f"Error during comparison: {str(e)}",
            "status": "error",
            "deskripsi_analisis": "Terjadi kesalahan saat melakukan analisis perbandingan",
            "nilai": 0,
            "nilai_maksimal": 4,
            "persentase": 0,
            "parameter_salah": [],
            "parameter_benar": [],
            "koreksi": "Tidak dapat melakukan perbandingan"
        }), 500

@app.route("/api/solve_text", methods=['POST'])
def solve_text():
    # Get the JSON data from the request
    data = request.get_json()

    text_input = data.get("text_input", None)
    if not text_input:
        return jsonify({"error": "text_input is required"}), 400

    print(f"solve_text - input: {text_input}")

    # Simple algorithm for extracting math components
    result = extract_math_very_simple(text_input)
    
    # Check if we need Gemini analysis for complex/unknown operators
    needs_gemini_analysis = (
        result.get("operator") in ["Tidak diketahui", "Mix", "Campuran"] or
        result.get("operator", "").lower() in ["unknown", "mixed", "complex"]
    )
    
    if needs_gemini_analysis and PEDAGOGIC_ANALYSIS_AVAILABLE:
        print(f"solve_text - Using Gemini analysis for complex operator")
        try:
            gemini_result = analyze_math_problem_with_gemini(text_input)
            
            # If Gemini provides better analysis, replace existing data
            if gemini_result.get("status") == "success":
                gemini_analysis = gemini_result.get("analysis", {})
                
                # Replace the main fields with Gemini results
                result["operator"] = gemini_analysis.get("operator", result["operator"])
                result["angka_dalam_soal"] = gemini_analysis.get("angka_dalam_soal", result["angka_dalam_soal"])
                result["jawaban"] = gemini_analysis.get("jawaban", result["jawaban"])
                
                # Add simple flag to indicate Gemini was used
                result["enhanced_by_ai"] = True
                
                print(f"solve_text - Gemini analysis successful, data replaced")
                print(f"solve_text - Updated result: operator={result['operator']}, angka={result['angka_dalam_soal']}, jawaban={result['jawaban']}")
            else:
                print(f"solve_text - Gemini analysis failed: {gemini_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"solve_text - Gemini analysis exception: {str(e)}")
    
    print(f"solve_text - final result: {result}")
    return jsonify(result)

@app.route("/api/solve_text_simple", methods=['POST'])
def solve_text_simple():
    # Get the JSON data from the request
    data = request.get_json()

    text_input = data.get("text_input", None)
    if not text_input:
        return jsonify({"error": "text_input is required"}), 400

    # print(f"solve_text - input: {text_input}")

    # Simple algorithm for extracting math components
    result = extract_math_very_simple(text_input)

    print(f"solve_text_simple - result: {result}")
    
    return jsonify(result)


def extract_math_very_simple(text_input):
    """
    Ekstraksi sangat sederhana untuk format seperti 1+2=3, 15-7=8, 6x4=24, 48:6=8
    - Ambil dua angka pertama sebagai angka_dalam_soal
    - Angka ketiga (jika ada) sebagai jawaban
    - Operator di antara dua angka pertama
    """
    try:
        text = text_input.replace(' ', '')
        # Ekstrak angka
        numbers = re.findall(r'\d+', text)
        # Ekstrak operator (karakter non-digit di antara angka)
        operator = None
        operator_label = 'Tidak diketahui'
        if len(numbers) >= 2:
            # Cari operator di antara dua angka pertama
            idx1 = text.find(numbers[0]) + len(numbers[0])
            idx2 = text.find(numbers[1], idx1)
            operator_raw = text[idx1:idx2]
            operator_mapping = {
                '+': 'Penjumlahan',
                '-': 'Pengurangan',
                '*': 'Perkalian',
                'x': 'Perkalian',
                '×': 'Perkalian',
                '/': 'Pembagian',
                ':': 'Pembagian',
                '÷': 'Pembagian',
            }
            operator = operator_raw
            operator_label = operator_mapping.get(operator, operator)
            angka_dalam_soal = f"{numbers[0]},{numbers[1]}"
            jawaban = numbers[2] if len(numbers) >= 3 else ''
        elif len(numbers) == 1:
            angka_dalam_soal = f"{numbers[0]},0"
            jawaban = numbers[0]
        else:
            angka_dalam_soal = "0,0"
            jawaban = "0"
        return {
            'soal_cerita': text_input,
            'operator': operator_label,
            'angka_dalam_soal': angka_dalam_soal,
            'jawaban': jawaban
        }
    except Exception:
        return {
            'soal_cerita': text_input,
            'operator': 'Tidak diketahui',
            'angka_dalam_soal': '0,0',
            'jawaban': '0'
        }

def extract_math_simple(text_input):
    """
    Enhanced algorithm to extract math components from text
    Handles both explicit equations and story problems
    Now includes detection for mixed/complex operations
    """
    try:
        # Clean the input text
        text_clean = text_input.strip()
        
        # Extract all numbers using regex
        numbers = re.findall(r'\d+', text_clean)
        
        print(f"extract_math_simple - input: {text_input[:100]}...")
        print(f"extract_math_simple - numbers found: {numbers}")
        
        # Detect operation type from story context using keywords
        operator_keywords = {
            'Penjumlahan': [
                'tambah', 'ditambah', 'plus', 'jumlah', 'total', 'keseluruhan',
                'bersama', 'bertambah', 'menambah', 'gabungan', 'semua'
            ],
            'Pengurangan': [
                'kurang', 'dikurangi', 'minus', 'sisa', 'tersisa', 'memberikan',
                'memberi', 'mengurangi', 'berkurang', 'hilang', 'diambil',
                'dipinjam', 'dipakai', 'digunakan', 'keluar'
            ],
            'Perkalian': [
                'kali', 'dikali', 'dikalikan', 'x', '×', '*', 'setiap', 'per',
                'masing-masing', 'tiap', 'baris', 'kolom', 'grup', 'kelompok',
                'pak', 'kotak', 'menghasilkan', 'produksi', 'berisi'
            ],
            'Pembagian': [
                'bagi', 'dibagi', 'dibagikan', '÷', '/', ':', 'rata', 'merata',
                'sama banyak', 'sama rata', 'per kelompok', 'setiap kelompok',
                'masing-masing kelompok', 'ke dalam', 'dimasukkan'
            ]
        }
        
        # Check for explicit mathematical notation first
        explicit_operators = ['+', '-', '*', 'x', '×', '/', ':', '÷', '=']
        has_explicit_math = any(op in text_clean for op in explicit_operators)
        
        # Count different types of operations in the text
        text_lower = text_clean.lower()
        operation_scores = {}
        for operation, keywords in operator_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                operation_scores[operation] = score
        
        # Check for multiple operations (mixed/complex problems)
        multiple_operations = len(operation_scores) > 1 or len(numbers) > 2
        
        # Additional indicators for complex problems
        complex_indicators = [
            'kemudian', 'lalu', 'setelah itu', 'selanjutnya', 'dan', 'juga',
            'namun', 'tetapi', 'akan tetapi', 'sementara', 'sambil'
        ]
        has_complex_indicators = any(indicator in text_lower for indicator in complex_indicators)
        
        # Multiple explicit operators
        operator_count = sum(1 for op in explicit_operators[:-1] if op in text_clean)  # exclude '='
        has_multiple_explicit_ops = operator_count > 1
        
        operator_label = "Tidak diketahui"
        operator_sign = ""
        
        # Determine if this is a mixed/complex problem
        if (multiple_operations and has_complex_indicators) or has_multiple_explicit_ops or len(numbers) > 2:
            operator_label = "Mix"
            operator_sign = "mixed"
            print(f"extract_math_simple - detected complex/mixed operation")
            print(f"extract_math_simple - operation_scores: {operation_scores}")
            print(f"extract_math_simple - complex_indicators: {has_complex_indicators}")
            print(f"extract_math_simple - multiple_explicit_ops: {has_multiple_explicit_ops}")
        elif has_explicit_math:
            # Handle explicit mathematical notation
            text_no_spaces = text_clean.replace(" ", "")
            
            # Extract operator by removing numbers and equals sign
            temp_text = text_no_spaces
            for num in numbers:
                temp_text = temp_text.replace(num, '', 1)
            temp_text = temp_text.replace('=', '')
            operator_sign = temp_text.strip()
            
            # Map operator to label
            operator_mapping = {
                '+': "Penjumlahan",
                '-': "Pengurangan", 
                '*': "Perkalian",
                'x': "Perkalian",
                '×': "Perkalian",
                '/': "Pembagian",
                ':': "Pembagian",
                '÷': "Pembagian"
            }
            
            operator_label = operator_mapping.get(operator_sign, "Tidak diketahui")
        else:
            # Handle story problems by analyzing keywords
            
            # Choose operation with highest score
            if operation_scores:
                operator_label = max(operation_scores, key=operation_scores.get)
                print(f"extract_math_simple - detected operation: {operator_label} (scores: {operation_scores})")
            
            # Set operator sign based on detected operation
            operation_to_sign = {
                'Penjumlahan': '+',
                'Pengurangan': '-',
                'Perkalian': 'x',
                'Pembagian': '/'
            }
            operator_sign = operation_to_sign.get(operator_label, '')
        
        print(f"extract_math_simple - operator: {operator_label} ({operator_sign})")
        
        # Process numbers and calculate result
        if len(numbers) >= 2:
            if operator_label == "Mix":
                # For mixed operations, use all numbers
                angka_dalam_soal = ",".join(numbers)
                jawaban = "Perlu analisis lanjutan"
            else:
                angka1 = int(numbers[0])
                angka2 = int(numbers[1])
                angka_dalam_soal = f"{angka1},{angka2}"
                
                # Calculate the result based on operation
                jawaban = "Tidak bisa dihitung"
                
                if operator_label == "Penjumlahan":
                    jawaban = angka1 + angka2
                elif operator_label == "Pengurangan":
                    jawaban = angka1 - angka2
                elif operator_label == "Perkalian":
                    jawaban = angka1 * angka2
                elif operator_label == "Pembagian":
                    jawaban = int(round(angka1 / angka2)) if angka2 != 0 else "Tak terdefinisi"
                
                # If there's a third number and explicit equation, use it as provided answer
                if len(numbers) >= 3 and has_explicit_math and '=' in text_clean:
                    jawaban = int(numbers[2])
                
        elif len(numbers) == 1:
            # Single number case
            angka_dalam_soal = f"{numbers[0]},0"
            jawaban = numbers[0]
        else:
            # No numbers found
            angka_dalam_soal = "0,0"
            jawaban = "0"
        
        # Construct response
        response = {
            "soal_cerita": text_input,
            "operator": operator_label,
            "angka_dalam_soal": angka_dalam_soal,
            "jawaban": str(jawaban) if isinstance(jawaban, int) else jawaban
        }
        
        print(f"extract_math_simple - result: {response}")
        return response
        
    except Exception as e:
        print(f"extract_math_simple - error: {str(e)}")
        return {
            "soal_cerita": text_input,
            "operator": "Tidak diketahui", 
            "angka_dalam_soal": "0,0",
            "jawaban": "0"
        }

# Student exam routes
@app.route('/api/student/exams', methods=['GET'])
@student_required
def get_student_exams():
    user_id = session['user_id']
    kelas_id = session['kelas_id']  # Use kelas_id from session
    
    # Get siswa data
    siswa = Siswa.query.filter_by(user_id=user_id).first()
    if not siswa:
        return jsonify({'error': 'Student data not found'}), 404
    
    # Get exams for student's class
    ujian_list = Ujian.query.filter_by(kelas=kelas_id).all()
    exams = []
    
    for ujian in ujian_list:
        # Check if student has already taken this exam
        ujian_siswa = UjianSiswa.query.filter_by(
            ujian=ujian.id, 
            siswa=siswa.no  # Use siswa.no instead of user_id
        ).first()
        
        exam_data = {
            'id': ujian.id,
            'nama_ujian': ujian.nama_ujian,
            'pelaksanaan': ujian.pelaksanaan.strftime('%Y-%m-%d'),
            'status': ujian.status,
            'is_taken': ujian_siswa is not None,
            'nilai': ujian_siswa.nilai if ujian_siswa else None,
            'label_nilai': ujian_siswa.label_nilai if ujian_siswa else None
        }
        exams.append(exam_data)
    
    return jsonify(exams)

@app.route('/api/student/exam/<int:exam_id>/questions', methods=['GET'])
@student_required
def get_exam_questions(exam_id):
    user_id = session['user_id']
    
    # Get siswa data
    siswa = Siswa.query.filter_by(user_id=user_id).first()
    if not siswa:
        return jsonify({'error': 'Student data not found'}), 404
    
    # Check if student has already taken this exam
    ujian_siswa = UjianSiswa.query.filter_by(
        ujian=exam_id, 
        siswa=siswa.no  # Use siswa.no instead of user_id
    ).first()
    
    if ujian_siswa:
        return jsonify({'error': 'You have already taken this exam'}), 400
    
    # Get exam questions
    soal_list = Soal.query.filter_by(ujian=exam_id).all()
    questions = []
    
    for soal in soal_list:
        question_data = {
            'id': soal.id,
            'soal': soal.soal,
            'json_result': soal.json_result
        }
        questions.append(question_data)
    
    return jsonify(questions)

@app.route('/api/student/exam/<int:exam_id>/submit', methods=['POST'])
@student_required
def submit_exam(exam_id):
    user_id = session['user_id']
    data = request.get_json()
    answers = data.get('answers', [])  # List of {soal_id, jawaban_text}
    
    # Get siswa data
    siswa = Siswa.query.filter_by(user_id=user_id).first()
    if not siswa:
        return jsonify({'error': 'Student data not found'}), 404
    
    # Check if student has already taken this exam
    ujian_siswa = UjianSiswa.query.filter_by(
        ujian=exam_id, 
        siswa=siswa.no  # Use siswa.no instead of user_id
    ).first()
    
    if ujian_siswa:
        return jsonify({'error': 'You have already taken this exam'}), 400
    
    try:
        # Process each answer
        correct_count = 0
        total_questions = len(answers)
        
        for answer_data in answers:
            soal_id = answer_data['soal_id']
            jawaban_text = answer_data['jawaban_text']
            
            # Get the soal
            soal = Soal.query.get(soal_id)
            if not soal:
                continue
            
            # Compare with correct answer
            correct_answer = soal.json_result.get('jawaban', '')
            is_correct = str(jawaban_text).strip() == str(correct_answer).strip()
            
            # Save student answer
            jawaban_siswa = JawabanSiswa(
                nisn=siswa.NISN,  # Use NISN instead of siswa_id
                soal=soal_id,
                status='correct' if is_correct else 'incorrect',
                json_result={
                    'jawaban_siswa': jawaban_text,
                    'jawaban_benar': correct_answer,
                    'is_correct': is_correct
                }
            )
            db.session.add(jawaban_siswa)
            
            if is_correct:
                correct_count += 1
        
        # Calculate score (integer)
        score = int(round((correct_count / total_questions) * 100)) if total_questions > 0 else 0
        
        # Determine label
        if score >= 80:
            label = 'Baik'
        elif score >= 60:
            label = 'Cukup'
        else:
            label = 'Kurang'
        
        # Create exam result
        ujian_siswa = UjianSiswa(
            ujian=exam_id,
            siswa=siswa.no,  # Use siswa.no instead of siswa_id
            nilai=score,
            label_nilai=label,
            deskripsi_analisis=f"Siswa menjawab {correct_count} dari {total_questions} soal dengan benar"
        )
        db.session.add(ujian_siswa)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Exam submitted successfully',
            'score': score,
            'label': label,
            'correct_answers': correct_count,
            'total_questions': total_questions
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error submitting exam: {str(e)}'}), 500

@app.route('/api/student/exam/<int:exam_id>/result', methods=['GET'])
@student_required
def get_exam_result(exam_id):
    user_id = session['user_id']
    siswa = Siswa.query.filter_by(user_id=user_id).first()
    if not siswa:
        return jsonify({'error': 'Student data not found'}), 404
    ujian_siswa = UjianSiswa.query.filter_by(
        ujian=exam_id, 
        siswa=siswa.no
    ).first()
    if not ujian_siswa:
        return jsonify({'error': 'Exam result not found'}), 404
    jawaban_list = JawabanSiswa.query.filter_by(nisn=siswa.NISN).join(Soal).filter(Soal.ujian == exam_id).all()
    nilai_jawaban = sum([j.nilai or 0 for j in jawaban_list])
    max_points = len(jawaban_list) * 4
    answers_detail = []
    for jawaban in jawaban_list:
        soal = jawaban.soal_ref
        answer_detail = {
            'soal': soal.soal,
            'jawaban_siswa': jawaban.json_result.get('jawaban_siswa', ''),
            'jawaban_benar': jawaban.json_result.get('jawaban_benar', ''),
            'is_correct': jawaban.json_result.get('is_correct', False),
            'status': jawaban.status,
            'nilai': jawaban.nilai
        }
        answers_detail.append(answer_detail)
    return jsonify({
        'exam_result': {
            'nilai': ujian_siswa.nilai,
            'label_nilai': ujian_siswa.label_nilai,
            'deskripsi_analisis': ujian_siswa.deskripsi_analisis,
            'total_points': nilai_jawaban,
            'max_points': max_points
        },
        'answers_detail': answers_detail
    })

def extract_math_manual(text_input):
    """
    Ekstraksi manual operator, angka, dan jawaban dari string matematika sederhana.
    Contoh: '1+2=3' -> operator: '+', angka: '1,2', jawaban: '3'
    Jika ada lebih dari 2 angka, ambil 2 angka pertama sebagai angka_dalam_soal, angka ketiga sebagai jawaban.
    """
    try:
        text = text_input.replace(' ', '')
        # Ekstrak sebelum dan sesudah '='
        if '=' in text:
            left, right = text.split('=', 1)
        else:
            left, right = text, ''
        # Ekstrak angka
        numbers = re.findall(r'\d+', left)
        # Ekstrak operator (karakter non-digit di antara angka)
        operator = ''.join([c for c in left if not c.isdigit()])
        # Map operator ke label
        operator_mapping = {
            '+': 'Penjumlahan',
            '-': 'Pengurangan',
            '*': 'Perkalian',
            'x': 'Perkalian',
            '×': 'Perkalian',
            '/': 'Pembagian',
            ':': 'Pembagian',
            '÷': 'Pembagian',
        }
        operator_label = operator_mapping.get(operator, operator)
        # Penentuan angka dan jawaban
        if len(numbers) >= 3:
            angka_dalam_soal = ','.join(numbers[:2])
            jawaban = numbers[2]
        elif len(numbers) == 2:
            angka_dalam_soal = ','.join(numbers)
            jawaban = right.strip() if right.strip() else numbers[1]
        elif len(numbers) == 1:
            angka_dalam_soal = numbers[0]
            jawaban = right.strip() if right.strip() else numbers[0]
        else:
            angka_dalam_soal = '0,0'
            jawaban = '0'
        return {
            'soal_cerita': text_input,
            'operator': operator_label,
            'angka_dalam_soal': angka_dalam_soal,
            'jawaban': jawaban
        }
    except Exception:
        return {
            'soal_cerita': text_input,
            'operator': 'Tidak diketahui',
            'angka_dalam_soal': '0,0',
            'jawaban': '0'
        }

def solve_text_internal(text_input):
    """Internal function to solve text problems (without HTTP request)"""
    # Simple algorithm for extracting math components
    result = extract_math_simple(text_input)
    
    # Check if we need Gemini analysis for complex/unknown operators
    needs_gemini_analysis = (
        result.get("operator") in ["Tidak diketahui", "Mix", "Campuran"] or
        result.get("operator", "").lower() in ["unknown", "mixed", "complex"]
    )
    
    if needs_gemini_analysis and PEDAGOGIC_ANALYSIS_AVAILABLE:
        try:
            gemini_result = analyze_math_problem_with_gemini(text_input)
            
            # If Gemini provides better analysis, replace existing data
            if gemini_result.get("status") == "success":
                gemini_analysis = gemini_result.get("analysis", {})
                
                # Replace the main fields with Gemini results
                result["operator"] = gemini_analysis.get("operator", result["operator"])
                result["angka_dalam_soal"] = gemini_analysis.get("angka_dalam_soal", result["angka_dalam_soal"])
                result["jawaban"] = gemini_analysis.get("jawaban", result["jawaban"])
                
                # Add simple flag to indicate Gemini was used
                result["enhanced_by_ai"] = True
                
        except Exception as e:
            pass  # Fallback to simple analysis
    
    return result

def get_difficulty_level(operation, numbers):
    """
    Menentukan tingkat kesulitan berdasarkan operasi dan range bilangan cacah
    
    Args:
        operation (str): Jenis operasi (Penjumlahan, Pengurangan, Perkalian, Pembagian)
        numbers (list): List angka yang digunakan dalam soal
    
    Returns:
        dict: Informasi tingkat kesulitan
    """
    try:
        # Convert numbers to integers
        num_list = []
        for num_str in numbers:
            try:
                num_list.append(int(num_str.strip()))
            except (ValueError, AttributeError):
                continue
        
        if not num_list:
            return {
                "level": "unknown",
                "description": "Tidak dapat menentukan tingkat kesulitan",
                "max_number": 0,
                "category": "invalid"
            }
        
        max_number = max(num_list)
        
        # Klasifikasi berdasarkan operasi dan range angka
        if operation in ["Penjumlahan", "Pengurangan"]:
            if max_number <= 20:
                return {
                    "level": "dasar",
                    "description": f"{operation} bilangan cacah hingga 20",
                    "max_number": max_number,
                    "category": "elementary",
                    "complexity_score": 1
                }
            elif max_number <= 100:
                return {
                    "level": "menengah",
                    "description": f"{operation} bilangan cacah hingga 100",
                    "max_number": max_number,
                    "category": "intermediate",
                    "complexity_score": 2
                }
            elif max_number <= 1000:
                return {
                    "level": "lanjut",
                    "description": f"{operation} bilangan cacah hingga 1000",
                    "max_number": max_number,
                    "category": "advanced",
                    "complexity_score": 3
                }
            else:
                return {
                    "level": "sangat_lanjut",
                    "description": f"{operation} bilangan cacah di atas 1000",
                    "max_number": max_number,
                    "category": "expert",
                    "complexity_score": 4
                }
        
        elif operation in ["Perkalian", "Pembagian"]:
            if max_number <= 100:
                return {
                    "level": "dasar",
                    "description": f"{operation} bilangan cacah hingga 100",
                    "max_number": max_number,
                    "category": "elementary",
                    "complexity_score": 2
                }
            else:
                return {
                    "level": "lanjut",
                    "description": f"{operation} bilangan cacah di atas 100",
                    "max_number": max_number,
                    "category": "advanced", 
                    "complexity_score": 3
                }
        
        else:
            return {
                "level": "unknown",
                "description": "Operasi tidak dikenali",
                "max_number": max_number,
                "category": "invalid",
                "complexity_score": 0
            }
            
    except Exception as e:
        return {
            "level": "error",
            "description": f"Error menentukan tingkat kesulitan: {str(e)}",
            "max_number": 0,
            "category": "invalid",
            "complexity_score": 0
        }

def standardize_operator(op):
    op = str(op).strip().lower()
    mapping = {
        '+': 'Penjumlahan',
        'penjumlahan': 'Penjumlahan',
        'Penjumlahan': 'Penjumlahan',
        '-': 'Pengurangan',
        'pengurangan': 'Pengurangan',
        'Pengurangan': 'Pengurangan',
        '*': 'Perkalian',
        'x': 'Perkalian',
        'perkalian': 'Perkalian',
        'Perkalian': 'Perkalian',
        '/': 'Pembagian',
        ':': 'Pembagian',
        '÷': 'Pembagian',
        'pembagian': 'Pembagian',
        'Pembagian': 'Pembagian',
    }
    return mapping.get(op, op.capitalize())

def standardize_angka_dalam_soal(angka):
    if isinstance(angka, list):
        angka_list = [str(a).strip() for a in angka]
    else:
        angka_list = [s.strip() for s in str(angka).split(',')]
    return ','.join(angka_list)

def standardize_jawaban(jwb):
    try:
        return str(int(float(jwb)))
    except Exception:
        return str(jwb).strip()

def compare_answers_internal(ai_answer, student_answer):
    correct_parameters = []
    wrong_parameters = []
    nilai = 0
    koreksi = []
    global GEMINI_SLEEP_SECONDS
    
    # Validate input data - ensure all required keys exist
    required_keys = ["operator", "angka_dalam_soal", "jawaban"]

    print(f"ai_answer: {ai_answer}")
    print(f"student_answer: {student_answer}")

    student_answer_json_result = student_answer.get("ai_analysis", {})
    
    # Normalize data - provide defaults for missing keys
    ai_normalized = {
        "operator": ai_answer.get("operator", "Tidak diketahui"),
        "angka_dalam_soal": ai_answer.get("angka_dalam_soal", "0,0"),
        "jawaban": str(ai_answer.get("jawaban", "")).strip()
    }
    
    student_normalized = {
        "operator": student_answer_json_result.get("operator", "Tidak diketahui"),
        "angka_dalam_soal": student_answer_json_result.get("angka_dalam_soal", "0,0"),
        "jawaban": str(student_answer_json_result.get("jawaban", "")).strip()
    }

    # check if student_answer_json_result is not empty
    if not student_answer_json_result:
        student_normalized = {
        "operator": student_answer.get("operator", "Tidak diketahui"),
        "angka_dalam_soal": student_answer.get("angka_dalam_soal", "0,0"),
        "jawaban": str(student_answer.get("jawaban", "")).strip()
    }

    # print("AI Answer:", ai_answer)
    print("Student Answer:", student_answer)

    # Standarisasi sebelum dibandingkan
    ai_normalized["operator"] = standardize_operator(ai_normalized["operator"])
    student_normalized["operator"] = standardize_operator(student_normalized["operator"])
    ai_normalized["angka_dalam_soal"] = standardize_angka_dalam_soal(ai_normalized["angka_dalam_soal"])
    student_normalized["angka_dalam_soal"] = standardize_angka_dalam_soal(student_normalized["angka_dalam_soal"])
    ai_normalized["jawaban"] = standardize_jawaban(ai_normalized["jawaban"])
    student_normalized["jawaban"] = standardize_jawaban(student_normalized["jawaban"])

    print("ai_normalized:", ai_normalized)
    print("student_normalized:", student_normalized)

    # Compare operator (1 point)
    if ai_normalized["operator"] == student_normalized["operator"]:
        correct_parameters.append("operator")
        nilai += 1
    else:
        wrong_parameters.append("operator")
        koreksi.append(f"Operator yang benar adalah {ai_normalized['operator']}")

    # Compare operands separately (1 point each for operand 1 and operand 2)
    try:
        ai_numbers = ai_normalized["angka_dalam_soal"].split(",")
        student_numbers = student_normalized["angka_dalam_soal"].split(",")
        
        # Check operand 1 (1 point)
        if len(ai_numbers) > 0 and len(student_numbers) > 0:
            if int(ai_numbers[0].strip()) == int(student_numbers[0].strip()):
                correct_parameters.append("operan_1")
                nilai += 1
            else:
                wrong_parameters.append("operan_1")
                koreksi.append(f"Operan 1 yang benar adalah {ai_numbers[0].strip()}")
        
        # Check operand 2 (1 point)
        if len(ai_numbers) > 1 and len(student_numbers) > 1:
            if ai_numbers[1].strip() == student_numbers[1].strip():
                correct_parameters.append("operan_2")
                nilai += 1
            else:
                wrong_parameters.append("operan_2")
                koreksi.append(f"Operan 2 yang benar adalah {ai_numbers[1].strip()}")
        elif len(ai_numbers) > 1:
            # Student didn't provide second operand
            wrong_parameters.append("operan_2")
            koreksi.append(f"Operan 2 yang benar adalah {ai_numbers[1].strip()}")
            
    except Exception as e:
        wrong_parameters.extend(["operan_1", "operan_2"])
        koreksi.append("Format angka dalam soal tidak valid")

    # Compare jawaban (1 point)
    if ai_normalized["jawaban"] == student_normalized["jawaban"]:
        correct_parameters.append("jawaban")
        nilai += 1
    else:
        wrong_parameters.append("jawaban")
        koreksi.append(f"Jawaban yang benar adalah {ai_normalized['jawaban']}")

    # Analyze difficulty level based on correct answer (AI answer)
    ai_numbers = ai_normalized["angka_dalam_soal"].split(",")
    difficulty_analysis = get_difficulty_level(ai_normalized["operator"], ai_numbers)
    
    # Generate deskripsi_analisis based on 4-point system with difficulty context
    difficulty_context = f" pada {difficulty_analysis['description']}"
    
    if nilai == 4:
        deskripsi_analisis = f"Siswa telah menjawab dengan benar semua aspek soal (4/4 poin){difficulty_context}"
    elif nilai == 3:
        aspek_benar = []
        if "operator" in correct_parameters:
            aspek_benar.append("operator")
        if "operan_1" in correct_parameters:
            aspek_benar.append("operan 1")
        if "operan_2" in correct_parameters:
            aspek_benar.append("operan 2")
        if "jawaban" in correct_parameters:
            aspek_benar.append("jawaban")
        deskripsi_analisis = f"Siswa menjawab benar 3 dari 4 aspek: {', '.join(aspek_benar)} (3/4 poin){difficulty_context}"
    elif nilai == 2:
        aspek_benar = []
        if "operator" in correct_parameters:
            aspek_benar.append("operator")
        if "operan_1" in correct_parameters:
            aspek_benar.append("operan 1")
        if "operan_2" in correct_parameters:
            aspek_benar.append("operan 2")
        if "jawaban" in correct_parameters:
            aspek_benar.append("jawaban")
        deskripsi_analisis = f"Siswa menjawab benar 2 dari 4 aspek: {', '.join(aspek_benar)} (2/4 poin){difficulty_context}"
    elif nilai == 1:
        aspek_benar = []
        if "operator" in correct_parameters:
            aspek_benar.append("operator")
        if "operan_1" in correct_parameters:
            aspek_benar.append("operan 1")
        if "operan_2" in correct_parameters:
            aspek_benar.append("operan 2")
        if "jawaban" in correct_parameters:
            aspek_benar.append("jawaban")
        deskripsi_analisis = f"Siswa hanya menjawab benar 1 dari 4 aspek: {', '.join(aspek_benar)} (1/4 poin){difficulty_context}"
    else:
        detail = []
        if "operan_1" in wrong_parameters:
            detail.append("operan 1 salah")
        if "operan_2" in wrong_parameters:
            detail.append("operan 2 salah")
        if "operator" in wrong_parameters:
            detail.append("operator salah")
        if "jawaban" in wrong_parameters:
            detail.append("jawaban salah")
        deskripsi_analisis = f"Siswa belum menjawab dengan benar semua aspek soal (0/4 poin){difficulty_context}. {', '.join(detail) if detail else ''}"

    # --- Tambahan: Selalu lampirkan hasil Gemini sebagai analisis tambahan ---
    # gemini_used = False
    # gemini_penjelasan = None
    # from flask import current_app
    # soal_text = ai_normalized.get("soal_cerita") or student_normalized.get("soal_cerita")
    # if not soal_text:
    #     soal_text = f"Operator: {ai_normalized['operator']}, Angka: {ai_normalized['angka_dalam_soal']}, Jawaban: {ai_normalized['jawaban']}"
    # gemini_result = analyze_math_problem_with_gemini(soal_text)
    # gemini_used = True
    # if gemini_result.get("status") == "success":
    #     analysis = gemini_result.get("analysis", {})
    #     penjelasan = gemini_result.get("penjelasan", "")
    #     gemini_deskripsi_analisis = f"\n[Gemini] Operator: {analysis.get('operator', '')}, Angka: {analysis.get('angka_dalam_soal', '')}, Jawaban: {analysis.get('jawaban', '')}. Penjelasan: {penjelasan}"
    #     deskripsi_analisis += gemini_deskripsi_analisis
    #     gemini_penjelasan = penjelasan
    # else:
    #     deskripsi_analisis += f" [Gemini error: {gemini_result.get('error', 'unknown')}]"
    # # Sleep setelah Gemini
    # time.sleep(GEMINI_SLEEP_SECONDS)

    print(deskripsi_analisis)
    
    

    return {
        "status": "excellent" if nilai == 4 else "good" if nilai == 3 else "fair" if nilai == 2 else "poor" if nilai == 1 else "incorrect",
        "deskripsi_analisis": deskripsi_analisis,
        "nilai": nilai,
        "nilai_maksimal": 4,
        "persentase": round((nilai / 4) * 100, 2),
        "parameter_salah": wrong_parameters,
        "parameter_benar": correct_parameters,
        "koreksi": koreksi,
        "difficulty_analysis": difficulty_analysis,
        "gemini_used": "false",
        "gemini_penjelasan": ""
    }

def analyze_math_problem_with_gemini(soal_text):
    """
    Menggunakan Gemini AI untuk menganalisis soal matematika yang kompleks
    ketika operator campuran atau tidak diketahui
    """
    try:
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return {
                "status": "error",
                "error": "GEMINI_API_KEY not found in environment variables",
                "confidence": "low"
            }
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        time.sleep(GEMINI_SLEEP_SECONDS)
        
        # Prompt untuk analisis soal matematika
        prompt = f"""
Analisis soal matematika berikut ini dengan teliti dan berikan hasilnya dalam format JSON yang tepat.

Soal: "{soal_text}"

Tugas Anda:
1. Identifikasi operator matematika yang digunakan (Penjumlahan, Pengurangan, Perkalian, Pembagian, atau Mix jika lebih dari satu)
2. Ekstrak semua angka yang relevan dalam soal
3. Hitung jawaban yang benar
4. Berikan tingkat kepercayaan analisis (high, medium, low)

Format respons JSON yang diinginkan:
{{
    "operator": "Penjumlahan|Pengurangan|Perkalian|Pembagian|Mix",
    "angka_dalam_soal": "angka1,angka2",
    "jawaban": "hasil_perhitungan",
    "penjelasan": "penjelasan_singkat_proses_analisis",
    "confidence": "high|medium|low",
    "operasi_detail": "step by step calculation if Mix"
}}

Contoh untuk soal sederhana:
- "Ana mempunyai 5 apel, kemudian diberi 3 apel lagi" → operator: "Penjumlahan", angka_dalam_soal: "5,3", jawaban: "8"
- "Budi membeli 4 buku seharga 2000 rupiah per buku" → operator: "Perkalian", angka_dalam_soal: "4,2000", jawaban: "8000"

Untuk soal dengan operator campuran:
- "Ana membeli 3 kotak permen, setiap kotak berisi 5 permen, kemudian membagikan 10 permen" → operator: "Mix", angka_dalam_soal: "3,5,10", jawaban: "5", operasi_detail: "3×5=15, 15-10=5"

Berikan analisis untuk soal yang diberikan:
"""

        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Parse JSON response
        import json
        import re
        
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            try:
                analysis = json.loads(json_str)
                
                # Validate required fields
                required_fields = ["operator", "angka_dalam_soal", "jawaban"]
                if all(field in analysis for field in required_fields):
                    # Ensure consistent format
                    if "," not in str(analysis["angka_dalam_soal"]) and "Mix" not in analysis["operator"]:
                        # Single number case, add placeholder
                        analysis["angka_dalam_soal"] = f"{analysis['angka_dalam_soal']},0"
                    
                    return {
                        "status": "success",
                        "analysis": {
                            "operator": analysis["operator"],
                            "angka_dalam_soal": str(analysis["angka_dalam_soal"]),
                            "jawaban": str(analysis["jawaban"]),
                            "soal_cerita": soal_text
                        },
                        "confidence": analysis.get("confidence", "medium"),
                        "penjelasan": analysis.get("penjelasan", ""),
                        "operasi_detail": analysis.get("operasi_detail", ""),
                        "raw_response": response_text
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"Missing required fields in Gemini response: {required_fields}",
                        "raw_response": response_text,
                        "confidence": "low"
                    }
                    
            except json.JSONDecodeError as e:
                return {
                    "status": "error",
                    "error": f"Failed to parse Gemini JSON response: {str(e)}",
                    "raw_response": response_text,
                    "confidence": "low"
                }
        else:
            return {
                "status": "error", 
                "error": "No JSON found in Gemini response",
                "raw_response": response_text,
                "confidence": "low"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": f"Gemini API error: {str(e)}",
            "confidence": "low"
        }

# ============================================================================
# PEDAGOGIC ANALYSIS ENDPOINTS
# ============================================================================

@app.route('/api/pedagogic/analyze-answer', methods=['POST'])
@teacher_required
def analyze_student_answer_pedagogic():
    """
    Analisis pedagogik untuk jawaban siswa individual
    """
    if not PEDAGOGIC_ANALYSIS_AVAILABLE:
        return jsonify({
            'error': 'Pedagogic analysis not available. Please install google-generativeai package.'
        }), 503
    
    try:
        data = request.get_json()
        soal_id = data.get('soal_id')
        jawaban_siswa_id = data.get('jawaban_siswa_id')
        
        if not soal_id or not jawaban_siswa_id:
            return jsonify({'error': 'soal_id and jawaban_siswa_id are required'}), 400
        
        # Get soal data
        soal = Soal.query.get(soal_id)
        if not soal:
            return jsonify({'error': 'Soal not found'}), 404
        
        # Get jawaban siswa data
        jawaban_siswa = JawabanSiswa.query.get(jawaban_siswa_id)
        if not jawaban_siswa:
            return jsonify({'error': 'Jawaban siswa not found'}), 404
        
        # Get student data using NISN
        siswa = Siswa.query.filter_by(NISN=jawaban_siswa.nisn).first()
        if not siswa:
            return jsonify({'error': 'Siswa not found'}), 404
        
        # Prepare data for analysis
        soal_data = {
            'soal': soal.soal,
            'json_result': soal.json_result or {}
        }
        
        jawaban_data = {
            'operator': jawaban_siswa.json_result.get('operator', 'Tidak diketahui'),
            'angka_dalam_soal': jawaban_siswa.json_result.get('angka_dalam_soal', 'Tidak diketahui'),
            'jawaban': jawaban_siswa.json_result.get('jawaban', 'Tidak diketahui')
        }
        
        # Map status to nilai (4-point system)
        status_to_nilai = {
            'excellent': 4, 'good': 3, 'fair': 2, 'poor': 1, 'incorrect': 0
        }
        nilai_from_status = status_to_nilai.get(jawaban_siswa.status, 0)
        
        hasil_analisis = {
            'operator': soal.json_result.get('operator', 'Tidak diketahui') if soal.json_result else 'Tidak diketahui',
            'angka_dalam_soal': soal.json_result.get('angka_dalam_soal', 'Tidak diketahui') if soal.json_result else 'Tidak diketahui',
            'jawaban': soal.json_result.get('jawaban', 'Tidak diketahui'),
            'status': jawaban_siswa.status,
            'nilai': nilai_from_status,
            'nilai_maksimal': 4,
            'correct_parameters': ['operator', 'operan_1', 'operan_2', 'jawaban'] if jawaban_siswa.status == 'excellent' else [],
            'wrong_parameters': ['operator', 'operan_1', 'operan_2', 'jawaban'] if jawaban_siswa.status == 'incorrect' else []
        }
        
        # Perform pedagogic analysis
        analyzer = get_pedagogic_analyzer()
        analysis_result = analyzer.analyze_student_answer(soal_data, jawaban_data, hasil_analisis)
        
        # Save analysis result to database
        if analysis_result['status'] == 'success':
            jawaban_siswa.json_result = {
                **jawaban_siswa.json_result,
                'pedagogic_analysis': analysis_result['analisis_pedagogik']
            }
            db.session.commit()
        
        return jsonify(analysis_result)
        
    except Exception as e:
        return jsonify({'error': f'Error in pedagogic analysis: {str(e)}'}), 500

@app.route('/api/pedagogic/analyze-class/<int:kelas_id>', methods=['GET'])
@teacher_required
def analyze_class_performance(kelas_id):
    """
    Analisis pedagogik untuk performa kelas
    """
    if not PEDAGOGIC_ANALYSIS_AVAILABLE:
        return jsonify({
            'error': 'Pedagogic analysis not available. Please install google-generativeai package.'
        }), 503
    
    try:
        # Verify kelas exists dan pastikan milik guru yang sedang login
        guru_id = session['user_id']
        kelas = Kelas.query.filter_by(id=kelas_id, guru_id=guru_id).first()
        if not kelas:
            return jsonify({'error': 'Kelas not found or access denied'}), 404
        
        # Get all students in the class with their exam results
        siswa_list = Siswa.query.filter_by(kelas=kelas_id).all()
        
        data_kelas = []
        for siswa in siswa_list:
            # Get latest exam result for this student
            latest_exam = UjianSiswa.query.filter_by(siswa=siswa.no).order_by(UjianSiswa.id.desc()).first()
            
            student_data = {
                'nisn': siswa.NISN,
                'nama_siswa': siswa.nama_siswa,
                'kelas': siswa.kelas,
                'nilai': latest_exam.nilai if latest_exam else 0,
                'label_nilai': latest_exam.label_nilai if latest_exam else 'Belum ada ujian',
                'deskripsi_analisis': latest_exam.deskripsi_analisis if latest_exam else 'Belum ada analisis'
            }
            data_kelas.append(student_data)
        
        # Perform pedagogic analysis
        analyzer = get_pedagogic_analyzer()
        analysis_result = analyzer.analyze_class_performance(data_kelas)
        
        return jsonify(analysis_result)
        
    except Exception as e:
        return jsonify({'error': f'Error in class analysis: {str(e)}'}), 500

@app.route('/api/pedagogic/analyze-student/<int:siswa_no>', methods=['GET'])
@teacher_required
def analyze_student_learning_patterns(siswa_no):
    """
    Analisis pola pembelajaran siswa
    """
    if not PEDAGOGIC_ANALYSIS_AVAILABLE:
        return jsonify({
            'error': 'Pedagogic analysis not available. Please install google-generativeai package.'
        }), 503
    
    try:
        # Verify siswa exists
        siswa = Siswa.query.get(siswa_no)
        if not siswa:
            return jsonify({'error': 'Siswa not found'}), 404
        
        # Get all exam results for this student
        exam_results = UjianSiswa.query.filter_by(siswa=siswa_no).order_by(UjianSiswa.id).all()
        
        data_siswa = []
        for result in exam_results:
            ujian = Ujian.query.get(result.ujian)
            student_data = {
                'ujian_id': result.ujian,
                'nama_ujian': ujian.nama_ujian if ujian else 'Ujian tidak diketahui',
                'nilai': result.nilai,
                'label_nilai': result.label_nilai,
                'deskripsi_analisis': result.deskripsi_analisis,
                'tanggal_ujian': ujian.pelaksanaan.isoformat() if ujian and ujian.pelaksanaan else None
            }
            data_siswa.append(student_data)
        
        # Perform pedagogic analysis
        analyzer = get_pedagogic_analyzer()
        analysis_result = analyzer.analyze_learning_patterns(data_siswa)
        
        return jsonify(analysis_result)
        
    except Exception as e:
        return jsonify({'error': f'Error in student analysis: {str(e)}'}), 500

@app.route('/api/pedagogic/analyze-exam/<int:exam_id>', methods=['GET'])
@teacher_required
def analyze_exam_results(exam_id):
    """
    Analisis pedagogik untuk hasil ujian tertentu
    """
    if not PEDAGOGIC_ANALYSIS_AVAILABLE:
        return jsonify({
            'error': 'Pedagogic analysis not available. Please install google-generativeai package.'
        }), 503
    
    try:
        # Verify exam exists
        ujian = Ujian.query.get(exam_id)
        if not ujian:
            return jsonify({'error': 'Ujian not found'}), 404
        
        # Get all exam results for this exam
        exam_results = UjianSiswa.query.filter_by(ujian=exam_id).all()
        
        data_ujian = []
        for result in exam_results:
            siswa = Siswa.query.get(result.siswa)
            exam_data = {
                'siswa_id': result.siswa,
                'nisn': siswa.NISN if siswa else 'Tidak diketahui',
                'nama_siswa': siswa.nama_siswa if siswa else 'Tidak diketahui',
                'nilai': result.nilai,
                'label_nilai': result.label_nilai,
                'deskripsi_analisis': result.deskripsi_analisis
            }
            data_ujian.append(exam_data)
        
        # Perform pedagogic analysis
        analyzer = get_pedagogic_analyzer()
        analysis_result = analyzer.analyze_class_performance(data_ujian)
        
        # Add exam-specific information
        analysis_result['exam_info'] = {
            'exam_id': exam_id,
            'nama_ujian': ujian.nama_ujian,
            'kelas': ujian.kelas,
            'pelaksanaan': ujian.pelaksanaan.isoformat() if ujian.pelaksanaan else None,
            'status': ujian.status,
            'total_participants': len(data_ujian)
        }
        
        return jsonify(analysis_result)
        
    except Exception as e:
        return jsonify({'error': f'Error in exam analysis: {str(e)}'}), 500

@app.route('/api/pedagogic/status', methods=['GET'])
def get_pedagogic_analysis_status():
    """
    Check status of pedagogic analysis service
    """
    return jsonify({
        'available': PEDAGOGIC_ANALYSIS_AVAILABLE,
        'model': 'gemini-2.0-flash' if PEDAGOGIC_ANALYSIS_AVAILABLE else None,
        'message': 'Pedagogic analysis service is ready' if PEDAGOGIC_ANALYSIS_AVAILABLE else 'Service not available'
    })

@app.route('/api/pedagogic/analyze-text', methods=['POST'])
def analyze_text_pedagogic():
    data = request.get_json()
    text = data.get('text')
    if not text:
        return jsonify({'error': 'Text is required'}), 400

    if not PEDAGOGIC_ANALYSIS_AVAILABLE:
        # Dummy response jika modul tidak tersedia
        return jsonify({
            'available': False,
            'message': 'Pedagogic analysis not available. Please install google-generativeai package.',
            'input_text': text,
            'analisis_pedagogik': 'Fitur analisis pedagogik belum aktif.'
        }), 503

    try:
        analyzer = get_pedagogic_analyzer()
        result = analyzer.analyze_text(text)
        return jsonify({
            'available': True,
            'input_text': text,
            'analisis_pedagogik': result
        })
    except Exception as e:
        return jsonify({'error': f'Error in pedagogic analysis: {str(e)}'}), 500

@app.route('/api/teacher/test-gemini-analysis', methods=['POST'])
@teacher_required
def test_gemini_math_analysis():
    """
    Endpoint khusus untuk guru testing analisis Gemini pada soal matematika
    """
    data = request.get_json()
    soal_text = data.get('soal_text')
    
    if not soal_text:
        return jsonify({'error': 'soal_text is required'}), 400
    
    if not PEDAGOGIC_ANALYSIS_AVAILABLE:
        return jsonify({
            'error': 'Gemini analysis not available. Please install google-generativeai package.',
            'available': False
        }), 503
    
    # Check for GEMINI_API_KEY
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return jsonify({
            'error': 'GEMINI_API_KEY not found in environment variables',
            'available': False,
            'setup_instructions': 'Please add GEMINI_API_KEY to your .env file'
        }), 400
    
    try:
        # Test complete analysis (simple + Gemini if needed)
        complete_result = solve_text_internal(soal_text)
        
        # Test simple analysis only for comparison
        simple_only_result = extract_math_simple(soal_text)
        
        # Test Gemini analysis directly for detailed info
        gemini_result = analyze_math_problem_with_gemini(soal_text)
        
        return jsonify({
            'available': True,
            'input_soal': soal_text,
            'final_result': complete_result,
            'simple_only': simple_only_result,
            'gemini_raw': gemini_result,
            'analysis_summary': {
                'final_operator': complete_result.get('operator'),
                'final_angka': complete_result.get('angka_dalam_soal'),
                'final_jawaban': complete_result.get('jawaban'),
                'enhanced_by_ai': complete_result.get('enhanced_by_ai', False),
                'simple_operator': simple_only_result.get('operator'),
                'gemini_operator': gemini_result.get('analysis', {}).get('operator'),
                'needs_gemini': simple_only_result.get('operator') in ['Tidak diketahui', 'Mix', 'Campuran'],
                'gemini_successful': gemini_result.get('status') == 'success'
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error in Gemini testing: {str(e)}',
            'available': False
        }), 500

@app.route('/api/gemini/setup-check', methods=['GET'])
def check_gemini_setup():
    """
    Check Gemini setup status
    """
    api_key = os.getenv('GEMINI_API_KEY')
    
    return jsonify({
        'gemini_available': PEDAGOGIC_ANALYSIS_AVAILABLE,
        'api_key_configured': api_key is not None,
        'api_key_length': len(api_key) if api_key else 0,
        'setup_instructions': {
            'step_1': 'Install google-generativeai package: pip install google-generativeai',
            'step_2': 'Get API key from https://aistudio.google.com/app/apikey',
            'step_3': 'Add GEMINI_API_KEY=your_api_key to .env file',
            'step_4': 'Restart the application'
        } if not (PEDAGOGIC_ANALYSIS_AVAILABLE and api_key) else None
    })

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 204
    else:
        data = request.get_json()
        
        # Login dengan email (untuk guru/admin)
        if 'email' in data and 'nisn' not in data:
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return jsonify({'error': 'Email dan password wajib diisi'}), 400
                
            user = User.query.filter_by(email=email).first()
            if not user:
                return jsonify({'error': 'Email tidak ditemukan'}), 401
                
            if not check_password_hash(user.password, password):
                return jsonify({'error': 'Password salah'}), 401
            
            # Clear previous session
            session.clear()
            
            # Set session data with debug
            session['user_id'] = user.id
            session['role'] = user.role
            session['email'] = user.email
            session['nama_lengkap'] = user.nama_lengkap
            session.permanent = True
            
            print(f"Login - Setting session: user_id={user.id}, role={user.role}")
            
            # Check if user is actually a student (has siswa profile)
            siswa = Siswa.query.filter_by(user_id=user.id).first()
            if siswa:
                # This is a student, get kelas info
                kelas = Kelas.query.filter_by(id=siswa.kelas).first()
                session['kelas_id'] = kelas.id
                session['nama_kelas'] = kelas.nama
                session['role'] = 'siswa'  # Force role to siswa
                
                print(f"Login - Student found: NISN={siswa.NISN}, kelas={kelas.nama}")
                print(f"Login - Final session: {dict(session)}")
                
                return jsonify({
                    'message': 'Login berhasil',
                    'role': 'siswa',
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'nama_lengkap': user.nama_lengkap,
                        'jenis_kelamin': user.jenis_kelamin,
                        'role': 'siswa',
                        'kelas': {
                            'id': kelas.id,
                            'nama': kelas.nama
                        }
                    }
                })
            else:
                # This is a teacher/admin
                print(f"Login - Teacher/Admin login: {user.role}")
                print(f"Login - Final session: {dict(session)}")
                
                return jsonify({
                    'message': 'Login berhasil',
                    'role': user.role,
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'nama_lengkap': user.nama_lengkap,
                        'jenis_kelamin': user.jenis_kelamin,
                        'role': user.role,
                        'kelas': None
                    }
                })

        # Login dengan NISN (untuk siswa)
        elif 'nisn' in data:
            nisn = data.get('nisn')
            password = data.get('password')
            
            if not nisn or not password:
                return jsonify({'error': 'NISN dan password wajib diisi'}), 400
            
            # Get user and student data with JOIN
            user_data = db.session.query(User, Siswa, Kelas)\
                .join(Siswa, User.id == Siswa.user_id)\
                .join(Kelas, Siswa.kelas == Kelas.id)\
                .filter(Siswa.NISN == nisn)\
                .first()
            
            if not user_data:
                return jsonify({'error': 'NISN tidak ditemukan'}), 401
                
            user, siswa, kelas = user_data
            
            if not check_password_hash(user.password, password):
                return jsonify({'error': 'Password salah'}), 401
            
            # Clear previous session
            session.clear()
            
            # Set session data
            session['user_id'] = user.id
            session['role'] = 'siswa'
            session['email'] = user.email
            session['nama_lengkap'] = user.nama_lengkap
            session['nisn'] = siswa.NISN
            session['nama_siswa'] = siswa.nama_siswa
            session['kelas_id'] = kelas.id
            session['nama_kelas'] = kelas.nama
            session.permanent = True
            
            print(f"NISN Login - Setting session: user_id={user.id}, role=siswa, NISN={siswa.NISN}")
            print(f"NISN Login - Final session: {dict(session)}")
            
            return jsonify({
                'message': 'Login berhasil',
                'role': 'siswa',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'nama_lengkap': user.nama_lengkap,
                    'jenis_kelamin': user.jenis_kelamin,
                    'role': 'siswa',
                    'kelas': {
                        'id': kelas.id,
                        'nama': kelas.nama
                    }
                }
            })
        else:
            return jsonify({'error': 'Email/NISN dan password wajib diisi'}), 400



# Endpoint baru untuk siswa menambah jawaban dengan analisis compare answer
@app.route('/api/student/jawaban-siswa', methods=['POST'])
@student_required
def create_jawaban_siswa_by_student():
    data = request.get_json()
    user_id = session.get('user_id')
    
    # Debug logging
    print(f"Session data: {dict(session)}")
    print(f"User ID from session: {user_id}")
    
    # Get student data using user_id from session
    siswa_obj = Siswa.query.filter_by(user_id=user_id).first()
    print(f"Found siswa: {siswa_obj}")
    
    if not siswa_obj:
        return jsonify({'error': 'Siswa tidak ditemukan di database'}), 404
    
    # Get soal to compare with correct answer
    soal_id = data['soal']
    soal = Soal.query.get(soal_id)
    
    # Initialize json_result with student answer
    json_result = data.get('json_result', {})
    
    # Perform comparison analysis if both soal and student answer exist
    try:
        if soal and soal.json_result and json_result:
            ai_answer = soal.json_result  # Correct answer from soal
            student_answer = json_result  # Student's answer
            
            print(f"AI Answer: {ai_answer}")
            print(f"Student Answer: {student_answer}")
            
            # Perform comparison analysis using internal function
            comparison_result = compare_answers_internal(ai_answer, student_answer)
            
            # Add comparison result to json_result
            json_result['comparison'] = comparison_result
            
            # Update status based on comparison
            if comparison_result['nilai'] >= 3:
                status = 'correct'
            else:
                status = 'incorrect'
        else:
            status = data.get('status', 'unknown')
            print(f"Skipping comparison - soal: {soal is not None}, soal.json_result: {soal.json_result if soal else None}, json_result: {json_result}")
    except Exception as e:
        print(f"Error during comparison analysis: {str(e)}")
        status = data.get('status', 'unknown')
        # Add error info to json_result
        if 'comparison' not in json_result:
            json_result['comparison'] = {
                'status': 'error',
                'error_message': str(e),
                'deskripsi_analisis': 'Terjadi kesalahan saat melakukan analisis perbandingan',
                'nilai': 0,
                'parameter_salah': [],
                'koreksi': []
            }
    
    # Create jawaban siswa
    jawaban = JawabanSiswa(
        nisn=siswa_obj.NISN,  # Use NISN from database
        soal=data['soal'],
        status=status,
        json_result=json_result,
        nilai=comparison_result['nilai']
    )
    
    print(f"Creating jawaban: NISN={siswa_obj.NISN}, soal={data['soal']}, status={status}")
    
    db.session.add(jawaban)
    db.session.commit()
    
    return jsonify({
        'message': 'Jawaban siswa created successfully with comparison analysis',
        'comparison_result': json_result.get('comparison', {})
    })

# Endpoint untuk menambahkan analisis comparison pada jawaban yang sudah ada
@app.route('/api/teacher/jawaban-siswa/<int:jawaban_id>/analyze', methods=['POST'])
@teacher_required
def analyze_existing_jawaban(jawaban_id):
    """
    Endpoint untuk guru menambahkan analisis comparison pada jawaban siswa yang sudah ada
    """
    jawaban = JawabanSiswa.query.get_or_404(jawaban_id)
    
    # Get soal data for correct answer
    soal = Soal.query.get(jawaban.soal)
    if not soal or not soal.json_result:
        return jsonify({'error': 'Soal atau jawaban benar tidak ditemukan'}), 404
    
    # Get student answer from jawaban.json_result
    if not jawaban.json_result:
        return jsonify({'error': 'Data jawaban siswa tidak ditemukan'}), 404
    
    ai_answer = soal.json_result  # Correct answer from soal
    student_answer = jawaban.json_result  # Student's answer
    
    # Perform comparison analysis
    comparison_result = compare_answers_internal(ai_answer, student_answer)
    
    # Update json_result with comparison analysis
    updated_json_result = jawaban.json_result.copy()
    updated_json_result['comparison'] = comparison_result
    
    # Update status based on comparison
    if comparison_result['nilai'] >= 3:
        jawaban.status = 'correct'
    else:
        jawaban.status = 'incorrect'
    
    jawaban.json_result = updated_json_result
    
    db.session.commit()
    
    return jsonify({
        'message': 'Analisis comparison berhasil ditambahkan',
        'jawaban_id': jawaban_id,
        'comparison_result': comparison_result,
        'updated_status': jawaban.status
    })

# Endpoint untuk analisis batch pada semua jawaban dalam ujian tertentu
@app.route('/api/teacher/ujian/<int:ujian_id>/analyze-all-answers', methods=['POST'])
@teacher_required
def analyze_all_answers_in_exam(ujian_id):
    """
    Endpoint untuk guru menganalisis semua jawaban siswa dalam ujian tertentu
    """
    # Pastikan ujian ada di kelas yang dimiliki guru yang sedang login
    guru_id = session['user_id']
    ujian = Ujian.query.join(Kelas).filter(
        Ujian.id == ujian_id,
        Kelas.guru_id == guru_id
    ).first()
    
    if not ujian:
        return jsonify({'error': 'Ujian not found or access denied'}), 404
    
    # Get all soal for this ujian
    soal_list = Soal.query.filter_by(ujian=ujian_id).all()
    
    updated_count = 0
    errors = []
    
    for soal in soal_list:
        if not soal.json_result:
            errors.append(f"Soal ID {soal.id}: Tidak ada jawaban benar")
            continue
        
        # Get all jawaban for this soal
        jawaban_list = JawabanSiswa.query.filter_by(soal=soal.id).all()
        
        for jawaban in jawaban_list:
            if not jawaban.json_result:
                errors.append(f"Jawaban ID {jawaban.id}: Tidak ada data jawaban siswa")
                continue
            
            try:
                ai_answer = soal.json_result
                student_answer = jawaban.json_result
                
                # Perform comparison analysis
                comparison_result = compare_answers_internal(ai_answer, student_answer)
                
                # Update json_result with comparison analysis
                updated_json_result = jawaban.json_result.copy()
                updated_json_result['comparison'] = comparison_result
                
                # Update status based on comparison
                if comparison_result['nilai'] >= 3:
                    jawaban.status = 'correct'
                else:
                    jawaban.status = 'incorrect'
                
                jawaban.json_result = updated_json_result
                updated_count += 1
                
            except Exception as e:
                errors.append(f"Jawaban ID {jawaban.id}: Error - {str(e)}")
    
    db.session.commit()
    
    return jsonify({
        'message': f'Analisis selesai. {updated_count} jawaban berhasil dianalisis',
        'updated_count': updated_count,
        'errors': errors,
        'ujian_id': ujian_id
    })

# Endpoint untuk melihat hasil analisis comparison jawaban siswa
@app.route('/api/teacher/jawaban-siswa/<int:jawaban_id>/comparison', methods=['GET'])
@teacher_required
def get_jawaban_comparison(jawaban_id):
    """
    Endpoint untuk melihat hasil analisis comparison dari jawaban siswa
    """
    jawaban = JawabanSiswa.query.get_or_404(jawaban_id)
    
    if not jawaban.json_result or 'comparison' not in jawaban.json_result:
        return jsonify({'error': 'Analisis comparison belum dilakukan pada jawaban ini'}), 404
    
    # Get student and soal info
    siswa = Siswa.query.filter_by(NISN=jawaban.nisn).first()
    soal = Soal.query.get(jawaban.soal)
    
    return jsonify({
        'jawaban_id': jawaban_id,
        'siswa_info': {
            'nisn': siswa.NISN if siswa else 'Unknown',
            'nama_siswa': siswa.nama_siswa if siswa else 'Unknown'
        },
        'soal_info': {
            'id': soal.id if soal else None,
            'soal': soal.soal if soal else 'Unknown'
        },
        'student_answer': {
            'operator': jawaban.json_result.get('operator', 'Tidak diketahui'),
            'angka_dalam_soal': jawaban.json_result.get('angka_dalam_soal', 'Tidak diketahui'),
            'jawaban': jawaban.json_result.get('jawaban', 'Tidak diketahui')
        },
        'correct_answer': soal.json_result if soal else {},
        'comparison_analysis': jawaban.json_result['comparison'],
        'overall_status': jawaban.status
    })

# Endpoint untuk melihat semua analisis comparison dalam ujian
@app.route('/api/teacher/ujian/<int:ujian_id>/comparison-report', methods=['GET'])
@teacher_required
def get_ujian_comparison_report(ujian_id):
    """
    Endpoint untuk melihat laporan analisis comparison semua jawaban dalam ujian
    """
    # Pastikan ujian ada di kelas yang dimiliki guru yang sedang login
    guru_id = session['user_id']
    ujian = Ujian.query.join(Kelas).filter(
        Ujian.id == ujian_id,
        Kelas.guru_id == guru_id
    ).first()
    
    if not ujian:
        return jsonify({'error': 'Ujian not found or access denied'}), 404
    
    # Get all soal for this ujian
    soal_list = Soal.query.filter_by(ujian=ujian_id).all()
    
    report_data = {
        'ujian_info': {
            'id': ujian.id,
            'nama_ujian': ujian.nama_ujian,
            'kelas': ujian.kelas,
            'pelaksanaan': ujian.pelaksanaan.isoformat() if ujian.pelaksanaan else None
        },
        'soal_analysis': [],
        'summary': {
            'total_jawaban': 0,
            'jawaban_with_comparison': 0,
            'jawaban_without_comparison': 0,
            'correct_answers': 0,
            'incorrect_answers': 0
        }
    }
    
    for soal in soal_list:
        jawaban_list = JawabanSiswa.query.filter_by(soal=soal.id).all()
        
        soal_data = {
            'soal_id': soal.id,
            'soal_text': soal.soal,
            'correct_answer': soal.json_result,
            'student_answers': []
        }
        
        for jawaban in jawaban_list:
            report_data['summary']['total_jawaban'] += 1
            
            # Get student info
            siswa = Siswa.query.filter_by(NISN=jawaban.nisn).first()
            
            jawaban_data = {
                'jawaban_id': jawaban.id,
                'siswa_info': {
                    'nisn': siswa.NISN if siswa else 'Unknown',
                    'nama_siswa': siswa.nama_siswa if siswa else 'Unknown'
                },
                'student_answer': jawaban.json_result,
                'status': jawaban.status,
                'has_comparison': 'comparison' in (jawaban.json_result or {}),
                'comparison_analysis': jawaban.json_result.get('comparison') if jawaban.json_result else None
            }
            
            if jawaban_data['has_comparison']:
                report_data['summary']['jawaban_with_comparison'] += 1
                if jawaban.status in ['excellent', 'good']:
                    report_data['summary']['correct_answers'] += 1
                else:
                    report_data['summary']['incorrect_answers'] += 1
            else:
                report_data['summary']['jawaban_without_comparison'] += 1
            
            soal_data['student_answers'].append(jawaban_data)
        
        report_data['soal_analysis'].append(soal_data)
    
    return jsonify(report_data)

# Debug endpoint untuk mengecek session
@app.route('/api/debug/session', methods=['GET'])
def debug_session():
    return jsonify({
        'session_data': dict(session),
        'session_keys': list(session.keys()),
        'has_user_id': 'user_id' in session,
        'has_role': 'role' in session,
        'user_id': session.get('user_id'),
        'role': session.get('role')
    })

@app.route('/api/debug/ujian-siswa/<int:ujian_siswa_id>/detail', methods=['GET'])
def debug_ujian_siswa_detail_sp(ujian_siswa_id):
    """
    DEBUG: Get detailed ujian siswa data using stored procedure (no auth required)
    """
    try:
        print(f"DEBUG: Calling stored procedure for ujian_siswa_id: {ujian_siswa_id}")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Call stored procedure
        cursor.callproc('get_ujian_siswa_detail', [ujian_siswa_id])
        print(f"DEBUG: Stored procedure called successfully")
        
        # Get results and column names
        results = []
        columns = []
        
        for result in cursor.stored_results():
            columns = [desc[0] for desc in result.description]
            fetched_data = result.fetchall()
            results.extend(fetched_data)
        
        print(f"DEBUG: Retrieved {len(results)} records from stored procedure")
        print(f"DEBUG: Columns: {columns}")
        
        cursor.close()
        conn.close()
        
        if not results:
            return jsonify({'error': 'Data ujian siswa tidak ditemukan'}), 404
        
        # Convert to dictionary format
        dict_results = []
        for row in results:
            row_dict = {}
            for i, col in enumerate(columns):
                row_dict[col] = row[i]
            dict_results.append(row_dict)
        
        print(f"DEBUG: Converted to dictionary format")
        
        # Serialize results to handle bytes/JSON fields
        print(f"DEBUG: Serializing results...")
        serialized_results = serialize_stored_procedure_result(dict_results)
        print(f"DEBUG: Serialization completed")
        
        return jsonify({
            'ujian_siswa_id': ujian_siswa_id,
            'total_records': len(serialized_results),
            'data': serialized_results
        })
        
    except Exception as e:
        print(f"DEBUG: Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error calling stored procedure: {str(e)}'}), 500

# ============================================================================
# STORED PROCEDURE ENDPOINTS
# ============================================================================

@app.route('/api/teacher/ujian-siswa/<int:ujian_siswa_id>/detail', methods=['GET'])
@teacher_required
def get_ujian_siswa_detail_sp(ujian_siswa_id):
    """
    Get detailed ujian siswa data using stored procedure
    """
    try:
        print(f"DEBUG: Calling stored procedure for ujian_siswa_id: {ujian_siswa_id}")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Call stored procedure
        cursor.callproc('get_ujian_siswa_detail', [ujian_siswa_id])
        print(f"DEBUG: Stored procedure called successfully")
        
        # Get results and column names
        results = []
        columns = []
        
        for result in cursor.stored_results():
            columns = [desc[0] for desc in result.description]
            fetched_data = result.fetchall()
            results.extend(fetched_data)
        
        print(f"DEBUG: Retrieved {len(results)} records from stored procedure")
        print(f"DEBUG: Columns: {columns}")
        
        cursor.close()
        conn.close()
        
        if not results:
            return jsonify({'error': 'Data ujian siswa tidak ditemukan'}), 404
        
        # Convert to dictionary format
        dict_results = []
        for row in results:
            row_dict = {}
            for i, col in enumerate(columns):
                row_dict[col] = row[i]
            dict_results.append(row_dict)
        
        print(f"DEBUG: Converted to dictionary format")
        
        # Serialize results to handle bytes/JSON fields
        print(f"DEBUG: Serializing results...")
        serialized_results = serialize_stored_procedure_result(dict_results)
        print(f"DEBUG: Serialization completed")
        
        return jsonify({
            'ujian_siswa_id': ujian_siswa_id,
            'total_records': len(serialized_results),
            'data': serialized_results
        })
        
    except Exception as e:
        return jsonify({'error': f'Error calling stored procedure: {str(e)}'}), 500

@app.route('/api/teacher/ujian-siswa/<int:ujian_siswa_id>/summary', methods=['GET'])
@teacher_required
def get_ujian_siswa_summary_sp(ujian_siswa_id):
    """
    Get ujian siswa summary using stored procedure
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Call stored procedure
        cursor.callproc('get_ujian_siswa_summary', [ujian_siswa_id])
        
        # Get results
        result = None
        columns = []
        
        for stored_result in cursor.stored_results():
            columns = [desc[0] for desc in stored_result.description]
            result = stored_result.fetchone()
            break
        
        cursor.close()
        conn.close()
        
        if not result:
            return jsonify({'error': 'Data ujian siswa tidak ditemukan'}), 404
        
        # Convert to dictionary format
        result_dict = {}
        for i, col in enumerate(columns):
            result_dict[col] = result[i]
        
        # Serialize result to handle bytes/JSON fields
        serialized_result = serialize_stored_procedure_result(result_dict)
        
        return jsonify(serialized_result)
        
    except Exception as e:
        return jsonify({'error': f'Error calling stored procedure: {str(e)}'}), 500

@app.route('/api/teacher/ujian-siswa/<int:ujian_siswa_id>/comparison-analysis', methods=['GET'])
@teacher_required
def get_ujian_siswa_comparison_analysis_sp(ujian_siswa_id):
    """
    Get ujian siswa comparison analysis using stored procedure
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Call stored procedure
        cursor.callproc('get_ujian_siswa_comparison_analysis', [ujian_siswa_id])
        
        # Get results
        results = []
        columns = []
        
        for result in cursor.stored_results():
            columns = [desc[0] for desc in result.description]
            results.extend(result.fetchall())
        
        cursor.close()
        conn.close()
        
        # Convert to dictionary format
        dict_results = []
        for row in results:
            row_dict = {}
            for i, col in enumerate(columns):
                row_dict[col] = row[i]
            dict_results.append(row_dict)
        
        # Serialize results to handle bytes/JSON fields
        serialized_results = serialize_stored_procedure_result(dict_results)
        
        return jsonify({
            'ujian_siswa_id': ujian_siswa_id,
            'total_analyzed': len(serialized_results),
            'data': serialized_results
        })
        
    except Exception as e:
        return jsonify({'error': f'Error calling stored procedure: {str(e)}'}), 500

@app.route('/api/teacher/ujian-siswa/list', methods=['GET'])
@teacher_required
def get_ujian_siswa_list():
    """
    Get list of ujian siswa with basic info for navigation - hanya untuk kelas guru yang sedang login
    Menggunakan stored procedure get_ujian_siswa_by_guru
    """
    try:
        guru_id = session['user_id']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Call stored procedure
        cursor.callproc('get_ujian_siswa_by_guru', [guru_id])
        
        # Get results and column names
        results = []
        columns = []
        
        for result in cursor.stored_results():
            columns = [desc[0] for desc in result.description]
            results.extend(result.fetchall())
        
        cursor.close()
        conn.close()
        
        # Convert to dictionary format
        dict_results = []
        for row in results:
            row_dict = {}
            for i, col in enumerate(columns):
                row_dict[col] = row[i]
            dict_results.append(row_dict)
        
        # Serialize results to handle any potential JSON fields
        serialized_result = serialize_stored_procedure_result(dict_results)
        
        return jsonify(serialized_result)
        
    except Exception as e:
        return jsonify({'error': f'Error fetching ujian siswa list: {str(e)}'}), 500

@app.route('/api/teacher/dashboard/stats', methods=['GET'])
@teacher_required
def get_teacher_dashboard_stats():
    """
    Get dashboard statistics untuk guru menggunakan stored procedure
    """
    try:
        guru_id = session['user_id']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Call stored procedure
        cursor.callproc('get_guru_dashboard_stats', [guru_id])
        
        # Get results and column names
        result = None
        columns = []
        
        for stored_result in cursor.stored_results():
            columns = [desc[0] for desc in stored_result.description]
            result = stored_result.fetchone()
            break
        
        cursor.close()
        conn.close()
        
        if not result:
            return jsonify({'error': 'No statistics available'}), 404
        
        # Convert to dictionary format
        result_dict = {}
        for i, col in enumerate(columns):
            result_dict[col] = result[i]
        
        # Serialize result to handle any potential JSON/bytes fields
        serialized_result = serialize_stored_procedure_result(result_dict)
        
        return jsonify(serialized_result)
        
    except Exception as e:
        return jsonify({'error': f'Error fetching dashboard stats: {str(e)}'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 