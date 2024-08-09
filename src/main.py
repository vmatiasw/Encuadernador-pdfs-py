from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4 # type: ignore
from reportlab.lib.units import mm # type: ignore
from reportlab.pdfgen import canvas # type: ignore
import os

MIN_PAPERS_PER_BOOKLET = 8
MAX_PAPERS_PER_BOOKLET = 12
WIDTH, HEIGHT = A4
TEMP_DIR = "temp"

class PDFBookletCreator:
    def __init__(self, input_pdf, output_pdf, papers_per_booklet = 10, margin = 10.0):
        self.check_parameters(input_pdf, output_pdf, papers_per_booklet, margin)
        
        # creamos un directorio temporal para almacenar los archivos temporales
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)

        # Constantes
        self.INPUT_PDF = input_pdf
        self.OUTPUT_PDF = output_pdf
        self.PAGES_PER_BOOKLET = papers_per_booklet * 4
        self.MARGIN = margin
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        # Variables
        self.working_pdf = os.path.join(TEMP_DIR, "working.pdf")
        self.working_pdf_reader = PdfReader(self.INPUT_PDF)
    
    def check_parameters(self, input_pdf, output_pdf, papers_per_booklet, margin):

        # input_pdf
        if not os.path.exists(input_pdf):
            raise FileNotFoundError(f"El archivo {input_pdf} no existe.")
        if not input_pdf.endswith(".pdf"):
            raise ValueError("El archivo de entrada debe ser un PDF.")
        
        # output_pdf
        if not output_pdf.endswith(".pdf"):
            raise ValueError("El archivo de salida debe ser un PDF.")

        # papers_per_booklet
        if not isinstance(papers_per_booklet, int):
            raise TypeError("El número de hojas por cuadernillo debe ser un número entero.")
        if papers_per_booklet < MIN_PAPERS_PER_BOOKLET or MAX_PAPERS_PER_BOOKLET < papers_per_booklet:
            raise ValueError(f"El número de hojas por cuadernillo debe estar entre {MIN_PAPERS_PER_BOOKLET} y {MAX_PAPERS_PER_BOOKLET}.")

        # margin
        if not isinstance(margin, (int, float)):
            raise TypeError("El margen debe ser un número.")
        if margin < 0:
            raise ValueError("El margen debe ser un número positivo.")
        
    def _add_blank_pages_to_writer(self, writer, num_pages = 1):
        '''
        Agrega `num_pages` páginas en blanco al final del documento de `writer`.
        '''
        for _ in range(num_pages):
            writer.add_blank_page(self.WIDTH, self.HEIGHT)

    def _add_blank_pages(self):
        '''
        Agrega 2 páginas en blanco al inicio y final del documento de self.input_pdf en self.working_pdf.
        Luego, agrega paginas en blanco al final hasta que la cantidad de hojas sea multiplo de self.pages_per_booklet.
        '''
        reader = self.working_pdf_reader
        writer = PdfWriter()
        total_pages = len(reader.pages)

        # Agregar 2 páginas en blanco al inicio
        self._add_blank_pages_to_writer(writer, 2)

        # Agregar las páginas del documento original
        for i in range(total_pages):
            writer.add_page(reader.pages[i])

        # Agregar 2 páginas en blanco al final
        self._add_blank_pages_to_writer(writer, 2)

        # Agregar páginas en blanco al final para que self.working_pdf tenga un 
        # número de hojas múltiplo de self.PAGES_PER_BOOKLET
        pages_to_complete = self.PAGES_PER_BOOKLET - len(writer.pages) % self.PAGES_PER_BOOKLET
        if pages_to_complete != self.PAGES_PER_BOOKLET:
            self._add_blank_pages_to_writer(writer, pages_to_complete)

        # Guardar el documento final
        self.update_working_pdf(writer)

    def update_working_pdf(self,writer):
        with open(self.working_pdf, "wb") as output_file:
            writer.write(output_file)
        self.working_pdf_reader = PdfReader(self.working_pdf)

    
    
    # FIXME: El codigo de abajo no esta revisado ni completado
   
    def create_booklet(self):
        
        self._add_blank_pages()

        reader = PdfReader(self.working_pdf)
        writer = PdfWriter()
        total_pages = len(reader.pages)
        width, height = A4

        # Crear cuadernillos
        for start in range(0, total_pages, self.PAGES_PER_BOOKLET):
            end = min(start + self.PAGES_PER_BOOKLET, total_pages)
            booklet_pages = [reader.pages[i] for i in range(start, end)]
            
            for i in range(0, len(booklet_pages), 4):
                # Crear una nueva hoja A4 con 4 carillas
                c = canvas.Canvas("temp.pdf", pagesize=A4)
                for j in range(4):
                    if i + j < len(booklet_pages):
                        page = booklet_pages[i + j]
                        c.setPageSize(A4)
                        c.drawImage(page, self.MARGIN * mm, self.MARGIN * mm, width / 2 - 2 * self.MARGIN * mm, height / 2 - 2 * self.MARGIN * mm)
                        c.showPage()
                c.save()
                
                # Agregar la hoja al documento final
                temp_reader = PdfReader("temp.pdf")
                writer.add_page(temp_reader.pages[0])
            
            os.remove("temp.pdf")
        
        with open(self.OUTPUT_PDF, "wb") as output_file:
            writer.write(output_file)

# Uso de la clase
creator = PDFBookletCreator("input.pdf", "output_booklet.pdf")
creator.create_booklet()