import streamlit as st
import paho.mqtt.client as mqtt
import json

st.set_page_config(page_title="BookNook | Sanctuary", page_icon="🦢", layout="wide")

# --- DISEÑO CSS EDITORIAL (DARK ACADEMIA / COZY LATTE / GIRLY) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');

    .stApp {
        background: radial-gradient(circle at top right, #FDFBF7 0%, #F4EBE1 55%, #E8D8C8 100%);
        color: #3B281E;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2C1D14 0%, #3E2A1E 100%) !important;
        border-right: 2px solid #C89F81;
    }
    section[data-testid="stSidebar"] * {
        color: #F7EFE6 !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    h1, h2, h3, .serif-title {
        font-family: 'Cormorant Garamond', serif !important;
        color: #2C1D14 !important;
        letter-spacing: -0.02em;
    }

    /* Hero Banner con imagen estética */
    .hero-banner {
        position: relative;
        background-image: linear-gradient(90deg, rgba(44, 29, 20, 0.82) 0%, rgba(44, 29, 20, 0.45) 100%), 
                          url('https://images.unsplash.com/photo-1507842229356-51c61504d3ab?auto=format&fit=crop&w=1400&q=80');
        background-size: cover;
        background-position: center;
        border-radius: 26px;
        padding: 52px 45px;
        color: #FDFBF7 !important;
        box-shadow: 0 18px 40px rgba(44, 29, 20, 0.18);
        margin-bottom: 30px;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    .hero-banner h1 {
        color: #FDFBF7 !important;
        font-size: 3.4rem !important;
        margin-bottom: 8px;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(212, 163, 115, 0.35);
        backdrop-filter: blur(6px);
        border: 1px solid #E6CCB2;
        color: #FFF8F0;
        padding: 6px 16px;
        border-radius: 30px;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 15px;
    }

    /* Tarjetas Glassmorphism */
    .luxe-card {
        background: rgba(255, 252, 248, 0.78);
        backdrop-filter: blur(12px);
        border: 1px solid #E6D7C3;
        border-radius: 22px;
        padding: 26px;
        box-shadow: 0 10px 30px rgba(74, 53, 37, 0.07);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        height: 100%;
    }
    .luxe-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 16px 35px rgba(74, 53, 37, 0.13);
        border-color: #C89F81;
    }

    .metric-pill {
        background: linear-gradient(135deg, #FFFDF9 0%, #F3E5D8 100%);
        border: 1px solid #DECBB7;
        border-radius: 18px;
        padding: 18px 22px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(59, 40, 30, 0.05);
    }
    .metric-number {
        font-family: 'Cormorant Garamond', serif;
        font-size: 2.3rem;
        font-weight: 700;
        color: #6F4E37;
        line-height: 1.1;
    }

    .stButton > button {
        background: linear-gradient(135deg, #8C624C 0%, #5E3A24 100%) !important;
        color: #FFFDF9 !important;
        border: 1px solid #D4A373 !important;
        border-radius: 30px !important;
        padding: 10px 28px !important;
        font-weight: 500 !important;
        letter-spacing: 0.03em;
        box-shadow: 0 6px 18px rgba(94, 58, 36, 0.28) !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #A4755D 0%, #6E452C 100%) !important;
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# --- ESTADO GLOBAL Y MEMORIA DE BOOKNOOK ---
if 'libros' not in st.session_state:
    st.session_state['libros'] = [
        {"titulo": "A Court of Thorns and Roses", "autor": "Sarah J. Maas", "genero": "Fantasía / Romance", "progreso": 85, "estrellas": 5, "portada": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80"},
        {"titulo": "Dead Letters (Borrador)", "autor": "Mariana R.", "genero": "Indie Rock / Drama", "progreso": 60, "estrellas": 5, "portada": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80"},
        {"titulo": " La Biblioteca de la Medianoche", "autor": "Matt Haig", "genero": "Ficción", "progreso": 100, "estrellas": 4, "portada": "https://images.unsplash.com/photo-1495446815901-a7297e633e8d?auto=format&fit=crop&w=600&q=80"}
    ]
if 'minutos_leidos' not in st.session_state:
    st.session_state['minutos_leidos'] = 145
if 'estado_sesion' not in st.session_state:
    st.session_state['estado_sesion'] = "En espera"
if 'calificacion_fisica' not in st.session_state:
    st.session_state['calificacion_fisica'] = 5

# --- CONEXIÓN MQTT BIDIRECCIONAL CON WOKWI ---
broker = "broker.mqttdashboard.com"
port = 1883

def on_connect(client, userdata, flags, rc):
    client.subscribe("booknook/estacion")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    st.session_state['ultimo_mensaje'] = payload
    try:
        datos = json.loads(payload)
        if "evento" in datos:
            st.session_state['estado_sesion'] = "📖 Leyendo ahora" if datos["evento"] == "inicio" else "⏸️ Sesión en pausa"
        if "estrellas" in datos:
            st.session_state['calificacion_fisica'] = datos["estrellas"]
    except:
        pass

if 'mqtt_client' not in st.session_state:
    try:
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(broker, port, 60)
        client.loop_start()
        st.session_state['mqtt_client'] = client
        mqtt_status = "🟢 Estación Física Wokwi Sincronizada"
    except Exception as e:
        mqtt_status = "🔴 Modo desconectado"
else:
    mqtt_status = "🟢 Estación Física Wokwi Sincronizada"

# --- HERO BANNER ---
st.markdown(f"""
<div class="hero-banner">
    <div class="hero-badge">{mqtt_status}</div>
    <h1>BookNook Sanctuary 🦢☕</h1>
    <p style="font-size: 1.15rem; max-width: 650px; opacity: 0.95; font-weight: 300; line-height: 1.6;">
        Tu refugio literario inteligente. Sincroniza tu lámpara física, ambienta tu espacio 
        con comandos de voz y transforma tus páginas impresas en audiolibros al instante.
    </p>
</div>
""", unsafe_allow_html=True)

# --- MÉTRICAS DEL RINCÓN DE LECTURA ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="metric-pill">
        <div style="font-size:0.8rem; text-transform:uppercase; letter-spacing:0.08em; color:#8C624C;">Estado Estación</div>
        <div class="metric-number" style="font-size:1.5rem; margin-top:6px;">{st.session_state['estado_sesion']}</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="metric-pill">
        <div style="font-size:0.8rem; text-transform:uppercase; letter-spacing:0.08em; color:#8C624C;">Tiempo de Lectura</div>
        <div class="metric-number">{st.session_state['minutos_leidos']} min</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="metric-pill">
        <div style="font-size:0.8rem; text-transform:uppercase; letter-spacing:0.08em; color:#8C624C;">Reto Anual 2026</div>
        <div class="metric-number">{len(st.session_state['libros'])} / 12 📚</div>
    </div>
    """, unsafe_allow_html=True)
with c4:
    estrellas_str = "★" * int(st.session_state['calificacion_fisica'])
    st.markdown(f"""
    <div class="metric-pill">
        <div style="font-size:0.8rem; text-transform:uppercase; letter-spacing:0.08em; color:#8C624C;">Perilla Física</div>
        <div class="metric-number" style="color:#D4A373;">{estrellas_str}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.markdown("### ✨ Experiencias Multimodales")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="luxe-card">
        <img src="https://images.unsplash.com/photo-1519682337058-a94d519337bc?auto=format&fit=crop&w=600&q=80" style="width:100%; height:150px; object-fit:cover; border-radius:14px; margin-bottom:15px;">
        <h3>🏛️ I. Mi Biblioteca</h3>
        <p style="color:#6E5644; font-size:0.92rem; line-height:1.5;">
            Colecciona tus lecturas actuales, registra tus portadas favoritas y recibe la calificación en estrellas directamente desde el potenciómetro físico de tu estación.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="luxe-card">
        <img src="https://images.unsplash.com/photo-1513519245088-0e12902e5a38?auto=format&fit=crop&w=600&q=80" style="width:100%; height:150px; object-fit:cover; border-radius:14px; margin-bottom:15px;">
        <h3>🕯️ II. Sesión por Voz</h3>
        <p style="color:#6E5644; font-size:0.92rem; line-height:1.5;">
            Dile a BookNook qué género vas a leer (<i>Romance, Misterio o Ciencia Ficción</i>) y observa cómo la matriz LED de tu escritorio dibuja corazones, lunas o estrellas.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="luxe-card">
        <img src="https://images.unsplash.com/photo-1457369804613-52c61a468e7d?auto=format&fit=crop&w=600&q=80" style="width:100%; height:150px; object-fit:cover; border-radius:14px; margin-bottom:15px;">
        <h3>🎧 III. Página que Habla</h3>
        <p style="color:#6E5644; font-size:0.92rem; line-height:1.5;">
            ¿Ocupada mientras cocinas o descansas? Captura una foto de la página de tu libro; nuestro motor OCR extraerá el texto y lo narrará con voz cálida para ti.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.write("")
if 'ultimo_mensaje' in st.session_state:
    st.markdown(f"""
    <div class="luxe-card" style="background: linear-gradient(90deg, #EFE5DC 0%, #FAF6F0 100%); border-left: 5px solid #8C624C; padding: 18px 24px;">
        <strong>📡 Telemetría en vivo desde Wokwi (`booknook/estacion`):</strong> 
        <code style="background:#FFF; padding:4px 10px; border-radius:8px; color:#5E3A24;">{st.session_state['ultimo_mensaje']}</code>
    </div>
    """, unsafe_allow_html=True)

if st.button("🔄 Actualizar telemetría de la estación"):
    st.rerun()
