-- Creación de la tabla de inventario
CREATE TABLE inventario (
    id_producto VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    categoria VARCHAR(50),
    precio DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL,
    uso_tecnico TEXT,       -- Información clave para que el chatbot asesore
    alternativas TEXT       -- IDs de productos que pueden reemplazar a este
);

-- Inserción de productos de prueba (Ferretería típica)
INSERT INTO inventario (id_producto, nombre, categoria, precio, stock, uso_tecnico, alternativas) VALUES
('CL-MAD-2', 'Clavo para madera de 2 pulgadas', 'Clavos', 1.50, 150, 'Ideal para uniones sencillas de madera en interiores. No usar en exteriores porque se oxida.', 'TR-MAD-2'),
('CL-GALV-2', 'Clavo galvanizado de 2 pulgadas', 'Clavos', 2.50, 0, 'Clavo resistente a la oxidación. Ideal para construcciones de madera en exteriores o cercas.', 'TR-MAD-2'),
('TR-MAD-2', 'Tornillo para madera de 2 pulgadas', 'Tornillos', 3.00, 80, 'Tornillo de acero para madera. Ofrece mayor agarre y fijación estructural que un clavo común.', 'CL-MAD-2'),
('PE-PVC-4', 'Pegamento para tubería PVC de 4oz', 'Adhesivos', 85.00, 25, 'Pegamento de secado rápido para tuberías de agua fría de PVC bajo presión.', 'PE-MULTI-3'),
('PE-MULTI-3', 'Pegamento Epóxico Multiusos 3oz', 'Adhesivos', 120.00, 15, 'Pegamento de dos componentes ultra fuerte. Sirve para metal, madera, cerámica y algunos plásticos.', 'PE-PVC-4'),
('TA-CON-14', 'Tarugo plástico para concreto 1/4 pulgada', 'Fijaciones', 1.00, 500, 'Tarugo o taquete gris para fijar tornillos en paredes de concreto o ladrillo.', 'TA-CON-516'),
('TR-CON-14', 'Tornillo para concreto de 1/4 pulgada', 'Tornillos', 2.50, 300, 'Tornillo resistente para fijar repisas u objetos en concreto junto con un tarugo de 1/4.', 'TR-MAD-2');