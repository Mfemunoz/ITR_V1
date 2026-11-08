FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY ITR_V1/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt \
    && pip install "psycopg[binary]>=3.2,<4"

COPY ITR_V1/ /app/ITR_V1/

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=3)" || exit 1

CMD ["streamlit", "run", "ITR_V1/abastecimiento_v2_mockup.py", "--server.address=0.0.0.0", "--server.port=8501"]
