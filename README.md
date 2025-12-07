# Encuadernador de PDFs

Convierte archivos PDF en cuadernillos listos para imprimir en formato doble faz.

## ¿Qué hace?

Transforma un PDF normal en un PDF reorganizado para imprimir como cuadernillo:

- Reorganiza las páginas para impresión doble faz
- Agrega páginas en blanco donde sea necesario
- Soporta páginas de tapa opcionales
- Divide el documento en cuadernillos del tamaño especificado

## Uso

```bash
python src/main.py <entrada.pdf> <salida.pdf> <hojas_por_cuadernillo> [páginas_tapa]
```

### Parámetros

- `entrada.pdf`: Archivo PDF original
- `salida.pdf`: Archivo PDF de salida (cuadernillo)
- `hojas_por_cuadernillo`: Número de hojas físicas por cuadernillo (recomendado entre 6 y 12)
- `páginas_tapa`: Número de páginas en blanco al inicio y final (default: 0)

### Ejemplos

```bash
# Cuadernillo de 10 hojas sin tapa
python src/main.py libro.pdf libro_cuadernillo.pdf 10 0

# Cuadernillo de 8 hojas con 2 páginas de tapa
python src/main.py libro.pdf libro_cuadernillo.pdf 8 2
```

## Impresión

El PDF generado debe imprimirse con estas configuraciones:

- **4 carillas por hoja**
- **Doble faz** (voltear en borde largo)
- **Sin ajustar márgenes** (configurar manualmente en la impresora)
- Orden de lectura: izquierda a derecha, arriba hacia abajo

## Requisitos

```bash
pip install -r requirements.txt
```

## Con Docker

Crea un archivo `.env` en la raíz del proyecto:

```bash
INPUT_DIR=./mis-pdfs
OUTPUT_DIR=./mis-pdfs
INPUT_FILE=mi-libro.pdf
OUTPUT_FILE=mi-libro-cuadernillo.pdf
PAPERS_PER_BOOKLET=10
COVER_PAGES=0
```

Luego ejecuta:

```bash
docker-compose up
```

### Variables de entorno (todas requeridas)

- `INPUT_DIR`: Carpeta local con el PDF de entrada
- `OUTPUT_DIR`: Carpeta local para el PDF de salida
- `INPUT_FILE`: Nombre del archivo de entrada (dentro de INPUT_DIR)
- `OUTPUT_FILE`: Nombre del archivo de salida (se creará en OUTPUT_DIR)
- `PAPERS_PER_BOOKLET`: Hojas por cuadernillo (entre 6 y 12)
- `COVER_PAGES`: Páginas de tapa
