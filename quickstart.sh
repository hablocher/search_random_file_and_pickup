#!/bin/bash
# Quick start script for Linux/macOS

echo "===================================="
echo "Random File Picker - Quick Start"
echo "===================================="
echo ""

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Poetry não encontrado. Por favor, instale Poetry primeiro:"
    echo "https://python-poetry.org/docs/#installation"
    echo ""
    echo "Execute no terminal:"
    echo "curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

echo "Poetry encontrado!"
echo ""

# Install dependencies
echo "Instalando dependências..."
poetry install
if [ $? -ne 0 ]; then
    echo "Erro ao instalar dependências!"
    exit 1
fi

echo ""
echo "===================================="
echo "Instalação concluída!"
echo "===================================="
echo ""
echo "Para usar:"
echo "  poetry run rfp-gui              - Interface gráfica"
echo "  poetry run random-file-picker --help  - Linha de comando"
echo ""
