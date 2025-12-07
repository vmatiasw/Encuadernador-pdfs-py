FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

CMD ["sh", "-c", "python src/main.py \"/app/input/$INPUT_FILE\" \"/app/output/$OUTPUT_FILE\" \"$PAPERS_PER_BOOKLET\" \"$COVER_PAGES\""]
