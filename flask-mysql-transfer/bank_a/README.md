# BANK_A

- DB por defecto: `bank_a_db`
- Puerto por defecto: `5000`
- Otra API destino: `http://127.0.0.1:5001`

## Variables de entorno
- `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`
- `DEST_API_BASE` (URL de la otra API)
- `BANK_NAME` (Etiqueta de este banco / servicio)
- `FLASK_PORT`

## Comandos rápidos
```bash
# Crear y activar venv
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Crear base/tablas y datos iniciales en MySQL
# (abre un cliente mysql y ejecuta schema.sql)
# mysql -u root -p < schema.sql  (si tienes permisos)

# Correr la app
flask --app app.py run --port 5000 --debug
```
