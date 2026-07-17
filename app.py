import os
import sqlite3
from dotenv import load_dotenv
import google.generativeai as genai  # <-- Librería oficial de Google Gemini

load_dotenv()

# Configurar la API Key de Google Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Memoria en caché para el historial del chat estructurada para Gemini
# Formato requerido por Gemini: {"role": "user"|"model", "parts": ["..."]}
historial_conversacion = []

def inicializar_base_de_datos():
    """Crea la base de datos local de FerroTecniHN."""
    conn = sqlite3.connect("ferre_inventario.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventario (
        id_producto TEXT PRIMARY KEY,
        nombre TEXT,
        categoria TEXT,
        precio REAL,
        stock INTEGER,
        uso_tecnico TEXT,
        alternativas TEXT
    )
    """)
    cursor.execute("SELECT COUNT(*) FROM inventario")
    if cursor.fetchone()[0] == 0:
        productos = [
            ('CL-MAD-2', 'Clavo para madera de 2 pulgadas', 'Clavos', 1.50, 150, 'Ideal para uniones sencillas de madera en interiores. No usar en exteriores.', 'TR-MAD-2'),
            ('CL-GALV-2', 'Clavo galvanizado de 2 pulgadas', 'Clavos', 2.50, 0, 'Clavo resistente a la oxidación. Ideal para maderas en exteriores.', 'TR-MAD-2'),
            ('TR-MAD-2', 'Tornillo para madera de 2 pulgadas', 'Tornillos', 3.00, 80, 'Ofrece mayor agarre que un clavo en madera.', 'CL-MAD-2'),
            ('PE-PVC-4', 'Pegamento para tubería PVC de 4oz', 'Adhesivos', 85.00, 25, 'Para pegar tuberías de PVC de agua bajo presión.', 'PE-MULTI-3'),
            ('PE-MULTI-3', 'Pegamento Epóxico Multiusos 3oz', 'Adhesivos', 120.00, 12, 'Pegamento ultra fuerte de dos componentes para metal o plástico.', 'PE-PVC-4'),
            ('TA-CON-14', 'Tarugo plástico para concreto 1/4', 'Fijaciones', 1.00, 500, 'Tarugo gris para concreto o ladrillo.', 'TA-CON-516')
        ]
        cursor.executemany("INSERT INTO inventario VALUES (?, ?, ?, ?, ?, ?, ?)", productos)
        conn.commit()
    conn.close()

def buscar_productos_relacionados(pregunta_usuario):
    """Busca productos en la base de datos basados en palabras clave."""
    conn = sqlite3.connect("ferre_inventario.db")
    cursor = conn.cursor()
    palabras = pregunta_usuario.lower().split()
    query_condiciones = []
    valores = []
    
    for p in palabras:
        if len(p) > 3:
            query_condiciones.append("(nombre LIKE ? OR categoria LIKE ? OR uso_tecnico LIKE ?)")
            termino = f"%{p}%"
            valores.extend([termino, termino, termino])
            
    if not query_condiciones:
        cursor.execute("SELECT * FROM inventario LIMIT 10")
    else:
        sql = "SELECT * FROM inventario WHERE " + " OR ".join(query_condiciones)
        cursor.execute(sql, valores)
        
    resultados = cursor.fetchall()
    conn.close()
    
    inventario_texto = ""
    for prod in resultados:
        inventario_texto += (
            f"- Código: {prod[0]} | Producto: {prod[1]} | Categoría: {prod[2]} | "
            f"Precio: L.{prod[3]:.2f} | Stock: {prod[4]} unidades | "
            f"Uso sugerido: {prod[5]} | Alternativas: {prod[6]}\n"
        )
    return inventario_texto

def consultar_chatbot(pregunta_cliente):
    global historial_conversacion
    
    # 1. Buscar inventario relevante
    contexto_inventario = buscar_productos_relacionados(pregunta_cliente)
    
    # 2. Configurar el Prompt de Sistema (Instrucciones de comportamiento)
    system_instruction = (
        "Eres el asistente virtual experto de 'FerroTecniHN'. Tu misión es ayudar al cliente a elegir "
        "el producto adecuado para su proyecto y concretar la venta de forma muy amable.\n\n"
        "Reglas estrictas:\n"
        "1. Usa SIEMPRE los productos listados en el 'Inventario Disponible' provisto abajo.\n"
        "2. Si un producto que necesita el cliente NO TIENE STOCK (stock = 0), recomiéndale obligatoriamente "
        "la alternativa sugerida que sí tenga stock en el inventario.\n"
        "3. Responde de manera clara, técnica pero accesible.\n"
        "4. Muestra siempre los precios en Lempiras (L.) e indica la disponibilidad del stock.\n\n"
        f"--- INVENTARIO DISPONIBLE EN TIENDA ---\n{contexto_inventario}\n--------------------------------------"
    )
    
    try:
        # 3. Inicializar el modelo Gemini 1.5 Flash pasándole el System Prompt
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction
        )
        
        # 4. Iniciar el chat pasándole el historial de conversación acumulado
        chat = model.start_chat(history=historial_conversacion)
        
        # 5. Enviar el mensaje actual del usuario y obtener respuesta
        response = chat.send_message(pregunta_cliente)
        respuesta_ia = response.text
        
        # 6. Actualizar el historial en el formato interno que Gemini espera para la próxima iteración
        historial_conversacion.append({"role": "user", "parts": [pregunta_cliente]})
        historial_conversacion.append({"role": "model", "parts": [respuesta_ia]})
        
        # Limitar historial a las últimas 15 interacciones para un rendimiento óptimo
        if len(historial_conversacion) > 30:
            historial_conversacion = historial_conversacion[-30:]
            
        return respuesta_ia
        
    except Exception as e:
        return f"Error al procesar con Gemini: {str(e)}"

if __name__ == "__main__":
    inicializar_base_de_datos()
    print("==================================================")
    print("🤖 ¡Bienvenido al motor de FerroTecniHN! (Versión Google Gemini)")
    print("Base de datos cargada. Escribe 'salir' para terminar.")
    print("==================================================\n")
    
    while True:
        pregunta = input("Cliente: ")
        if pregunta.lower() == "salir":
            break
        
        respuesta = consultar_chatbot(pregunta)
        print(f"\nFerroTecniHN 🤖:\n{respuesta}\n")
        print("-" * 50)