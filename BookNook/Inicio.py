import streamlit as st
import paho.mqtt.client as mqtt

# Configuración de la página
st.set_page_config(page_title="BookNook", page_icon="📚", layout="centered")

st.title("Bienvenida a BookNook ✨")
st.markdown("Tu rincón donde los libros cobran vida.")

# Configuración del chat MQTT
broker = "broker.mqttdashboard.com"
port = 1883

def on_connect(client, userdata, flags, rc):
    client.subscribe("booknook/estacion")

def on_message(client, userdata, msg):
    mensaje = msg.payload.decode()
    st.session_state['ultimo_mensaje'] = mensaje

# Iniciar la conexión en segundo plano
if 'mqtt_client' not in st.session_state:
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(broker, port, 60)
        client.loop_start()
        st.session_state['mqtt_client'] = client
        st.success("Conectado a la estación BookNook 📡")
    except Exception as e:
        st.error(f"Error de conexión: {e}")

st.write("Usa el menú lateral para navegar a tu biblioteca, tu sesión de lectura o la página que habla.")

# Mostrar en vivo lo que manda Wokwi
if 'ultimo_mensaje' in st.session_state:
    st.info(f"Mensaje desde la estación: {st.session_state['ultimo_mensaje']}")
