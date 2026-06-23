import json
import numpy as np
import pandas as pd

class Reranker:
    def __init__(self, w_sim=0.50, w_rating=0.25, w_popularity=0.15, w_price=0.10):
        self.w_sim = w_sim
        self.w_rating = w_rating
        self.w_popularity = w_popularity
        self.w_price = w_price
        
    def _detect_intent_and_score_price(self, query: str, candidates: list) -> list:
        query_lower = query.lower()
        
        # Check keywords
        k_murah = ["murah", "hemat", "budget", "ekonomis", "terjangkau"]
        k_lengkap = ["lengkap", "full", "komplit"]
        k_gratis = ["gratis", "free"]
        
        has_murah = any(k in query_lower for k in k_murah)
        has_lengkap = any(k in query_lower for k in k_lengkap)
        has_gratis = any(k in query_lower for k in k_gratis)
        
        price_scores = []
        
        if has_gratis:
            for c in candidates:
                # Harga minimum 0 atau tidak ada biaya
                harga = c.get('harga_minimum')
                if harga == 0 or harga is None:
                    price_scores.append(1.0)
                else:
                    price_scores.append(0.0)
                    
        elif has_murah:
            hargas = [c.get('harga_minimum') for c in candidates if c.get('harga_minimum') is not None]
            min_h = min(hargas) if hargas else 0
            max_h = max(hargas) if hargas else 0
            
            for c in candidates:
                harga = c.get('harga_minimum')
                if harga is None:
                    price_scores.append(0.5) # Netral untuk yang tidak ada harga
                else:
                    if max_h == min_h:
                        price_scores.append(1.0)
                    else:
                        # Terendah dapat 1.0, tertinggi dapat 0.0
                        score = 1.0 - ((harga - min_h) / (max_h - min_h))
                        price_scores.append(score)
                        
        elif has_lengkap:
            # Hitung jumlah item di price_items (asumsi item JSON atau string list fasilitas)
            # Karena PRD bilang "Price_Items lebih banyak item dapat skor lebih tinggi"
            # Kita parse list dari facilities aja atau dari price_items
            def get_item_count(c):
                f = c.get('facilities')
                if f and f != 'nan':
                    try:
                        return len(json.loads(f)) if isinstance(f, str) and f.startswith('[') else len(str(f).split('|'))
                    except:
                        pass
                return 0
                
            counts = [get_item_count(c) for c in candidates]
            max_c = max(counts) if counts else 0
            min_c = min(counts) if counts else 0
            
            for count in counts:
                if max_c == min_c:
                    price_scores.append(1.0)
                else:
                    price_scores.append((count - min_c) / (max_c - min_c))
                    
        else:
            # Tidak ada keyword harga
            price_scores = [1.0] * len(candidates)
            
        return price_scores

    def rerank(self, query: str, candidates: list, top_k: int = 10) -> dict:
        if not candidates:
            return {"query": query, "results": []}
            
        # 1. Normalisasi Sinyal
        # Rating (1-5) ke (0-1)
        # Jika NaN/0, kita beri nilai tengah misal 3 -> norm 0.5
        norm_ratings = []
        for c in candidates:
            r = c.get('rating_rata')
            if r is None or np.isnan(r) or r == 0:
                norm_ratings.append(0.5)
            else:
                norm_ratings.append((r - 1) / 4)
                
        # Popularitas (Jumlah_Review) min-max scaling
        reviews = [c.get('jumlah_review') for c in candidates]
        reviews = [0 if (r is None or np.isnan(r)) else r for r in reviews]
        min_rev = min(reviews) if reviews else 0
        max_rev = max(reviews) if reviews else 0
        
        norm_reviews = []
        for r in reviews:
            if max_rev == min_rev:
                norm_reviews.append(1.0 if max_rev > 0 else 0.0)
            else:
                norm_reviews.append((r - min_rev) / (max_rev - min_rev))
                
        # Deteksi Intent untuk price_match
        price_matches = self._detect_intent_and_score_price(query, candidates)
        
        # 2. Hitung Final Score
        for i, c in enumerate(candidates):
            sim_score = c.get('similarity_score', 0)
            
            # Jika sim_score sudah cosine similarity (bisa negatif tapi dari FAISS/SBERT biasa > 0)
            # Kita cap di 0-1
            sim_score = max(0.0, min(1.0, sim_score))
            
            final_score = (self.w_sim * sim_score) + \
                          (self.w_rating * norm_ratings[i]) + \
                          (self.w_popularity * norm_reviews[i]) + \
                          (self.w_price * price_matches[i])
                          
            c['final_score'] = round(final_score, 4)
            
        # 3. Urutkan berdasarkan final_score descending
        ranked_candidates = sorted(candidates, key=lambda x: x['final_score'], reverse=True)
        
        # 4. Ambil top-k dan tambahkan urutan
        final_results = []
        for rank, c in enumerate(ranked_candidates[:top_k], 1):
            c_copy = c.copy()
            c_copy['rank'] = rank
            
            # Format price items untuk JSON output (hindari string JSON ganda)
            pi = c_copy.get('price_items')
            if isinstance(pi, str) and pi.startswith('['):
                try:
                    c_copy['price_items'] = json.loads(pi)
                except:
                    pass
            
            # Format facilities
            fac = c_copy.get('facilities')
            if isinstance(fac, str) and fac != 'nan':
                if fac.startswith('['):
                    try:
                        c_copy['facilities'] = json.loads(fac)
                    except:
                        c_copy['facilities'] = [f.strip() for f in fac.split('|')]
                else:
                    c_copy['facilities'] = [f.strip() for f in fac.split('|')]
            elif fac == 'nan' or pd.isna(fac):
                c_copy['facilities'] = []
                
            final_results.append(c_copy)
            
        return {
            "query": query,
            "results": final_results
        }

def test():
    # Memerlukan modul 3 untuk tes nyata, ini mock data
    query = "camping keluarga dengan fasilitas lengkap dan murah"
    candidates = [
        {
            "nama_tempat": "Tempat A",
            "similarity_score": 0.85,
            "rating_rata": 4.5,
            "jumlah_review": 120,
            "harga_minimum": 50000,
            "facilities": "Toilet | Mushola"
        },
        {
            "nama_tempat": "Tempat B",
            "similarity_score": 0.80,
            "rating_rata": 4.8,
            "jumlah_review": 300,
            "harga_minimum": 20000,
            "facilities": "Toilet | Mushola | Wifi | Kolam Renang"
        }
    ]
    
    reranker = Reranker()
    res = reranker.rerank(query, candidates)
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    test()
