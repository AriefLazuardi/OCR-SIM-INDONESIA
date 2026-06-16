from fastapi import APIRouter, HTTPException, Depends
from domain.sim import OCRRequest, SIMData
from services.sim_service import SIMService
from data.ocr_repository import OCRRepository

router = APIRouter()

# Dependency Injection ala FastAPI (Mirip init di main.go)
def get_sim_service():
    repo = OCRRepository()
    return SIMService(repo)

@router.post("/ocr/sim")
async def process_ocr_sim(req: OCRRequest, service: SIMService = Depends(get_sim_service)):
    try:
        # Panggil service layer
        result_data = service.process_ocr_sim(req.image_base64, req.tipe_sim)
        
        # Return format mengikuti yang kamu inginkan
        return {
            "status": "success",
            "data": result_data.model_dump() # model_dump() mengubah Pydantic ke dictionary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memproses gambar: {str(e)}")