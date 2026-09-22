# ReviewTap - Reglas del proyecto

## Reglas obligatorias
- Git: nunca ejecutes git add, commit, push, reset, rebase ni stash sin mi autorización explícita en el mismo mensaje. Antes de pedirla, muéstrame el git diff.
- Base de datos: nunca borres, recrees ni resetees ninguna base. No ejecutes flask db upgrade/downgrade contra producción. No imprimas DATABASE_URL.
- Secretos: no leas ni imprimas valores de .env, SECRET_KEY, DATABASE_URL ni claves de Render, y no los escribas en archivos.
- Alcance: solo D:\Proyectos\reviewtap. No toques otros proyectos ni hagas cambios no relacionados con la tarea.
- Cambios pequeños, modulares y por fases. Antes de tocar código, explica el plan en pocas líneas.
- Después de cambios relevantes, corre pytest tú mismo sin pedir permiso y muéstrame el resultado.
- No inventes datos, credenciales ni evidencia, y no afirmes que algo funciona si no lo comprobaste.
- Si pido "solo lectura" o "solo diagnostica", no modifiques nada.
- render.yaml, migrations/ y app/config.py solo se modifican si la tarea lo pide expresamente. No edites migraciones existentes.

## Estilo de respuesta
- Español, directo y conciso. Resultados en tablas. Indica rutas como archivo:línea.

## Contexto técnico
- Stack: Flask 3.1.3, SQLAlchemy 2.0.51, Flask-Migrate, Flask-Login, Flask-WTF, Flask-Limiter, Gunicorn. Local: Python 3.13. Render usa Python 3.14.3.
- Desarrollo y tests usan SQLite. Producción usa PostgreSQL en Render.
- Estructura: run.py, app/__init__.py (create_app), app/config.py, app/extensions.py, app/routes/, app/services/, app/templates/, migrations/, render.yaml.
- Render: Build Command "pip install -r requirements.txt && flask db upgrade". Start Command "gunicorn run:app". Variables de entorno definidas en el panel de Render: FLASK_ENV, BASE_URL, DATABASE_URL, SECRET_KEY (solo nombres, nunca valores).
- Producción https://reviewtap.onrender.com: registro y login funcionan. /dashboard exige sesión y devuelve JSON.