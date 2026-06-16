import re
from datetime import datetime
from domain.sim import SIMData
from data.ocr_repository import OCRRepository
from utils.helpers import clean_text
from utils.helpers import has_vowel


class SIMService:
    def __init__(self, repo: OCRRepository):
        self.repo = repo

    def process_ocr_sim(self, image_base64: str, tipe_sim: str) -> SIMData:
        raw_lines = self.repo.process_base64_image(image_base64)
        return self._parse_sim(raw_lines, tipe_sim)

    def _parse_sim(self, lines: list, tipe_sim: str) -> SIMData:
        res = SIMData(type=tipe_sim.upper())
        res.raw_text = lines 
        
        re_date = re.compile(r'(\d{2}[-\/\s\.\*]{1,2}\d{2}[-\/\s\.\*]{1,2}\d{4})')
        sim_num_idx = -1
        type_detected_by_ocr = ""

        for i, line in enumerate(lines):
            upper_line = line.upper().strip()
            
            # --- 1. SINKRONISASI GOLANG: DETEKSI OTOMATIS TIPE SIM ---
            if "SEPEDA MOTOR" in upper_line or "MOTORCYCLES" in upper_line:
                type_detected_by_ocr = "C"
            elif "MOBIL PENUMPANG" in upper_line or "PASSENGER CAR" in upper_line:
                type_detected_by_ocr = "A"
            elif any(k in upper_line for k in ["MOBIL BUS", "MOBIL BARANG", "ALAT BERAT", "GANDENGAN"]):
                type_detected_by_ocr = "B"
            
            # Fallback regex tipe SIM di pojok (seperti di Golang)
            if not type_detected_by_ocr:
                re_tipe = re.compile(r'\b([ABC]|B[I]{1,2})\b')
                if re_tipe.search(upper_line) and len(upper_line) < 10:
                    type_detected_by_ocr = re_tipe.search(upper_line).group(1)

            # --- 2. EKSTRAK NOMOR SIM ---
            if not res.number:
                clean_number = re.sub(r'\D', '', line)
                if re.match(r'^\d{12,14}$|^\d{16}$', clean_number): # Sesuai dengan regex Golang
                    res.number = clean_number
                    sim_num_idx = i

        # SINKRONISASI: Jika OCR berhasil mendeteksi tipe SIM secara valid, override input default
        if type_detected_by_ocr:
            res.type = type_detected_by_ocr

        # --- 3. EKSTRAK NAMA ---
        for i, line in enumerate(lines):
            upper_line = line.upper().strip()
            is_anchor = bool(re.search(r'NAM[AW]|NAME|N[AM]{2,4}[WS]?N[AM]{2,4}O|^1[\.\s\-\']+$|^1$', upper_line))
            
            if is_anchor and not res.name:
                clean_inline = re.sub(r'^1[\.\s\-]*|NAM[AW]|NAME|N[AM]{2,4}[WS]?N[AM]{2,4}O|[\/:\.]', ' ', upper_line)
                inline_words = self._clean_name_words(clean_inline)
                
                if inline_words:
                    res.name = " ".join(inline_words)
                else:
                    res.name = self._get_name_from_next_lines(lines, i)
                break

        if not res.name and sim_num_idx != -1:
            res.name = self._get_name_from_next_lines(lines, sim_num_idx)

        # --- 4. EKSTRAK TANGGAL EXPIRED ---
        all_expired_candidates = []
        for line in lines:
            match = re_date.search(line)
            if match:
                tgl_raw = match.group(1)
                tgl_clean = re.sub(r'[\s\./\*]+', '-', tgl_raw)
                
                if tgl_clean.startswith("00"):
                    tgl_clean = f"{datetime.now().strftime('%d')}{tgl_clean[2:]}"
                
                year_match = re.search(r'\d{4}$', tgl_clean)
                if year_match:
                    year = int(year_match.group())
                    if year >= 2024:
                        all_expired_candidates.append(tgl_clean)
                    elif year >= 2010:
                        all_expired_candidates.insert(0, tgl_clean)

        if all_expired_candidates:
            final_date = all_expired_candidates[-1]
            res.expired_date = final_date.replace("-", "/")

        # --- 5. POST-PROCESSING NAMA & STATUS ---
        if res.name:
            res.name = clean_text(res.name)

        if res.expired_date:
            try:
                expired_time = datetime.strptime(res.expired_date, "%d/%m/%Y")
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                res.status_sim = "EXPIRED" if expired_time < today else "ACTIVE"
            except ValueError:
                res.status_sim = "UNKNOWN_DATE_FORMAT"
        else:
            res.status_sim = "NOT_FOUND"

        return res

    def _clean_name_words(self, text: str) -> list:
        clean_str = re.sub(r'[^A-Z\s]', ' ', text.upper())
        words = clean_str.split()
        valid_words = []
        
        card_headers = {
            "INDONESIA", "DRIVING", "LICENSE", "SURAT", "IZIN", "MENGEMUDI", 
            "POLRI", "POLRESTA", "GOL", "DARAH", "BLOOD", "TYPE", "JENIS", 
            "KELAMIN", "SEX", "PRIA", "WANITA", "ALAMAT", "ADDRESS", "PEKERJAAN", 
            "OCCUPATION", "DITERBITKAN", "OLEH", "ISSUED", "TEMPAT", "LAHIR", "PLACE",
            "BLLUMUM", "BIIUMUM", "BILUMUM", "UMUM", "A", "B", "C", "D", "AIEIFSILKENSI",
            "NAMSNENO", "NAMWNAMO", "NMPNAN", "MOBI", "PENUMPANG", "PRIBADI",
            "PASSENDER", "CATIPOFSONS", "DDODS", "SEPEDA", "MOTOR", "MOTORCYCLES"
        }
        
        for w in words:
            if w in card_headers:
                continue
            # SINKRONISASI + PROTEKSI: Huruf tunggal 'M' lolos, kata lain minimal 2 huruf & punya vokal
            if len(w) == 1 and w != "M":
                continue
            if len(w) >= 2 and not has_vowel(w): # Mengadopsi esensi HasVowel Golang untuk menyaring noise konsonan spt "KXT"
                continue
            valid_words.append(w)
            
        return valid_words

    def _get_name_from_next_lines(self, lines: list, current_idx: int) -> str:
        for j in range(1, 5):
            if current_idx + j >= len(lines):
                break
                
            next_line = lines[current_idx + j].upper().strip()
            if re.search(r'TEMPAT|LAHIR|PLACE|GOL|DARAH|ALAMAT|PEKERJAAN', next_line):
                continue
                
            words = self._clean_name_words(next_line)
            if words:
                if len(words) == 1 and words[0].isdigit():
                    continue
                return " ".join(words)
        return ""