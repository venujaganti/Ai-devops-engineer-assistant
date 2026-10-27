FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY requirements-runtime.txt ./requirements-runtime.txt
RUN python -m pip install --upgrade pip && python -m pip install --no-cache-dir -r requirements-runtime.txt
COPY config ./config
COPY .streamlit ./.streamlit
COPY src ./src
COPY streamlit_app.py README.md ./
COPY deployment ./deployment
COPY data ./data
RUN useradd --create-home --uid 10001 appuser && chmod +x /app/deployment/start.sh && chown -R appuser:appuser /app
USER appuser
EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD python deployment/healthcheck.py
CMD ["/app/deployment/start.sh"]
