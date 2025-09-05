-- Crear base y tabla para bank_b
CREATE DATABASE IF NOT EXISTS bank_b_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bank_b_db;

DROP TABLE IF EXISTS cuentas;
CREATE TABLE cuentas (
  id_cliente INT PRIMARY KEY,
  saldo DECIMAL(12,2) NOT NULL DEFAULT 0.00
);

-- Seed de ejemplo
INSERT INTO cuentas (id_cliente, saldo) VALUES
  (2, 1000.00);
