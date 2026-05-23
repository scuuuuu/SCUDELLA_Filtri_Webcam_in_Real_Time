#!/bin/bash
# run.sh — avvia l'applicazione webcam filtri

set -e

# controlla che python3 sia disponibile
if ! command -v python3 &> /dev/null; then
    echo "Errore: python3 non trovato. Installa Python 3.9 o superiore."
    exit 1
fi

# se non esiste un venv, lo crea e installa le dipendenze
if [ ! -d "venv" ]; then
    echo "Creo l'ambiente virtuale..."
    python3 -m venv venv
    echo "Installo le dipendenze..."
    venv/bin/pip install --upgrade pip
    venv/bin/pip install -r requirements.txt
fi

# crea le cartelle di output se non esistono
mkdir -p screenshots videos assets

echo "Avvio Webcam Filtri..."
venv/bin/python main.py