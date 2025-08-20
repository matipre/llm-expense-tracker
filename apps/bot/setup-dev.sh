#!/bin/bash

echo "🚀 Configurando entorno de desarrollo Python..."

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Actualizar pip
echo "⬆️ Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias del proyecto
echo "📚 Instalando dependencias del proyecto..."
pip install -r requirements.txt

# Instalar dependencias de desarrollo
echo "🛠️ Instalando dependencias de desarrollo..."
pip install -e ".[dev]"

# Instalar pre-commit hooks
echo "🔒 Configurando pre-commit hooks..."
pre-commit install

# Crear directorio de tipos si no existe
mkdir -p typings

echo "✅ Entorno de desarrollo configurado correctamente!"
echo ""
echo "Para activar el entorno virtual en el futuro:"
echo "  source venv/bin/activate"
echo ""
echo "Para ejecutar el linter:"
echo "  ruff check ."
echo ""
echo "Para formatear el código:"
echo "  black ."
echo ""
echo "Para ordenar imports:"
echo "  isort ."
