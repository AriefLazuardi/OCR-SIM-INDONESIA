from pydantic import BaseModel
from typing import List

class OCRRequest(BaseModel):
    image_base64: str
    tipe_sim: str

class SIMData(BaseModel):
    type: str = ""
    number: str = ""
    name: str = ""
    expired_date: str = ""
    status_sim: str = "NOT_FOUND"
    raw_text: List[str] = []