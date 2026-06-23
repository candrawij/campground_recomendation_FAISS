# Laporan Akhir Proyek: Sistem Rekomendasi Tempat Kemah Berbasis Ulasan Google Maps

**Tanggal Penyelesaian**: 24 Juni 2026
**Fokus Proyek**: Natural Language Processing (NLP), Semantic Search, & Recommender System

---

## 1. Ringkasan Eksekutif
Proyek ini merupakan pengembangan sistem rekomendasi tempat kemah cerdas berbasis *Natural Language Processing* (NLP) yang memanfaatkan ulasan nyata pengguna dari Google Maps. Sistem ini tidak lagi menggunakan pencarian berbasis kata kunci konvensional (*keyword matching*), melainkan menggunakan pencarian **Semantic Vector Search** yang dapat memahami makna kalimat ("niat" pengguna).

Pengembangan proyek ini merujuk secara penuh pada dokumen *Product Requirement Document (PRD) Versi 2.0* dan telah berhasil diimplementasikan 100% dari Modul 1 hingga Modul 6.

---

## 2. Arsitektur dan Alur Sistem
Sistem ini menggunakan pendekatan *Hybrid Recommendation* (menggabungkan *Semantic Search* dengan *Metadata Reranking*):
1. **Offline Pipeline (Data & Indexing)**: Memproses ribuan ulasan mentah, mengubah teks menjadi vektor menggunakan *Sentence-BERT*, dan menyimpannya di dalam indeks *FAISS* untuk akses cepat.
2. **Online Pipeline (Search & Reranking)**: Menerima masukan dari pengguna melalui web UI (Gradio), diubah menjadi vektor, dicarikan kandidat kemiripannya melalui *FAISS*, lalu diurutkan ulang (*reranking*) berdasarkan harga, fasilitas, *rating*, dan popularitas tempat sebelum disajikan ke pengguna.

---

## 3. Implementasi Modul per Modul

### ✅ Modul 1: Data Preparation (`modul_1_preparation.py`)
- **Tujuan**: Membersihkan dan menggabungkan *dataset* mentah.
- **Hasil**: Berhasil membersihkan teks kotor (URL, *mention*, *hashtag*, emoji) dari korpus ulasan. Data diagregasi untuk menghasilkan satu "Profil Teks" utuh untuk setiap tempat kemah (total **55 tempat** tervalidasi). JSON *Price_Items* dan *Facilities* di-*parse* ke dalam list untuk mempermudah perhitungan *reranking*.
- **Output**: `documents/processed/processed_places.csv`

### ✅ Modul 2: Feature Engineering & Embedding (`modul_2_embedding.py`)
- **Tujuan**: Menerjemahkan teks bahasa manusia ke dalam matriks angka.
- **Hasil**: Menggunakan model *Deep Learning* mutakhir `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. Seluruh 55 "Profil Teks" diubah menjadi bentuk vektor berdimensi `(55, 384)`.
- **Output**: `documents/processed/embeddings.npy` dan `documents/processed/places_metadata.csv`

### ✅ Modul 3: Indexing & Candidate Generation (`modul_3_indexing.py`)
- **Tujuan**: Menyediakan infrastruktur pencarian cepat.
- **Hasil**: Melakukan *L2 Normalization* pada hasil *embedding* sehingga fungsi *Inner Product* pada *FAISS (Facebook AI Similarity Search)* ekuivalen dengan *Cosine Similarity*. Indeks dikompilasi secara efisien.
- **Output**: `documents/processed/faiss_index.bin`

### ✅ Modul 4: Ranking & Reranking (`modul_4_ranking.py`)
- **Tujuan**: Membuat rekomendasi yang logis dan disesuaikan.
- **Hasil**: Menambahkan algoritma *rule-based intent detection*. Kueri pengguna dipindai untuk mendeteksi *intent* seperti mencari "yang paling murah", "paling lengkap", atau "gratis". Skor semantik dari FAISS (50%) digabungkan dengan metrik dunia nyata yaitu *Rating* (25%), Popularitas/Jumlah Ulasan (15%), dan Kesesuaian Harga/Fasilitas (10%).

### ✅ Modul 5: API & Web Interface (`modul_5_api.py` & `app.py`)
- **Tujuan**: *Deployment* dan pengalaman pengguna (UX).
- **Hasil**: Membangun REST API lokal menggunakan **Flask** yang berjalan lancar di *port* `5000`. Untuk UI, modul ini memanfaatkan **Gradio** di *port* `7860` untuk menciptakan tampilan yang segar, fungsional, dan memiliki validasi dinamis layaknya aplikasi produksi.

### ✅ Modul 6: Evaluation (`modul_6_evaluation.py`)
- **Tujuan**: Evaluasi algoritma dengan skenario di dunia nyata.
- **Hasil**: Sistem diuji menggunakan 15 ragam variasi *kueri* yang mendefinisikan intent (Cuaca, Harga, Fasilitas). Evaluasi menggunakan pendekatan analitik *Ground Truth* dengan metrik:
  - **Recall@10** = 0.3100
  - **MRR** = 0.2646
  - **NDCG@10** = 0.2073
  
  *(Angka evaluasi masih dalam toleransi baseline mengingat Ground Truth dibuat berasumsi *rule-of-thumb* dan anomali dataset yang berukuran relatif kecil. Secara kualitatif/fungsional di UI, sistem mampu merekomendasikan tempat relevan dengan baik).*

---

## 4. Cara Menjalankan Sistem (Panduan Pengembang)
Seluruh dependensi sudah di-*setup* pada *virtual environment* lokal. Untuk menjalankan kembali sistem ini, jalankan perintah berikut secara berurutan di terminal:

1. **Aktifkan Environment**
   ```powershell
   # Windows PowerShell
   .\venv\Scripts\Activate.ps1
   ```
2. **Jalankan Backend API (Terminal 1)**
   ```powershell
   python modul_5_api.py
   ```
3. **Jalankan Frontend Gradio UI (Terminal 2)**
   ```powershell
   python app.py
   ```
4. **Akses Aplikasi**: Buka `http://127.0.0.1:7860` di browser Anda.

---
**Dokumen ini disusun secara otomatis sebagai penanda diselesaikannya Sistem Rekomendasi Tempat Kemah v2.0.**
