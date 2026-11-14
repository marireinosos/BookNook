import streamlit as st
import speech_recognition as sr
import pandas as pd
import json
import time
from Inicio import obtener_estado_compartido, iniciar_mqtt

st.set_page_config(page_title="Sesión de Lectura | BookNook", page_icon="⏱️", layout="wide")

estado_hw = obtener_estado_compartido()
cliente = iniciar_mqtt()

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    .stApp { background: radial-gradient(circle at top, #FBF7F2 0%, #F3EAE0 60%, #EADBC8 100%); color: #4A332D; font-family: 'Plus Jakarta Sans', sans-serif; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #4A332D 0%, #36221C 100%) !important; border-right: 3px solid #B5838D; }
    section[data-testid="stSidebar"] * { color: #FBF7F2 !important; }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #4A332D !important; }
    .panel-sesion { background: #FFFDF9; border: 1.5px solid #E2D0BE; border-top: 5px solid #B5838D; border-radius: 22px; padding: 26px; box-shadow: 0 10px 25px rgba(74, 51, 45, 0.06); margin-bottom: 20px; }
    .timer-display { background: linear-gradient(135deg, #4A332D 0%, #6D4C41 100%); color: #FBF7F2; border: 2px solid #D4AF37; border-radius: 22px; padding: 25px; text-align: center; margin-bottom: 20px; }
    .stButton > button { background: linear-gradient(135deg, #B5838D 0%, #8E5B66 100%) !important; color: #FFFFFF !important; border-radius: 25px !important; border: 1px solid #D4AF37 !important; padding: 10px 24px !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

st.title("⏱️ Sesión de Lectura & Ambiente por Voz")
st.markdown("*Todo lo que haces aquí o en Wokwi se sincroniza de verdad: sin minutos pre-cargados.*")

tiempo_en_curso = 0
if estado_hw["leyendo_ahora"] and estado_hw["inicio_timestamp"]:
    tiempo_en_curso = int(time.time() - estado_hw["inicio_timestamp"])

minutos_reales_hoy = estado_hw["minutos_hoy"] + tiempo_en_curso

# Avisar automáticamente a Wokwi si se cumplen los 30 minutos (RF12)
if minutos_reales_hoy >= 30 and not st.session_state.get("meta_celebrada", False):
    cliente.publish("booknook/app", json.dumps({"meta": True}))
    st.session_state["meta_celebrada"] = True
    st.balloons()

estado_cronometro = f"🟢 CRONÓMETRO ACTIVO EN WOKWI: +{tiempo_en_curso} min en esta sesión" if estado_hw["leyendo_ahora"] else "⏸️ En espera (Presiona el botón verde en Wokwi para iniciar/detener el cronómetro)"

st.markdown(f"""
<div class="timer-display">
    <div style="font-size:0.85rem; letter-spacing:0.1em; text-transform:uppercase; color:#EADBC8;">LIBRO ACTIVO EN LA ESTACIÓN Y PARA CALIFICAR CON LA PERILLA</div>
    <h2 style="color:#FBF7F2 !important; font-size:2.3rem !important; margin:5px 0;">📖 {estado_hw['libro_activo']} · <span style="color:#E6B8C0;">{estado_hw['ambiente_activo']}</span></h2>
    <div style="font-size:1.9rem; font-weight:700; color:#D4AF37; margin-top:8px;">
        Hoy has leído: {minutos_reales_hoy} minutos reales (Meta: 30 min)
    </div>
    <div style="font-size:0.95rem; margin-top:8px; color:#F3EAE0;">{estado_cronometro}</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="panel-sesion">
        <h3>📟 1. Elegir el libro activo (RF3 y RF10)</h3>
        <p style="color:#6D4C41; font-size:0.92rem;">
            El libro que elijas aquí aparecerá en el LCD de Wokwi, recibirá los minutos que cronometres con el botón físico y recibirá las estrellas cuando gires la perilla.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    df_l = pd.read_csv("data/libros.csv")
    lista_titulos = df_l["titulo"].tolist()
    libro_elegido = st.selectbox("Selecciona tu libro:", lista_titulos)
    
    if st.button("✨ Enviar libro a la estación Wokwi"):
        estado_hw["libro_activo"] = libro_elegido
        cliente.publish("booknook/app", json.dumps({"libro": libro_elegido}))
        st.success(f"📡 '{libro_elegido}' enviado al LCD de Wokwi. Si giras la perilla o presionas el botón, se aplicará a **{libro_elegido}**.")
        time.sleep(0.5)
        st.rerun()

    st.write("")
    st.markdown("""
    <div class="panel-sesion">
        <h3>🎛️ Estado de la Perilla y Botón en Vivo</h3>
        <p style="color:#6D4C41; font-size:0.92rem;">
            • <b>Botón verde en Wokwi:</b> Presiónalo una vez para iniciar el conteo desde 0, y otra vez para terminar.<br>
            • <b>Perilla en Wokwi:</b> Gírala para darle de 1 a 5 estrellas a <b>{0}</b>.
        </p>
    </div>
    """.format(estado_hw["libro_activo"]), unsafe_allow_html=True)
    
    if estado_hw["estrellas_actuales"] > 0:
        st.success(f"⭐ Última calificación desde la perilla física: **{estado_hw['estrellas_actuales']} estrellas** para **{estado_hw['ultimo_libro_calificado']}**")

with col2:
    st.markdown("""
    <div class="panel-sesion">
        <h3>🎙️ 2. Ambiente luminoso por Voz (RF4 y RF5)</h3>
        <p style="color:#6D4C41; font-size:0.92rem;">
            Di en voz alta el género de tu libro. La matriz de luces 8x8 en Wokwi dibujará la figura animada:
            <br>• <b>Romance:</b> Corazones que laten 💖
            <br>• <b>Ciencia ficción:</b> Estrellas que titilan ⭐
            <br>• <b>Misterio y terror:</b> Una luna en la noche 🌙
            <br>• <b>Fantasía:</b> Destellos mágicos ✨
        </p>
    </div>
    """, unsafe_allow_html=True)

    def activar_luces(clave_mqtt, descripcion_ambiente):
        estado_hw["ambiente_activo"] = descripcion_ambiente
        cliente.publish("booknook/app", json.dumps({"genero": clave_mqtt}))
        st.success(f"📡 Matriz LED en Wokwi dibujando: **{descripcion_ambiente}**")

    audio_voz = st.audio_input("🎤 Graba tu voz diciendo el género (ej: 'voy a leer romance' o 'fantasía'):")

    if audio_voz is not None:
        r = sr.Recognizer()
        with sr.AudioFile(audio_voz) as source:
            audio_data = r.record(source)
            try:
                frase = r.recognize_google(audio_data, language="es-ES").lower()
                st.info(f"🗣️ Tu voz dijo: **\"{frase}\"**")
                if "romance" in frase or "amor" in frase or "corazon" in frase:
                    activar_luces("romance", "Corazones que laten 💖 (Romance)")
                elif "ciencia" in frase or "ficcion" in frase or "ficción" in frase or "estrella" in frase:
                    activar_luces("ciencia ficcion", "Estrellas que titilan ⭐ (Ciencia ficción)")
                elif "misterio" in frase or "terror" in frase or "luna" in frase:
                    activar_luces("misterio", "Una luna en la noche 🌙 (Misterio)")
                elif "fantasía" in frase or "fantasia" in frase or "magia" in frase or "destello" in frase:
                    activar_luces("fantasia", "Destellos mágicos ✨ (Fantasía)")
                else:
                    st.warning("Di una de las palabras clave: romance, ciencia ficción, misterio o fantasía.")
            except Exception:
                st.warning("No se entendió claro el audio. Intenta de nuevo o usa los botones de respaldo.")

    st.markdown("**Botones directos para cambiar las figuras de la Matriz LED (Plan B):**")
    b1, b2 = st.columns(2)
    with b1:
        if st.button("💖 Romance → Corazones"):
            activar_luces("romance", "Corazones que laten 💖")
        if st.button("🌙 Misterio → Luna"):
            activar_luces("misterio", "Una luna en la noche 🌙")
    with b2:
        if st.button("⭐ Sci-Fi → Estrellas"):
            activar_luces("ciencia ficcion", "Estrellas que titilan ⭐")
        if st.button("✨ Fantasía → Destellos"):
            activar_luces("fantasia", "Destellos mágicos ✨")

if estado_hw["leyendo_ahora"]:
    time.sleep(2)
    st.rerun()
