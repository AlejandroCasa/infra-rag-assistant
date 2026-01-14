#!/bin/bash
set -e

# Verificamos si la carpeta vector_db existe y tiene contenido
if [ ! -d "vector_db" ] || [ -z "$(ls -A vector_db)" ]; then
    echo "⚡ No Vector DB found. Running auto-ingestion inside Docker..."
    python src/ingest.py
else
    echo "✅ Vector DB found. Skipping ingestion."
fi

# Ejecutamos el comando original (la app de Streamlit)
echo "🚀 Starting InfraOps Guardian..."
exec "$@"