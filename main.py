from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from generadorcarnet import GeneradorCarnet
import zipfile
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
        generador.generar_carnetizacion("templates/Front.png", "templates/Rear.png")

        # Nombre de ZIP temporal (NO usar NamedTemporaryFile aquí)
        zip_path = f"/tmp/carnet_{cedula}.zip"

        # Crear el zip
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(f"{cedula}_frontal.png", arcname="frontal.png")
            zipf.write(f"{cedula}_trasera.png", arcname="trasera.png")

        # Responder con el archivo
        return FileResponse(zip_path, media_type='application/zip', filename=f"carnet_{cedula}.zip")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Hello from Render!"}
