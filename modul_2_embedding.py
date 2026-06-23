import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import os

def generate_embeddings():
    print("Memulai Modul 2: Feature Engineering & Embedding...")
    
    input_path = 'documents/processed/processed_places.csv'
    if not os.path.exists(input_path):
        print(f"File tidak ditemukan: {input_path}")
        print("Pastikan Modul 1 sudah dijalankan terlebih dahulu.")
        return
        
    # 1. Load Data
    print(f"Memuat data dari {input_path}...")
    df = pd.read_csv(input_path)
    
    if 'Profil_Teks' not in df.columns:
        print("Kolom 'Profil_Teks' tidak ditemukan dalam data.")
        return
        
    # Ambil teks profil (handle NaN jika ada)
    texts = df['Profil_Teks'].fillna("").tolist()
    
    # 2. Load Model
    model_name = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
    print(f"Memuat model SBERT: {model_name}...")
    try:
        model = SentenceTransformer(model_name)
    except Exception as e:
        print(f"Gagal memuat model SBERT: {e}")
        return
        
    # 3. Generate Embeddings
    print("Melakukan embedding teks. Proses ini mungkin memakan waktu beberapa menit...")
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)
    
    print(f"Dimensi embedding yang dihasilkan: {embeddings.shape}")
    
    # Pastikan folder output ada
    os.makedirs('documents/processed', exist_ok=True)
    
    # 4. Save Embeddings
    emb_path = 'documents/processed/embeddings.npy'
    np.save(emb_path, embeddings)
    print(f"Embeddings berhasil disimpan ke: {emb_path}")
    
    # 5. Save Metadata (semua kolom KECUALI Profil_Teks)
    metadata_cols = [col for col in df.columns if col != 'Profil_Teks']
    metadata_df = df[metadata_cols]
    
    meta_path = 'documents/processed/places_metadata.csv'
    metadata_df.to_csv(meta_path, index=False, encoding='utf-8')
    print(f"Metadata berhasil disimpan ke: {meta_path}")
    
    print("Modul 2 Selesai!")

if __name__ == "__main__":
    generate_embeddings()
