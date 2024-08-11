from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4 # type: ignore
import os
import tempfile
import sys

MIN_PAPERS_PER_BOOKLET = 6
MAX_PAPERS_PER_BOOKLET = 12
WIDTH, HEIGHT = A4
TEMP_DIR = tempfile.mkdtemp()

INPUT_PDF = ''
OUTPUT_PDF = ''
papers_per_booklet = 0
PAGES_PER_BOOKLET = 0

working_pdf = None
working_pdf_reader = None
    
def put_and_check_parameters():
    global INPUT_PDF, OUTPUT_PDF, papers_per_booklet, PAGES_PER_BOOKLET

    if len(sys.argv) == 1:
        print("Debe ingresar el archivo de entrada, el archivo de salida y la cantidad de hojas por cuadernillo.")
        print(f"Ejemplo: python {sys.argv[0]} input.pdf output.pdf 10")
        sys.exit(1)

    if len(sys.argv) != 4:
        raise ValueError("Cantidad de argumentos incorrecta. Debe ingresar el archivo de entrada, el archivo de salida y la cantidad de hojas por cuadernillo.")

    try:
        INPUT_PDF = sys.argv[1]
        OUTPUT_PDF = sys.argv[2]
        papers_per_booklet = int(sys.argv[3])
    except ValueError:
        raise ValueError("El tercer argumento debe ser un número entero que indique las hojas por cuadernillo.")
    
    PAGES_PER_BOOKLET = papers_per_booklet * 4

    # input_pdf
    if not os.path.exists(INPUT_PDF):
        raise FileNotFoundError(f"El archivo {INPUT_PDF} no existe.")
    if not INPUT_PDF.endswith(".PDF") and not INPUT_PDF.endswith(".pdf"):
        raise ValueError("El archivo de entrada debe ser un PDF.")
    
    # output_pdf
    if not os.path.exists(OUTPUT_PDF):
        with open(OUTPUT_PDF, "w") as f:
            pass
    if not OUTPUT_PDF.endswith(".PDF") and not OUTPUT_PDF.endswith(".pdf"):
        raise ValueError("El archivo de salida debe ser un PDF.")
    
    # papers_per_booklet
    if not isinstance(papers_per_booklet, int):
        raise TypeError("El número de hojas por cuadernillo debe ser un número entero.")
    if papers_per_booklet < MIN_PAPERS_PER_BOOKLET or MAX_PAPERS_PER_BOOKLET < papers_per_booklet:
        raise ValueError(f"El número de hojas por cuadernillo debe estar entre {MIN_PAPERS_PER_BOOKLET} y {MAX_PAPERS_PER_BOOKLET}.")

    # Inicializar el lector después de la validación de parámetros
    global working_pdf_reader, working_pdf
    working_pdf = os.path.join(TEMP_DIR, "working.pdf")
    working_pdf_reader = PdfReader(INPUT_PDF)

def _add_blank_pages_to_writer(writer, num_pages = 1):
    '''
    Agrega `num_pages` páginas en blanco al final del documento de `writer`.
    '''
    global WIDTH, HEIGHT

    for _ in range(num_pages):
        writer.add_blank_page(WIDTH, HEIGHT)

def add_blank_pages():
    '''
    Agrega 2 páginas en blanco al inicio y final del working_pdf.
    Luego, agrega paginas en blanco al final hasta que la cantidad de hojas sea multiplo de pages_per_booklet.
    '''
    global working_pdf_reader, PAGES_PER_BOOKLET

    reader = working_pdf_reader
    writer = PdfWriter()
    total_pages = len(reader.pages)

    # Agregar 2 páginas en blanco al inicio
    _add_blank_pages_to_writer(writer, 2)

    # Agregar las páginas del documento original
    for i in range(total_pages):
        writer.add_page(reader.pages[i])

    # Agregar 2 páginas en blanco al final
    _add_blank_pages_to_writer(writer, 2)

    # Agregar páginas en blanco al final para que working_pdf tenga un 
    # número de hojas múltiplo de PAGES_PER_BOOKLET
    pages_to_complete = PAGES_PER_BOOKLET - len(writer.pages) % PAGES_PER_BOOKLET
    if pages_to_complete != PAGES_PER_BOOKLET:
        _add_blank_pages_to_writer(writer, pages_to_complete)

    # Guardar el documento final
    _update_working_pdf(writer)

def _update_working_pdf(writer):
    global working_pdf_reader

    with open(working_pdf, "wb") as output_file:
        writer.write(output_file)
    working_pdf_reader = PdfReader(working_pdf)

def create_booklet():
    '''
    Separa en cuadernillos de PAGES_PER_BOOKLET carillas el working_pdf.
    '''
    global working_pdf_reader, PAGES_PER_BOOKLET

    reader = working_pdf_reader
    total_pages = len(reader.pages)
    writer = PdfWriter()
    assert PAGES_PER_BOOKLET % 4 == 0 and total_pages % PAGES_PER_BOOKLET == 0 , "El número de hojas por cuadernillo debe ser múltiplo de 4 y el número total de hojas debe ser múltiplo de PAGES_PER_BOOKLET."
    for i in range(0, total_pages, PAGES_PER_BOOKLET):
        end = i + PAGES_PER_BOOKLET - 1
        init = i
        while (init < end):
            assert init + 1 < total_pages and end - 1 >= 0, "ERROR en _create_booklet"
            writer.add_page(reader.pages[init + 1])
            writer.add_page(reader.pages[end - 1])
            writer.add_page(reader.pages[end])#.rotate(180)) Los rota ya la impresora creo, 
            writer.add_page(reader.pages[init])#.rotate(180)) solo hace falta el orden.
            init += 2
            end -= 2
    
    _update_working_pdf(writer)

def save_booklet():
    global working_pdf_reader
    
    try:
        with open(OUTPUT_PDF, "wb") as output_file:
            writer = PdfWriter()
            reader = working_pdf_reader
            for i in range(len(reader.pages)):
                writer.add_page(reader.pages[i])
            writer.write(output_file)
    except Exception as e:
        print(f"Error al guardar el cuadernillo: {e}")
        raise
    finally:
        _cleanup_temp_files()

def _cleanup_temp_files():
    if os.path.exists(working_pdf):
        os.remove(working_pdf)
    if os.path.exists(TEMP_DIR):
        for root, dirs, files in os.walk(TEMP_DIR):
            for file in files:
                os.remove(os.path.join(root, file))
        os.rmdir(TEMP_DIR)

if __name__ == "__main__":
    put_and_check_parameters()
    add_blank_pages()
    create_booklet()
    save_booklet()
    print("El archivo se ha guardado correctamente.")

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