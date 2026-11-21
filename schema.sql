-- MoneyFlow - estrutura do banco (categorias e despesas)
-- Compatível com MySQL 8.0.16+ e MariaDB 10.2+
-- ATENÇÃO: este script apaga e recria o banco. Rode o seed.sql depois.

DROP DATABASE IF EXISTS moneyflow;

CREATE DATABASE moneyflow
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE moneyflow;

-- Categorias de gasto (ex.: Alimentação, Transporte)
CREATE TABLE categorias (
    id        INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome      VARCHAR(100) NOT NULL UNIQUE,
    descricao VARCHAR(255)
);

-- Despesas: cada uma pertence a uma categoria
CREATE TABLE despesas (
    id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    descricao    VARCHAR(150)  NOT NULL,
    valor        DECIMAL(10,2) NOT NULL,
    data         DATE          NOT NULL,
    essencial    ENUM('sim', 'nao') NOT NULL,
    categoria_id INT UNSIGNED  NOT NULL,

    CONSTRAINT fk_despesa_categoria
        FOREIGN KEY (categoria_id) REFERENCES categorias (id)
        ON DELETE RESTRICT   -- não deixa apagar categoria que tem despesas
        ON UPDATE CASCADE,

    CONSTRAINT chk_valor CHECK (valor > 0)
);

-- Índice para acelerar a ordenação e o filtro por valor
CREATE INDEX idx_despesas_valor ON despesas (valor);

-- Categorias padrão
INSERT INTO categorias (nome, descricao) VALUES
('Alimentação', 'Gastos com alimentação'),
('Transporte', 'Gastos com transporte'),
('Moradia', 'Gastos com moradia'),
('Lazer', 'Gastos com lazer'),
('Educação', 'Gastos com educação'),
('Saúde', 'Gastos com saúde'),
('Assinaturas', 'Serviços de assinatura'),
('Reserva de emergência', 'Economia para emergências');