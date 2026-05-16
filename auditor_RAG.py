# =====================================================================
# INTERFAZ DE AUDITORÍA ACADÉMICA - FACULTAD DE INGENIERÍAS UTI
# Desarrollado por: Alejandro Tituaña
# Enfoque: Poka-Yoke Digital / Arquitectura de Producción Google GenAI
# =====================================================================

from google import genai
import os

# 1. AUTENTICACIÓN
API_KEY = "AIzaSyC4eTyMAdtmlKU9Q9RPsRZWQIhYdAbVErU"
client = genai.Client(api_key=API_KEY)

# 2. CONFIGURACIÓN DE LAS FUENTES DE INFORMACIÓN (Múltiples Documentos)
lista_instructivos = [
    "../PDF legal - pagina indoamerica/Instructivos/INSTRU-ORG-APREN-LINEA-DIST-SEMI.pdf",
    "../PDF legal - pagina indoamerica/Instructivos/Instructivo-para-subida-de-titulos-1.pdf"
]

base_conocimiento_archivos = []

print("Iniciando fase de Recuperación Multi-Documento (Retrieval)...")

for ruta in lista_instructivos:
    if not os.path.exists(ruta):
        print(f"[ERROR OPERATIVO]: No se encontró el archivo en: '{ruta}'")
        print("Por favor, verifica que las carpetas y mayúsculas coincidan exactamente.")
    else:
        print(f"Indexando en el servidor de Google: '{ruta}'...")
        archivo_subido = client.files.upload(file=ruta)
        base_conocimiento_archivos.append(archivo_subido)

# 3. PROCESAMIENTO E INGENIERÍA DE PROMPT
if len(base_conocimiento_archivos) > 0:
    print(f"✓ Éxito: {len(base_conocimiento_archivos)} documentos listos en la mesa de trabajo.\n")
    
    consulta_estudiante = "¿Cuáles son los pasos obligatorios que debo seguir para subir mi título a la plataforma?"

    prompt_maestro = f"""
    Actúas como el Agente Automatizado de Auditoría Académica de la Facultad de Ingenierías de la UTI.
    Tu objetivo es responder a la consulta del estudiante utilizando EXCLUSIVAMENTE la información
    de los documentos de instructivos provistos.

    Reglas operativas estrictas:
    1. Consolida la información de ambos documentos si es necesario para dar una respuesta completa.
    2. Si la respuesta exacta se encuentra en los textos, redacta los pasos de forma clara, ordenada (usa viñetas) y cita el nombre del instructivo correspondiente.
    3. Si la información NO está explícita, responde exactamente: "La información solicitada no consta en los instructivos digitales. Por favor, acérquese a la ventanilla de Secretaría."
    4. No asumas, no inventes ni utilices conocimiento externo bajo ninguna circunstancia.

    Consulta del estudiante a procesar: {consulta_estudiante}
    """

    print("Analizando consulta contra el lote de documentos normativos con Gemini 2.5 Flash...")
    
    paquete_envio = base_conocimiento_archivos + [prompt_maestro]
    
    # AJUSTE TÉCNICO: Actualización al motor de producción compatible con GenAI v2
    respuesta = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=paquete_envio
    )

    # 4. SALIDA Y DESPACHO DEL VEREDICTO
    print("\n================ VEREDICTO DEL AGENTE UTI ================")
    print(respuesta.text)
    print("==========================================================")
    print("Proceso completado de forma eficiente y libre de defectos.")
else:
    print("[FALLO DE SISTEMA]: No se pudo procesar porque el lote de archivos está vacío.")