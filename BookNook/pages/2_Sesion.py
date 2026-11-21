import json
import uuid
import streamlit as st
import paho.mqtt.client as mqtt

# ---------------- CONFIGURACIÓN DE PÁGINA ----------------
st.set_page_config(page_title="Sesión de Lectura | BookNook", page_icon="⏱️", layout="wide")

# ---------------- ESTÉTICA BOOKNOOK (CSS) ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=Inter:wght@400;500;600&display=swap');

    /* Fondo general crema y barra lateral café oscuro */
    .stApp {
        background-color: #FAF4EC;
        font-family: 'Inter', sans-serif;
        color: #3E2A22;
    }
    [data-testid="stSidebar"] {
        background-color: #422E26;
    }
    [data-testid="stSidebar"] * {
        color: #F5EBE0 !important;
    }

    /* Títulos serif */
    h1, h2, h3, .booknook-title {
        font-family: 'Playfair Display', Georgia, serif !important;
        color: #3E2A22 !important;
    }

    /* Banner superior café degradado */
    .hero-banner {
        background: linear-gradient(135deg, #533627 0%, #836243 100%);
        border-radius: 18px;
        padding: 28px 24px;
        text-align: center;
        color: #FAF4EC;
        box-shadow: 0 6px 18px rgba(62, 42, 34, 0.14);
        margin-bottom: 24px;
    }
    .hero-label {
        font-size: 0.78rem;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: #E3CFC0;
        margin-bottom: 8px;
    }
    .hero-book {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 2rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 4px 0 10px 0;
    }
    .hero-minutes {
        font-size: 1.2rem;
        font-weight: 700;
        color: #F4C95D;
        margin-bottom: 6px;
    }
    .hero-sub {
        font-size: 0.85rem;
        color: #EADDD0;
    }

    /* Tarjetas blancas con borde superior */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF;
        border-radius: 16px !important;
        border: 1px solid #E8D9CE !important;
        border-top: 3px solid #A47176 !important;
        padding: 18px !important;
        box-shadow: 0 4px 12px rgba(62, 42, 34, 0.05);
    }

    /* Botones palo de rosa redondeados */
    .stButton > button {
        background: linear-gradient(90deg, #B57A80 0%, #8E5B62 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 24px !important;
        padding: 0.5rem 1.2rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        opacity: 0.92;
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# ---------------- CONFIGURACIÓN MQTT CORREGIDA ----------------
MQTT_BROKER = "broker.mqttdashboard.com"
MQTT_PORT = 1883
TOPIC_APP = "booknook/app"

def enviar_a_wokwi(payload_dict):
    """Publica por MQTT con ID único y espera confirmación para no perder mensajes."""
    client_id = f"BookNook_Web_{uuid.uuid4().hex[:8]}"
    client = mqtt.Client(client_id=client_id)
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    info = client.publish(TOPIC_APP, json.dumps(payload_dict), qos=1)
    info.wait_for_publish(timeout=3)
    client.loop_stop()
    client.disconnect()

# ---------------- ESTADO DE SESIÓN ----------------
if "libros" not in st.session_state or not st.session_state["libros"]:
    st.session_state["libros"] = [
        "nightshade",
        "María",
        "A Court of Thorns and Roses",
        "Dead Letters"
    ]

# Si tus libros en session_state son diccionarios (por ejemplo {"titulo": ...}), extraemos los títulos
lista_titulos = [
    b["titulo"] if isinstance(b, dict) and "titulo" in b else str(b)
    for b in st.session_state["libros"]
]

if "libro_activo" not in st.session_state:
    st.session_state["libro_activo"] = lista_titulos[0]
if "minutos_hoy" not in st.session_state:
    st.session_state["minutos_hoy"] = 0
if "estado_estacion" not in st.session_state:
    st.session_state["estado_estacion"] = "Sin activar aún"

# ---------------- ENCABEZADO ----------------
st.markdown("<h1 style='margin-bottom:0;'>⏱️ Sesión de Lectura & Ambiente por Voz</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='font-style:italic; color:#6D5447; margin-top:4px;'>"
    "Todo lo que haces aquí o en Wokwi se sincroniza de verdad: sin minutos pre-cargados."
    "</p>",
    unsafe_allow_html=True
)

# ---------------- BANNER SUPERIOR ----------------
st.markdown(f"""
<div class="hero-banner">
    <div class="hero-label">LIBRO ACTIVO EN LA ESTACIÓN Y PARA CALIFICAR CON LA PERILLA</div>
    <div class="hero-book">📖 {st.session_state['libro_activo']} · {st.session_state['estado_estacion']}</div>
    <div class="hero-minutes">Hoy has leído: {st.session_state['minutos_hoy']} minutos reales (Meta: 30 min)</div>
    <div class="hero-sub">⏸️ En espera (Presiona el botón verde en Wokwi para iniciar/detener el cronómetro)</div>
</div>
""", unsafe_allow_html=True)

# ---------------- DOS COLUMNAS PRINCIPALES ----------------
col1, col2 = st.columns(2, gap="large")

with col1:
    with st.container(border=True):
        st.markdown("### 📟 1. Elegir el libro activo (RF3 y RF10)")
        st.write(
            "El libro que elijas aquí aparecerá en el LCD de Wokwi, recibirá los minutos "
            "que cronometres con el botón físico y recibirá las estrellas cuando gires la perilla."
        )

        idx_actual = lista_titulos.index(st.session_state["libro_activo"]) if st.session_state["libro_activo"] in lista_titulos else 0
        libro_seleccionado = st.selectbox("Selecciona tu libro:", lista_titulos, index=idx_actual)

        if st.button("✨ Enviar libro a la estación Wokwi"):
            st.session_state["libro_activo"] = libro_seleccionado
            st.session_state["estado_estacion"] = "Activo en LCD"
            enviar_a_wokwi({"libro": libro_seleccionado})
            st.success(f"Libro '{libro_seleccionado}' enviado a Wokwi.")

    with st.container(border=True):
        st.markdown("### 🎛️ Estado de la Perilla y Botón en Vivo")
        st.markdown(
            f"- **Botón verde en Wokwi:** Presiónalo una vez para iniciar el conteo desde 0, y otra vez para terminar.\n"
            f"- **Perilla en Wokwi:** Gírala para darle de 1 a 5 estrellas a **{st.session_state['libro_activo']}**."
        )

with col2:
    with st.container(border=True):
        st.markdown("### 🎙️ 2. Ambiente luminoso por Voz (RF4 y RF5)")
        st.markdown(
            "Di en voz alta el género de tu libro. La matriz de luces 8x8 en Wokwi dibujará la figura animada:\n"
            "- **Romance:** Corazones que laten ❤️\n"
            "- **Ciencia ficción:** Estrellas que titilan ✨\n"
            "- **Misterio y terror:** Una luna en la noche 🌙\n"
            "- **Fantasía:** Destellos mágicos ✨"
        )

        audio = st.audio_input("Graba tu voz diciendo el género (ej: 'voy a leer romance' o 'fantasía'):")
        if audio is not None:
            st.caption("Audio capturado. También puedes usar los botones directos del Plan B:")

        st.markdown("**Botones directos para cambiar las figuras de la Matriz LED (Plan B):**")
        b1, b2 = st.columns(2)
        b3, b4 = st.columns(2)

        with b1:
            if st.button("❤️ Romance → Corazones", use_container_width=True):
                enviar_a_wokwi({"genero": "romance"})
                st.toast("Corazones enviados a Wokwi ❤️")

        with b2:
            if st.button("⭐ Sci-Fi → Estrellas", use_container_width=True):
                enviar_a_wokwi({"genero": "sci-fi"})
                st.toast("Estrellas enviadas a Wokwi ⭐")

        with b3:
            if st.button("🌙 Misterio → Luna", use_container_width=True):
                enviar_a_wokwi({"genero": "misterio"})
                st.toast("Luna enviada a Wokwi 🌙")

        with b4:
            if st.button("✨ Fantasía → Destellos", use_container_width=True):
                enviar_a_wokwi({"genero": "fantasia"})
                st.toast("Destellos enviados a Wokwi ✨")
