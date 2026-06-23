import pandas as pd
import numpy as np
import re
import json
import os

def clean_text(text):
    if not isinstance(text, str):
        return ""
    
    # Hapus URL
    text = re.sub(r'http[s]?://\S+', '', text)
    
    # Hapus mention
    text = re.sub(r'@\w+', '', text)
    
    # Hapus hashtag
    text = re.sub(r'#\w+', '', text)
    
    # Hapus karakter unicode rusak/aneh (pertahankan huruf, angka, spasi, dan tanda baca dasar)
    # Ini juga akan menghapus emoji
    text = re.sub(r'[^\w\s\.,!\?\'"-]', ' ', text)
    
    # Hapus tanda baca berlebihan
    text = re.sub(r'!+', '!', text)
    text = re.sub(r'\?+', '?', text)
    text = re.sub(r'\.+', '.', text)
    
    # Case folding ke lowercase
    text = text.lower()
    
    # Normalisasi whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing spaces
    return text.strip()

def process_data():
    print("Memulai Modul 1: Data Preparation...")
    
    # Pastikan folder output ada
    os.makedirs('documents/processed', exist_ok=True)
    
    # 1. Load Data
    try:
        corpus_df = pd.read_csv('documents/corpus_master.csv')
        info_df = pd.read_csv('documents/info_tempat.csv')
    except Exception as e:
        print(f"Error loading files: {e}")
        return

    # 2. Text Cleaning
    print("Membersihkan teks...")
    corpus_df['Teks_Bersih'] = corpus_df['Teks_Mentah'].apply(clean_text)
    
    # 3. Group & Aggregate
    print("Menggabungkan data per tempat...")
    # Pastikan kolom Doc_ID, Rating_Teks ada dan tidak null
    # Kalau null, kita drop atau isi
    
    grouped = corpus_df.groupby('Nama_Tempat').agg(
        Profil_Teks=('Teks_Bersih', lambda x: ' '.join(x[x != ""])),
        Rating_Rata=('Rating', 'mean'),
        Jumlah_Review=('Doc_ID', 'count'),
        Lokasi=('Lokasi', 'first')
    ).reset_index()
    
    # 5. Merge Metadata
    print("Menggabungkan dengan metadata...")
    merged_df = pd.merge(grouped, info_df, on='Nama_Tempat', how='left')
    
    # 6. Parse Price_Items
    print("Memproses harga dan fasilitas...")
    def parse_price(row):
        price_str = row['Price_Items']
        if pd.isna(price_str) or not isinstance(price_str, str):
            return np.nan
        try:
            items = json.loads(price_str)
            if not items:
                return np.nan
            min_price = sum(item.get('harga', 0) for item in items if item.get('kategori') in ['biaya wajib', 'sewa pokok'])
            return min_price
        except json.JSONDecodeError:
            return np.nan

    merged_df['Harga_Minimum'] = merged_df.apply(parse_price, axis=1)
    
    # 7. Parse Facilities
    def parse_facilities(row):
        fac_str = row['Facilities']
        if pd.isna(fac_str) or not isinstance(fac_str, str):
            return np.nan
        facilities = [f.strip() for f in fac_str.split('|') if f.strip()]
        if not facilities:
            return np.nan
        return json.dumps(facilities)

    merged_df['Facilities_List'] = merged_df.apply(parse_facilities, axis=1)
    
    # Susun kolom sesuai PRD
    columns_order = [
        'Nama_Tempat', 'Profil_Teks', 'Rating_Rata', 'Jumlah_Review', 'Lokasi',
        'Photo_URL', 'Gmaps_Link', 'Waktu_Buka', 'Price_Items', 'Harga_Minimum',
        'Facilities', 'Facilities_List'
    ]
    
    # Handle missing columns if info_tempat.csv doesn't have some
    for col in columns_order:
        if col not in merged_df.columns:
            merged_df[col] = np.nan
            
    final_df = merged_df[columns_order]
    
    # 8. Save Output
    output_path = 'documents/processed/processed_places.csv'
    final_df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Selesai! Data disimpan ke {output_path}")
    print(f"Jumlah tempat terproses: {len(final_df)}")

if __name__ == "__main__":
    process_data()
