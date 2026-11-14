import streamlit as st
import paho.mqtt.client as mqtt

st.set_page_config(page_title="BookNook", page_icon="☕", layout="centered")

# --- DISEÑO CSS INTEGRADO (ESTÉTICA CAFÉ / COZY / GIRLY) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,400&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap');

    /* Fondo principal crema suave y tipografía */
    .stApp {
        background-color: #FAF6F0;
        color: #4A3525;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Barra lateral en tono Latte */
    section[data-testid="stSidebar"] {
        background-color: #EFE6DD !important;
        border-right: 1px solid #E2D5C8;
    }
    section[data-testid="stSidebar"] * {
        color: #4A3525 !important;
    }

    /* Títulos estilo editorial */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #3D2817 !important;
        font-weight: 600 !important;
    }

    /* Tarjetas decorativas */
    .cozy-card {
        background-color: #FFFFFF;
        border: 1px solid #EAE0D5;
        border-radius: 18px;
        padding: 26px;
        box-shadow: 0 6px 20px rgba(74, 53, 37, 0.05);
        margin-bottom: 20px;
    }

    /* Botones estéticos redondeados */
    .stButton > button {
        background-color: #9C7A63 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 10px 26px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(156, 122, 99, 0.25) !important;
    }
    .stButton > button:hover {
        background-color: #7D5E49 !important;
        transform: translateY(-2px);
    }

    /* Cajas de texto y entradas */
    .stTextInput > div > div > input {
        background-color: #FFFFFF !important;
        border: 1.5px solid #DFD3C3 !important;
        border-radius: 12px !important;
        color: #4A3525 !important;
        padding: 10px !important;
    }

    /* Etiqueta de estado */
    .status-badge {
        display: inline-block;
        background-color: #EFE6DD;
        color: #6F4E37;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN MQTT CON WOKWI ---
broker = "broker.mqttdashboard.com"
port = 1883

def on_connect(client, userdata, flags, rc):
    client.subscribe("booknook/estacion")

def on_message(client, userdata, msg):
    st.session_state['ultimo_mensaje'] = msg.payload.decode()

if 'mqtt_client' not in st.session_state:
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(broker, port, 60)
        client.loop_start()
        st.session_state['mqtt_client'] = client
        estado_mqtt = "🟢 Estación física conectada"
    except Exception as e:
        estado_mqtt = f"🔴 Sin conexión ({e})"
else:
    estado_mqtt = "🟢 Estación física conectada"

# --- INTERFAZ DE BIENVENIDA ---
st.markdown(f'<div class="status-badge">{estado_mqtt}</div>', unsafe_allow_html=True)
st.title("BookNook ☕📖")
st.markdown("*Tu rincón inteligente donde cada página cuenta y los libros cobran vida.*")

st.markdown("""
<div class="cozy-card">
    <h3>✨ Bienvenida a tu espacio de lectura</h3>
    <p style="line-height: 1.6; color: #6E5644;">
        Conecta tu lectura física con tu mundo digital sin distracciones. 
        Desde el menú lateral puedes gestionar tu colección, ambientar tu escritorio con tu voz 
        o escuchar tus páginas favoritas mientras haces otras actividades.
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="cozy-card" style="text-align: center; padding: 18px;">
        <h4>📚 Mi Biblioteca</h4>
        <p style="font-size: 0.88rem; color: #7A6251;">Guarda tus portadas, progreso y calificaciones.</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="cozy-card" style="text-align: center; padding: 18px;">
        <h4>🕯️ Sesión</h4>
        <p style="font-size: 0.88rem; color: #7A6251;">Activa las luces de tu estación con tu voz.</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="cozy-card" style="text-align: center; padding: 18px;">
        <h4>🎧 Página que habla</h4>
        <p style="font-size: 0.88rem; color: #7A6251;">Toma una foto a tu libro y escúchalo en voz alta.</p>
    </div>
    """, unsafe_allow_html=True)

if 'ultimo_mensaje' in st.session_state:
    st.markdown(f"""
    <div class="cozy-card" style="background-color: #F4EBE1; border-left: 5px solid #9C7A63;">
        <strong>📡 Señal en vivo desde tu estación Wokwi:</strong><br>
        <code>{st.session_state['ultimo_mensaje']}</code>
    </div>
    """, unsafe_allow_html=True)
