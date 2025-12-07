from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4 # type: ignore
import os
import tempfile
import sys


class BookletProcessor:
    def __init__(self, input_pdf: str, output_pdf: str, papers_per_booklet: int, cover_pages: int = 0):
        """        
        Args:
            input_pdf: Ruta al archivo PDF de entrada
            output_pdf: Ruta al archivo PDF de salida
            papers_per_booklet: Número de hojas por cuadernillo
            cover_pages: Número de páginas de tapa
        """
        self.input_pdf = input_pdf
        self.output_pdf = output_pdf
        self.papers_per_booklet = papers_per_booklet
        self.cover_pages = cover_pages
        self.pages_per_booklet = papers_per_booklet * 4 # carillas
        self.width, self.height = A4
        self.temp_dir = tempfile.mkdtemp()
        
        self._validate_parameters()
        self.reader = PdfReader(input_pdf)
    
    def _validate_parameters(self):
        """Valida los parámetros de entrada."""
        # Validar input_pdf
        if not os.path.exists(self.input_pdf):
            raise FileNotFoundError(f"El archivo {self.input_pdf} no existe.")
        if not self.input_pdf.lower().endswith(".pdf"):
            raise ValueError("El archivo de entrada debe ser un PDF.")
        
        # Validar output_pdf
        if not self.output_pdf.lower().endswith(".pdf"):
            raise ValueError("El archivo de salida debe ser un PDF.")
        
        # Validar papers_per_booklet
        if not isinstance(self.papers_per_booklet, int):
            raise TypeError("El número de hojas por cuadernillo debe ser un número entero.")
    
    def _add_blank_pages(self, writer: PdfWriter, num_pages: int):
        """Agrega páginas en blanco al writer."""
        for _ in range(num_pages):
            writer.add_blank_page(self.width, self.height)
    
    def _prepare_pages(self) -> PdfWriter:
        """
        Agrega páginas de tapa y páginas en blanco para completar cuadernillos.
        
        Returns:
            PdfWriter con las páginas preparadas
        """
        writer = PdfWriter()
        
        # Agregar páginas de tapa al inicio
        self._add_blank_pages(writer, self.cover_pages)
        
        # Agregar páginas originales
        for page in self.reader.pages:
            writer.add_page(page)
        
        # Agregar páginas de tapa al final
        self._add_blank_pages(writer, self.cover_pages)
        
        # Completar para que sea múltiplo de pages_per_booklet
        pages_to_complete = self.pages_per_booklet - len(writer.pages) % self.pages_per_booklet
        if pages_to_complete != self.pages_per_booklet:
            self._add_blank_pages(writer, pages_to_complete)
        
        return writer
    
    def _create_booklet(self, reader: PdfReader) -> PdfWriter:
        """
        Reordena las páginas en formato cuadernillo.
        
        Args:
            reader: PdfReader con las páginas preparadas
            
        Returns:
            PdfWriter con las páginas en orden de cuadernillo
        """
        total_pages = len(reader.pages)
        writer = PdfWriter()
        
        # Procesar cada cuadernillo
        for i in range(0, total_pages, self.pages_per_booklet):
            start = i
            end = i + self.pages_per_booklet - 1
            
            # Reordenar páginas del cuadernillo
            while start < end:
                writer.add_page(reader.pages[start + 1])
                writer.add_page(reader.pages[end - 1])
                writer.add_page(reader.pages[end])
                writer.add_page(reader.pages[start])
                start += 2
                end -= 2
        
        return writer
    
    def process(self):
        """Procesa el PDF completo y genera el cuadernillo."""
        try:
            # Preparar páginas
            prepared_writer = self._prepare_pages()
            
            # Crear archivo temporal con páginas preparadas
            temp_pdf = os.path.join(self.temp_dir, "temp.pdf")
            with open(temp_pdf, "wb") as f:
                prepared_writer.write(f)
            
            # Crear cuadernillo
            temp_reader = PdfReader(temp_pdf)
            booklet_writer = self._create_booklet(temp_reader)
            
            # Guardar resultado
            with open(self.output_pdf, "wb") as f:
                booklet_writer.write(f)
                
        finally:
            self._cleanup()
    
    def _cleanup(self):
        """Limpia archivos temporales."""
        if os.path.exists(self.temp_dir):
            for root, dirs, files in os.walk(self.temp_dir, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(self.temp_dir)


def parse_arguments():
    """
    Parsea los argumentos de línea de comandos.
    
    Returns:
        Tupla con (input_pdf, output_pdf, papers_per_booklet, cover_pages)
    """
    if len(sys.argv) != 5:
        print( "Debe ingresar el archivo de entrada, el archivo de salida," \
               "la cantidad de hojas por cuadernillo y las páginas de tapa.")
        print(f"Ejemplo: python {sys.argv[0]} input.pdf output.pdf 10 2")
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]
    papers_per_booklet = int(sys.argv[3])
    cover_pages = int(sys.argv[4])
    return input_pdf, output_pdf, papers_per_booklet, cover_pages


if __name__ == "__main__":
    input_pdf, output_pdf, papers_per_booklet, cover_pages = parse_arguments()
    
    processor = BookletProcessor(input_pdf, output_pdf, papers_per_booklet, cover_pages)
    processor.process()
    
    print("El archivo se ha guardado correctamente.")