import streamlit as st
import paho.mqtt.client as mqtt
import pandas as pd
import json
import os
import time

st.set_page_config(page_title="BookNook | Cada página cuenta", page_icon="✨", layout="wide")

os.makedirs("data", exist_ok=True)

# Inicializar libros sin minutos falsos hoy
if not os.path.exists("data/libros.csv"):
    df_init_libros = pd.DataFrame([
        {"titulo": "María", "autor": "Jorge Isaacs", "genero": "Romance", "estante": "Leyendo", "estrellas": 0, "portada": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80"},
        {"titulo": "A Court of Thorns and Roses", "autor": "Sarah J. Maas", "genero": "Fantasía", "estante": "Leyendo", "estrellas": 5, "portada": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=600&q=80"},
        {"titulo": "Dead Letters", "autor": "Mari Reinoso", "genero": "Romance", "estante": "Leyendo", "estrellas": 5, "portada": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80"},
        {"titulo": "Dune", "autor": "Frank Herbert", "genero": "Ciencia ficción", "estante": "Quiero leer", "estrellas": 0, "portada": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=600&q=80"},
        {"titulo": "Drácula", "autor": "Bram Stoker", "genero": "Misterio y terror", "estante": "Leídos", "estrellas": 5, "portada": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=600&q=80"}
    ])
    df_init_libros.to_csv("data/libros.csv", index=False)

if not os.path.exists("data/sesiones.csv"):
    df_init_ses = pd.DataFrame(columns=["fecha", "libro", "minutos"])
    df_init_ses.to_csv("data/sesiones.csv", index=False)

if not os.path.exists("data/citas.csv"):
    df_init_citas = pd.DataFrame([
        {"libro": "María - Jorge Isaacs", "cita": "Era yo niño aún cuando me alejaron de la casa paterna para que diera principio a mis estudios..."}
    ])
    df_init_citas.to_csv("data/citas.csv", index=False)

# --- BUZÓN EN TIEMPO REAL PARA MQTT (Soluciona que Streamlit sí reciba datos de Wokwi) ---
@st.cache_resource
def obtener_estado_compartido():
    return {
        "libro_activo": "María",
        "ambiente_activo": "Sin activar aún",
        "leyendo_ahora": False,
        "inicio_timestamp": None,
        "minutos_hoy": 0,
        "estrellas_actuales": 0,
        "ultimo_libro_calificado": "Ninguno aún",
        "ultimo_payload": "Esperando acciones en Wokwi..."
    }

estado_hw = obtener_estado_compartido()

@st.cache_resource
def iniciar_mqtt():
    def on_connect(client, userdata, flags, rc):
        client.subscribe("booknook/estacion")

    def on_message(client, userdata, msg):
        payload = msg.payload.decode()
        estado_hw["ultimo_payload"] = payload
        try:
            data = json.loads(payload)
            if "libro" in data:
                estado_hw["libro_activo"] = data["libro"]
            if "evento" in data:
                if data["evento"] == "inicio":
                    estado_hw["leyendo_ahora"] = True
                    estado_hw["inicio_timestamp"] = time.time()
                elif data["evento"] == "fin":
                    estado_hw["leyendo_ahora"] = False
                    mins = int(data.get("minutos", 1))
                    estado_hw["minutos_hoy"] += mins
                    estado_hw["inicio_timestamp"] = None
                    # Guardar sesión real en CSV
                    df_s = pd.read_csv("data/sesiones.csv")
                    nuevo = pd.DataFrame([{"fecha": time.strftime("%d %b %H:%M"), "libro": estado_hw["libro_activo"], "minutos": mins}])
                    df_s = pd.concat([df_s, nuevo], ignore_index=True)
                    df_s.to_csv("data/sesiones.csv", index=False)
            if "estrellas" in data:
                est = int(data["estrellas"])
                lib_calif = data.get("libro", estado_hw["libro_activo"])
                estado_hw["estrellas_actuales"] = est
                estado_hw["ultimo_libro_calificado"] = lib_calif
                # Actualizar estrellas reales del libro en CSV
                if os.path.exists("data/libros.csv"):
                    df_l = pd.read_csv("data/libros.csv")
                    mask = df_l["titulo"].str.lower().str.contains(lib_calif[:5].lower(), na=False)
                    if mask.any():
                        df_l.loc[mask, "estrellas"] = est
                        df_l.to_csv("data/libros.csv", index=False)
        except Exception:
            pass

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("broker.mqttdashboard.com", 1883, 60)
    client.loop_start()
    return client

mqtt_client = iniciar_mqtt()

# --- ESTILO VISUAL ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    .stApp { background: radial-gradient(circle at top, #FBF7F2 0%, #F3EAE0 60%, #EADBC8 100%); color: #4A332D; font-family: 'Plus Jakarta Sans', sans-serif; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #4A332D 0%, #36221C 100%) !important; border-right: 3px solid #B5838D; }
    section[data-testid="stSidebar"] * { color: #FBF7F2 !important; }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #4A332D !important; }
    .hero-box {
        background: linear-gradient(135deg, rgba(74, 51, 45, 0.88) 0%, rgba(181, 131, 141, 0.82) 100%),
                    url('https://images.unsplash.com/photo-1519682337058-a94d519337bc?auto=format&fit=crop&w=1400&q=80');
        background-size: cover; background-position: center; border-radius: 28px; padding: 42px;
        color: #FBF7F2 !important; box-shadow: 0 18px 40px rgba(74, 51, 45, 0.18); border: 2px solid #D4AF37; margin-bottom: 24px; text-align: center;
    }
    .hero-box h1 { color: #FBF7F2 !important; font-size: 3.1rem !important; margin-bottom: 6px; }
    .pill-tag { display: inline-block; background-color: #B5838D; color: #FFF !important; padding: 6px 18px; border-radius: 25px; font-size: 0.82rem; font-weight: 600; border: 1px solid #F3EAE0; margin-bottom: 12px; }
    .card-cozy { background: #FFFDF9; border: 1.5px solid #E2D0BE; border-top: 5px solid #B5838D; border-radius: 22px; padding: 24px; box-shadow: 0 10px 25px rgba(74, 51, 45, 0.06); height: 100%; }
    .kpi-card { background: linear-gradient(135deg, #FFFDF9 0%, #F7EDE4 100%); border: 1.5px solid #D8C2B0; border-radius: 20px; padding: 18px; text-align: center; box-shadow: 0 6px 16px rgba(74, 51, 45, 0.05); }
    .kpi-val { font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 700; color: #B5838D; }
    .stButton > button { background: linear-gradient(135deg, #B5838D 0%, #8E5B66 100%) !important; color: #FFFFFF !important; border: 1px solid #D4AF37 !important; border-radius: 30px !important; padding: 10px 24px !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-box">
    <div class="pill-tag">🟢 Sincronización Bidireccional MQTT Activa en Tiempo Real</div>
    <h1>✨ BookNook ✨</h1>
    <p style="font-size: 1.25rem; font-style: italic;">"Tu rincón donde los libros cobran vida · Porque cada página cuenta"</p>
</div>
""", unsafe_allow_html=True)

df_libros = pd.read_csv("data/libros.csv")
leidos_count = len(df_libros[df_libros["estante"] == "Leídos"])

# Calcular tiempo en vivo si el botón físico de Wokwi está encendido
tiempo_en_curso = 0
if estado_hw["leyendo_ahora"] and estado_hw["inicio_timestamp"]:
    tiempo_en_curso = int(time.time() - estado_hw["inicio_timestamp"])

minutos_reales_hoy = estado_hw["minutos_hoy"] + tiempo_en_curso
estado_boton_txt = f"🟢 Leyendo en vivo ({tiempo_en_curso} min actuales)" if estado_hw["leyendo_ahora"] else "⏸️ Cronómetro detenido (Presiona el botón en Wokwi)"
meta_txt = "🎉 ¡Meta de 30 min cumplida!" if minutos_reales_hoy >= 30 else f"Faltan {30 - minutos_reales_hoy} min para tu meta diaria de 30 min"

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div style="font-size:0.78rem; font-weight:700; color:#6D4C41;">LIBRO EN ESTACIÓN (LCD)</div>
        <div class="kpi-val">{estado_hw['libro_activo']}</div>
        <div style="font-size:0.8rem; color:#8D6E63;">{estado_boton_txt}</div>
    </div>
    """, unsafe_allow_html=True)
with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div style="font-size:0.78rem; font-weight:700; color:#6D4C41;">HOY HAS LEÍDO (REAL)</div>
        <div class="kpi-val">{minutos_reales_hoy} min</div>
        <div style="font-size:0.8rem; color:#2E7D32;">{meta_txt}</div>
    </div>
    """, unsafe_allow_html=True)
with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div style="font-size:0.78rem; font-weight:700; color:#6D4C41;">RETO ANUAL 2026</div>
        <div class="kpi-val">{leidos_count} de 12 📚</div>
        <div style="font-size:0.8rem; color:#8D6E63;">Libros terminados en tu biblioteca</div>
    </div>
    """, unsafe_allow_html=True)
with k4:
    est_num = int(estado_hw["estrellas_actuales"])
    est_iconos = "⭐" * est_num if est_num > 0 else "Sin calificar"
    st.markdown(f"""
    <div class="kpi-card">
        <div style="font-size:0.78rem; font-weight:700; color:#6D4C41;">PERILLA FÍSICA (WOKWI)</div>
        <div class="kpi-val">{est_iconos}</div>
        <div style="font-size:0.8rem; color:#8D6E63;">Aplicado a: <b>{estado_hw['ultimo_libro_calificado']}</b></div>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.info(f"📡 **Señal en vivo desde Wokwi (`booknook/estacion`):** `{estado_hw['ultimo_payload']}`")

col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    if st.button("🔄 Refrescar panel"):
        st.rerun()

# Si el cronómetro está encendido en Wokwi, refresca cada 2 segundos automáticamente
if estado_hw["leyendo_ahora"]:
    time.sleep(2)
    st.rerun()
