import requests
import pandas as pd
from datetime import datetime
import pytz
import time
import logging
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# Konfigurasi Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ShopeeScraper:
    def __init__(self, shop_id: int, limit: int = 100):
        self.shop_id = shop_id
        self.limit = limit
        self.batch_size = 20 # Shopee biasanya membatasi 20 per request
        self.session = self._setup_session()
        self.base_url = 'https://shopee.co.id/api/v2/shop/get_ratings'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'referer': f'https://shopee.co.id/shop/{shop_id}/search'
        }
        self.collected_data = []

    def _setup_session(self):
        session = requests.Session()
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        return session

    def _process_items(self, items):
        tz = pytz.timezone('Asia/Jakarta')
        count = 0
        
        for item in items:
            try:
                comment = item.get('comment', '').replace('\n', ' ').strip()
                # Hanya ambil yang ada komentarnya
                if not comment:
                    continue

                timestamp = item.get('submit_time', 0)
                dt_object = datetime.fromtimestamp(timestamp, tz)
                
                product_items = item.get('product_items', [])
                product_name = product_items[0].get('name', '') if product_items else ''
                
                row = {
                    'Username': item.get('author_username', 'Anonim'),
                    'Rating': item.get('rating_star', 0),
                    'Tanggal': dt_object.strftime('%Y-%m-%d %H:%M:%S'),
                    'Produk': product_name,
                    'Review': comment
                }
                self.collected_data.append(row)
                count += 1
            except Exception as e:
                logger.error(f"Error parsing item: {e}")
        return count

    def scrape(self, progress_callback=None):
        """
        Menjalankan scraping.
        progress_callback: fungsi (str) -> void untuk update status di UI
        """
        offset = 0
        total_collected = 0
        self.collected_data = []
        
        while total_collected < self.limit:
            if progress_callback:
                progress_callback(f"Mengambil data... ({total_collected}/{self.limit})")
            
            params = {
                'limit': self.batch_size,
                'offset': offset,
                'shopid': self.shop_id,
                'type': 0 # Type 0 = All ratings
            }
            
            try:
                response = self.session.get(self.base_url, headers=self.headers, params=params, timeout=10)
                data = response.json()
                
                if 'data' not in data or 'items' not in data['data']:
                    break
                    
                items = data['data']['items']
                if not items:
                    break
                    
                processed_count = self._process_items(items)
                total_collected += processed_count
                
                offset += self.batch_size
                time.sleep(1) # Rate limit agar tidak diblokir
                
            except Exception as e:
                logger.error(f"Request error: {e}")
                break
                
        if progress_callback:
            progress_callback(f"Selesai! {total_collected} data terkumpul.")
            
        return pd.DataFrame(self.collected_data)