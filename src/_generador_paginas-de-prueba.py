from reportlab.lib.pagesizes import A4 # type: ignore
from reportlab.lib.units import cm # type: ignore
from reportlab.pdfgen import canvas # type: ignore

def crear_pdf(numero_paginas, archivo_salida):
    c = canvas.Canvas(archivo_salida, pagesize=A4)
    ancho, alto = A4
    
    for i in range(1, numero_paginas + 1):
        # Posiciona el número de página en la esquina inferior derecha, casi invisible
        c.setFont("Helvetica", 6)
        c.drawString(ancho - 2*cm, 1*cm, str(i))
        c.showPage()  # Crea una nueva página en blanco

    c.save()

# Generar un PDF con páginas en blanco numeradas
crear_pdf(31, "paginas_numeradas.pdf")