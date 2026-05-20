# =====================================================================
# INTERFAZ WEB DEL AGENTE DE AUDITORÍA ACADÉMICA - INDOAMÉRICA
# Desarrollado por: Alejandro Tituaña
# Enfoque: Enrutamiento Inteligente de Archivos (UX Optimizada sin Filtros)
# =====================================================================

import streamlit as st
from google import genai
from google.genai import types
import os
from pypdf import PdfReader

# Configuración visual de la plataforma
st.set_page_config(page_title="Agente UTI - Inteligente", page_icon="🎓", layout="centered")

st.title("🎓 Asistente Virtual de Titulación - UTI")
st.write("Dime tu duda académica y el sistema localizará automáticamente el reglamento correcto en la base de datos.")
st.markdown("---")

# 1. CONEXIÓN AL MOTOR DE IA
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("🔑 Error: No se ha detectado la GEMINI_API_KEY en los Secrets de Streamlit.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# 2. ESCANEO GLOBAL DE LA BODEGA DIGITAL
DIRECTORIO_RAIZ = "documentos_uti"
mapa_archivos = {}

if os.path.exists(DIRECTORIO_RAIZ):
    for root, dirs, files in os.walk(DIRECTORIO_RAIZ):
        for file in files:
            if file.lower().endswith('.pdf'):
                ruta_completa = os.path.join(root, file)
                # Guardamos el nombre del archivo como clave y su ruta completa como valor
                mapa_archivos[file] = ruta_completa

# 3. INTERFAZ DE USUARIO SIMPLE (Búsqueda Única)
pdf_estudiante = st.file_uploader("Carga tu documento de prueba aquí (Opcional)", type=["pdf"])
consulta_alumno = st.text_input("¿Qué deseas consultar sobre tu proceso de titulación o normativas?")

if st.button("Ejecutar Consulta Inteligente"):
    if not consulta_alumno:
        st.warning("⚠️ Por favor, ingresa una pregunta para iniciar el análisis.")
    elif not mapa_archivos:
        st.error("❌ Error: La bodega 'documentos_uti' está vacía o no contiene archivos PDF.")
    else:
        with st.spinner("Localizando el documento idóneo en la base de datos..."):
            
            # --- PASO 1: ENRUTAMIENTO INTELIGENTE (Filtro invisible de nombres) ---
            lista_nombres_archivos = "\n".join(mapa_archivos.keys())
            
            prompt_enrutador = f"""
            Actúas como el clasificador de inventario de la UTI. Tu única tarea es leer la siguiente lista de nombres de archivos PDF disponibles y determinar cuál o cuáles de ellos contienen la respuesta más probable a la consulta del alumno.

            === LISTA DE ARCHIVOS DISPONIBLES EN BODEGA ===
            {lista_nombres_archivos}
            ================================================
            
            Consulta del alumno: "{consulta_alumno}"

            Regla de respuesta: Devuelve ÚNICAMENTE los nombres de los archivos seleccionados de la lista, uno por línea, exactamente igual a como están escritos. No agregues explicaciones, saludos ni introducciones. Si ninguno aplica, devuelve "NINGUNO".
            """
            
            try:
                seleccion_enrutador = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt_enrutador
                )
                
                archivos_seleccionados = [linea.strip() for linea in seleccion_enrutador.text.split("\n") if linea.strip() in mapa_archivos]
                
                if not archivos_seleccionados:
                    st.info("ℹ️ La consulta no parece estar mapeada en los reglamentos digitales actuales. Intentando análisis general...")
                    archivos_seleccionados = list(mapa_archivos.keys())[:3] # Fallback de seguridad: toma los 3 primeros

                # --- PASO 2: EXTRACCIÓN QUIRÚRGICA DEL TEXTO ---
                texto_base_reducido = ""
                for archivo_nombre in archivos_seleccionados:
                    ruta_real = mapa_archivos[archivo_nombre]
                    try:
                        reader = PdfReader(ruta_real)
                        texto_base_reducido += f"\n\n--- INICIO: {archivo_nombre} ---\n"
                        for page in reader.pages:
                            texto_base_reducido += page.extract_text() + "\n"
                    except Exception as e:
                        continue

                # --- PASO 3: RESPUESTA FINAL AL ESTUDIANTE ---
                st.caption(f"🔍 *Documentos seleccionados estratégicamente:* {', '.join(archivos_seleccionados)}")
                
                prompt_maestro = f"""
                Actúas como el Agente Automatizado de Auditoría Académica de la Facultad de Ingenierías de la UTI.
                Responde con total precisión usando EXCLUSIVAMENTE el texto provisto.

                === TEXTO NORMATIVO SELECCIONADO ===
                {texto_base_reducido}
                ====================================

                Reglas operativas estrictas:
                1. Responde de forma clara usando viñetas y cita explícitamente el nombre del archivo del cual extrajiste la información.
                2. Si el texto no contiene la respuesta exacta, contesta: "La información solicitada no consta en los instructivos digitales. Por favor, acérquese a la ventanilla de Secretaría."
                3. No inventes datos.

                Consulta: {consulta_alumno}
                """
                
                paquete_envio = []
                if pdf_estudiante is not None:
                    bytes_data = pdf_estudiante.read()
                    documento_en_linea = types.Part.from_bytes(data=bytes_data, mime_type="application/pdf")
                    paquete_envio.append(documento_en_linea)
                
                paquete_envio.append(prompt_maestro)
                
                respuesta_final = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=paquete_envio
                )
                
                st.markdown("### 📝 Veredicto del Agente UTI:")
                st.info(respuesta_final.text)
                st.success("✓ Búsqueda automatizada optimizada con éxito.")

            except Exception as e:
                st.error(f"❌ Error operativo del motor: {e}")