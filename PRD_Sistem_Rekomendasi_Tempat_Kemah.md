PRODUCT REQUIREMENT DOCUMENT (PRD)
Sistem Rekomendasi Tempat Kemah Berbasis Ulasan Google Maps dengan Query Semantik
Versi	2.0
Tanggal	24 Juni 2026
Status	Final Draft
Acuan Akademik	Raza, S., Rahman, M., et al. (2026). A comprehensive review of recommender systems: Transitioning from theory to practice. Computer Science Review, 59, 100849.
Daftar Isi
Product Overview

System Architecture

Project Structure

Data Schema

Modul 1: Data Preparation

Modul 2: Feature Engineering & Embedding

Modul 3: Indexing & Candidate Generation

Modul 4: Ranking (Reranking)

Modul 5: API & Web Interface

Modul 6: Evaluation

Tech Stack

Development Milestones

Referensi Akademik

Lampiran

1. Product Overview
1.1 Ringkasan Produk
Sistem rekomendasi berbasis web yang memungkinkan pengguna mencari tempat kemah menggunakan query bahasa alami (natural language). Sistem memanfaatkan ulasan Google Maps sebagai sumber data utama, mengubahnya menjadi representasi semantik menggunakan Sentence-BERT, dan melakukan pencarian berbasis kemiripan makna menggunakan FAISS. Hasil pencarian diurutkan ulang (reranking) dengan mempertimbangkan metadata seperti rating, harga, fasilitas, dan popularitas.

1.2 Tujuan
Memudahkan pengguna menemukan tempat kemah yang sesuai dengan preferensi spesifik

Memanfaatkan ulasan nyata dari Google Maps sebagai sumber informasi rekomendasi

Memberikan hasil yang lebih relevan dibanding pencarian berbasis kata kunci biasa

Menghadirkan antarmuka yang modern dan mudah digunakan

1.3 Target Pengguna
Individu atau keluarga yang mencari tempat camping

Komunitas atau organisasi yang membutuhkan lokasi kegiatan outdoor

Wisatawan yang mencari pengalaman camping sesuai preferensi spesifik

1.4 Contoh Use Case
Query Pengguna	Hasil yang Diharapkan
"camping keluarga dengan fasilitas lengkap dan murah"	Tempat dengan harga terjangkau, banyak fasilitas, cocok untuk keluarga
"tempat sejuk buat healing sendiri"	Tempat dengan suasana tenang, pemandangan bagus, disebut "sejuk" di ulasan
"camping ground buat rombongan besar ada api unggun"	Tempat yang muat banyak orang, menyediakan fasilitas api unggun
2. System Architecture
text
┌──────────────────────────────────────────────────────────────────────┐
│                          SYSTEM ARCHITECTURE                         │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐                │
│  │  Gradio  │    │  Flask API   │    │    FAISS     │                │
│  │  (UI)    │───▶│  (Backend)   │───▶│  (Vector     │                │
│  │          │    │              │    │   Search)    │                │
│  └──────────┘    └──────┬───────┘    └──────┬───────┘                │
│                         │                   │                        │
│                         ▼                   ▼                        │
│                  ┌──────────────┐   ┌──────────────┐                │
│                  │  SBERT Model │   │  documents/  │                │
│                  │  (Embedding) │   │  processed/  │                │
│                  └──────────────┘   │  *.csv, *.npy│                │
│                                     │  *.bin       │                │
│                                     └──────────────┘                │
│                                                                      │
│  Data Pipeline (Offline):                                           │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐       │
│  │  Modul 1 │───▶│  Modul 2 │───▶│  Modul 3 │───▶│  Modul 4 │       │
│  │  Data    │    │ Embedding│    │ Indexing │    │ Ranking  │       │
│  │  Prep    │    │          │    │          │    │          │       │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘       │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
Alur Kerja Sistem:

Offline Pipeline (sekali jalan): Modul 1 → Modul 2 → Modul 3 memproses data dan membangun indeks

Online Query (setiap pencarian): Modul 4 + Modul 5 menerima query, mencari, mererank, dan menampilkan hasil

