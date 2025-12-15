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

Para modificar los pdfs antes de crear el cuadernillo a partir de un unico pdf son utiles los comandos de `qpdf` y `poppler-utils` incluidos en el contenedor Docker.

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

### Configuración básica

- **Orientación**: Horizontal/Apaisada (Landscape)
- **Impresión**: Doble cara
- **Voltear en**: Borde largo (Long Edge / Flip on Long Edge)
- **Páginas por hoja de un lado**: 2
- **Orden de las páginas**: Izquierda a derecha, arriba hacia abajo

### Configuración de márgenes

- **Sin escalar ni ajustar**: Tamaño real (100%)
- **Sin márgenes automáticos**: Desactivar "Ajustar al área imprimible"

### Pasos recomendados

1. Abrir el PDF generado
2. Seleccionar impresión doble cara con volteo en borde largo
3. Configurar 4 páginas por hoja en orientación horizontal
4. Desactivar cualquier ajuste automático de escala o márgenes
5. Imprimir todas las páginas en orden

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
PAPERS_PER_BOOKLET=10 # 4*PAPERS_PER_BOOKLET carillas por cuadernillo
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

### Usar comandos qpdf y poppler-utils con Docker

El contenedor incluye qpdf y poppler-utils para manipular PDFs. Puedes ejecutar comandos de tres maneras:

**1. Ejecutar de a un comando único:**

```bash
# Unir PDFs - Opción 1: pdfunite (MÁS SIMPLE)
docker-compose run --rm encuadernador pdfunite /app/input/file1.pdf /app/input/file2.pdf /app/output/merged.pdf

# Extraer páginas específicas
docker-compose run --rm encuadernador qpdf /app/input/input.pdf --pages . 1-7,12 -- /app/output/extracted.pdf

# Rotar páginas
docker-compose run --rm encuadernador qpdf /app/input/input.pdf --rotate=+90:1-7,12 -- /app/output/rotated.pdf

# Reparar el PDF corrupto
qpdf --linearize /app/input/file.pdf /app/output/file-reparado.pdf
```

**2. Modo interactivo (ejecutar varios comandos):**

```bash
# Iniciar shell interactivo
docker-compose run --rm encuadernador bash

# Dentro del contenedor puedes ejecutar:
pdfunite /app/input/resumen.pdf /app/input/ResumenLenguajes.pdf /app/output/resumenLenguajes.pdf
qpdf /app/input/input.pdf --pages . 1-7,12 -- /app/output/extracted.pdf
qpdf /app/input/input.pdf --rotate=+90:1-7,12 -- /app/output/rotated.pdf
exit
```

**Notas de qpdf**:

- Antes del archivo de salida es obligatorio el `--`.
- En vez de especificar un archivo de salida, puedes usar `--replace-input` para sobrescribir el archivo original.

**Notas de poppler-utils**:

- aun ninguna
