#!/bin/bash
# Script per creare l'eseguibile (Linux/Mac)

echo "Creazione eseguibile Matrici..."
echo ""

# Verifica installazione PyInstaller
if ! python3 -m pip show pyinstaller &> /dev/null; then
    echo "PyInstaller non trovato. Installazione in corso..."
    python3 -m pip install pyinstaller
fi

# Crea l'eseguibile
echo "Compilazione in corso..."
pyinstaller build_exe.spec

echo ""
if [ -f "dist/Matrici" ]; then
    echo "✓ Eseguibile creato con successo!"
    echo "Percorso: dist/Matrici"
else
    echo "✗ Errore nella creazione dell'eseguibile"
fi
