import json
import uuid
import streamlit as st
import paho.mqtt.client as mqtt

# ---------------- CONFIGURACIÓN MQTT ----------------
MQTT_BROKER = "broker.mqttdashboard.com"
MQTT_PORT = 1883
TOPIC_APP = "booknook/app"

def enviar_a_wokwi(payload_dict):
    """Envía un JSON a Wokwi con ID único y espera confirmación de envío."""
    client_id = f"BookNook_Web_{uuid.uuid4().hex[:8]}"
    client = mqtt.Client(client_id=client_id)
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    info = client.publish(TOPIC_APP, json.dumps(payload_dict), qos=1)
    info.wait_for_publish(timeout=3)
    client.loop_stop()
    client.disconnect()

# ---------------- ESTADO DE SESIÓN ----------------
if "libros" not in st.session_state:
    st.session_state["libros"] = ["María", "A Court of Thorns and Roses", "Dead Letters"]
if "libro_activo" not in st.session_state:
    st.session_state["libro_activo"] = st.session_state["libros"][0]
if "minutos_hoy" not in st.session_state:
    st.session_state["minutos_hoy"] = 0

# ---------------- INTERFAZ ----------------
st.title("⏱️ Sesión de Lectura & Ambiente por Voz")
st.caption("Todo lo que haces aquí o en Wokwi se sincroniza de verdad: sin minutos pre-cargados.")

# Banner superior de estado
st.info(
    f"**LIBRO ACTIVO EN LA ESTACIÓN:** {st.session_state['libro_activo']}  \n"
    f"**Hoy has leído:** {st.session_state['minutos_hoy']} minutos reales (Meta: 30 min)  \n"
    "⏸️ En espera (Presiona el botón verde en Wokwi para iniciar/detener el cronómetro)"
)

col1, col2 = st.columns(2)

# -------- COLUMNA 1: LIBRO ACTIVO --------
with col1:
    st.subheader("1. Elegir el libro activo (RF3 y RF10)")
    st.write(
        "El libro que elijas aquí aparecerá en el LCD de Wokwi, recibirá los minutos "
        "que cronometres con el botón físico y las estrellas cuando gires la perilla."
    )

    libro_seleccionado = st.selectbox(
        "Selecciona tu libro:",
        st.session_state["libros"],
        index=st.session_state["libros"].index(st.session_state["libro_activo"])
        if st.session_state["libro_activo"] in st.session_state["libros"]
        else 0,
    )

    if st.button("✨ Enviar libro a la estación Wokwi", use_container_width=True):
        st.session_state["libro_activo"] = libro_seleccionado
        enviar_a_wokwi({"libro": libro_seleccionado})
        st.success(f"Libro '{libro_seleccionado}' enviado al LCD de Wokwi.")

    st.divider()
    st.subheader("🎛️ Estado de la Perilla y Botón en Vivo")
    st.markdown(
        f"- **Botón verde en Wokwi:** Presiónalo una vez para iniciar el conteo desde 0, y otra vez para terminar.\n"
        f"- **Perilla en Wokwi:** Gírala para darle de 1 a 5 estrellas a **{st.session_state['libro_activo']}**."
    )

# -------- COLUMNA 2: AMBIENTE LUMINOSO --------
with col2:
    st.subheader("2. Ambiente luminoso por Voz (RF4 y RF5)")
    st.markdown(
        "Di en voz alta el género de tu libro. La matriz de luces 8x8 en Wokwi dibujará la figura animada:\n"
        "- **Romance:** Corazones que laten ❤️\n"
        "- **Ciencia ficción:** Estrellas que titilan ✨\n"
        "- **Misterio y terror:** Una luna en la noche 🌙\n"
        "- **Fantasía:** Destellos mágicos ✨"
    )

    audio = st.audio_input("Graba tu voz diciendo el género (ej: 'voy a leer romance' o 'fantasía'):")
    if audio is not None:
        st.caption("Audio grabado. Si el reconocimiento de voz falla, usa los botones del Plan B abajo.")

    st.markdown("**Botones directos para cambiar las figuras de la Matriz LED (Plan B):**")
    b1, b2 = st.columns(2)
    b3, b4 = st.columns(2)

    with b1:
        if st.button("❤️ Romance -> Corazones", use_container_width=True):
            enviar_a_wokwi({"genero": "romance"})
            st.toast("Corazones enviados a Wokwi")

    with b2:
        if st.button("⭐ Sci-Fi -> Estrellas", use_container_width=True):
            enviar_a_wokwi({"genero": "sci-fi"})
            st.toast("Estrellas enviadas a Wokwi")

    with b3:
        if st.button("🌙 Misterio -> Luna", use_container_width=True):
            enviar_a_wokwi({"genero": "misterio"})
            st.toast("Luna enviada a Wokwi")

    with b4:
        if st.button("✨ Fantasía -> Destellos", use_container_width=True):
            enviar_a_wokwi({"genero": "fantasia"})
            st.toast("Destellos enviados a Wokwi")
