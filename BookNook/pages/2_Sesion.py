import streamlit as st
import speech_recognition as sr
import pandas as pd
import json
import time

st.set_page_config(page_title="Sesión de Lectura | BookNook", page_icon="⏱️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    .stApp { background: radial-gradient(circle at top, #FBF7F2 0%, #F3EAE0 60%, #EADBC8 100%); color: #4A332D; font-family: 'Plus Jakarta Sans', sans-serif; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #4A332D 0%, #36221C 100%) !important; border-right: 3px solid #B5838D; }
    section[data-testid="stSidebar"] * { color: #FBF7F2 !important; }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #4A332D !important; }
    .panel-sesion {
        background: #FFFDF9;
        border: 1.5px solid #E2D0BE;
        border-top: 5px solid #B5838D;
        border-radius: 22px;
        padding: 26px;
        box-shadow: 0 10px 25px rgba(74, 51, 45, 0.06);
        margin-bottom: 20px;
    }
    .timer-display {
        background: linear-gradient(135deg, #4A332D 0%, #6D4C41 100%);
        color: #FBF7F2;
        border: 2px solid #D4AF37;
        border-radius: 22px;
        padding: 25px;
        text-align: center;
        margin-bottom: 20px;
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

if 'mqtt_client' not in st.session_state:
    import paho.mqtt.client as mqtt
    client = mqtt.Client()
    client.connect("broker.mqttdashboard.com", 1883, 60)
    client.loop_start()
    st.session_state['mqtt_client'] = client

cliente = st.session_state['mqtt_client']

st.title("⏱️ Sesión de Lectura & Ambiente por Voz")
st.markdown("*Elige tu libro, di el género por voz para iluminar tu estación en Wokwi y mide cada minuto que lees.*")

# --- BANNER DE CRONÓMETRO EN VIVO (RF6, RF7, RF12) ---
minutos_actuales = st.session_state.get('minutos_hoy', 35)
estado_estacion = st.session_state.get('evento_wokwi', 'Listo para empezar')
libro_activo = st.session_state.get('libro_actual', 'María')
ambiente_activo = st.session_state.get('ambiente_actual', 'Romance 💖 (Corazones)')

st.markdown(f"""
<div class="timer-display">
    <div style="font-size:0.85rem; letter-spacing:0.1em; text-transform:uppercase; color:#EADBC8;">LEYENDO AHORA EN LA ESTACIÓN</div>
    <h2 style="color:#FBF7F2 !important; font-size:2.4rem !important; margin:5px 0;">📖 {libro_activo} · <span style="color:#E6B8C0;">{ambiente_activo}</span></h2>
    <div style="font-size:1.8rem; font-weight:700; color:#D4AF37; margin-top:8px;">
        Hoy has leído {minutos_actuales} minutos · Meta diaria: 30 min
    </div>
    <div style="font-size:0.9rem; margin-top:6px; color:#F3EAE0;">Estado del botón físico en Wokwi: <b>{estado_estacion}</b></div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="panel-sesion">
        <h3>📟 1. Elegir el libro actual (RF3)</h3>
        <p style="color:#6D4C41; font-size:0.92rem;">Selecciona el libro de tu biblioteca para enviar su título a la pantalla LCD 16x2 de la estación en Wokwi.</p>
    </div>
    """, unsafe_allow_html=True)
    
    libro_elegido = st.selectbox("Libro activo para esta sesión:", ["María", "Dead Letters", "A Court of Thorns and Roses", "Dune", "Drácula"])
    if st.button("✨ Mostrar título en la pantalla LCD de Wokwi"):
        st.session_state['libro_actual'] = libro_elegido
        cliente.publish("booknook/app", json.dumps({"libro": libro_elegido}))
        st.success(f"📡 Enviado `{{'libro':'{libro_elegido}'}}` por MQTT a `booknook/app`.")

    st.write("")
    st.markdown("""
    <div class="panel-sesion">
        <h3>🏆 3. Cronómetro y Meta Diaria (RF6, RF7, RF12)</h3>
        <p style="color:#6D4C41; font-size:0.92rem;">
            Presiona el botón físico en Wokwi al empezar y al terminar, o registra tu sesión aquí. 
            Al superar los 30 minutos, avisamos a la estación con <code>{"meta":true}</code>.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    min_manual = st.slider("Minutos leídos en esta sesión:", 5, 90, 35)
    if st.button("🎉 Terminar sesión y celebrar meta en Wokwi"):
        st.session_state['minutos_hoy'] = min_manual
        if min_manual >= 30:
            cliente.publish("booknook/app", json.dumps({"meta": True}))
            st.balloons()
            st.success(f"🌟 ¡Hoy has leído {min_manual} minutos! Meta diaria cumplida. Se envió `{{'meta':true}}` a la estación.")
        else:
            st.info(f"Hoy has leído {min_manual} minutos.")

with col2:
    st.markdown("""
    <div class="panel-sesion">
        <h3>🎙️ 2. Cambiar el ambiente con tu voz (RF4 y RF5)</h3>
        <p style="color:#6D4C41; font-size:0.92rem;">
            Haz clic en el micrófono y di: <b>"Voy a leer romance"</b>, <b>"ciencia ficción"</b>, <b>"misterio"</b> o <b>"fantasía"</b>.
            La matriz LED 8x8 de Wokwi cambiará de figura en menos de 2 segundos.
        </p>
    </div>
    """, unsafe_allow_html=True)

    audio_voz = st.audio_input("🎤 Presiona el micrófono para decir el género de tu libro:")

    def enviar_ambiente(gen_clave, etiqueta_visual):
        st.session_state['ambiente_actual'] = etiqueta_visual
        cliente.publish("booknook/app", json.dumps({"genero": gen_clave}))
        st.success(f"✨ Matriz de luces en Wokwi actualizada: **{etiqueta_visual}** (`{{'genero':'{gen_clave}'}}`)")

    if audio_voz is not None:
        r = sr.Recognizer()
        with sr.AudioFile(audio_voz) as source:
            audio_data = r.record(source)
            try:
                frase = r.recognize_google(audio_data, language="es-ES").lower()
                st.info(f"🗣️ Dijiste: **\"{frase}\"**")
                if "romance" in frase or "amor" in frase or "maría" in frase or "maria" in frase:
                    enviar_ambiente("romance", "Romance 💖 (Corazones que laten)")
                elif "ciencia" in frase or "ficción" in frase or "ficcion" in frase or "estrellas" in frase:
                    enviar_ambiente("ciencia ficcion", "Ciencia Ficción ⭐ (Estrellas que titilan)")
                elif "misterio" in frase or "terror" in frase or "luna" in frase:
                    enviar_ambiente("misterio", "Misterio y Terror 🌙 (Luna en la noche)")
                elif "fantasía" in frase or "fantasia" in frase or "magia" in frase:
                    enviar_ambiente("fantasia", "Fantasía ✨ (Destellos mágicos)")
                else:
                    enviar_ambiente("romance", f"Romance 💖 ({frase})")
            except Exception:
                st.warning("No se escuchó con claridad. Puedes intentar de nuevo o usar los botones de respaldo aquí abajo.")

    st.markdown("**Plan B (Requerimiento No Funcional - Botones directos de ambiente):**")
    b1, b2 = st.columns(2)
    with b1:
        if st.button("💖 Romance (Corazones)"):
            enviar_ambiente("romance", "Romance 💖 (Corazones que laten)")
        if st.button("🌙 Misterio y terror (Luna)"):
            enviar_ambiente("misterio", "Misterio y Terror 🌙 (Luna en la noche)")
    with b2:
        if st.button("⭐ Ciencia ficción (Estrellas)"):
            enviar_ambiente("ciencia ficcion", "Ciencia Ficción ⭐ (Estrellas que titilan)")
        if st.button("✨ Fantasía (Destellos)"):
            enviar_ambiente("fantasia", "Fantasía ✨ (Destellos mágicos)")
