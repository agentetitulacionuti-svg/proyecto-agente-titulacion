# =====================================================================
# INTERFAZ WEB DEL AGENTE DE AUDITORÍA ACADÉMICA - INDOAMÉRICA
# Desarrollado por: Alejandro Tituaña
# Migrado a: GROQ CLOUD (Plan Gratuito de Alta Disponibilidad)
# =====================================================================

import streamlit as st
from groq import Groq
import os
from pypdf import PdfReader

# Configuración visual de la plataforma
st.set_page_config(page_title="Agente UTI - Groq", page_icon="🎓", layout="centered")

st.title("🎓 Asistente Virtual de Titulación - UTI")
st.write("Motor de IA optimizado con Groq Cloud para consultas ilimitadas y fluidas.")
st.markdown("---")

# 1. CONEXIÓN AL MOTOR DE GROQ
# Dejamos el código limpio de contraseñas. El script buscará la llave en la nube.
API_KEY = os.environ.get("GROQ_API_KEY")
if not API_KEY:
    st.error("🔑 Error: No se ha detectado la GROQ_API_KEY en los Secrets de Streamlit.")
    st.stop()

client = Groq(api_key=API_KEY)
MODELO_IA = "llama-3.3-70b-versatile" # El modelo más potente y estable de Groq

# 2. ESCANEO GLOBAL DE LA BODEGA DIGITAL
DIRECTORIO_RAIZ = "documentos_uti"
mapa_archivos = {}

if os.path.exists(DIRECTORIO_RAIZ):
    for root, dirs, files in os.walk(DIRECTORIO_RAIZ):
        for file in files:
            if file.lower().endswith('.pdf'):
                ruta_completa = os.path.join(root, file)
                mapa_archivos[file] = ruta_completa

# 3. INTERFAZ DE USUARIO
pdf_estudiante = st.file_uploader("Carga tu documento de prueba aquí (Opcional)", type=["pdf"])
consulta_alumno = st.text_input("¿Qué deseas consultar sobre tu proceso de titulación o normativas?")

if st.button("Ejecutar Consulta Inteligente"):
    if not consulta_alumno:
        st.warning("⚠️ Por favor, ingresa una pregunta para iniciar el análisis.")
    elif not mapa_archivos:
        st.error("❌ Error: La bodega 'documentos_uti' está vacía o no tiene PDFs.")
    else:
        with st.spinner("Localizando documentos con el motor LPU de Groq..."):
            
            # --- PASO 1: ENRUTAMIENTO INTELIGENTE ---
            lista_nombres_archivos = "\n".join(mapa_archivos.keys())
            
            prompt_enrutador = f"""
            Eres el clasificador de la UTI. Lee la lista de PDFs disponibles y determina cuál o cuáles contienen la respuesta a la consulta.
            LISTA:
            {lista_nombres_archivos}
            
            CONSULTA: "{consulta_alumno}"
            Regla: Devuelve ÚNICAMENTE los nombres de los archivos seleccionados, uno por línea. No agregues texto extra. Si ninguno aplica, responde "NINGUNO".
            """
            
            try:
                # Consulta al enrutador usando la sintaxis oficial de Groq
                seleccion_enrutador = client.chat.completions.create(
                    model=MODELO_IA,
                    messages=[{"role": "user", "content": prompt_enrutador}],
                    temperature=0.0
                )
                
                respuesta_enrutador = seleccion_enrutador.choices[0].message.content
                archivos_seleccionados = [linea.strip() for linea in respuesta_enrutador.split("\n") if linea.strip() in mapa_archivos]
                
                if not archivos_seleccionados:
                    archivos_seleccionados = list(mapa_archivos.keys())[:3] # Fallback

                # --- PASO 2: EXTRACCIÓN DEL TEXTO ---
                texto_base_reducido = ""
                for archivo_nombre in archivos_seleccionados:
                    ruta_real = mapa_archivos[archivo_nombre]
                    try:
                        reader = PdfReader(ruta_real)
                        texto_base_reducido += f"\n\n--- INICIO: {archivo_nombre} ---\n"
                        for page in reader.pages:
                            texto_base_reducido += page.extract_text() + "\n"
                    except:
                        continue

                # --- PASO 3: RESPUESTA FINAL ---
                st.caption(f"🔍 *Documentos analizados críticamente:* {', '.join(archivos_seleccionados)}")
                
                # Extraemos también el PDF del alumno si existe para mandarlo como texto plano
                texto_alumno = ""
                if pdf_estudiante is not None:
                    try:
                        reader_alumno = PdfReader(pdf_estudiante)
                        for page in reader_alumno.pages:
                            texto_alumno += page.extract_text() + "\n"
                    except:
                        st.warning("⚠️ No se pudo extraer el texto de tu PDF adjunto.")

                prompt_maestro = f"""
                Actúas como el Agente Automatizado de Auditoría Académica de la Facultad de Ingenierías de la UTI.
                Responde con total precisión usando EXCLUSIVAMENTE el texto provisto.

                === BASE DE CONOCIMIENTO INSTITUCONAL ===
                {texto_base_reducido}
                
                === DOCUMENTO ADJUNTO DEL ESTUDIANTE ===
                {texto_alumno}
                ====================================

                Reglas operativas estrictas:
                1. Responde de forma clara usando viñetas y cita explícitamente el nombre del archivo normativo.
                2. Si el texto no contiene la respuesta exacta, contesta: "La información solicitada no consta en los instructivos digitales. Por favor, acérquese a la ventanilla de Secretaría."
                3. No inventes datos.

                Consulta: {consulta_alumno}
                """
                
                respuesta_final = client.chat.completions.create(
                    model=MODELO_IA,
                    messages=[{"role": "user", "content": prompt_maestro}],
                    temperature=0.2
                )
                
                st.markdown("### 📝 Veredicto del Agente UTI (Groq):")
                st.info(respuesta_final.choices[0].message.content)
                st.success("✓ Búsqueda procesada sin límites de cuota diarios.")

            except Exception as e:
                st.error(f"❌ Error operativo en el servidor de Groq: {e}")