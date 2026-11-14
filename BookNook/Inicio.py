import streamlit as st
import paho.mqtt.client as mqtt
import pandas as pd
import json
import os

st.set_page_config(page_title="BookNook | Cada página cuenta", page_icon="✨", layout="wide")

# --- CREACIÓN AUTOMÁTICA DE ARCHIVOS CSV (Capítulo 6 de la Propuesta) ---
os.makedirs("data", exist_ok=True)

if not os.path.exists("data/libros.csv"):
    df_init_libros = pd.DataFrame([
        {"titulo": "María", "autor": "Jorge Isaacs", "genero": "Romance", "estante": "Leyendo", "estrellas": 5, "portada": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80"},
        {"titulo": "A Court of Thorns and Roses", "autor": "Sarah J. Maas", "genero": "Fantasía", "estante": "Leídos", "estrellas": 5, "portada": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=600&q=80"},
        {"titulo": "Dead Letters", "autor": "Mari Reinoso", "genero": "Romance", "estante": "Leyendo", "estrellas": 5, "portada": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80"},
        {"titulo": "Dune", "autor": "Frank Herbert", "genero": "Ciencia ficción", "estante": "Leídos", "estrellas": 4, "portada": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=600&q=80"},
        {"titulo": "Drácula", "autor": "Bram Stoker", "genero": "Misterio y terror", "estante": "Quiero leer", "estrellas": 5, "portada": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=600&q=80"},
        {"titulo": "Orgullo y Prejuicio", "autor": "Jane Austen", "genero": "Romance", "estante": "Leídos", "estrellas": 5, "portada": "https://images.unsplash.com/photo-1495446815901-a7297e633e8d?auto=format&fit=crop&w=600&q=80"},
        {"titulo": "El Nombre del Viento", "autor": "Patrick Rothfuss", "genero": "Fantasía", "estante": "Leídos", "estrellas": 5, "portada": "https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=600&q=80"},
        {"titulo": "Frankenstein", "autor": "Mary Shelley", "genero": "Misterio y terror", "estante": "Leídos", "estrellas": 4, "portada": "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&w=600&q=80"},
        {"titulo": "Cien años de soledad", "autor": "Gabriel García Márquez", "genero": "Fantasía", "estante": "Leídos", "estrellas": 5, "portada": "https://images.unsplash.com/photo-1476275466078-4007374efbbe?auto=format&fit=crop&w=600&q=80"},
        {"titulo": " Pedro Páramo", "autor": "Juan Rulfo", "genero": "Misterio y terror", "estante": "Leídos", "estrellas": 5, "portada": "https://images.unsplash.com/photo-1519682337058-a94d519337bc?auto=format&fit=crop&w=600&q=80"}
    ])
    df_init_libros.to_csv("data/libros.csv", index=False)

if not os.path.exists("data/sesiones.csv"):
    df_init_ses = pd.DataFrame([
        {"fecha": "10 Nov", "libro": "María", "minutos": 25},
        {"fecha": "11 Nov", "libro": "María", "minutos": 40},
        {"fecha": "12 Nov", "libro": "Dead Letters", "minutos": 30},
        {"fecha": "13 Nov", "libro": "María", "minutos": 35}
    ])
    df_init_ses.to_csv("data/sesiones.csv", index=False)

if not os.path.exists("data/citas.csv"):
    df_init_citas = pd.DataFrame([
        {"libro": "María - Jorge Isaacs", "cita": "Era yo niño aún cuando me alejaron de la casa paterna para que diera principio a mis estudios..."}
    ])
    df_init_citas.to_csv("data/citas.csv", index=False)

# --- ESTILO VISUAL: PALETA BEIGE, PALO DE ROSA Y CAFÉ (IGUAL AL PDF) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    .stApp {
        background: radial-gradient(circle at top, #FBF7F2 0%, #F3EAE0 60%, #EADBC8 100%);
        color: #4A332D;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #4A332D 0%, #36221C 100%) !important;
        border-right: 3px solid #B5838D;
    }
    section[data-testid="stSidebar"] * {
        color: #FBF7F2 !important;
    }
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #4A332D !important;
    }
    .hero-box {
        background: linear-gradient(135deg, rgba(74, 51, 45, 0.88) 0%, rgba(181, 131, 141, 0.82) 100%),
                    url('https://images.unsplash.com/photo-1519682337058-a94d519337bc?auto=format&fit=crop&w=1400&q=80');
        background-size: cover;
        background-position: center;
        border-radius: 28px;
        padding: 48px 42px;
        color: #FBF7F2 !important;
        box-shadow: 0 18px 40px rgba(74, 51, 45, 0.18);
        border: 2px solid #D4AF37;
        margin-bottom: 28px;
        text-align: center;
    }
    .hero-box h1 { color: #FBF7F2 !important; font-size: 3.3rem !important; margin-bottom: 6px; }
    .pill-tag {
        display: inline-block;
        background-color: #B5838D;
        color: #FFF !important;
        padding: 6px 18px;
        border-radius: 25px;
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        border: 1px solid #F3EAE0;
        margin-bottom: 14px;
    }
    .card-cozy {
        background: #FFFDF9;
        border: 1.5px solid #E2D0BE;
        border-top: 5px solid #B5838D;
        border-radius: 22px;
        padding: 24px;
        box-shadow: 0 10px 25px rgba(74, 51, 45, 0.06);
        height: 100%;
    }
    .kpi-card {
        background: linear-gradient(135deg, #FFFDF9 0%, #F7EDE4 100%);
        border: 1.5px solid #D8C2B0;
        border-radius: 20px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 6px 16px rgba(74, 51, 45, 0.05);
    }
    .kpi-val {
        font-family: 'Playfair Display', serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: #B5838D;
    }
    .stButton > button {
        background: linear-gradient(135deg, #B5838D 0%, #8E5B66 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid #D4AF37 !important;
        border-radius: 30px !important;
        padding: 10px 26px !important;
        font-weight: 600 !important;
        box-shadow: 0 6px 15px rgba(181, 131, 141, 0.35) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- MEMORIA DE ESTADOS Y CONEXIÓN MQTT ---
if 'evento_wokwi' not in st.session_state:
    st.session_state['evento_wokwi'] = "Esperando botón físico..."
if 'minutos_hoy' not in st.session_state:
    st.session_state['minutos_hoy'] = 35
if 'estrellas_perilla' not in st.session_state:
    st.session_state['estrellas_perilla'] = 5
if 'libro_actual' not in st.session_state:
    st.session_state['libro_actual'] = "María"

def on_connect(client, userdata, flags, rc):
    client.subscribe("booknook/estacion")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    st.session_state['raw_mqtt'] = payload
    try:
        data = json.loads(payload)
        if "evento" in data:
            if data["evento"] == "inicio":
                st.session_state['evento_wokwi'] = "⏱️ Cronómetro corriendo"
            elif data["evento"] == "fin":
                mins = data.get("minutos", 35)
                st.session_state['minutos_hoy'] = mins
                st.session_state['evento_wokwi'] = f"✅ Terminado ({mins} min)"
        if "estrellas" in data:
            st.session_state['estrellas_perilla'] = int(data["estrellas"])
    except:
        pass

if 'mqtt_client' not in st.session_state:
    try:
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect("broker.mqttdashboard.com", 1883, 60)
        client.loop_start()
        st.session_state['mqtt_client'] = client
        estado_red = "🟢 Estación Wokwi Conectada · broker.mqttdashboard.com"
    except:
        estado_red = "🔴 Reconectando MQTT..."
else:
    estado_red = "🟢 Estación Wokwi Conectada · broker.mqttdashboard.com"

# --- BANNER DE PORTADA ---
st.markdown(f"""
<div class="hero-box">
    <div class="pill-tag">{estado_red}</div>
    <h1>✨ BookNook ✨</h1>
    <p style="font-size: 1.35rem; font-style: italic; margin-bottom: 10px;">
        "Tu rincón donde los libros cobran vida · Porque cada página cuenta"
    </p>
    <p style="font-size: 0.98rem; max-width: 680px; margin: 0 auto; opacity: 0.95;">
        Una estación de lectura en Wokwi que crea el ambiente de tu libro y cuenta cada minuto, 
        conectada por MQTT a tu app que te lee cualquier página en voz alta.
    </p>
</div>
""", unsafe_allow_html=True)

# --- INDICADORES EN VIVO (RF7, RF10, RF11) ---
df_libros = pd.read_csv("data/libros.csv")
leidos_count = len(df_libros[df_libros["estante"] == "Leídos"])

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div style="font-size:0.8rem; font-weight:600; color:#6D4C41;">LIBRO EN ESTACIÓN (LCD)</div>
        <div class="kpi-val">{st.session_state['libro_actual']}</div>
        <div style="font-size:0.8rem; color:#8D6E63;">{st.session_state['evento_wokwi']}</div>
    </div>
    """, unsafe_allow_html=True)
with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div style="font-size:0.8rem; font-weight:600; color:#6D4C41;">HOY HAS LEÍDO</div>
        <div class="kpi-val">{st.session_state['minutos_hoy']} min</div>
        <div style="font-size:0.8rem; color:#2E7D32;">🎯 Meta diaria: 30 min ¡Cumplida!</div>
    </div>
    """, unsafe_allow_html=True)
with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div style="font-size:0.8rem; font-weight:600; color:#6D4C41;">RETO ANUAL 2026</div>
        <div class="kpi-val">{leidos_count} de 12 📚</div>
        <div style="font-size:0.8rem; color:#8D6E63;">🔥 Racha activa: 4 días</div>
    </div>
    """, unsafe_allow_html=True)
with k4:
    estrellas_txt = "⭐" * int(st.session_state['estrellas_perilla'])
    st.markdown(f"""
    <div class="kpi-card">
        <div style="font-size:0.8rem; font-weight:600; color:#6D4C41;">PERILLA FÍSICA (WOKWI)</div>
        <div class="kpi-val">{estrellas_txt}</div>
        <div style="font-size:0.8rem; color:#8D6E63;">{st.session_state['estrellas_perilla']} de 5 estrellas</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.markdown("### 🌸 Dos mundos que se hablan (Capítulos 4 y 6)")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
    <div class="card-cozy">
        <h3>📚 1. Mi biblioteca</h3>
        <p style="color:#6D4C41; font-size:0.93rem;">
            Sube la foto de la portada (como <b>María de Jorge Isaacs</b>), organiza tus estantes 
            (<i>Leyendo, Quiero leer, Leídos</i>), califica con la perilla física y revisa tu avance del reto 2026 con gráficas.
        </p>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown("""
    <div class="card-cozy">
        <h3>⏱️ 2. Sesión de lectura</h3>
        <p style="color:#6D4C41; font-size:0.93rem;">
            Elige tu libro para mostrarlo en el LCD, di por voz <b>"voy a leer romance"</b> para llenar la matriz 
            de corazones (o lunas, estrellas y destellos) y cronometra tu tiempo con el botón físico.
        </p>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown("""
    <div class="card-cozy">
        <h3>📸 3. Página que habla</h3>
        <p style="color:#6D4C41; font-size:0.93rem;">
            ¿Te toca cocinar o tienes las manos ocupadas? Tómale foto o screenshot a la página, 
            extrae el texto con <b>OCR</b>, escúchala en voz alta con <b>gTTS</b> y guarda tus citas favoritas.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.write("")
if 'raw_mqtt' in st.session_state:
    st.info(f"📡 **Último mensaje recibido desde la estación Wokwi (`booknook/estacion`):** `{st.session_state['raw_mqtt']}`")
