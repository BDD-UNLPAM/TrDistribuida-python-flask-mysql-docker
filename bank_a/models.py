from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Numeric

db = SQLAlchemy()

class Cuenta(db.Model):
    __tablename__ = "cuentas"
    id_cliente = db.Column(db.Integer, primary_key=True)
    saldo = db.Column(Numeric(12, 2), nullable=False, default=0)

    def __repr__(self):
        return f"<Cuenta id={self.id_cliente} saldo={self.saldo}>"