3. Project Structure
text
root/
│
├── asisten/
│   └── scraper_gmaps.py              # Kode scraping Google Maps (Playwright)
│
├── documents/
│   ├── corpus_master.csv              # Data mentah ulasan (INPUT)
│   ├── info_tempat.csv                # Metadata tambahan tempat (INPUT)
│   │
│   └── processed/                     # Hasil olahan tiap tahap (OUTPUT)
│       ├── processed_places.csv       # Output Modul 1
│       ├── embeddings.npy             # Output Modul 2
│       ├── places_metadata.csv        # Output Modul 2
│       └── faiss_index.bin            # Output Modul 3
│
├── modul_1_preparation.py             # Data cleaning & merging
├── modul_2_embedding.py               # SBERT embedding
├── modul_3_indexing.py                # FAISS index building
├── modul_4_ranking.py                 # Reranking logic
├── modul_5_api.py                     # Flask API server
├── modul_6_evaluation.py              # Metrik evaluasi
├── app.py                             # Gradio UI
└── requirements.txt                   # Dependencies
4. Data Schema
4.1 Input: corpus_master.csv
Sumber: Hasil scraping dari asisten/scraper_gmaps.py

#	Kolom	Tipe	Deskripsi	Contoh
1	Doc_ID	int	ID unik setiap ulasan	7990
2	Nama_Tempat	string	Nama tempat kemah	Sinolewah Camping Ground
3	Lokasi	string	Format "Kecamatan, Provinsi"	Sleman, DIY
4	Rating_Teks	float	Rating bintang dari pengulas	5.0
5	Teks_Mentah	string	Isi ulasan lengkap (masih kotor)	Tempat cocok untuk ngecamp...
6	Waktu	date	Estimasi tanggal ulasan dibuat	2025-10-01
Catatan: File ini memiliki banyak baris per tempat (satu baris = satu ulasan). Contoh: "Sinolewah Camping Ground" memiliki 186 baris.

4.2 Input: info_tempat.csv
Sumber: Data tambahan yang dikumpulkan terpisah (tidak tersedia untuk semua tempat)

#	Kolom	Tipe	Deskripsi	Contoh
1	Nama_Tempat	string	Nama tempat (key untuk join)	Kuncen Camp Ground
2	Photo_URL	string	URL gambar tempat	https://www.gemasulawesi.com/...
3	Gmaps_Link	string	Short link Google Maps	https://maps.app.goo.gl/Wpo7JY...
4	Waktu_Buka	string	Jam operasional (format tidak seragam)	Check In - Out : 12.00 - 11.00
5	Price_Items	JSON string	Daftar harga dalam format JSON	[{"item":"Tiket Masuk","harga":15000,...}]
6	Facilities	string	Fasilitas (pipe-separated)	Tempat Parkir | Toilet | Stop Kontak
Catatan Penting tentang Format Data:

Price_Items adalah JSON string, bukan teks biasa. Struktur per item:

json
{
  "item": "Tiket Masuk",
  "harga": 15000,
  "kategori": "biaya wajib" | "sewa pokok" | "sewa mewah" | "layanan"
}
Bisa bernilai [] (kosong) untuk tempat yang tidak memiliki data harga.

Facilities adalah string dengan separator pipe (|). Contoh: "Tempat Parkir | Toilet | Stop Kontak". Bisa kosong.

Waktu_Buka formatnya tidak seragam dan bisa berisi teks seperti "Cek Gmaps" atau kosong.

Tidak semua tempat memiliki data di file ini. Join dilakukan dengan LEFT JOIN pada Nama_Tempat.

4.3 Output Final: processed_places.csv
Hasil Modul 1 — Satu baris per tempat

#	Kolom	Tipe	Deskripsi
1	Nama_Tempat	string	Nama tempat kemah (unique key)
2	Profil_Teks	string	Gabungan semua ulasan bersih
3	Rating_Rata	float	Rata-rata rating (1.0 - 5.0)
4	Jumlah_Review	int	Total ulasan
5	Lokasi	string	Kecamatan, Provinsi
6	Photo_URL	string	URL foto (nullable)
7	Gmaps_Link	string	Link Google Maps (nullable)
8	Waktu_Buka	string	Jam operasional (nullable)
9	Price_Items	string	JSON string asli (nullable)
10	Harga_Minimum	float	Total biaya minimal (nullable)
11	Facilities	string	Teks asli pipe-separated (nullable)
12	Facilities_List	string	JSON list hasil parse (nullable)
5. Modul 1: Data Preparation
File: modul_1_preparation.py

