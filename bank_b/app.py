from decimal import Decimal, InvalidOperation
from flask import Flask, request, render_template, jsonify, redirect, url_for
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
import requests
from config import Config
from models import db, Cuenta

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    @app.route("/")
    def home():
        # Permite elegir el cliente con ?id_cliente=
        try:
            id_cliente = int(request.args.get("id_cliente", "1"))
        except ValueError:
            id_cliente = 1

        with app.app_context():
            # Busca o crea la cuenta si no existe (solo para demo)
            cuenta = db.session.get(Cuenta, id_cliente)
            if not cuenta:
                cuenta = Cuenta(id_cliente=id_cliente, saldo=Decimal("0.00"))
                db.session.add(cuenta)
                db.session.commit()

            # Render HTML
            return render_template(
                "index.html",
                bank_name=app.config["BANK_NAME"],
                id_cliente=cuenta.id_cliente,
                saldo=str(cuenta.saldo),
            )

    # ---------- REST: Consultar cuenta ----------
    @app.get("/api/account/<int:id_cliente>")
    def get_account(id_cliente):
        cuenta = db.session.get(Cuenta, id_cliente)
        if not cuenta:
            return jsonify({"error": "Cuenta no encontrada"}), 404
        return jsonify({"id_cliente": cuenta.id_cliente, "saldo": str(cuenta.saldo)})

    # ---------- REST: Recibir acreditación ----------
    @app.post("/api/receive")
    def receive():
        data = request.get_json(silent=True) or {}
        try:
            to_id = int(data.get("to_id"))
            amount = Decimal(str(data.get("amount")))
            from_bank = str(data.get("from_bank"))
            from_id = int(data.get("from_id"))
        except Exception:
            return jsonify({"error": "Payload inválido"}), 400

        if amount <= 0:
            return jsonify({"error": "El monto debe ser positivo"}), 400

        try:
            with db.session.begin():
                # Bloquea la fila de destino
                stmt = select(Cuenta).where(Cuenta.id_cliente == to_id).with_for_update()
                cuenta = db.session.execute(stmt).scalar_one_or_none()

                if not cuenta:
                    # En demo, si no existe la creamos con saldo 0
                    cuenta = Cuenta(id_cliente=to_id, saldo=Decimal("0.00"))
                    db.session.add(cuenta)
                    db.session.flush()  # asegura PK

                cuenta.saldo = (cuenta.saldo or Decimal("0.00")) + amount
                db.session.add(cuenta)

            return jsonify({"status": "ok", "credited_to": to_id, "amount": str(amount)}), 200
        except IntegrityError as e:
            db.session.rollback()
            return jsonify({"error": "Error de BD al acreditar", "details": str(e)}), 500
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Fallo inesperado al acreditar", "details": str(e)}), 500

    # ---------- HTML/REST: Iniciar transferencia hacia la otra API ----------
    @app.post("/transfer")
    def transfer_form():
        # Endpoint HTML (form) que delega en la REST interna
        try:
            from_id = int(request.form.get("from_id"))
            to_id = int(request.form.get("to_id"))
            amount = Decimal(request.form.get("amount"))
        except Exception:
            return "Datos inválidos", 400

        return _initiate_transfer(from_id, to_id, amount)

    @app.post("/api/transfer")
    def transfer_api():
        data = request.get_json(silent=True) or {}
        try:
            from_id = int(data.get("from_id"))
            to_id = int(data.get("to_id"))
            amount = Decimal(str(data.get("amount")))
        except Exception:
            return jsonify({"error": "Payload inválido"}), 400

        return _initiate_transfer(from_id, to_id, amount)

    def _initiate_transfer(from_id: int, to_id: int, amount: Decimal):
        if amount <= 0:
            return jsonify({"error": "El monto debe ser positivo"}), 400

        # 1) Debitar localmente con bloqueo de fila
        try:
            with db.session.begin():
                stmt = select(Cuenta).where(Cuenta.id_cliente == from_id).with_for_update()
                cuenta = db.session.execute(stmt).scalar_one_or_none()
                if not cuenta:
                    return jsonify({"error": "Cuenta origen no existe"}), 404

                saldo_actual = cuenta.saldo or Decimal("0.00")
                if saldo_actual < amount:
                    return jsonify({"error": "Saldo insuficiente"}), 400

                cuenta.saldo = saldo_actual - amount
                db.session.add(cuenta)
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "No se pudo debitar (transacción)", "details": str(e)}), 500

        # 2) Llamar a la otra API para acreditar
        dest_base = app.config["DEST_API_BASE"].rstrip("/")
        try:
            resp = requests.post(
                f"{dest_base}/api/receive",
                json={"to_id": to_id, "amount": str(amount), "from_bank": app.config["BANK_NAME"], "from_id": from_id},
                timeout=10,
            )
            if resp.status_code // 100 != 2:
                # 3) Compensación: si falla el destino, revertimos el débito
                with db.session.begin():
                    stmt = select(Cuenta).where(Cuenta.id_cliente == from_id).with_for_update()
                    cuenta = db.session.execute(stmt).scalar_one_or_none()
                    if cuenta:
                        cuenta.saldo = (cuenta.saldo or Decimal("0.00")) + amount
                        db.session.add(cuenta)
                return jsonify({"error": "Fallo al acreditar en destino", "dest_status": resp.status_code, "dest_body": resp.text}), 502
        except Exception as e:
            # Compensación también en excepciones de red
            with db.session.begin():
                stmt = select(Cuenta).where(Cuenta.id_cliente == from_id).with_for_update()
                cuenta = db.session.execute(stmt).scalar_one_or_none()
                if cuenta:
                    cuenta.saldo = (cuenta.saldo or Decimal("0.00")) + amount
                    db.session.add(cuenta)
            return jsonify({"error": "Error de red al llamar destino", "details": str(e)}), 502

        return jsonify({"status": "ok", "debited_from": from_id, "credited_to": to_id, "amount": str(amount)}), 200

    return app

app = create_app()

if __name__ == "__main__":
    # Ejecutar con: flask --app app.py run --port 5001 --debug
    app.run(host="0.0.0.0", port=5001, debug=True)
