from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from generadorcarnet import GeneradorCarnet
import zipfile
import tempfile
import os
app = FastAPI()

class Carnetizacion(BaseModel):
    Nombre: str
    Cedula: str
    Cargo: str
    RH: str
    Foto: str
@app.post("/generadorcarnet/")
def generar_carnet(datos: Carnetizacion):
    try:
        generador = GeneradorCarnet(datos.dict())
        cedula = datos.Cedula

        # 📌 Usar carpeta temporal para evitar errores en Render
        with tempfile.TemporaryDirectory() as tmpdir:
            frontal_path = os.path.join(tmpdir, "frontal.png")
            trasera_path = os.path.join(tmpdir, "trasera.png")

            # 🎯 Generar imágenes en esa ruta
            generador.generar_carnetizacion(frontal_path, trasera_path)

            # 📦 Crear archivo ZIP también dentro del tmpdir
            zip_path = os.path.join(tmpdir, f"carnet_{cedula}.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                zipf.write(frontal_path, arcname="frontal.png")
                zipf.write(trasera_path, arcname="trasera.png")

            # 🚀 Retornar ZIP como descarga
            return FileResponse(zip_path, media_type='application/zip', filename=f"carnet_{cedula}.zip")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {"message": "Hello from Render!"}
