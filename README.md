Aplicación simple de control de jornada (modo oscuro y responsive).

Instalación:
1. python -m venv .venv && source .venv/bin/activate
2. pip install -r requirements.txt

Ejecutar:
- python main.py
o
- uvicorn main:app --reload --host 0.0.0.0 --port 8000

Funcionalidad:
- "Marcar Entrada" crea una entrada con hora de inicio.
- "Marcar Salida" cierra la entrada abierta más reciente.
Base de datos: SQLite en ./app.db (connect_args={'check_same_thread': False}).