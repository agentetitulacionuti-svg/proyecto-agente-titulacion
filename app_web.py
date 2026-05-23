# =====================================================================
# INTERFAZ WEB DEL AGENTE DE AUDITORÍA ACADÉMICA - INDOAMÉRICA
# Desarrollado por: Alejandro Tituaña
# Enfoque: Blindaje Total Anticaídas (Control Estricto de Contexto de 12K)
# =====================================================================

import streamlit as st
from groq import Groq
import os
from pypdf import PdfReader

st.set_page_config(page_title="Agente UTI - Blindado", page_icon="🎓", layout="centered")

col1, col2 = st.columns([1, 4])
with col1:
    st.image("logo_uti.png", width=110)
with col2:
    st.title("Asistente Virtual de Titulación - UTI")
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
        with st.spinner("Procesando consulta bajo estándares de alta disponibilidad..."):
            
            # --- PASO 1: ENRUTAMIENTO INTELIGENTE QUIRÚRGICO ---
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
                archivos_seleccionados = [linea.strip() for linea in respuesta_enrutador.split("\n") if linea.strip() in mapa_archivos]
                
                if not archivos_seleccionados:
                    archivos_seleccionados = [list(mapa_archivos.keys())[:1][0]]
                else:
                    archivos_seleccionados = [archivos_seleccionados[0]]

                # --- PASO 2: EXTRACCIÓN EXTRA-LIMITADA (Poka-Yoke de TPM) ---
                texto_base_reducido = ""
                archivo_nombre = archivos_seleccionados[0]
                ruta_real = mapa_archivos[archivo_nombre]
                
                try:
                    reader = PdfReader(ruta_real)
                    texto_base_reducido += f"\n\n--- INICIO: {archivo_nombre} ---\n"
                    
                    # Calibración de seguridad: Máximo 12 páginas para proteger la cuota de Groq
                    max_paginas = min(len(reader.pages), 12)
                    for i in range(max_paginas):
                        texto_base_reducido += reader.pages[i].extract_text() + "\n"
                except:
                    st.error(f"⚠️ Error al abrir el archivo institucional.")

                # --- PASO 3: EXTRACCIÓN LIMITADA DEL PDF DEL ESTUDIANTE ---
                texto_alumno = ""
                if pdf_estudiante is not None:
                    try:
                        reader_alumno = PdfReader(pdf_estudiante)
                        # Limitación estricta a las primeras 8 páginas del archivo del alumno
                        max_paginas_alumno = min(len(reader_alumno.pages), 8)
                        for i in range(max_paginas_alumno):
                            texto_alumno += reader_alumno.pages[i].extract_text() + "\n"
                    except:
                        pass

                st.caption(f"🔍 *Documento seleccionado:* {archivo_nombre} (Límites de carga activos)")
                
                # --- PASO 4: FORMULACIÓN DE RESPUESTA ---
                prompt_maestro = f"""
                Actúas como el Agente de Auditoría Académica de la UTI.
                Responde con precisión usando EXCLUSIVAMENTE el texto provisto.

                === BASE DE CONOCIMIENTO ===
                {texto_base_reducido}
                
                === DOCUMENTO ADJUNTO ===
                {texto_alumno}
                ============================

                Reglas:
                1. Responde de forma clara usando viñetas y cita el documento: {archivo_nombre}.
                2. Si el texto no contiene la respuesta exacta, contesta exactamente: "La información solicitada no consta en los instructivos digitales. Por favor, acérquese a la ventanilla de Secretaría."
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
                st.success("✓ Proceso completado con éxito.")

            except Exception as e:
                st.error(f"❌ Error operativo en el servidor de Groq: {e}")