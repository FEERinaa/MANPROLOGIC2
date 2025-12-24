from transformers import pipeline
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Kamus Slang (Bisa ditambahkan sendiri)
SLANG_DICT = {
    "yg": "yang", "gak": "tidak", "ga": "tidak", "bgs": "bagus",
    "sy": "saya", "bgt": "banget", "sdh": "sudah", "krn": "karena",
    "mantul": "mantap", "recomended": "rekomen", "kecewa": "buruk"
}

class SentimentAnalyzer:
    def __init__(self):
        logger.info("Memuat model IndoBERT...")
        # Menggunakan model yang sudah fine-tuned untuk sentimen Indonesia
        self.pipeline = pipeline(
            "sentiment-analysis",
            model="w11wo/indonesian-roberta-base-sentiment-classifier",
            tokenizer="w11wo/indonesian-roberta-base-sentiment-classifier"
        )
    
    def clean_text(self, text):
        if not isinstance(text, str): return ""
        text = text.lower()
        words = text.split()
        words = [SLANG_DICT.get(w, w) for w in words]
        text = " ".join(words)
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        return text

    def predict(self, text):
        clean = self.clean_text(text)
        if not clean: return "Netral", 0.0
        
        # Truncate jika terlalu panjang (batas BERT 512 token)
        clean = clean[:512]
        
        result = self.pipeline(clean)[0]
        label = result['label']
        score = result['score']
        
        # Mapping label model ke Bahasa Indonesia
        label_map = {"positive": "Positif", "neutral": "Netral", "negative": "Negatif"}
        sentiment = label_map.get(label, "Netral")
        
        return sentiment, score