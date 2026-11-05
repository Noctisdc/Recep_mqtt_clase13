import streamlit as st
import paho.mqtt.client as mqtt
import json
import time

st.set_page_config(page_title="Monitor IoT", layout="wide", page_icon="📡")

# Estilos CSS limpios y legibles
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
.stApp {
    background-color: #121212; /* Fondo sólido oscuro */
    font-family: 'Inter', sans-serif;
    color: #ffffff; /* Texto principal blanco */
}
.header-title {
    text-align: center;
    font-size: 2.5rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 5px;
}
.header-subtitle {
    text-align: center;
    color: #a0a0a0; /* Gris claro */
    margin-bottom: 30px;
    font-size: 1.1rem;
}
.metric-box {
    background: #1e1e1e; /* Gris muy oscuro */
    border: 1px solid #333333; /* Borde sutil */
    border-radius: 8px;
    padding: 25px;
    text-align: center;
    margin-bottom: 20px;
}
.metric-val {
    font-size: 3rem;
    font-weight: 600;
    color: #ffffff;
    margin: 5px 0;
}
.metric-label {
    color: #888888; /* Gris medio */
    font-size: 1rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}
div[data-testid="stButton"] > button {
    background: #ffffff;
    color: #121212 !important;
    font-weight: 600;
    border: none;
    padding: 12px 24px;
    border-radius: 6px;
    transition: background 0.2s ease;
}
div[data-testid="stButton"] > button:hover {
    background: #e0e0e0; /* Hover un poco más oscuro */
}
/* Inputs */
.stTextInput > div > div > input, .stNumberInput > div > div > input {
    background-color: #1e1e1e;
    color: #ffffff;
    border: 1px solid #333333;
}
/* Alertas */
.stAlert {
    background-color: #1e1e1e;
    color: #ffffff;
    border: 1px solid #333333;
}
</style>
""", unsafe_allow_html=True)

if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = None

def get_mqtt_message(broker, port, topic, client_id):
    message_received = {"received": False, "payload": None}
    
    def on_message(client, userdata, message):
        try:
            message_received["payload"] = json.loads(message.payload.decode())
            message_received["received"] = True
        except:
            message_received["payload"] = message.payload.decode()
            message_received["received"] = True
    
    try:
        client = mqtt.Client(client_id=client_id)
        client.on_message = on_message
        client.connect(broker, port, 60)
        client.subscribe(topic)
        client.loop_start()
        
        timeout = time.time() + 5
        while not message_received["received"] and time.time() < timeout:
            time.sleep(0.1)
        
        client.loop_stop()
        client.disconnect()
        
        return message_received["payload"]
    except Exception as e:
        return {"error": str(e)}


st.markdown('<p class="header-title">Centro de Monitoreo IoT</p>', unsafe_allow_html=True)
st.markdown('<p class="header-subtitle">Adquisición de datos telemétricos en tiempo real vía MQTT</p>', unsafe_allow_html=True)


col_config, col_data = st.columns([1, 2], gap="large")

with col_config:
    with st.container(border=True):
        st.subheader("Configuración")
        broker = st.text_input("Broker MQTT", value="broker.mqttdashboard.com")
        port = st.number_input("Puerto TCP", value=1883)
        topic = st.text_input("Tópico de Suscripción", value="Sensor/THP2")
        client_id = st.text_input("ID Cliente", value="dashboard_iot_camilo")
        
        st.write("")
        if st.button("Capturar Datos", use_container_width=True):
            with st.spinner("Conectando..."):
                st.session_state.sensor_data = get_mqtt_message(broker, int(port), topic, client_id)

with col_data:
    data = st.session_state.sensor_data
    
    if data is None:
        st.info("Presiona 'Capturar Datos' para obtener la lectura más reciente del simulador.")
    
    elif isinstance(data, dict) and "error" in data:
        st.error(f"Error de conexión: {data['error']}")
    
    else:
