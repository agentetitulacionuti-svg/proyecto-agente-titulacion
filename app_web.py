# =====================================================================
# POKA-YOKE ESTÉTICO INDUSTRIAL: PALETA DE ALTO CONTRASTE UTI
# =====================================================================
st.markdown(
    """
    <style>
    /* Fondo exterior de la aplicación: Gris tecnológico limpio y profesional */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #F0F4F8 0%, #D9E2EC 100%) !important;
        background-attachment: fixed;
    }

    /* Volvemos totalmente transparentes las capas intermedias */
    [data-testid="stHeader"], [data-testid="stApp"], .main {
        background-color: transparent !important;
    }
    
    /* Contenedor principal (Tarjeta Ejecutiva Flotante de Contraste) */
    .block-container {
        background-color: #FFFFFF !important; /* Blanco Puro para que resalte */
        padding: 50px !important;
        border-radius: 16px;
        box-shadow: 0px 10px 30px rgba(0, 51, 102, 0.1); /* Sombra sutil en azul */
        margin-top: 50px;
    }
    
    /* CONTROL ABSOLUTO DE COLORES DE TEXTO (FORZADO INSTITUCIONAL) */
    /* Título Principal H1 */
    h1 {
        color: #003366 !important;
        font-weight: 800 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Subtítulos, textos explicativos y etiquetas de carga de archivos */
    .stMarkdown, p, label, span, .stText {
        color: #102A43 !important; /* Azul marino oscuro de alta legibilidad */
        font-weight: 500 !important;
    }
    
    /* Forzar color oscuro en las etiquetas de los inputs de texto */
    [data-testid="stWidgetLabel"] p {
        color: #102A43 !important;
        font-weight: 600 !important;
    }
    
    /* Estilización del botón de ejecución de Ingeniería */
    .stButton>button {
        background-color: #003366 !important;
        color: #FFFFFF !important; /* Texto del botón estrictamente blanco */
        border-radius: 8px !important;
        width: 100%;
        font-weight: bold;
        border: none;
        padding: 12px;
        font-size: 16px;
        transition: 0.3s ease;
    }
    
    /* Efecto de respuesta al pasar el mouse por el botón (Feedback visual) */
    .stButton>button:hover {
        background-color: #002244 !important;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.15);
    }
    </style>
    """,
    unsafe_allow_html=True
)