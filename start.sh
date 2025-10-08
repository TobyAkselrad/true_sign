#!/bin/bash
# Script para iniciar TrueSign sin activar venv manualmente

cd "$(dirname "$0")"

echo "🚀 Iniciando TrueSign..."
venv/bin/python app/run.py

