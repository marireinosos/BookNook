import streamlit as st
from PIL import Image
import pytesseract
from gtts import gTTS
import pandas as pd
import io
import os

st.set_page_config(page_title="Página que habla | BookNook", page_icon="📸", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    .stApp { background: radial-gradient(circle at top, #FBF7F2 0%, #F3EAE0 60%, #EADBC8 100%); color: #4A332D; font-family: 'Plus Jakarta Sans', sans-serif; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #4A332D 0%, #36221C 100%) !important; border-right: 3px solid #B5838D; }
    section[data-testid="stSidebar"] * { color: #FBF7F2 !important; }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #4A332D !important; }
    .ocr-box {
        background: #FFFDF9;
        border: 1.5px solid #E2D0BE;
        border-top: 5px solid #B5838D;
        border-radius: 22px;
        padding: 24px;
        box-shadow: 0 10px 25px rgba(74, 51, 45, 0.06);
        margin-bottom: 18px;
    }
    .quote-card {
        background: #F7EDE4;
        border-left: 5px solid #B5838D;
        border-radius: 14px;
        padding: 16px 20px;
        font-style: italic;
        margin-bottom: 12px;
        color: #4A332D;
    }
    .stButton > button {
        background: linear-gradient(135deg, #B5838D 0%, #8E5B66 100%) !important;
        color: #FFFFFF !important;
        border-radius: 25px !important;
        border: 1px solid #D4AF37 !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📸 Página que Habla (OCR & Texto a Voz)")
st.markdown("*¿Te toca cocinar o tienes las manos ocupadas? Tómale foto o screenshot a la página y la app te la lee en voz alta.*")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="ocr-box">
        <h3>📷 1. Captura la página de tu libro (RF8)</h3>
        <p style="color:#6D4C41; font-size:0.92rem;">Sube una foto/screenshot de tu página física o digital, o usa la cámara.</p>
    </div>
    """, unsafe_allow_html=True)
    
    modo = st.radio("Elige cómo capturar la página:", ["📁 Subir foto o screenshot", "📸 Tomar foto con la cámara"], horizontal=True)
    img_pagina = None
    if modo == "📁 Subir foto o screenshot":
        archivo = st.file_uploader("Selecciona la imagen de la página", type=["png", "jpg", "jpeg"])
        if archivo:
            img_pagina = Image.open(archivo)
    else:
        cam = st.camera_input("Enfoca la página de tu libro")
        if cam:
            img_pagina = Image.open(cam)

    if img_pagina:
        st.image(img_pagina, caption="Página cargada para reconocimiento OCR", use_container_width=True)

with col2:
    st.markdown("""
    <div class="ocr-box">
        <h3>🔊 2. Escuchar página y guardar cita (RF9)</h3>
        <p style="color:#6D4C41; font-size:0.92rem;">Revisamos el texto extraído con Tesseract OCR, lo leemos en voz alta con gTTS y guardamos tus citas favoritas.</p>
    </div>
    """, unsafe_allow_html=True)

    texto_ocr = ""
    if img_pagina is not None:
        with st.spinner("🔍 Extrayendo texto de la foto con OCR..."):
            try:
                texto_ocr = pytesseract.image_to_string(img_pagina, lang="spa")
            except:
                try:
                    texto_ocr = pytesseract.image_to_string(img_pagina)
                except:
                    st.info("Puedes revisar o pegar el texto directamente abajo.")

    texto_lectura = st.text_area(
        "📜 Texto de la página (fragmento de 'María' de Jorge Isaacs listo para la demo o resultado de tu foto):",
        value=texto_ocr.strip() if texto_ocr.strip() else "Era yo niño aún cuando me alejaron de la casa paterna para que diera principio a mis estudios en el colegio del doctor Lorenzo María Lleras, establecido en Bogotá hacía pocos años.",
        height=150
    )

    c_audio, c_cita = st.columns(2)
    with c_audio:
        if st.button("▶️ Escuchar en voz alta (gTTS)"):
            if texto_lectura.strip():
                with st.spinner("Generando voz cálida..."):
                    tts = gTTS(text=texto_lectura, lang="es")
                    mp3_fp = io.BytesIO()
                    tts.write_to_fp(mp3_fp)
                    mp3_fp.seek(0)
                    st.audio(mp3_fp, format="audio/mp3")
                    st.success("🎧 ¡Escuchando tu página!")

    with c_cita:
        if st.button("💖 Guardar en Citas Favoritas"):
            os.makedirs("data", exist_ok=True)
            df_citas = pd.read_csv("data/citas.csv") if os.path.exists("data/citas.csv") else pd.DataFrame(columns=["libro", "cita"])
            libro_ref = st.session_state.get('libro_actual', 'María - Jorge Isaacs')
            nueva_cita = pd.DataFrame([{"libro": libro_ref, "cita": texto_lectura.strip()}])
            df_citas = pd.concat([nueva_cita, df_citas], ignore_index=True)
            df_citas.to_csv("data/citas.csv", index=False)
            st.toast("✨ Cita guardada en tu colección")

st.write("---")
st.subheader("✨ Mis Citas Favoritas Guardadas")
if os.path.exists("data/citas.csv"):
    df_citas_mostrar = pd.read_csv("data/citas.csv")
    for _, row in df_citas_mostrar.iterrows():
        st.markdown(f"""
        <div class="quote-card">
            "{row['cita']}"<br>
            <strong style="font-style:normal; color:#B5838D; font-size:0.85rem;">— {row['libro']}</strong>
        </div>
        """, unsafe_allow_html=True)
