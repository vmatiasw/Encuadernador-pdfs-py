FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y qpdf poppler-utils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

CMD ["sh", "-c", "python src/main.py \"/app/input/$INPUT_FILE\" \"/app/output/$OUTPUT_FILE\" \"$PAPERS_PER_BOOKLET\" \"$COVER_PAGES\""]
