import os
from datetime import date

from fpdf import FPDF

CARPETA = os.getenv("PDF_DIR", "./storage/pdf")


def _pdf_base(titulo: str, lineas: list[str], fichero: str) -> str:
    os.makedirs(CARPETA, exist_ok=True)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(w=0, h=10, text=titulo)
    pdf.ln()
    pdf.set_font("helvetica", "", 11)
    for linea in lineas:
        pdf.multi_cell(w=0, h=7, text=linea)
        pdf.ln(1)
    ruta = os.path.join(CARPETA, fichero)
    pdf.output(ruta)
    return ruta


def generar_pdf_build(build_id: int, datos: dict) -> str:
    lineas = [
        f"ID build: {datos.get('id') or build_id}",
        f"Personaje: {datos.get('persona', '-')}",
        f"Clase: {datos.get('clase', '')} - Nivel: {datos.get('nivel', '')}",
        f"Sistema: Pathfinder 1e - Fecha: {date.today().isoformat()}",
        "- Ficha generada por TFinder AE2 -",
    ]
    return _pdf_base("Ficha de personaje", lineas, f"build_{build_id}.pdf")


def generar_pdf_diario(sesion_id: int, datos: dict) -> str:
    lineas = [
        f"Sesion {sesion_id}",
        str(datos.get("titulo", "")),
        "",
        str(datos.get("cuerpo", "")),
    ]
    return _pdf_base("Diario de sesion", lineas, f"diario_{sesion_id}.pdf")