import streamlit as st
import speech_recognition as sr
import json

st.title("Tu Sesión de Lectura ⏱️")

# Verificamos si la conexión MQTT ya se hizo en la página de inicio
if 'mqtt_client' not in st.session_state:
    st.warning("⚠️ Ve primero a la página de Inicio para conectar la estación.")
else:
    cliente = st.session_state['mqtt_client']

    st.subheader("1. Elige tu libro")
    libro = st.text_input("¿Qué libro vas a leer hoy?")
    if st.button("Enviar a la estación"):
        msg = json.dumps({"libro": libro})
        cliente.publish("booknook/app", msg)
        st.success(f"¡Libro '{libro}' enviado a tu BookNook!")

    st.subheader("2. Crea el ambiente con tu voz 🎙️")
    st.write("Presiona el botón y di el género (Ej: romance, misterio, ciencia ficcion).")
    
    if st.button("🎤 Hablar género"):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Escuchando... ¡Habla ahora!")
            try:
                # Escucha el micrófono de tu Mac
                audio = r.listen(source, timeout=5)
                texto = r.recognize_google(audio, language="es-ES").lower()
                st.success(f"Escuché: {texto}")
                
                # Enviar el género por MQTT a la matriz de Wokwi
                msg_genero = json.dumps({"genero": texto})
                cliente.publish("booknook/app", msg_genero)
                
            except sr.UnknownValueError:
                st.error("No pude entender el audio. Intenta hablar más cerca.")
            except sr.WaitTimeoutError:
                st.error("Se acabó el tiempo de espera.")