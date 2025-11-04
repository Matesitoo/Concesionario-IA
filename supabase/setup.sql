-- Eliminar tablas si existen (para limpiar)
DROP TABLE IF EXISTS pedidos;
DROP TABLE IF EXISTS autos;
DROP TABLE IF EXISTS clientes;
DROP TYPE IF EXISTS estado_pedido;
DROP TYPE IF EXISTS tipo_combustible;

-- Crear tipos ENUM
CREATE TYPE estado_pedido AS ENUM ('pendiente', 'aprobado', 'entregado', 'cancelado');
CREATE TYPE tipo_combustible AS ENUM ('gasolina', 'diesel', 'eléctrico', 'híbrido');

-- Crear tabla clientes
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    telefono VARCHAR,
    direccion VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Crear tabla autos
CREATE TABLE autos (
    id SERIAL PRIMARY KEY,
    marca VARCHAR NOT NULL,
    modelo VARCHAR NOT NULL,
    año INTEGER NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    color VARCHAR,
    combustible tipo_combustible NOT NULL,
    disponible BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Crear tabla pedidos
CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(id),
    auto_id INTEGER REFERENCES autos(id),
    fecha_pedido TIMESTAMP DEFAULT NOW(),
    estado estado_pedido DEFAULT 'pendiente',
    total DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insertar datos de ejemplo
INSERT INTO clientes (nombre, email, telefono, direccion) VALUES
('Juan Pérez', 'juan@email.com', '123456789', 'Calle 123'),
('María García', 'maria@email.com', '987654321', 'Avenida 456');

INSERT INTO autos (marca, modelo, año, precio, color, combustible, disponible) VALUES
('Toyota', 'Corolla', 2023, 25000.00, 'Blanco', 'gasolina', true),
('Honda', 'Civic', 2023, 27000.00, 'Negro', 'gasolina', true),
('Tesla', 'Model 3', 2023, 45000.00, 'Rojo', 'eléctrico', true);

INSERT INTO pedidos (cliente_id, auto_id, total, estado) VALUES
(1, 1, 25000.00, 'pendiente'),
(2, 3, 45000.00, 'aprobado');