from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from ETL_colegio import ejecutar_etl
import os

app = FastAPI()

# Configurar CORS por si fuera necesario
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/run-etl")
def run_etl_endpoint():
    """
    Ejecuta el ETL y transmite los eventos en tiempo real al frontend
    usando Server-Sent Events (SSE).
    """
    # Envolvemos el generador para dar formato SSE estándar
    def event_stream():
        for log in ejecutar_etl():
            yield f"data: {log}\n\n"
            
    return StreamingResponse(event_stream(), media_type="text/event-stream")

# Crear el directorio public si no existe
os.makedirs("public", exist_ok=True)

# Montar los archivos estáticos del frontend (HTML, CSS, JS)
app.mount("/", StaticFiles(directory="public", html=True), name="public")

if __name__ == "__main__":
    print("Iniciando servidor web de validación ETL en http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
