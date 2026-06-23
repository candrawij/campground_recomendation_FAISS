import numpy as np
import pandas as pd
import faiss
import os
from sentence_transformers import SentenceTransformer

class CamperRecommender:
    def __init__(self, model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'):
        self.model_name = model_name
        self.model = None
        self.index = None
        self.metadata = None
        self.embeddings = None

    def load_resources(self, embedding_path='documents/processed/embeddings.npy',
                       metadata_path='documents/processed/places_metadata.csv',
                       index_path='documents/processed/faiss_index.bin'):
        print("Memuat metadata...")
        self.metadata = pd.read_csv(metadata_path)
        
        print("Memuat embeddings...")
        self.embeddings = np.load(embedding_path)
        
        if os.path.exists(index_path):
            print("Memuat FAISS index yang sudah ada...")
            self.index = faiss.read_index(index_path)
        else:
            print("FAISS index tidak ditemukan. Silakan jalankan build_index() terlebih dahulu.")
            
        print(f"Memuat model SBERT: {self.model_name}...")
        self.model = SentenceTransformer(self.model_name)

    def build_index(self, embedding_path='documents/processed/embeddings.npy', 
                    output_path='documents/processed/faiss_index.bin'):
        print("Memulai pembuatan FAISS Index...")
        
        # 1. Load Data
        embeddings = np.load(embedding_path)
        print(f"Dimensi embedding: {embeddings.shape}")
        
        # 2. Normalize Vectors (L2 Normalization)
        print("Melakukan L2 normalization pada vektor...")
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        normalized_embeddings = embeddings / norms
        
        # 3. Build Index
        d = normalized_embeddings.shape[1] # Dimensi (384)
        print(f"Membuat FAISS IndexFlatIP dengan dimensi {d}...")
        self.index = faiss.IndexFlatIP(d)
        
        # 4. Add Vectors
        print("Menambahkan vektor ke dalam index...")
        self.index.add(normalized_embeddings.astype('float32'))
        
        # 5. Save Index
        print(f"Menyimpan index ke {output_path}...")
        faiss.write_index(self.index, output_path)
        print("Index berhasil dibuat dan disimpan!")

    def search(self, query_text: str, top_k: int = 20) -> list:
        """
        Mencari tempat kemah berdasarkan query semantik.
        """
        if self.model is None or self.index is None or self.metadata is None:
            raise ValueError("Model, index, atau metadata belum dimuat. Panggil load_resources() terlebih dahulu.")
            
        # 1. Encode query dengan SBERT
        query_vector = self.model.encode([query_text])[0]
        
        # 2. Normalize L2
        query_norm = np.linalg.norm(query_vector)
        if query_norm > 0:
            query_vector = query_vector / query_norm
            
        # Reshape untuk FAISS (n_queries, d)
        query_vector = np.array([query_vector]).astype('float32')
        
        # 3. FAISS Search
        distances, indices = self.index.search(query_vector, top_k)
        
        # 4. Ambil metadata dan susun hasil
        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1: # FAISS mengembalikan -1 jika hasil kurang dari top_k
                continue
                
            sim_score = float(distances[0][i])
            row = self.metadata.iloc[idx]
            
            # Format output sesuai PRD
            result = {
                'nama_tempat': row.get('Nama_Tempat', ''),
                'similarity_score': sim_score,
                'lokasi': row.get('Lokasi', ''),
                'rating_rata': float(row.get('Rating_Rata', 0)) if not pd.isna(row.get('Rating_Rata')) else 0.0,
                'jumlah_review': int(row.get('Jumlah_Review', 0)) if not pd.isna(row.get('Jumlah_Review')) else 0,
                'photo_url': row.get('Photo_URL', ''),
                'gmaps_link': row.get('Gmaps_Link', ''),
                'price_items': row.get('Price_Items', ''),
                'harga_minimum': float(row.get('Harga_Minimum', 0)) if not pd.isna(row.get('Harga_Minimum')) else None,
                'facilities': row.get('Facilities', '')
            }
            results.append(result)
            
        return results

def main():
    recommender = CamperRecommender()
    
    # Buat index
    recommender.build_index()
    
    # Tes search function (opsional, untuk memastikan berjalan baik)
    print("\n--- Testing Search Function ---")
    recommender.load_resources()
    
    test_query = "camping keluarga dengan fasilitas lengkap dan murah"
    print(f"Query: '{test_query}'")
    
    try:
        results = recommender.search(test_query, top_k=3)
        print("\nTop 3 Hasil:")
        for i, res in enumerate(results, 1):
            print(f"{i}. {res['nama_tempat']} (Score: {res['similarity_score']:.4f})")
            print(f"   Lokasi: {res['lokasi']} | Rating: {res['rating_rata']}")
            print(f"   Fasilitas: {res['facilities']}")
            print("-" * 30)
    except Exception as e:
        print(f"Terjadi error saat testing search: {e}")

if __name__ == "__main__":
    main()
