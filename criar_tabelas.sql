CREATE DATABASE IF NOT EXISTS california_cafe
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE california_cafe;

CREATE TABLE IF NOT EXISTS usuario (
    id     INT AUTO_INCREMENT PRIMARY KEY,
    email  VARCHAR(255) NOT NULL,
    nome   VARCHAR(255) NOT NULL,
    senha  VARCHAR(255) NOT NULL,
    CONSTRAINT uq_usuario_email UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS categoria (
	id 		 INT AUTO_INCREMENT PRIMARY KEY,
    nome	 VARCHAR(255) UNIQUE NOT NULL,
    descricao		 VARCHAR(500)	
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS produto (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    id_categoria     INT NOT NULL,
    cod_barras       VARCHAR(13) UNIQUE NOT NULL,
    nome             VARCHAR(255) NOT NULL,
    quantidade       INT NOT NULL,
    data_validade    DATE NOT NULL,
    valor_compra     FLOAT NOT NULL,
    valor_venda      FLOAT NOT NULL,
    lucro            FLOAT GENERATED ALWAYS AS (valor_venda - valor_compra) STORED,
    imagem           LONGBLOB,
    CONSTRAINT fk_produto_categoria
        FOREIGN KEY (id_categoria)
        REFERENCES categoria (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE usuario
    ADD COLUMN cargo VARCHAR(20) NOT NULL DEFAULT 'Vendedor';

ALTER TABLE usuario
    ADD CONSTRAINT chk_usuario_cargo CHECK (cargo IN ('Gerente', 'Vendedor'));
