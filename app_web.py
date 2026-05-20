# =====================================================================
# INTERFAZ WEB DEL AGENTE DE AUDITORÍA ACADÉMICA - INDOAMÉRICA
# Desarrollado por: Alejandro Tituaña
# Optimización: Control Estricto de TPM (Tokens per Minute) para Groq
# =====================================================================

import streamlit as st
from groq import Groq
import os
from pypdf import PdfReader

# Configuración visual de la plataforma
st.set_page_config(page_title="Agente UTI - Alta Disponibilidad", page_icon="🎓", layout="centered")

st.title("🎓 Asistente Virtual de Titulación - UTI")
st.write("Dime tu duda académica y el sistema localizará automáticamente el reglamento correcto.")
st.markdown("---")

# 1. CONEXIÓN AL MOTOR DE GROQ
API_KEY = os.environ.get("GROQ_API_KEY")
if not API_KEY:
    st.error("🔑 Error: No se ha detectado la GROQ_API_KEY en los Secrets de Streamlit.")
    st.stop()

client = Groq(api_key=API_KEY)
MODELO_IA = "llama-3.3-70b-versatile"

# 2. ESCANEO GLOBAL DE LA BODEGA DIGITAL
DIRECTORIO_RAIZ = "documentos_uti"
mapa_archivos = {}

if os.path.exists(DIRECTORIO_RAIZ):
    for root, dirs, files in os.walk(DIRECTORIO_RAIZ):
        for file in files:
            if file.lower().endswith('.pdf'):
                ruta_completa = os.path.join(root, file)
                mapa_archivos[file] = ruta_completa

# 3. INTERFAZ DE USUARIO SIMPLE
pdf_estudiante = st.file_uploader("Carga tu documento de prueba aquí (Opcional)", type=["pdf"])
consulta_alumno = st.text_input("¿Qué deseas consultar sobre tu proceso de titulación o normativas?")

if st.button("Ejecutar Consulta Inteligente"):
    if not consulta_alumno:
        st.warning("⚠️ Por favor, ingresa una pregunta para iniciar el análisis.")
    elif not mapa_archivos:
        st.error("❌ Error: La bodega 'documentos_uti' está vacía o no contiene archivos PDF.")
    else:
        with st.spinner("Localizando y procesando el documento idóneo en la base de datos..."):
            
            # --- PASO 1: ENRUTAMIENTO INTELIGENTE (Lista de archivos limpia) ---
            lista_nombres_archivos = "\n".join(mapa_archivos.keys())
            
            prompt_enrutador = f"""
            Eres el clasificador de la UTI. Lee la lista de PDFs y determina cuál contiene la respuesta a la consulta.
            LISTA:
            {lista_nombres_archivos}
            
            CONSULTA: "{consulta_alumno}"
            Regla: Devuelve ÚNICAMENTE el nombre del archivo principal que tenga la respuesta exacta. Solo una línea, nada más.
            """
            
            try:
                seleccion_enrutador = client.chat.completions.create(
                    model=MODELO_IA,
                    messages=[{"role": "user", "content": prompt_enrutador}],
                    temperature=0.0
                )
                
                respuesta_enrutador = seleccion_enrutador.choices[0].message.content.strip()
                
                # Buscamos si el archivo devuelto es válido
                archivos_seleccionados = [linea.strip() for linea in respuesta_enrutador.split("\n") if linea.strip() in mapa_archivos]
                
                # Si el enrutador falló o eligió demasiados, forzamos a tomar solo el primero más importante
                if not archivos_seleccionados:
                    archivos_seleccionados = [list(mapa_archivos.keys())[:1][0]]
                else:
                    archivos_seleccionados = [archivos_seleccionados[0]] # Poka-Yoke: Tomamos estrictamente SOLO EL MEJOR archivo para no saturar los tokens

                # --- PASO 2: EXTRACCIÓN LIMITADA DE TEXTO ---
                texto_base_reducido = ""
                archivo_nombre = archivos_seleccionados[0]
                ruta_real = mapa_archivos[archivo_nombre]
                
                try:
                    reader = PdfReader(ruta_real)
                    texto_base_reducido += f"\n\n--- INICIO: {archivo_nombre} ---\n"
                    
                    # Filtro de seguridad: Si el PDF es gigantesco (más de 25 páginas), solo leemos las primeras 25
                    # para mantener el envío por debajo del límite de tokens por minuto (TPM)
                    max_paginas = min(len(reader.pages), 25)
                    for i in range(max_paginas):
                        texto_base_reducido += reader.pages[i].extract_text() + "\n"
                        
                    if len(reader.pages) > 25:
                        texto_base_reducido += "\n[Texto truncado por alta extensión para optimización del sistema]\n"
                except:
                    st.error(f"⚠️ Error al abrir el archivo físico: {archivo_nombre}")

                # --- PASO 3: RESPUESTA FINAL AL ESTUDIANTE ---
                st.caption(f"🔍 *Documento seleccionado estratégicamente (Filtro TPM Activo):* {archivo_nombre}")
                
                texto_alumno = ""
                if pdf_estudiante is not None:
                    try:
                        reader_alumno = PdfReader(pdf_estudiante)
                        for page in reader_alumno.pages:
                            texto_alumno += page.extract_text() + "\n"
                    except:
                        pass

                prompt_maestro = f"""
                Actúas como el Agente Automatizado de Auditoría Académica de la Facultad de Ingenierías de la UTI.
                Responde con total precisión usando EXCLUSIVAMENTE el texto provisto.

                === BASE DE CONOCIMIENTO INSTITUCIONAL ===
                {texto_base_reducido}
                
                === DOCUMENTO ADJUNTO DEL ESTUDIANTE ===
                {texto_alumno}
                ====================================

                Reglas operativas estrictas:
                1. Responde de forma clara usando viñetas y cita el documento: {archivo_nombre}.
                2. Si el texto no contiene la respuesta exacta, contesta: "La información solicitada no consta en los instructivos digitales. Por favor, acérquese a la ventanilla de Secretaría."
                3. No inventes datos.

                Consulta: {consulta_alumno}
                """
                
                respuesta_final = client.chat.completions.create(
                    model=MODELO_IA,
                    messages=[{"role": "user", "content": prompt_maestro}],
                    temperature=0.2
                )
                
                st.markdown("### 📝 Veredicto del Agente UTI:")
                st.info(respuesta_final.choices[0].message.content)
                st.success("✓ Búsqueda procesada con éxito y balanceo de carga completado.")

            except Exception as e:
                st.error(f"❌ Error operativo en el servidor de Groq: {e}")