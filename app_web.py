# =====================================================================
# POKA-YOKE ESTÉTICO ULTRA-RESISTENTE: CONTROL TOTAL DE FONDO (CSS)
# =====================================================================
st.markdown(
    """
    <style>
    /* Forzamos el fondo con el logo en la raíz absoluta de la aplicación */
    [data-testid="stAppViewContainer"] {
        background-image: url("https://www.uti.edu.ec/wp-content/uploads/2018/06/Logotipo-Indoamerica.png");
        background-repeat: no-repeat;
        background-position: center 55%;
        background-attachment: fixed;
        background-size: 45%; /* Controla el tamaño del logo en pantalla */
    }

    /* Volvemos totalmente transparentes las capas intermedias para que dejen ver el fondo */
    [data-testid="stHeader"], [data-testid="stApp"], .main {
        background-color: transparent !important;
    }
    
    /* Contenedor principal donde flotan las cajas de texto y el título */
    .block-container {
        background-color: rgba(255, 255, 255, 0.95) !important; /* Blanco sólido al 95% para contraste óptimo */
        padding: 40px !important;
        border-radius: 12px;
        box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.08);
        margin-top: 40px;
    }
    
    /* Estilización del botón con azul corporativo */
    .stButton>button {
        background-color: #003366 !important;
        color: white !important;
        border-radius: 6px !important;
        width: 100%;
        font-weight: bold;
        border: none;
        padding: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)