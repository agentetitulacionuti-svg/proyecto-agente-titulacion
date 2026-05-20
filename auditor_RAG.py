# =====================================================================
# POKA-YOKE ESTÉTERICO MEJORADO: CONTROL DE CAPAS PARA LOGO INSTITUCIONAL
# =====================================================================
st.markdown(
    """
    <style>
    /* Aplicamos el fondo a la capa principal de la aplicación */
    .main {
        background-image: url("https://www.uti.edu.ec/wp-content/uploads/2018/06/Logotipo-Indoamerica.png");
        background-repeat: no-repeat;
        background-position: center 50%;
        background-attachment: fixed;
        background-size: 40%; /* Ajusta el tamaño si lo quieres más grande o pequeño */
    }
    
    /* Quitamos los fondos blancos por defecto de Streamlit para hacerlos transparentes */
    .stApp, .main, .block-container {
        background-color: transparent !important;
    }
    
    /* Creamos el contenedor de alto contraste para las cajas de texto y respuestas */
    .block-container {
        background-color: rgba(255, 255, 255, 0.94) !important; /* Blanco con 94% de opacidad */
        padding: 40px !important;
        border-radius: 12px;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);
        margin-top: 30px;
    }
    
    /* Estilización del botón institucional */
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