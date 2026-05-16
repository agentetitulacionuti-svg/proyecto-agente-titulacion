# =====================================================================
# INTERFAZ WEB DEL AGENTE DE AUDITORÍA ACADÉMICA - INDOAMÉRICA
# Desarrollado por: Alejandro Tituaña
# Enfoque: Poka-Yoke Digital / Sanitización de Datos e Interfaz Streamlit
# =====================================================================

import streamlit as st
from google import genai
from google.genai import types
import os

# Configuración del Layout visual de la página web institucional
st.set_page_config(page_title="Agente UTI - Auditoría", page_icon="🎓", layout="centered")

st.title("🎓 Asistente Virtual de Titulación - UTI")
st.markdown("---")

# 1. CONEXIÓN AL MOTOR DE IA
API_KEY = "AIzaSyC4eTyMAdtmlKU9Q9RPsRZWQIhYdAbVErU"
client = genai.Client(api_key=API_KEY)

# 2. CONFIGURACIÓN DE LAS FUENTES DE INFORMACIÓN (Múltiples Documentos de la Nube)
lista_instructivos = [
    "../PDF legal - pagina indoamerica/Instructivos/INSTRU-ORG-APREN-LINEA-DIST-SEMI.pdf",
    "../PDF legal - pagina indoamerica/Instructivos/Instructivo-para-subida-de-titulos-1.pdf"
]

base_conocimiento_archivos = []

# Fase de Retrieval fija (Carga de normativas de la universidad)
for ruta in lista_instructivos:
    if os.path.exists(ruta):
        archivo_subido = client.files.upload(file=ruta)
        base_conocimiento_archivos.append(archivo_subido)

# 3. INTERFAZ DE USUARIO (Frontend tipo Chat para el Estudiante)
st.subheader("📋 Módulo de Consulta y Auditoría de Documentos")
st.write("Realiza tus preguntas sobre el proceso o sube un archivo PDF personal para analizarlo contra las normativas.")

# Componente web para que el alumno suba su propio PDF de prueba
pdf_estudiante = st.file_uploader("Carga tu documento aquí (Opcional)", type=["pdf"])

# Caja de texto para ingresar la consulta académica
consulta_alumno = st.text_input("Escribe tu consulta académica sobre el proceso:")

# Botón operativo para ejecutar el flujo continuo
if st.button("Ejecutar Auditoría Digital"):
    if not consulta_alumno:
        st.warning("⚠️ Por favor, ingresa una pregunta para iniciar el análisis.")
    elif len(base_conocimiento_archivos) == 0:
        st.error("❌ Error: No se encontraron los archivos normativos en las rutas especificadas.")
    else:
        with st.spinner("Analizando documentos y normativas institucionales con Gemini 2.5 Flash..."):
            
            # Inicializamos el paquete de envío con las normativas institucionales fijas
            paquete_envio = list(base_conocimiento_archivos)
            
            # Poka-Yoke Avanzado: Evitamos la API de archivos para el alumno y enviamos los bytes puros codificados de forma segura
            if pdf_estudiante is not None:
                bytes_data = pdf_estudiante.read()
                documento_en_linea = types.Part.from_bytes(
                    data=bytes_data,
                    mime_type="application/pdf"
                )
                paquete_envio.append(documento_en_linea)

            # Ingeniería de Prompt Estricta (Límites de operación de la IA)
            prompt_maestro = f"""
            Actúas como el Agente Automatizado de Auditoría Académica de la Facultad de Ingenierías de la UTI.
            Tu objetivo es responder a la consulta del estudiante utilizando EXCLUSIVAMENTE la información
            de los documentos normativos provistos y, si existe, el documento cargado por el estudiante.

            Reglas operativas estrictas:
            1. Si el estudiante pregunta algo relacionado a su documento adjunto, analízalo a fondo y emite un veredicto basado en las reglas del reglamento.
            2. Si la respuesta exacta se encuentra en los textos, redacta los pasos de forma clara, ordenando los puntos usando viñetas y cita el nombre del instructivo o documento correspondiente.
            3. Si la información NO está explícita, responde exactamente: "La información solicitada no consta en los instructivos digitales. Por favor, acérquese a la ventanilla de Secretaría."
            4. No asumas, no inventes ni utilices conocimiento externo bajo ninguna circunstancia.

            Consulta del estudiante a procesar: {consulta_alumno}
            """
            
            paquete_envio.append(prompt_maestro)

            # Ejecución en el modelo de última generación
            respuesta = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=paquete_envio
            )

            # Despacho visual del veredicto directamente en la pantalla web
            st.markdown("### 📝 Veredicto del Agente UTI:")
            st.info(respuesta.text)
            st.success("✓ Proceso de auditoría digital completado sin defectos de información.")