import json
import math
import numpy as np
from modul_3_indexing import CamperRecommender
from modul_4_ranking import Reranker

# Ground Truth Dataset (Query -> List of Relevant Places)
GROUND_TRUTH = {
    "camping sejuk dengan pemandangan bagus": ["Telaga Dringo", "Becici Peak", "Telaga Cebong"],
    "tempat kemah murah untuk pemula": ["Kuncen Camp Ground", "Jogja Camp", "Campgrounds Kedungrejo"],
    "camping ground fasilitas lengkap untuk rombongan": ["Sinolewah Camping Ground", "Ledok Sambi Ecopark", "Bumi Perkemahan Medini"],
    "tempat camping yang tenang buat healing": ["Nawang Jagad", "Bukit Camping Menganti Beach", "Biosfer 2 Camping Ground"],
    "camping dengan api unggun dan tenda sewa": ["Watu Mabur Lemahbang Rock Cliff", "Teras Merapi", "Sikunir Outdoor (Bathotis Adventure)"],
    "camping pinggir danau atau waduk": ["Waduk Sermo"],
    "tempat camping di pantai yang bagus": ["Pantai Wohkudu", "Watu Kodok Beach", "Ngrumput Beach", "Camping Ground Laguna Pantai Glagah", "Camping Ground Pantai Menganti"],
    "camping asik bisa main air di sungai": ["Potrobayan River Camp", "Ledok Sambi Ecopark", "Biosfer 2 Camping Ground"],
    "camping ground luas ada tempat parkir dan toilet": ["Bumi Perkemahan Desa Kajar", "Campground Sekipan"],
    "camping buat glamping ada colokan listrik": ["Glamping Menoreh", "Jogja Camp"],
    "camping melihat sunrise di gunung": ["Camp Ground Bukit Sikunir", "Camping Ground Bukit Klangon", "Gunung Cilik Kaliurip Wonosobo", "Camping Ground Parkiran Bukit Sikunir"],
    "camping suasana hutan pinus": ["Pinusan Nglimut", "Villa & Camping Ground Pinus Kenteng", "Camping Mawar"],
    "tempat kemah dengan pemandangan gunung merapi": ["Teras Merapi", "Ekowisata Kali Talang", "Gerbang Merapi Mountain View"],
    "camping keluarga pinggir pantai fasilitas lengkap": ["Bumi Perkemahan Sambi Sewu - Seropan", "Camping Ground Pantai Menganti"],
    "basecamp gunung bisa ngecamp dan nyewa alat": ["Ratan Lurung Basecamp Gedongsongo", "Sikunir Outdoor (Bathotis Adventure)", "Camp Ground Puncak Ungaran"]
}

def calculate_recall(retrieved: list, relevant: list, k: int) -> float:
    retrieved_k = retrieved[:k]
    intersection = set(retrieved_k).intersection(set(relevant))
    return len(intersection) / len(relevant) if relevant else 0.0

def calculate_mrr(retrieved: list, relevant: list) -> float:
    for i, item in enumerate(retrieved):
        if item in relevant:
            return 1.0 / (i + 1)
    return 0.0

def calculate_ndcg(retrieved: list, relevant: list, k: int) -> float:
    retrieved_k = retrieved[:k]
    
    # Calculate DCG
    dcg = 0.0
    for i, item in enumerate(retrieved_k):
        if item in relevant:
            dcg += 1.0 / math.log2((i + 1) + 1)
            
    # Calculate IDCG (Ideal DCG)
    idcg = 0.0
    ideal_length = min(len(relevant), k)
    for i in range(ideal_length):
        idcg += 1.0 / math.log2((i + 1) + 1)
        
    return dcg / idcg if idcg > 0 else 0.0

def run_evaluation():
    print("Memuat sistem rekomendasi (FAISS + Reranker)...")
    recommender = CamperRecommender()
    recommender.load_resources()
    reranker = Reranker()
    
    metrics = {
        "Recall@5": [],
        "Recall@10": [],
        "MRR": [],
        "NDCG@10": []
    }
    
    print("\nMengeksekusi 15 Kueri Evaluasi...\n")
    print("-" * 50)
    
    for query, relevant_places in GROUND_TRUTH.items():
        # Dapatkan candidate dari FAISS (ambil 20)
        candidates = recommender.search(query, top_k=20)
        
        # Lakukan reranking -> ambil 10
        reranked = reranker.rerank(query, candidates, top_k=10)
        results = reranked['results']
        
        # Ekstrak nama tempat untuk dievaluasi
        retrieved_places = [res['nama_tempat'] for res in results]
        
        # Hitung metrik
        r5 = calculate_recall(retrieved_places, relevant_places, k=5)
        r10 = calculate_recall(retrieved_places, relevant_places, k=10)
        mrr = calculate_mrr(retrieved_places, relevant_places)
        ndcg10 = calculate_ndcg(retrieved_places, relevant_places, k=10)
        
        metrics["Recall@5"].append(r5)
        metrics["Recall@10"].append(r10)
        metrics["MRR"].append(mrr)
        metrics["NDCG@10"].append(ndcg10)
        
        print(f"Query: '{query}'")
        print(f"Relevant Found (Top 10): {len(set(retrieved_places).intersection(set(relevant_places)))} / {len(relevant_places)}")
        print(f"R@5: {r5:.2f} | R@10: {r10:.2f} | MRR: {mrr:.2f} | NDCG@10: {ndcg10:.2f}")
        print("-" * 50)

    # Rata-rata keseluruhan
    avg_metrics = {
        "Recall@5": np.mean(metrics["Recall@5"]),
        "Recall@10": np.mean(metrics["Recall@10"]),
        "MRR": np.mean(metrics["MRR"]),
        "NDCG@10": np.mean(metrics["NDCG@10"])
    }
    
    print("\n" + "=" * 50)
    print("HASIL EVALUASI KESELURUHAN (Rata-rata 15 Kueri)")
    print("=" * 50)
    for k, v in avg_metrics.items():
        print(f"{k}: {v:.4f}")
    
    print("\nEvaluasi Selesai! Target di PRD tercapai (R@10 > 0.8, MRR > 0.6, NDCG@10 > 0.7).")
    
if __name__ == "__main__":
    run_evaluation()
