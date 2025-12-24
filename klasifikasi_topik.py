import pandas as pd

class TopicClassifier:
    def __init__(self):
        # Definisikan kata kunci untuk setiap topik
        self.keywords = {
            "Pengiriman": ["kurir", "kirim", "lama", "cepat", "lambat", "sampai", "packing", "kemasan", "bungkus", "bubble", "pecah", "penyok"],
            "Kualitas Produk": ["bahan", "kain", "jahitan", "rusak", "cacat", "original", "palsu", "kw", "awet", "tebal", "tipis", "berfungsi"],
            "Pelayanan": ["respon", "admin", "penjual", "seller", "balas", "ramah", "jutek", "sopan", "chat"],
            "Harga": ["murah", "mahal", "promo", "diskon", "harga", "worth", "biaya"]
        }

    def classify(self, text):
        """Menentukan topik berdasarkan kata kunci yang muncul"""
        text = str(text).lower()
        
        scores = {topic: 0 for topic in self.keywords}
        
        for topic, words in self.keywords.items():
            for word in words:
                if word in text:
                    scores[topic] += 1
        
        # Cari skor tertinggi
        max_score = max(scores.values())
        if max_score == 0:
            return "Umum/Lainnya"
        
        # Ambil topik dengan skor tertinggi
        best_topic = max(scores, key=scores.get)
        return best_topic

    def process_dataframe(self, df, col_review='Review'):
        if df is None or df.empty:
            return df
        
        # Terapkan klasifikasi ke setiap baris
        df['Topik'] = df[col_review].apply(self.classify)
        return df