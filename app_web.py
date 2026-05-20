# =====================================================================
# INTERFAZ WEB DEL AGENTE DE AUDITORÍA ACADÉMICA - INDOAMÉRICA
# Desarrollado por: Alejandro Tituaña
# Enfoque: Poka-Yoke Avanzado / Extracción de Texto Estable en Memoria
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

# 1. CONEXIÓN AL MOTOR DE IA (Configuración Segura para Producción)
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("🔑 Error: No se ha detectado la GEMINI_API_KEY en las variables de entorno o Secrets de Streamlit.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# 2. CONFIGURACIÓN DE LAS FUENTES DE INFORMACIÓN (Búsqueda Dinámica y Recursiva)
DIRECTORIO_BASE = "documentos_uti"
lista_instructivos = []

if os.path.exists(DIRECTORIO_BASE):
    for root, dirs, files in os.walk(DIRECTORIO_BASE):
        for file in files:
            # Filtramos exclusivamente archivos con extensión .pdf, ignorando de forma segura .docx u otros
            if file.lower().endswith('.pdf'):
                lista_instructivos.append(os.path.join(root, file))
    lista_instructivos.sort()

# Optimizamos el almacenamiento leyendo el texto puro para evitar saturar la API con archivos binarios
@st.cache_data
def extraer_texto_base_conocimiento(archivos):
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

base_conocimiento_texto = extraer_texto_base_conocimiento(lista_instructivos)

# 3. INTERFAZ DE USUARIO (Frontend tipo Chat para el Estudiante)
st.subheader("📋 Módulo de Consulta y Auditoría de Documentos")
st.write("Realiza tus preguntas sobre el proceso o sube un archivo PDF personal para analizarlo contra las normativas.")

# Componente web para que el alumno suba su propio PDF de prueba
pdf_estudiante = st.file_uploader("Carga tu documento aquí (Opcional)", type=["pdf"])

# Caja de texto para ingresar la consulta académica
consulta_alumno = st.text_input("Escribe tu consulta académica sobre el proceso:")

# Botón operativo para ejecutar el flujo continuo sin fallas de API
if st.button("Ejecutar Auditoría Digital"):
    if not consulta_alumno:
        st.warning("⚠️ Por favor, ingresa una pregunta para iniciar el análisis.")
    elif not base_conocimiento_texto:
        st.error("❌ Error: No se pudo extraer información de los archivos normativos base. Verifica que la carpeta 'documentos_uti' exista y contenga archivos PDF válidos.")
    else:
        with st.spinner("Analizando documentos y normativas institucionales con Gemini 2.5 Flash..."):
            
            # Ingeniería de Prompt Estricta (Límites de operación de la IA)
            prompt_maestro = f"""
            Actúas como el Agente Automatizado de Auditoría Académica de la Facultad de Ingenierías de la UTI.
            Tu objetivo es responder a la consulta del estudiante utilizando EXCLUSIVAMENTE el texto de los
            documentos normativos de la base de conocimiento provista y, si existe, el documento cargado por el estudiante.

            === BASE DE CONOCIMIENTO NORMATIVA INSTITUCIONAL ===
            {base_conocimiento_texto}
            ====================================================

            Reglas operativas estrictas:
            1. Si el estudiante pregunta algo relacionado a su documento adjunto, analízalo a fondo y emite un veredicto basado en las reglas del reglamento institucional expuesto arriba.
            2. Si la respuesta exacta se encuentra en los textos, redacta los pasos de forma clara, ordenando los puntos usando viñetas y cita el nombre del instructivo o documento correspondiente.
            3. Si la información NO está explícita en la Base de Conocimiento, responde exactamente: "La información solicitada no consta en los instructivos digitales. Por favor, acérquese a la ventanilla de Secretaría."
            4. No asumas, no inventes ni utilices conocimiento externo bajo ninguna circunstancia.

            Consulta del estudiante a procesar: {consulta_alumno}
            """
            
            # Construcción del contenedor de contenidos
            paquete_envio = []
                
            # Si el alumno adjunta una carga, extraemos sus bytes puros en una Part
            if pdf_estudiante is not None:
                bytes_data = pdf_estudiante.read()
                documento_en_linea = types.Part.from_bytes(
                    data=bytes_data,
                    mime_type="application/pdf"
                )
                paquete_envio.append(documento_en_linea)
            
            # Consolidamos el Prompt maestro que ya incluye todo el texto normativo indexado
            paquete_envio.append(prompt_maestro)

            try:
                # Ejecución en el modelo de última generación
                respuesta = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=paquete_envio
                )

                # Despacho visual del veredicto directamente en la pantalla web
                st.markdown("### 📝 Veredicto del Agente UTI:")
                st.info(respuesta.text)
                st.success("✓ Proceso de auditoría digital completado sin defectos de información.")
                
            except Exception as e:
                st.error(f"❌ Ocurrió un error al procesar la solicitud con la API: {e}")