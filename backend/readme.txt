Langkah-langkah penggunaan aplikasi :
1. Instal python

2. Instal library yang dibutuhkan : 
pip install -r requirements.txt

3. Klik 2 kali pada file tesseract.exe. install dan untuk folder defaultnya ada di C:\Program Files\Tesseract-OCR\tesseract.exe , tunggu sampai instalasi selesai
4. Jalankan aplikasi dengan mengetikkan python apps.py lalu tekan enter

5. Kemudian akses halaman http://127.0.0.1:5000/ pada browser dan silahkan masukkan soal cerita atau upload gambar

6. atau gunakan rest API berikut detail request nya

url = http://localhost:5000/api/solve
method = POST
header = "Content-Type: application/json"
format json = {
    'image' : 'BASE64_IMAGE'
}

7. Soal cerita bisa didapatkan dari dataset atau gambar bisa didapatkan pada dataset.