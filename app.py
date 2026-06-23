import gradio as gr
import requests

API_URL = "http://127.0.0.1:5000"

def format_price(price):
    if price is None or price == 0:
        return "Gratis / Hubungi Pengelola"
    return f"Rp {int(price):,}".replace(",", ".")

def generate_html_card(place):
    foto = place.get('photo_url')
    if not foto or str(foto).lower() == 'nan':
        foto = "https://images.unsplash.com/photo-1504280390225-b8252277d3f8?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80" # Placeholder camping image
        
    nama = place.get('nama_tempat', 'Unknown')
    rating = place.get('rating_rata', 0.0)
    reviews = place.get('jumlah_review', 0)
    lokasi = place.get('lokasi', 'Unknown')
    harga = format_price(place.get('harga_minimum'))
    link = place.get('gmaps_link', '#')
    
    fasilitas = place.get('facilities', [])
    if isinstance(fasilitas, list) and fasilitas:
        fas_str = " | ".join(fasilitas[:5]) + ("..." if len(fasilitas) > 5 else "")
    elif isinstance(fasilitas, str) and fasilitas.lower() != 'nan' and fasilitas.strip():
        fas_str = fasilitas
    else:
        fas_str = "Informasi fasilitas tidak tersedia"
        
    html = f"""
    <div style="border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); background-color: white; transition: transform 0.2s; cursor: pointer;" onmouseover="this.style.transform='translateY(-5px)'" onmouseout="this.style.transform='translateY(0)'">
        <div style="height: 200px; overflow: hidden; position: relative;">
            <img src="{foto}" style="width: 100%; height: 100%; object-fit: cover;" alt="{nama}">
            <div style="position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.7); color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 0.9em;">
                ⭐ {rating:.1f}
            </div>
        </div>
        <div style="padding: 20px;">
            <h3 style="margin-top: 0; color: #1e293b; font-size: 1.25em; font-weight: 700;">{nama}</h3>
            <p style="margin: 8px 0; color: #64748b; font-size: 0.95em;">📍 {lokasi}</p>
            <p style="margin: 8px 0; color: #64748b; font-size: 0.95em;">👥 {reviews} ulasan</p>
            <p style="margin: 12px 0; color: #0f172a; font-weight: 600; font-size: 1.1em;">💰 Mulai {harga}</p>
            <p style="margin: 12px 0; font-size: 0.85em; color: #475569; background-color: #f1f5f9; padding: 8px; border-radius: 6px;">🏕️ {fas_str}</p>
            <a href="{link}" target="_blank" style="display: block; text-align: center; margin-top: 15px; padding: 10px 15px; background-color: #10b981; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 0.95em; transition: background-color 0.2s;" onmouseover="this.style.backgroundColor='#059669'" onmouseout="this.style.backgroundColor='#10b981'">Buka di Google Maps</a>
        </div>
    </div>
    """
    return html

def search_camping(query, top_k, lokasi_filter):
    if not query.strip():
        return "<p style='color:#ef4444; font-weight: bold; padding: 10px; background-color: #fee2e2; border-radius: 8px;'>⚠️ Masukkan kata kunci pencarian terlebih dahulu.</p>"
        
    try:
        response = requests.post(f"{API_URL}/api/search", json={"query": query, "top_k": int(top_k)})
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.ConnectionError:
        return "<p style='color:#ef4444; font-weight: bold; padding: 10px; background-color: #fee2e2; border-radius: 8px;'>⚠️ Gagal terhubung ke server. Pastikan Backend API (modul_5_api.py) sedang berjalan.</p>"
    except Exception as e:
        return f"<p style='color:#ef4444; font-weight: bold; padding: 10px; background-color: #fee2e2; border-radius: 8px;'>⚠️ Terjadi kesalahan: {str(e)}</p>"
        
    results = data.get('results', [])
    if not results:
        return "<p style='text-align: center; color: #64748b; padding: 20px;'>Tidak ditemukan tempat kemah yang sesuai dengan pencarian Anda.</p>"
        
    # Filter Lokasi (bisa juga diimplementasikan di backend, tapi untuk simplicity di sini)
    if lokasi_filter and lokasi_filter != "Semua Lokasi":
        results = [r for r in results if lokasi_filter.lower() in str(r.get('lokasi', '')).lower()]
        
    if not results:
        return f"<p style='text-align: center; color: #64748b; padding: 20px;'>Tidak ditemukan tempat kemah yang sesuai di area <b>{lokasi_filter}</b>.</p>"
        
    html_output = "<div style='display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; padding: 10px 0;'>"
    for res in results:
        html_output += generate_html_card(res)
    html_output += "</div>"
    
    return html_output

# Opsi Lokasi
opsi_lokasi = ["Semua Lokasi", "Sleman", "Bantul", "Gunungkidul", "Kulon Progo", "Yogyakarta", "Semarang", "Karanganyar", "Jawa Tengah"]

# Kustomisasi CSS
custom_css = """
footer {display: none !important;}
.container {max-width: 1200px !important; margin: auto;}
"""

with gr.Blocks(theme=gr.themes.Default(primary_hue="emerald", neutral_hue="slate"), css=custom_css) as demo:
    with gr.Column(elem_classes="container"):
        gr.Markdown("<h1 style='text-align: center; color: #0f172a; margin-bottom: 5px;'>🏕️ Cari Tempat Kemah Impianmu</h1>")
        gr.Markdown("<p style='text-align: center; color: #64748b; font-size: 1.1em; margin-bottom: 25px;'>Cari rekomendasi menggunakan bahasa sehari-hari. Berbasis ulasan riil pengguna Google Maps.</p>")
        
        with gr.Group():
            with gr.Row():
                with gr.Column(scale=4):
                    query_input = gr.Textbox(
                        label="Apa yang kamu cari?", 
                        placeholder="Contoh: camping keluarga ada sungai dan fasilitas lengkap...",
                        lines=1,
                        show_label=False,
                        container=False
                    )
                with gr.Column(scale=1, min_width=150):
                    search_btn = gr.Button("🔍 Cari", variant="primary")
                    
        with gr.Accordion("Pengaturan Pencarian", open=False):
            with gr.Row():
                top_k_input = gr.Slider(minimum=3, maximum=30, value=12, step=1, label="Batas Maksimal Hasil")
                lokasi_input = gr.Dropdown(choices=opsi_lokasi, value="Semua Lokasi", label="Filter Area/Lokasi")
                
        gr.Markdown("---")
        
        output_html = gr.HTML("<p style='text-align: center; color: #94a3b8; padding: 40px;'>Hasil pencarian akan muncul di sini</p>")
        
        # Contoh Kueri Cepat
        gr.Examples(
            examples=[
                ["tempat camping sejuk dengan pemandangan sunrise yang bagus"],
                ["camping campervan pinggir danau"],
                ["camping budget murah untuk pemula"]
            ],
            inputs=query_input,
            label="Coba kueri ini"
        )
        
    search_btn.click(
        fn=search_camping,
        inputs=[query_input, top_k_input, lokasi_input],
        outputs=output_html
    )
    query_input.submit(
        fn=search_camping,
        inputs=[query_input, top_k_input, lokasi_input],
        outputs=output_html
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
