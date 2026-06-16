import uvicorn
from fastapi import FastAPI
from handlers.sim_handler import router as sim_router

# Inisialisasi aplikasi
app = FastAPI(title="OCR SIM Microservice (EasyOCR + Clean Arch)")

# Registrasi Router dengan prefix (contoh: http://localhost:8080/api/v1/ocr/sim)
app.include_router(sim_router, prefix="/api/v1")

# Cek status server
@app.get("/health")
def health_check():
    return {"status": "Service is up and running!"}

if __name__ == "__main__":
    # Jalankan server via uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)