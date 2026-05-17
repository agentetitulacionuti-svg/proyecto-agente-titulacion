# =====================================================================
# INTERFAZ WEB DEL AGENTE DE AUDITORÍA ACADÉMICA - INDOAMÉRICA
# Desarrollado por: Alejandro Tituaña
# Enfoque: Poka-Yoke Digital / Conexión a Base de Datos en la Nube
# =====================================================================

import streamlit as st
from google import genai
from google.genai import types
import os

# Configuración del Layout visual de la página web institucional
st.set_page_config(page_title="Agente UTI - Auditoría", page_icon="🎓", layout="centered")

st.title("🎓 Asistente Virtual de Titulación - UTI")
st.markdown("---")

# 1. CONEXIÓN AL MOTOR DE IA (Configuración Segura para Producción)
# Poka-Yoke: Eliminamos la API Key fija expuesta para evitar bloqueos del servidor
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("🔑 Error: No se ha detectado la GEMINI_API_KEY en las variables de entorno o Secrets de Streamlit.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# 2. CONFIGURACIÓN DE LAS FUENTES DE INFORMACIÓN (Base de Datos en la Nube / Drive)
# Para máxima eficiencia en Streamlit Cloud, cargamos los documentos normativos 
# de tu base de datos mediante la lectura segura de bytes en memoria.
lista_instructivos = [
    "instructivoparalaorganizaciondelosaprendizajes.pdf",
    "Instructivo-para-subida-de-titulos-1.pdf"
]

base_conocimiento_archivos = []

# Fase de Retrieval en memoria: Evita buscar rutas absolutas de carpetas locales
for nombre_archivo in lista_instructivos:
    if os.path.exists(nombre_archivo):
        with open(nombre_archivo, "rb") as f:
            bytes_archivo = f.read()
            documento_normativo = types.Part.from_bytes(
                data=bytes_archivo,
                mime_type="application/pdf"
            )
            base_conocimiento_archivos.append(documento_normativo)

# 3. INTERFAZ DE USUARIO (Frontend tipo Chat para el Estudiante)
st.subheader("📋 Módulo de Consulta y Auditoría de Documentos")
st.write("Realiza tus preguntas sobre el proceso o sube un archivo PDF personal para analizarlo contra las normativas.")

# Componente web para que el alumno suba su propio PDF de prueba
pdf_estudiante = st.file_uploader("Carga tu documento aquí (Opcional)", type=["pdf"])

# Caja de texto para ingresar la consulta académica
consulta_alumno = st.text_input("Escribe tu consulta académica sobre el proceso:")

# Botón operativo para ejecutar el flujo continuo con estructura Poka-Yoke normalizada
if st.button("Ejecutar Auditoría Digital"):
    if not consulta_alumno:
        st.warning("⚠️ Por favor, ingresa una pregunta para iniciar el análisis.")
    elif len(base_conocimiento_archivos) == 0:
        st.error("❌ Error: No se encontraron los archivos normativos base en la raíz del proyecto. Asegúrate de subirlos a tu repositorio.")
    else:
        with st.spinner("Analizando documentos y normativas institucionales con Gemini 2.5 Flash..."):
            
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
            
            # NORMALIZACIÓN: Construcción limpia del contenedor secuencial para la API
            paquete_envio = []
            
            # 1. Agregamos las partes binarias de los reglamentos institucionales estables
            for doc in base_conocimiento_archivos:
                paquete_envio.append(doc)
                
            # 2. Si el alumno adjunta una carga, extraemos sus bytes puros en una nueva Part
            if pdf_estudiante is not None:
                bytes_data = pdf_estudiante.read()
                documento_en_linea = types.Part.from_bytes(
                    data=bytes_data,
                    mime_type="application/pdf"
                )
                paquete_envio.append(documento_en_linea)
            
            # 3. Consolidamos el Prompt de control operativo al final de la estructura
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