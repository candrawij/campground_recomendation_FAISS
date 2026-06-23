from flask import Flask, request, jsonify
from modul_3_indexing import CamperRecommender
from modul_4_ranking import Reranker
import pandas as pd

app = Flask(__name__)

# Load recommender global
print("Memuat sistem rekomendasi FAISS dan SBERT...")
recommender = CamperRecommender()
recommender.load_resources()
reranker = Reranker()
print("Backend API Siap!")

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    if not data:
        return jsonify({"error": "Request body harus JSON"}), 400
        
    query = data.get('query', '')
    top_k = data.get('top_k', 10)
    
    if not query:
        return jsonify({"error": "Query tidak boleh kosong"}), 400
        
    # Ambil candidate dari FAISS
    # Kita ambil lebih banyak dari top_k (misal 2-3x lipat) agar Reranker memiliki lebih banyak kandidat untuk diproses
    candidates = recommender.search(query, top_k=top_k * 3)
    
    # Reranking
    results = reranker.rerank(query, candidates, top_k=top_k)
    
    return jsonify(results)

@app.route('/api/place/<path:nama>', methods=['GET'])
def get_place(nama):
    # Cari di metadata
    matches = recommender.metadata[recommender.metadata['Nama_Tempat'].str.lower() == nama.lower()]
    if matches.empty:
        return jsonify({"error": "Tempat tidak ditemukan"}), 404
        
    place = matches.iloc[0].to_dict()
    # handle nan agar JSON valid
    for k, v in place.items():
        if pd.isna(v):
            place[k] = None
            
    return jsonify(place)

if __name__ == '__main__':
    # Jalankan flask di port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
