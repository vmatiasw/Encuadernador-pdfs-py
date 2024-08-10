from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4 # type: ignore
import os
import tempfile

MIN_PAPERS_PER_BOOKLET = 8
MAX_PAPERS_PER_BOOKLET = 12
WIDTH, HEIGHT = A4
TEMP_DIR = tempfile.mkdtemp()

class PDFBookletCreator:
    def __init__(self, input_pdf, output_pdf, papers_per_booklet = 10):
        self._check_parameters(input_pdf, output_pdf, papers_per_booklet)

        # Constantes
        self.INPUT_PDF = input_pdf
        self.OUTPUT_PDF = output_pdf
        self.PAGES_PER_BOOKLET = papers_per_booklet * 4
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT

        # Variables
        self.working_pdf = os.path.join(TEMP_DIR, "working.pdf")
        self.working_pdf_reader = PdfReader(self.INPUT_PDF)
    
    def _check_parameters(self, input_pdf, output_pdf, papers_per_booklet):

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
        
    def _add_blank_pages_to_writer(self, writer, num_pages = 1):
        '''
        Agrega `num_pages` páginas en blanco al final del documento de `writer`.
        '''
        for _ in range(num_pages):
            writer.add_blank_page(self.WIDTH, self.HEIGHT)

    def _add_blank_pages(self):
        '''
        Agrega 2 páginas en blanco al inicio y final del self.working_pdf.
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
        self._update_working_pdf(writer)

    def _update_working_pdf(self,writer):
        with open(self.working_pdf, "wb") as output_file:
            writer.write(output_file)
        self.working_pdf_reader = PdfReader(self.working_pdf)

    def _create_booklet(self):
        '''
        Separa en cuadernillos de self.PAGES_PER_BOOKLET carillas el self.working_pdf.
        '''
        reader = self.working_pdf_reader
        total_pages = len(reader.pages)
        writer = PdfWriter()

        assert self.PAGES_PER_BOOKLET % 4 == 0 and total_pages % self.PAGES_PER_BOOKLET == 0 , "El número de hojas por cuadernillo debe ser múltiplo de 4 y el número total de hojas debe ser múltiplo de self.PAGES_PER_BOOKLET."

        for i in range(0, total_pages, self.PAGES_PER_BOOKLET):
            end = i + self.PAGES_PER_BOOKLET - 1
            init = i
            while (init < end):
                assert init + 1 < total_pages and end - 1 >= 0, "ERROR en _create_booklet"
                writer.add_page(reader.pages[init + 1])
                writer.add_page(reader.pages[end - 1])
                writer.add_page(reader.pages[end].rotate_clockwise(180))
                writer.add_page(reader.pages[init].rotate_clockwise(180))
                init += 2
                end -= 2
        
        self._update_working_pdf(writer)

    def get_booklet(self):
        
        try:
            self._add_blank_pages()
            self._create_booklet()

            with open(self.OUTPUT_PDF, "wb") as output_file:
                writer = PdfWriter()
                reader = self.working_pdf_reader
                for i in range(len(reader.pages)):
                    writer.add_page(reader.pages[i])
                writer.write(output_file)
        finally:
            if os.path.exists(self.working_pdf):
                os.remove(self.working_pdf)
            if os.path.exists(TEMP_DIR):
                os.rmdir(TEMP_DIR)


# Uso de la clase
creator = PDFBookletCreator("input.pdf", "output_booklet.pdf", 10)
creator.get_booklet()

'''
El código recibe el archivo "input.pdf", agrega dos carillas en blanco al inicio y al final
y lo transforma en cuadernillos de 10 hojas en orden para imprimir doble faz. 
Finalmente, toma el resultado y lo guarda en "output_booklet.pdf".

"output_booklet.pdf" debe imprimirse de la siguiente manera:
2 carillas por hoja, doble faz, en orden de lectura de izquierda a derecha y de arriba 
hacia abajo.
Los margenes no se ajustan automáticamente, por lo que es necesario configurarlos en la
impresora.
'''