Tujuan: Mengubah data mentah (banyak ulasan per tempat) menjadi satu profil bersih per tempat, digabung dengan metadata tambahan.

5.1 Input
File	Path
Data ulasan mentah	documents/corpus_master.csv
Metadata tempat	documents/info_tempat.csv
5.2 Processing Steps
Step	Nama	Deskripsi	Detail Teknis
1	Load Data	Muat kedua file CSV	pd.read_csv() untuk corpus_master.csv dan info_tempat.csv
2	Text Cleaning	Bersihkan Teks_Mentah	• Hapus karakter unicode rusak/aneh (termasuk emoji tidak terbaca)
• Hapus URL (http://..., https://...)
• Hapus mention (@username)
• Hapus hashtag (#hashtag)
• Hapus tanda baca berlebihan (!!! → !, ??? → ?)
• Case folding ke lowercase
• Normalisasi whitespace (multiple spasi/baris → satu spasi)
• Strip leading/trailing spaces
3	Group & Aggregate	Gabungkan ulasan per Nama_Tempat	• groupby("Nama_Tempat")
• Gabung semua teks bersih → Profil_Teks (join dengan spasi)
• Rating_Rata = mean(Rating_Teks)
• Jumlah_Review = count(Doc_ID)
• Ambil Lokasi pertama (diasumsikan sama per tempat)
4	Bobot Waktu (Opsional)	Beri bobot lebih pada ulasan baru	• Hitung selisih hari dari Waktu ke hari ini
• Bobot = exp(-decay_rate * days_diff)
• Terapkan saat penggabungan teks (opsional, bisa di-skip dulu)
5	Merge Metadata	Gabungkan dengan info tempat	• Left join pada Nama_Tempat
• Tempat tanpa info tambahan akan memiliki nilai NaN di kolom metadata
6	Parse Price_Items	Parse JSON dan hitung harga minimum	• Parse string JSON → list of dict
• Harga_Minimum = sum harga untuk kategori "biaya wajib" + "sewa pokok"
• Null jika Price_Items kosong ([])
7	Parse Facilities	Parse pipe-separated string	• Split string |
• Strip whitespace tiap item
• Simpan sebagai JSON list string
• Null jika kosong
8	Save Output	Simpan hasil ke CSV	• documents/processed/processed_places.csv
• Encoding: UTF-8
5.3 Output
File	Path
Tempat terproses	documents/processed/processed_places.csv
5.4 Validasi Output
Jumlah baris = jumlah unik Nama_Tempat di corpus_master.csv

Tidak ada Profil_Teks yang kosong

Rating_Rata antara 1.0 - 5.0

Jumlah_Review ≥ 1

6. Modul 2: Feature Engineering & Embedding
File: modul_2_embedding.py

Tujuan: Mengubah Profil_Teks setiap tempat menjadi vektor numerik (embedding) menggunakan Sentence-BERT.

6.1 Input
File	Path
Tempat terproses	documents/processed/processed_places.csv
6.2 Processing Steps
Step	Nama	Deskripsi	Detail Teknis
1	Load Data	Muat hasil Modul 1	pd.read_csv("documents/processed/processed_places.csv")
2	Load Model	Inisialisasi SBERT	Model: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
Dimensi output: 384
Mendukung 50+ bahasa termasuk Indonesia
3	Generate Embeddings	Encode semua Profil_Teks	• Batch processing untuk efisiensi
• model.encode(texts, batch_size=32, show_progress_bar=True)
• Output: numpy array (N_tempat × 384)
4	Save Embeddings	Simpan vektor	np.save("documents/processed/embeddings.npy", embeddings)
5	Save Metadata	Simpan metadata tanpa teks	Metadata + indeks (untuk mapping hasil FAISS nanti)
documents/processed/places_metadata.csv
6.3 Output
File	Path	Deskripsi
Vektor embedding	documents/processed/embeddings.npy	Array numpy (N_tempat, 384)
Metadata	documents/processed/places_metadata.csv	Semua kolom dari input kecuali Profil_Teks
6.4 Catatan Teknis
Model SBERT multilingual dipilih karena mendukung Bahasa Indonesia dengan baik

Dimensi 384 cukup untuk menangkap makna semantik tanpa terlalu berat secara komputasi

Normalisasi L2 dilakukan di Modul 3 sebelum indexing

7. Modul 3: Indexing & Candidate Generation
File: modul_3_indexing.py

Tujuan: Membangun indeks FAISS untuk pencarian kemiripan semantik yang cepat.

7.1 Input
File	Path
Vektor embedding	documents/processed/embeddings.npy
Metadata tempat	documents/processed/places_metadata.csv
7.2 Processing Steps
Step	Nama	Deskripsi	Detail Teknis
1	Load Data	Muat embeddings dan metadata	np.load() dan pd.read_csv()
2	Normalize Vectors	L2 normalization	Setiap vektor di-normalize agar panjang = 1
Ini membuat Inner Product = Cosine Similarity
3	Build Index	Buat indeks FAISS	faiss.IndexFlatIP(384) — Inner Product untuk cosine similarity
4	Add Vectors	Masukkan vektor ke indeks	index.add(normalized_embeddings)
5	Save Index	Simpan ke file	faiss.write_index(index, "documents/processed/faiss_index.bin")
6	Define Search Function	Fungsi untuk query	search(query_text, top_k=20) → list of dict
7.3 Search Function Detail
python
def search(query_text: str, top_k: int = 20) -> list:
    """
    Mencari tempat kemah berdasarkan query semantik.
    
    Args:
        query_text: Query natural language dari pengguna
        top_k: Jumlah hasil yang dikembalikan (default 20)
    
    Returns:
        List of dict dengan keys:
        - nama_tempat, similarity_score, lokasi, rating_rata,
          jumlah_review, photo_url, gmaps_link, price_items,
          harga_minimum, facilities
    """
    # 1. Encode query dengan SBERT
    # 2. Normalize L2
    # 3. FAISS index.search(query_vector, top_k)
    # 4. Ambil metadata dari places_metadata.csv
    # 5. Return hasil
7.3 Query Flow Diagram
text
Query: "camping keluarga dengan fasilitas lengkap dan murah"
    │
    ▼
┌─────────────────────────────────────────┐
│ 1. SBERT ENCODE                         │
│    query → query_vector (384 dim)       │
│    → L2 Normalize                       │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│ 2. FAISS SEARCH                         │
│    index.search(query_vector, k=20)     │
│    → (distances, indices)               │
│    distances = cosine similarity score  │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│ 3. MAP TO METADATA                      │
│    indices → places_metadata.csv rows   │
│    → 20 tempat + similarity scores      │
└──────────────────┬──────────────────────┘
                   │
                   ▼
           Hasil untuk Modul 4 (Reranking)
7.4 Output
File	Path
FAISS Index	documents/processed/faiss_index.bin
8. Modul 4: Ranking (Reranking)
File: modul_4_ranking.py

Tujuan: Mengurutkan ulang hasil candidate generation dari FAISS menggunakan sinyal metadata (rating, popularitas, harga) untuk hasil yang lebih personal.

8.1 Input
Top-K hasil dari Modul 3 (list of dict dengan similarity_score dan metadata)

Query asli (untuk deteksi intent)

8.2 Scoring Formula
text
Final Score = (W_sim × sim_score) 
            + (W_rating × norm_rating) 
            + (W_popularity × norm_review_count) 
            + (W_price × price_match)
Sinyal	Bobot	Cara Normalisasi	Justifikasi
Semantic Similarity	0.50	Sudah 0-1 (cosine)	Sinyal utama — kemiripan makna dengan query
Rating_Rata	0.25	(rating - 1) / 4 → 0-1	Kepercayaan dan kepuasan pengguna
Jumlah_Review	0.15	Min-max scaling	Popularitas dan kredibilitas tempat
Price Match	0.10	1 jika relevan, 0 jika tidak	Kesesuaian budget (jika query menyebut harga)
8.3 Intent Detection untuk Price Match
Keyword dalam Query	Perilaku Reranking
"murah", "hemat", "budget", "ekonomis", "terjangkau"	Tempat dengan Harga_Minimum terendah dapat skor lebih tinggi
"lengkap", "full", "komplit"	Tempat dengan Price_Items lebih banyak item dapat skor lebih tinggi
"gratis", "free"	Tempat dengan Harga_Minimum = 0 atau tanpa "biaya wajib" diprioritaskan
Tidak ada keyword harga	Semua tempat dapat price_match = 1.0 (netral)
8.4 Processing Steps
Step	Deskripsi
1	Terima hasil FAISS search (20 kandidat) + query asli
2	Deteksi intent dari query (cek keyword harga)
3	Normalisasi semua sinyal ke skala 0-1
4	Hitung final_score untuk setiap kandidat
5	Urutkan ulang berdasarkan final_score (descending)
6	Return top-10 hasil
8.5 Output Format
json
{
  "query": "camping keluarga dengan fasilitas lengkap dan murah",
  "results": [
    {
      "rank": 1,
      "nama_tempat": "Kuncen Camp Ground",
      "lokasi": "Semarang, Jawa Tengah",
      "rating_rata": 4.7,
      "jumlah_review": 245,
      "similarity_score": 0.82,
      "final_score": 0.91,
      "harga_minimum": 35000,
      "price_items": [{"item": "Tiket Masuk", "harga": 15000}, ...],
      "facilities": ["Tempat Parkir", "Toilet", "Stop Kontak"],
      "photo_url": "https://...",
      "gmaps_link": "https://..."
    },
    // ... 9 hasil lainnya
  ]
}
9. Modul 5: API & Web Interface
File: modul_5_api.py (Flask API) dan app.py (Gradio UI)

Tujuan: Menyediakan endpoint pencarian dan antarmuka pengguna yang modern.

9.1 Backend API (Flask)
Endpoint	Method	Deskripsi	Request Body	Response
/api/search	POST	Cari tempat kemah	{"query": "...", "top_k": 10}	JSON hasil reranking
/api/place/<nama>	GET	Detail satu tempat	—	JSON detail tempat
/api/health	GET	Health check	—	{"status": "ok"}
9.2 Frontend (Gradio)
Alasan memilih Gradio:

Tampilan lebih modern dan variatif dibanding Streamlit

Mendukung tema kustom dan komponen interaktif

Integrasi mudah dengan backend Flask

Cocok untuk demonstrasi sistem AI/ML

Komponen	Tipe Gradio	Deskripsi
Search Input	gr.Textbox	Input query natural language, placeholder: "Cari tempat camping yang..."
Top-K Slider	gr.Slider	Pilih jumlah hasil (5-20, default 10)
Filter Lokasi	gr.Dropdown	Filter berdasarkan provinsi/kecamatan (opsional)
Search Button	gr.Button	Tombol "Cari"
Hasil	gr.HTML atau gr.Gallery	Card untuk setiap hasil (foto, nama, rating, lokasi, harga, fasilitas, link)
9.3 Tampilan Hasil (Mockup Card)
text
┌─────────────────────────────────────────────────────┐
│  ┌──────────┐                                        │
│  │          │  🌟 4.7  |  245 ulasan                 │
│  │  FOTO    │  📍 Semarang, Jawa Tengah              │
│  │  TEMPAT  │  💰 Mulai Rp 35.000                    │
│  │          │  🏕️ Tempat Parkir | Toilet | Stop Kontak│
│  └──────────┘  🔗 Buka di Google Maps               │
│                                                     │
│  "Tempatnya asik banget buat camping keluarga,       │
│   fasilitasnya lengkap..."                           │
└─────────────────────────────────────────────────────┘
10. Modul 6: Evaluation
File: modul_6_evaluation.py

Tujuan: Mengukur performa sistem rekomendasi secara kuantitatif.

10.1 Metrik Evaluasi
Metrik	Rumus	Deskripsi	Target
Recall@K	(Jumlah tempat relevan di top-K) / (Total tempat relevan)	Seberapa lengkap sistem mengambil tempat yang seharusnya muncul	≥ 0.80
MRR	(1/N) × Σ(1/rank_i)	Rata-rata posisi hasil relevan pertama (1/rank)	≥ 0.60
NDCG@K	DCG@K / IDCG@K	Kualitas ranking (posisi dan relevansi)	≥ 0.70
10.2 Dataset Uji (Ground Truth)
Siapkan 15-20 query uji yang mewakili berbagai intent pengguna:

#	Query Uji	Intent	Tempat Relevan (Ground Truth)
1	"camping sejuk dengan pemandangan bagus"	Suasana	Telaga Dringo, Bukit Bintang
2	"tempat kemah murah untuk pemula"	Budget	Kuncen Camp Ground
3	"camping ground fasilitas lengkap untuk rombongan"	Fasilitas	Sinolewah Camping Ground
4	"tempat camping yang tenang buat healing"	Suasana	...
5	"camping dengan api unggun dan tenda sewa"	Aktivitas	...
...	...	...	...
10.3 Prosedur Evaluasi
Jalankan setiap query uji melalui sistem

Catat peringkat tempat relevan di hasil

Hitung Recall@5, Recall@10, MRR, NDCG@10

Laporkan rata-rata semua metrik

11. Tech Stack
Komponen	Teknologi	Versi	Alasan Pemilihan
Scraping	Playwright (Python)	≥1.40	Menangani JS rendering, anti-deteksi
Data Processing	Pandas	≥2.0	Standar manipulasi data di Python
Embedding	Sentence-BERT	≥2.2	Model paraphrase-multilingual-MiniLM-L12-v2 — ringan, mendukung Bahasa Indonesia
Vector Search	FAISS	≥1.7	Cepat, open-source oleh Meta, produksi-siap
Backend	Flask	≥3.0	Ringan, mudah, cukup untuk API REST
Frontend	Gradio	≥4.0	Modern, variatif, cocok untuk demo AI/ML
Language	Python	≥3.10	Ekosistem data science dan ML terlengkap
12. Development Milestones
Minggu	Modul	Target	Deliverable
1	Modul 1	Data Preparation	processed_places.csv berhasil dibuat dan tervalidasi
2	Modul 2	Embedding	embeddings.npy dan places_metadata.csv siap
3	Modul 3	Indexing & Search	faiss_index.bin siap, fungsi search() berfungsi
4	Modul 4	Reranking	Hasil reranking lebih baik dari FAISS-only
5	Modul 5	API & UI	Flask API + Gradio UI berfungsi end-to-end
6	Modul 6	Evaluasi & Dokumentasi	Metrik evaluasi terhitung, laporan selesai
13. Referensi Akademik
Raza, S., Rahman, M., et al. (2026). A comprehensive review of recommender systems: Transitioning from theory to practice. Computer Science Review, 59, 100849. https://doi.org/10.1016/j.cosrev.2025.100849

Relevansi dengan Proyek:
Paper ini digunakan sebagai acuan utama pipeline karena:

Membahas review-based recommender systems secara eksplisit sebagai cabang sistem rekomendasi modern

Membahas aspect-based recommender systems yang relevan untuk ekstraksi informasi dari ulasan

Menyediakan kerangka implementasi end-to-end dari data acquisition hingga deployment

Menyebut model-model seperti AARM dan NARRE sebagai fondasi review-aware recommendation

Pipeline dalam proyek ini merupakan adaptasi dari kerangka yang dijelaskan dalam paper tersebut, disesuaikan untuk domain rekomendasi tempat kemah berbasis ulasan Google Maps.

14. Lampiran
A. Catatan Kode Scraping (asisten/scraper_gmaps.py)
Kode scraping sudah berfungsi dengan baik dan memiliki fitur-fitur berikut:

Anti-deteksi: User agent palsu dan argumen --disable-blink-features

Filter respons pemilik: Mendeteksi dan mengecualikan respons dari pengelola tempat

Deduplikasi: Mencegah ulasan ganda tersimpan

Auto-save: Menyimpan data secara berkala setiap 100 ulasan

Deteksi kebuntuan: Berhenti jika tidak ada ulasan baru setelah 25 kali scroll

Saran perbaikan untuk pengembangan selanjutnya (di luar lingkup proyek saat ini):

Tambahkan parsing Waktu relatif ("2 minggu lalu" → tanggal estimasi) — saat ini sudah berfungsi

Kurangi agresivitas filter pemilik (simpan ulasan yang difilter di file terpisah untuk audit manual)

Tambahkan exponential backoff untuk menghindari rate-limiting

B. Dependencies (requirements.txt)
text
pandas>=2.0
numpy>=1.24
sentence-transformers>=2.2
faiss-cpu>=1.7
flask>=3.0
gradio>=4.0
playwright>=1.40
scikit-learn>=1.3
Dokumen ini disetujui dan siap digunakan sebagai panduan implementasi.