from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from generadorcarnet import GeneradorCarnet
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
        generador.generar_carnetizacion()
        return {"mensaje": "Carnet generado correctamente", "cedula": datos.Cedula}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {"message": "Hello from Render!"}
