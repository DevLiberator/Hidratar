
#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

echo "========================================"
echo "       HIDRA - COMPILACAO LINUX"
echo "========================================"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 nao encontrado."
    exit 1
fi

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install plyer

python -m PyInstaller \
    --noconfirm \
    --clean \
    --onefile \
    --name Hidra \
    --hidden-import=plyer.platforms.linux.notification \
    main.py

echo
echo "Compilacao concluida!"
echo "Executavel: dist/Hidra"
echo
echo "Execute com: ./dist/Hidra"