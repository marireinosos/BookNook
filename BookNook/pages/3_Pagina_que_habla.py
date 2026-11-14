import streamlit as st
from PIL import Image
import pytesseract
from gtts import gTTS
import io

st.set_page_config(page_title="Página que Habla | BookNook", page_icon="🎧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');
    .stApp { background: radial-gradient(circle at top right, #FDFBF7 0%, #F4EBE1 60%, #E8D8C8 100%); color: #3B281E; font-family: 'Plus Jakarta Sans', sans-serif; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #2C1D14 0%, #3E2A1E 100%) !important; }
    section[data-testid="stSidebar"] * { color: #F7EFE6 !important; }
    h1, h2, h3 { font-family: 'Cormorant Garamond', serif !important; color: #2C1D14 !important; }
    .ocr-card {
        background: rgba(255, 252, 248, 0.88);
        border: 1px solid #E2D2BE;
        border-radius: 22px;
        padding: 26px;
        box-shadow: 0 10px 28px rgba(59, 40, 30, 0.07);
        margin-bottom: 20px;
    }
    .stButton > button {
        background: linear-gradient(135deg, #8C624C 0%, #5E3A24 100%) !important;
        color: #FFFDF9 !important;
        border-radius: 25px !important;
        border: none !important;
        padding: 10px 24px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎧 La Página que Habla (OCR & Narración)")
st.markdown("*¿Tus manos están ocupadas pero no quieres soltar la historia? Escanea la página de tu libro y deja que BookNook te la lea en voz alta.*")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("""
    <div class="ocr-card">
        <h3>📸 1. Captura o Sube tu Página</h3>
        <p style="color:#6E5644; font-size:0.9rem;">Sube una foto de la página de tu libro o tómala directamente con tu cámara.</p>
    </div>
    """, unsafe_allow_html=True)
    
    metodo = st.radio("Método de entrada visual:", ["Subir foto de una página", "Usar cámara web"], horizontal=True)
    
    imagen_cargada = None
    if metodo == "Subir foto de una página":
        archivo = st.file_uploader("Sube una imagen (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])
        if archivo:
            imagen_cargada = Image.open(archivo)
    else:
        camara = st.camera_input("Toma una foto a la página de tu libro")
        if camara:
            imagen_cargada = Image.open(camara)

    if imagen_cargada:
        st.image(imagen_cargada, caption="Página lista para lectura óptica", use_container_width=True)

with col2:
    st.markdown("""
    <div class="ocr-card">
        <h3>🔊 2. Transcripción Óptica y Audiolibro</h3>
        <p style="color:#6E5644; font-size:0.9rem;">Extraemos el texto mediante reconocimiento óptico de caracteres (OCR) y generamos la voz.</p>
    </div>
    """, unsafe_allow_html=True)

    texto_extraido = ""
    if imagen_cargada is not None:
        with st.spinner("✨ Leyendo los caracteres de la página con OCR..."):
            try:
                texto_extraido = pytesseract.image_to_string(imagen_cargada, lang="spa")
            except:
                try:
                    texto_extraido = pytesseract.image_to_string(imagen_cargada)
                except Exception as e:
                    st.warning("El motor OCR está iniciando. También puedes editar o pegar tu fragmento abajo.")

    texto_final = st.text_area(
        "📜 Fragmento literario detectado (puedes editarlo o probar con un pasaje propio):",
        value=texto_extraido.strip() if texto_extraido.strip() else "Aquella noche, las estrellas sobre la corte parecían susurrar antiguos secretos entre las páginas abiertas...",
        height=160
    )

    if st.button("🎶 Narrar página en voz alta"):
        if texto_final.strip():
            with st.spinner("Creando narración de voz..."):
                tts = gTTS(text=texto_final, lang='es')
                audio_bytes = io.BytesIO()
                tts.write_to_fp(audio_bytes)
                audio_bytes.seek(0)
                st.audio(audio_bytes, format="audio/mp3")
                st.success("✨ ¡Tu audiolibro está listo! Dale play al reproductor.")
