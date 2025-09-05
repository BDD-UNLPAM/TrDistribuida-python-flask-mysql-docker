# Flask + MySQL: Transferencia entre dos APIs

Este proyecto contiene **dos APIs REST independientes** (`bank_a` y `bank_b`) que se comunican entre sí para realizar **transferencias bancarias**. Cada API:
- Se conecta a **su propia base de datos MySQL**.
- Expone una **página HTML** para ver el saldo de un cliente y hacer una transferencia hacia la otra API.
- Implementa **transacciones** y **bloqueos de fila** (SELECT FOR UPDATE) para evitar condiciones de carrera.
- La tabla principal es `cuentas` con `id_cliente` (PK) y `saldo` (`DECIMAL(12,2)`).

> **Nota:** Esto es un demo educativo. No es un sistema bancario real. Falta autenticación, autorización, validación fuerte, auditoría, idempotencia, etc.

## Requisitos
- Python 3.10+
- MySQL 8+ (puede ser una sola instancia con **dos bases**: `bank_a_db` y `bank_b_db`)
- (Opcional) `virtualenv`

## Cómo levantar cada servicio

1. **Crea las bases y tablas** ejecutando `schema.sql` de cada servicio en tu MySQL:
   ```sql
   -- Para bank_a
   SOURCE schema.sql;
   -- Asegúrate de estar en la base correcta antes (USE bank_a_db;)
   ```
   Repite para `bank_b`.

2. **Configura variables de entorno** (o edita `config.py` directamente):
   - `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`
   - `DEST_API_BASE` (URL base de la **otra** API), p.ej. para `bank_a`: `http://127.0.0.1:5001`
   - `FLASK_PORT` (por defecto 5000 en A y 5001 en B)

3. **Instala dependencias** en cada carpeta:
   ```bash
   cd bank_a
   python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   flask --app app.py run --port 5000 --debug
   ```
   En otra terminal levanta `bank_b`:
   ```bash
   cd bank_b
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   flask --app app.py run --port 5001 --debug
   ```

4. **Probar en el navegador**:
   - `http://127.0.0.1:5000/?id_cliente=1` (bank A)
   - `http://127.0.0.1:5001/?id_cliente=2` (bank B)

Los **IDs de cliente** iniciales por defecto son 1 y 2 (uno en cada banco) y el saldo inicial es 1000.00.

## Endpoints principales

- `GET /api/account/<id_cliente>` → JSON con saldo.
- `POST /api/transfer` → inicia transferencia (requiere `from_id`, `to_id`, `amount`).
- `POST /api/receive` → acredita el monto en el banco destino (requiere `to_id`, `amount`, `from_bank`, `from_id`).

## Seguridad y consideraciones
- Se usa `SELECT FOR UPDATE` al debitar/acreditar para evitar condiciones de carrera.
- Si el **acreditado** en el banco destino falla, se **revierte** el débito (compensación simple).
- Para producción: agregar **autenticación**, **firma de mensajes/webhooks**, **TLS**, **idempotencia**, **logs de auditoría**, **reintentos** con backoff, etc.
