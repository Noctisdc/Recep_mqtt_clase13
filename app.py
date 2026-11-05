import streamlit as st
import paho.mqtt.client as mqtt
import json
import time

# Configuración de página
st.set_page_config(page_title="Monitor IoT", layout="wide", page_icon="📡")

# CSS para un diseño limpio, moderno y de alto contraste
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');

.stApp {
    background-color: #0f172a;
    background-image: radial-gradient(#1e3a5f 1.5px, transparent 1.5px);
    background-size: 26px 26px;
    font-family: 'Space Grotesk', sans-serif;
    color: #f8fafc;
}
.header-container {
    text-align: center;
    padding: 2rem 0;
    margin-bottom: 2rem;
}
.main-title {
    font-size: 3rem;
    font-weight: 700;
    color: #38bdf8;
    margin-bottom: 0.5rem;
}
.sub-title {
    font-size: 1.2rem;
    color: #94a3b8;
    font-weight: 400;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(30, 41, 59, 0.85);
    border: 1px solid #38bdf8;
    border-radius: 12px;
    padding: 1.5rem;
}
.data-card {
    background: rgba(30, 41, 59, 0.95);
    border-left: 4px solid #38bdf8;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
.data-label {
    font-size: 1rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}
.data-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: #ffffff;
}
.stTextInput label, .stNumberInput label {
    color: #e2e8f0 !important;
    font-weight: 600;
    font-size: 1rem;
}
.stTextInput > div > div > input, .stNumberInput > div > div > input {
    background-color: #0f172a;
    color: #ffffff;
    border: 1px solid #475569;
    border-radius: 6px;
}
.stTextInput > div > div > input:focus, .stNumberInput > div > div > input:focus {
    border-color: #38bdf8;
    box-shadow: 0 0 0 1px #38bdf8;
}
div[data-testid="stButton"] > button {
    background-color: #38bdf8;
    color: #0f172a !important;
    font-weight: 700;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    width: 100%;
    transition: all 0.2s;
}
div[data-testid="stButton"] > button:hover {
    background-color: #0ea5e9;
    color: #ffffff !important;
    transform: translateY(-1px);
}
.stAlert {
    background-color: rgba(56, 189, 248, 0.1);
    border: 1px solid #38bdf8;
    color: #f8fafc;
}
.stAlert p {
    color: #e2e8f0 !important;
}
</style>
""", unsafe_allow_html=True)

# Lógica MQTT
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

# Encabezado
st.markdown('''
<div class="header-container">
    <div class="main-title">📡 Panel de Adquisición IoT</div>
    <div class="sub-title">Recepción de datos telemétricos en tiempo real vía protocolo MQTT</div>
</div>
''', unsafe_allow_html=True)

# Diseño en dos columnas
col_config, col_visor = st.columns([1, 2], gap="large")

with col_config:
    with st.container(border=True):
        st.markdown("<h3 style='color: #38bdf8; margin-bottom: 1rem;'>⚙️ Configuración</h3>", unsafe_allow_html=True)
        
        broker = st.text_input("Broker MQTT", value="broker.mqttdashboard.com")
        port = st.number_input("Puerto TCP", value=1883)
        topic = st.text_input("Tópico de Suscripción", value="Sensor/THP2")
        client_id = st.text_input("ID de Cliente", value="portafolio_iot_client")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Obtener Datos del Sensor"):
            with st.spinner("Estableciendo conexión..."):
                st.session_state.sensor_data = get_mqtt_message(broker, int(port), topic, client_id)

with col_visor:
    data = st.session_state.sensor_data
    
    if data is None:
        st.info("💡 Asegúrate de que la simulación en Wokwi esté activa y presiona 'Obtener Datos del Sensor'.")
    
    elif isinstance(data, dict) and "error" in data:
        st.error(f"⚠️ Error de red: {data['error']}. Verifica el broker o tu conexión a internet.")
    
    else:
        if isinstance(data, dict):
            temp = data.get("Temp", "--")
            hum = data.get("Hum", "--")
            
            c1, c2 = st.columns(2)
            
            with c1:
                st.markdown(f'''
                <div class="data-card">
                    <div class="data-label">Temperatura Ambiente</div>
                    <div class="data-value">{temp} °C</div>
                </div>
                ''', unsafe_allow_html=True)
                
            with c2:
                st.markdown(f'''
                <div class="data-card">
                    <div class="data-label">Humedad Relativa</div>
                    <div class="data-value">{hum} %</div>
                </div>
                ''', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("Inspeccionar carga útil (JSON crudo)"):
                st.json(data)
                
        else:
            st.warning("Se recibió información, pero el payload no está formateado como JSON estructurado.")
            st.code(data)
