# =====================================================================
# INTERFAZ WEB DEL AGENTE DE AUDITORÍA ACADÉMICA - INDOAMÉRICA
# Desarrollado por: Alejandro Tituaña
# Enfoque: Poka-Yoke por Segregación de Carpetas (Control de Cuota API)
# =====================================================================

import streamlit as st
from google import genai
from google.genai import types
import os
from pypdf import PdfReader

# Configuración del Layout visual de la página web institucional
st.set_page_config(page_title="Agente UTI - Auditoría", page_icon="🎓", layout="centered")

st.title("🎓 Asistente Virtual de Titulación - UTI")
st.markdown("---")

# 1. CONEXIÓN AL MOTOR DE IA
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("🔑 Error: No se ha detectado la GEMINI_API_KEY en las variables de entorno o Secrets de Streamlit.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# 2. SELECCIÓN DE FILTRO DE BÚSQUEDA (Tu gran idea)
st.subheader("📁 Filtro de Selección de Base Normativa")

# Diccionario para mapear los nombres bonitos de la pantalla con las carpetas reales
carpetas_opciones = {
    "Todos los Documentos (Carga Completa)": "TODOS",
    "📚 Guías e Instructivos": "Guías e Instructivos",
    "📝 Formatos y Solicitudes": "Formatos y solicitudes",
    "🏛️ Modelos Educativos y Políticas": "PDF legal - pagina Indoamerica/Modelos educativos y Politicas",
    "⚖️ Normativa y Legislación Superior": "PDF legal - pagina Indoamerica/Normativa y Lesgislación Superior",
    "🤝 Protocolos y Bienestar": "PDF legal - pagina Indoamerica/Protocolos y Bienestar",
    "📜 Reglamentos (Titulación y Académicos)": "PDF legal - pagina Indoamerica/Reglamentos (Titulacián y Académicos)",
    "🎓 Plantillas y Estructuras de Tesis": "Plantillas y Estructuras de Tesis"
}

seleccion_usuario = st.selectbox(
    "Selecciona la sección específica donde deseas que el Agente busque la información:",
    options=list(carpetas_opciones.keys())
)

# Definimos el directorio base general
DIRECTORIO_RAIZ = "documentos_uti"
lista_instructivos = []

if os.path.exists(DIRECTORIO_RAIZ):
    subcarpeta_elegida = carpetas_opciones[seleccion_usuario]
    
    # Si elige "TODOS", el sistema barre toda la bodega recursivamente
    if subcarpeta_elegida == "TODOS":
        for root, dirs, files in os.walk(DIRECTORIO_RAIZ):
            for file in files:
                if file.lower().endswith('.pdf'):
                    lista_instructivos.append(os.path.join(root, file))
    else:
        # Si elige una sección, armamos la ruta directa a esa carpeta únicamente
        ruta_especifica = os.path.join(DIRECTORIO_RAIZ, subcarpeta_elegida)
        if os.path.exists(ruta_especifica):
            for root, dirs, files in os.walk(ruta_especifica):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        lista_instructivos.append(os.path.join(root, file))

    lista_instructivos.sort()

# Extraemos el texto usando la memoria caché indexada al filtro seleccionado
@st.cache_data
def extraer_texto_base_conocimiento(archivos, filtro):
    texto_consolidado = ""
    for nombre_archivo in archivos:
        if os.path.exists(nombre_archivo):
            try:
                reader = PdfReader(nombre_archivo)
                texto_consolidado += f"\n\n--- INICIO DOCUMENTO: {nombre_archivo} ---\n"
                for page in reader.pages:
                    texto_consolidado += page.extract_text() + "\n"
                texto_consolidado += f"--- FIN DOCUMENTO: {nombre_archivo} ---\n"
            except Exception as e:
                st.error(f"⚠️ Error al leer {nombre_archivo}: {e}")
    return texto_consolidado

# Pasamos la lista filtrada y el nombre de la selección para refrescar la caché si cambia el filtro
base_conocimiento_texto = extraer_texto_base_conocimiento(lista_instructivos, seleccion_usuario)

# 3. INTERFAZ DE USUARIO (Módulo de Consulta)
st.markdown("---")
st.subheader("📋 Módulo de Consulta y Auditoría de Documentos")
st.write(f"🔍 *Buscando activamente en la sección:* **{seleccion_usuario}** ({len(lista_instructivos)} archivos PDF detectados).")

pdf_estudiante = st.file_uploader("Carga tu documento aquí (Opcional)", type=["pdf"])
consulta_alumno = st.text_input("Escribe tu consulta académica sobre el proceso:")

if st.button("Ejecutar Auditoría Digital"):
    if not consulta_alumno:
        st.warning("⚠️ Por favor, ingresa una pregunta para iniciar el análisis.")
    elif not base_conocimiento_texto:
        st.error(f"❌ Error: No se encontraron archivos PDF válidos en la sección seleccionada: '{seleccion_usuario}'.")
    else:
        with st.spinner("Analizando documentos y normativas sectorizadas con Gemini 2.5 Flash..."):
            
            prompt_maestro = f"""
            Actúas como el Agente Automatizado de Auditoría Académica de la Facultad de Ingenierías de la UTI.
            Tu objetivo es responder a la consulta del estudiante utilizando EXCLUSIVAMENTE el texto de los
            documentos provistos en esta subsección seleccionada.

            === BASE DE CONOCIMIENTO NORMATIVA ({seleccion_usuario}) ===
            {base_conocimiento_texto}
            ============================================================

            Reglas operativas estrictas:
            1. Si el estudiante pregunta algo relacionado a su documento adjunto, analízalo a fondo bajo las reglas de esta sección.
            2. Si la respuesta exacta se encuentra en los textos, redacta los pasos de forma clara con viñetas y cita el nombre del instructivo o documento.
            3. Si la información NO está explícita o el tema pertenece a otra subcarpeta, responde exactamente: "La información solicitada no consta en los instructivos digitales de esta sección. Por favor, asegúrese de seleccionar el filtro correcto o acérquese a la ventanilla de Secretaría."
            4. No asumas ni inventes nada bajo ninguna circunstancia.

            Consulta del estudiante a procesar: {consulta_alumno}
            """
            
            paquete_envio = []
                
            if pdf_estudiante is not None:
                bytes_data = pdf_estudiante.read()
                documento_en_linea = types.Part.from_bytes(
                    data=bytes_data,
                    mime_type="application/pdf"
                )
                paquete_envio.append(documento_en_linea)
            
            paquete_envio.append(prompt_maestro)

            try:
                respuesta = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=paquete_envio
                )
                
                st.markdown("### 📝 Veredicto del Agente UTI:")
                st.info(respuesta.text)
                st.success("✓ Proceso de auditoría digital completado sin sobrecargar los límites del servidor.")
                
            except Exception as e:
                st.error(f"❌ Ocurrió un error al procesar la solicitud con la API: {e}")