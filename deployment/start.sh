#!/bin/sh
set -eu

if [ "${PROMETHEUS_METRICS_ENABLED:-false}" = "true" ]; then
  python -m src.devops_ai.observability.metrics_server &
fi

exec python -m streamlit run streamlit_app.py \
  --server.address=0.0.0.0 \
  --server.port=8501 \
  --server.headless=true
