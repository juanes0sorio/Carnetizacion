from PIL import Image, ImageDraw, ImageFont
from rembg import remove
import io
import qrcode
import hashlib
import json
import requests
from pathlib import Path

class GeneradorCarnet:
    def __init__(self, datos):
        self.datos = datos
        self.clave = "tempoconvision"
        self.coordenadas = {
            "Foto": {"x": 96, "y": 64, "w": 251, "h": 332},
            "Nombre": {"x": 201, "y": 450},
            "Cedula": {"x": 375, "y": 489},
            "Cargo": {"x": 312, "y": 531},
            "RH": {"x": 378, "y": 576},
            "QR": {"x": 338, "y": 60, "w": 227, "h": 227}
        }
        self.fuentes = (ImageFont.truetype("fonts/horizon.otf", size = 31), ImageFont.truetype("fonts/GlacialIndifference-Regular.otf", size = 34))

    def _generar_qr(self):

        clave_hash = hashlib.sha256(self.clave.encode()).hexdigest()
        datos_json = json.dumps({
            "nombre": self.datos["Nombre"],
            "cedula": self.datos["Cedula"],
            "clave_hash": clave_hash
        })

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4
        )
        qr.add_data(datos_json)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img = img.resize((self.coordenadas["QR"]["w"], self.coordenadas["QR"]["h"]), resample=Image.LANCZOS)

        return img

    def _construir_url_appsheet(self, ruta_relativa: str) -> str:
        # Reemplaza esto con el nombre exacto de tu tabla en AppSheet
        nombre_tabla = "Table 1"
        base_url = "https://www.appsheet.com/template/gettablefileurl"
        return f"{base_url}?tableName={nombre_tabla}&fileName={requests.utils.quote(ruta_relativa)}"

    def _procesar_foto(self):
        ruta_foto = self.datos["Foto"]

        # Si no es URL completa, la convierte usando AppSheet
        if not ruta_foto.startswith("http"):
            ruta_foto = self._construir_url_appsheet(ruta_foto)

        response = requests.get(ruta_foto)
        if response.status_code != 200:
            raise Exception("No se pudo descargar la foto desde la URL")

        bytes_img = response.content
        img = Image.open(io.BytesIO(bytes_img)).convert("RGB")

        img_final = img.resize(
            (self.coordenadas["Foto"]["w"], self.coordenadas["Foto"]["h"]),
            resample=Image.LANCZOS
        )

        return img_final

    def generar_carnetizacion(self):

        frontal = Image.open("templates/Front.png").convert("RGBA")
        trasera = Image.open("templates/Rear.png").convert("RGBA")
        dibujar_frontal = ImageDraw.Draw(frontal)

        textos = [
            ("Nombre", self.fuentes[0], self.datos['Nombre']),
            ("Cedula", self.fuentes[1], f"C.C {self.datos['Cedula']}"),
            ("Cargo", self.fuentes[1], self.datos["Cargo"]),
            ("RH", self.fuentes[1], f"RH: {self.datos['RH']}")
        ]

        ancho_img = frontal.width

        for clave, fuente, texto in textos:
            y = self.coordenadas[clave]["y"]
            ancho_texto = dibujar_frontal.textlength(texto, font=fuente)
            x = (ancho_img - ancho_texto) // 2
            dibujar_frontal.text((x, y), texto, font=fuente, fill="white")


        foto = self._procesar_foto()
        frontal.paste(foto, (self.coordenadas["Foto"]["x"], self.coordenadas["Foto"]["y"]))

        qr = self._generar_qr()
        trasera.paste(qr, (self.coordenadas["QR"]["x"], self.coordenadas["QR"]["y"]))

        cedula = self.datos["Cedula"]
        frontal.save(f"{cedula}_frontal.png")
        trasera.save(f"{cedula}_trasera.png")



