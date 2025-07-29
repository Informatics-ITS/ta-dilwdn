from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nama_lengkap = db.Column(db.String(100), nullable=False)
    jenis_kelamin = db.Column(db.String(10), nullable=False)
    role = db.Column(db.String(20), default='admin')  # admin, siswa

class Kelas(db.Model):
    __tablename__ = 'kelas'
    
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(50), nullable=False)
    guru_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    siswa = db.relationship('Siswa', backref='kelas_ref', lazy=True)
    ujian = db.relationship('Ujian', backref='kelas_ref', lazy=True)
    guru = db.relationship('User', backref='kelas_mengajar', lazy=True)

class Siswa(db.Model):
    __tablename__ = 'siswa'
    no = db.Column(db.Integer, primary_key=True)
    NISN = db.Column(db.String(20), unique=True, nullable=False)
    nama_siswa = db.Column(db.String(100), nullable=False)
    kelas = db.Column(db.Integer, db.ForeignKey('kelas.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    user = db.relationship('User', backref=db.backref('siswa_profile', uselist=False))
    jawaban = db.relationship('JawabanSiswa', backref='siswa_ref', lazy=True)
    ujian_siswa = db.relationship('UjianSiswa', backref='siswa_ref', lazy=True)

class Ujian(db.Model):
    __tablename__ = 'ujian'
    
    id = db.Column(db.Integer, primary_key=True)
    nama_ujian = db.Column(db.String(100), nullable=False)
    kelas = db.Column(db.Integer, db.ForeignKey('kelas.id'), nullable=False)
    pelaksanaan = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False)
    soal = db.relationship('Soal', backref='ujian_ref', lazy=True)
    ujian_siswa = db.relationship('UjianSiswa', backref='ujian_ref', lazy=True)

class UjianSiswa(db.Model):
    __tablename__ = 'ujian_siswa'
    id = db.Column(db.Integer, primary_key=True)
    ujian = db.Column(db.Integer, db.ForeignKey('ujian.id'), nullable=False)
    siswa = db.Column(db.Integer, db.ForeignKey('siswa.no'), nullable=False)
    nilai = db.Column(db.Integer)
    label_nilai = db.Column(db.String(20))
    deskripsi_analisis = db.Column(db.Text)
    __table_args__ = (db.UniqueConstraint('ujian', 'siswa', name='unique_ujian_siswa'),)

class Soal(db.Model):
    __tablename__ = 'soal'
    
    id = db.Column(db.Integer, primary_key=True)
    soal = db.Column(db.String(255), nullable=False)
    ujian = db.Column(db.Integer, db.ForeignKey('ujian.id'), nullable=False)
    json_result = db.Column(db.JSON, nullable=False)
    jawaban = db.relationship('JawabanSiswa', backref='soal_ref', lazy=True)

class JawabanSiswa(db.Model):
    __tablename__ = 'jawaban_siswa'
    
    id = db.Column(db.Integer, primary_key=True)
    nisn = db.Column(db.String(20), db.ForeignKey('siswa.NISN', ondelete='CASCADE'), nullable=False)
    soal = db.Column(db.Integer, db.ForeignKey('soal.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    json_result = db.Column(db.JSON, nullable=True) 
    nilai = db.Column(db.Integer, nullable=True)