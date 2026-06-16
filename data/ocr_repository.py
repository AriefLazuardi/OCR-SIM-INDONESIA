import base64
import io
import cv2
import numpy as np
import easyocr

READER = easyocr.Reader(['id', 'en'], gpu=False)

class OCRRepository:
    def process_base64_image(self, base64_str: str) -> list:
        if "," in base64_str:
            base64_str = base64_str.split(",")[1]
            
        img_bytes = base64.b64decode(base64_str)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return []

        # 1. Konversi ke Greyscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 2. Standarisasi Ukuran Maksimal
        h, w = gray.shape[:2]
        if max(h, w) > 1500:
            scale = 1500 / max(h, w)
            gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

        # 3. CEK STANDAR DEVIASI KONTRAS (Mengakali Gambar Hitam Putih / Berwarna)
        # Jika nilai stdDev rendah (< 45), artinya gambar redup/samar -> Butuh CLAHE
        # Jika nilai tinggi, gambar sudah punya kontras bagus -> Cukup gunakan grayscale polos
        _, std_dev = cv2.meanStdDev(gray)
        
        if std_dev[0][0] < 45:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            processed_img = clahe.apply(gray)
        else:
            processed_img = gray # Ambil polosnya agar angka tipis tidak hancur

        # 4. Eksekusi EasyOCR
        result = READER.readtext(processed_img)
        
        lines = []
        for res in result:
            text_string = res[1].strip()
            if text_string:
                lines.append(text_string)
                
        return lines