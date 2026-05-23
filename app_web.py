# =====================================================================
# INTERFAZ DE AUDITORÍA ACADÉMICA - FACULTAD DE INGENIERÍAS UTI
# Desarrollado por: Alejandro Tituaña
# Enfoque: Saneamiento de Código y Alta Disponibilidad (Sin imágenes locales)
# Motor: Groq Cloud (llama-3.3-70b-versatile)
# =====================================================================

import streamlit as st
from groq import Groq
import os
from pypdf import PdfReader

# 1. CONFIGURACIÓN VISUAL DEL FRAMEWORK
st.set_page_config(
    page_title="Agente UTI - Auditoría Académica", 
    page_icon="🎓", 
    layout="centered"
)

# =====================================================================
# INTERFAZ ESTÉTICA INSTITUCIONAL: INYECCIÓN DE CSS (MARCA DE AGUA UTI)
# =====================================================================
st.markdown(
    """
    <style>
    /* Marca de agua fija y centrada en el fondo de la pantalla */
    .main {
        background-image: url("https://www.uti.edu.ec/wp-content/uploads/2018/06/Logotipo-Indoamerica.png");
        background-repeat: no-repeat;
        background-position: center 50%;
        background-attachment: fixed;
        background-size: 40%;
    }
    
    /* Quitamos los fondos blancos por defecto de Streamlit para hacerlos transparentes */
    .stApp, .main, .block-container {
        background-color: transparent !important;
    }
    
    /* Contenedor de contraste: Asegura legibilidad 100% limpia sobre el fondo */
    .block-container {
        background-color: rgba(255, 255, 255, 0.94) !important;
        padding: 40px !important;
        border-radius: 12px;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);
        margin-top: 30px;
    }
    
    /* Estilización de botones institucionales */
    .stButton>button {
        background-color: #003366 !important;
        color: white !important;
        border-radius: 6px !important;
        width: 100%;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🎓 Asistente Virtual de Titulación - UTI")
st.write("Escribe tu consulta y el sistema localizará automáticamente el reglamento correcto en la base de datos.")
st.markdown("---")

# 2. AUTENTICACIÓN SEGURA (Poka-Yoke de Credenciales)
API_KEY = os.environ.get("GROQ_API_KEY")
if not API_KEY:
    st.error("🔑 Error de Infraestructura: No se ha detectado la 'GROQ_API_KEY' en los Secrets de Streamlit.")
    st.stop()

client = Groq(api_key=API_KEY)
MODELO_IA = "llama-3.3-70b-versatile"

# 3. ESCANEO Y LOGÍSTICA DE LA BODEGA DIGITAL (Ruta estandarizada)
DIRECTORIO_RAIZ = "documentos_uti"
mapa_archivos = {}

if os.path.exists(DIRECTORIO_RAIZ):
    for root, dirs, files in os.walk(DIRECTORIO_RAIZ):
        for file in files:
            if file.lower().endswith('.pdf'):
                ruta_completa = os.path.join(root, file)
                mapa_archivos[file] = ruta_completa

# 4. CAPTURA DE DATOS DE LA INTERFAZ (UI)
pdf_estudiante = st.file_uploader("Carga tu documento de prueba aquí (Opcional)", type=["pdf"])
consulta_alumno = st.text_input("¿Qué deseas consultar sobre tu proceso de titulación o normativas?")

if st.button("Ejecutar Consulta Inteligente"):
    if not consulta_alumno:
        st.warning("⚠️ Por favor, ingresa una pregunta para iniciar el análisis.")
    elif not mapa_archivos:
        st.error(f"❌ Error de Almacén: La carpeta '{DIRECTORIO_RAIZ}' está vacía o no existe en el repositorio.")
    else:
        with st.spinner("Buscando en la base normativa institucional..."):
            
            # --- PASO 1: ENRUTAMIENTO INTELIGENTE QUIRÚRGICO (Clasificación de Nombres) ---
            lista_nombres_archivos = "\n".join(mapa_archivos.keys())
            
            prompt_enrutador = f"""
            Eres el clasificador de inventario normativo de la UTI. Lee la lista de archivos PDF disponibles y determina cuál contiene la respuesta más exacta a la consulta del alumno.
            
            LISTA DE BODEGA:
            {lista_nombres_archivos}
            
            CONSULTA DEL ALUMNO: "{consulta_alumno}"
            
            Regla estricta: Devuelve ÚNICAMENTE el nombre del archivo seleccionado de la lista, en una sola línea. No agregues saludos, comentarios ni justificaciones. Si ninguno aplica, responde "NINGUNO".
            """
            
            try:
                # Consulta rápida al clasificador
                seleccion_enrutador = client.chat.completions.create(
                    model=MODELO_IA,
                    messages=[{"role": "user", "content": prompt_enrutador}],
                    temperature=0.0
                )
                
                respuesta_enrutador = seleccion_enrutador.choices[0].message.content.strip()
                archivos_seleccionados = [linea.strip() for linea in respuesta_enrutador.split("\n") if linea.strip() in mapa_archivos]
                
                # Fallback de control de errores
                if not archivos_seleccionados:
                    archivo_nombre = list(mapa_archivos.keys())[:1][0]
                else:
                    archivo_nombre = archivos_seleccionados[0]

                # --- PASO 2: EXTRACCIÓN Y TRUNCADO DE TEXTO (Control de Cuota TPM) ---
                texto_base_reducido = ""
                ruta_real = mapa_archivos[archivo_nombre]
                
                try:
                    reader = PdfReader(ruta_real)
                    texto_base_reducido += f"\n\n--- INICIO DEL DOCUMENTO: {archivo_nombre} ---\n"
                    
                    # Calibración de tolerancia: Máximo 12 páginas para no desbordar los 12,000 tokens por minuto
                    max_paginas = min(len(reader.pages), 12)
                    for i in range(max_paginas):
                        texto_base_reducido += reader.pages[i].extract_text() + "\n"
                except Exception as e:
                    st.error(f"⚠️ Error mecánico al leer el archivo físico: {archivo_nombre}")

                # --- PASO 3: LECTURA CONTROLADA DEL PDF DEL ESTUDIANTE ---
                texto_alumno = ""
                if pdf_estudiante is not None:
                    try:
                        reader_alumno = PdfReader(pdf_estudiante)
                        # Blindaje secundario: Máximo 8 páginas del documento del alumno
                        max_paginas_alumno = min(len(reader_alumno.pages), 8)
                        for i in range(max_paginas_alumno):
                            texto_alumno += reader_alumno.pages[i].extract_text() + "\n"
                    except:
                        pass

                # Panel de trazabilidad visual
                st.caption(f"🔍 *Filtro de Carga Activo -> Archivo Seleccionado:* **{archivo_nombre}**")

                # --- PASO 4: RAZONAMIENTO Y VEREDICTO FINAL ---
                prompt_maestro = f"""
                Actúas como el Agente Automatizado de Auditoría Académica de la Facultad de Ingenierías de la UTI.
                Tu objetivo es responder a la consulta utilizando EXCLUSIVAMENTE el texto provisto.

                === BASE DE CONOCIMIENTO INSTITUCIONAL ===
                {texto_base_reducido}
                
                === DOCUMENTO ADJUNTO DEL ESTUDIANTE ===
                {texto_alumno}
                ==========================================

                Reglas operativas de control de calidad:
                1. Responde de forma clara usando viñetas estructuradas y cita explícitamente el documento: {archivo_nombre}.
                2. Si la respuesta exacta no se encuentra en el texto provisto, responde textualmente: "La información solicitada no consta en los instructivos digitales. Por favor, acérquese a la ventanilla de Secretaría."
                3. No asumas, no inventes ni uses conocimiento externo.

                Consulta del estudiante a procesar: {consulta_alumno}
                """
                
                respuesta_final = client.chat.completions.create(
                    model=MODELO_IA,
                    messages=[{"role": "user", "content": prompt_maestro}],
                    temperature=0.1
                )
                
                # Despacho del resultado en interfaz limpia
                st.markdown("### 📝 Veredicto del Agente UTI:")
                st.info(respuesta_final.choices[0].message.content)
                st.success("✓ Proceso de auditoría digital completado sin defectos de cuota.")

            except Exception as e:
                st.error(f"❌ Excepción operativa en el clúster de Groq: {e}")