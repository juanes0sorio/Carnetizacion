from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from generadorcarnet import GeneradorCarnet
import zipfile
import tempfile
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
        generador.generar_carnetizacion()

        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        with zipfile.ZipFile(temp_zip.name, 'w') as zipf:
            zipf.write(f"{cedula}_frontal.png", arcname="frontal.png")
            zipf.write(f"{cedula}_trasera.png", arcname="trasera.png")

        return FileResponse(temp_zip.name, media_type='application/zip', filename=f"carnet_{cedula}.zip")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {"message": "Hello from Render!"}
