import streamlit as st
import paho.mqtt.client as mqtt
import json
import time

# Configuración de página a pantalla completa (Dashboard)
st.set_page_config(page_title="Monitor IoT", layout="wide", page_icon="📡")

# Estilos CSS personalizados
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&display=swap');
.stApp {
    background-color: #0f172a;
    background-image: radial-gradient(#1e3a5f 1.5px, transparent 1.5px);
    background-size: 26px 26px;
    font-family: 'Space Grotesk', sans-serif;
    color: #e2e8f0;
}
.header-title {
    text-align: center;
    font-size: 3rem;
    font-weight: 700;
    color: #38bdf8;
    margin-bottom: 0;
    text-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
}
.header-subtitle {
    text-align: center;
    color: #94a3b8;
    margin-bottom: 40px;
    font-size: 1.2rem;
}
.metric-box {
    background: #1e293b;
    border: 2px solid #38bdf8;
    border-radius: 15px;
    padding: 30px 20px;
    text-align: center;
    box-shadow: 6px 6px 0px #0ea5e9;
    margin-bottom: 20px;
}
.metric-val {
    font-size: 3.5rem;
    font-weight: 700;
    color: #f8fafc;
    margin: 10px 0;
}
.metric-label {
    color: #38bdf8;
    font-size: 1.2rem;
    text-transform: uppercase;
    letter-spacing: 2px;
}
div[data-testid="stButton"] > button {
    background: #38bdf8;
    color: #0f172a !important;
    font-weight: 700;
    border: none;
    padding: 15px 30px;
    border-radius: 10px;
    transition: all 0.3s ease;
}
div[data-testid="stButton"] > button:hover {
    background: #e2e8f0;
    transform: translateY(-2px);
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

# --- Interfaz Principal ---
st.markdown('<p class="header-title">📡 Centro de Monitoreo IoT</p>', unsafe_allow_html=True)
st.markdown('<p class="header-subtitle">Adquisición de datos telemétricos en tiempo real vía MQTT</p>', unsafe_allow_html=True)

# Layout: Panel lateral para configuración, área principal para visualización
col_config, col_data = st.columns([1, 2], gap="large")

with col_config:
    with st.container(border=True):
        st.subheader("⚙️ Conexión")
        broker = st.text_input("Broker MQTT", value="broker.mqttdashboard.com")
        port = st.number_input("Puerto TCP", value=1883)
        topic = st.text_input("Tópico de Suscripción", value="Sensor/THP2")
        client_id = st.text_input("ID Cliente", value="dashboard_iot_camilo")
        
        st.write("")
        if st.button("🔄 Capturar Datos", use_container_width=True):
            with st.spinner("Escuchando al sensor..."):
                st.session_state.sensor_data = get_mqtt_message(broker, int(port), topic, client_id)

with col_data:
    data = st.session_state.sensor_data
    
    if data is None:
        st.info("👈 Presiona 'Capturar Datos' (Asegúrate de que Wokwi esté corriendo).")
    
    elif isinstance(data, dict) and "error" in data:
        st.error(f"❌ Error de red: {data['error']}. Revisa la conexión o el puerto.")
    
    else:
        if isinstance(data, dict):
            # Extraer variables con valores por defecto por si acaso
            temp = data.get("Temp", "--")
            hum = data.get("Hum", "--")
            
            # Tarjetas de diseño personalizado
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">🌡️ Temperatura</div>
                    <div class="metric-val">{temp} °C</div>
                </div>
                """, unsafe_allow_html=True)
            
            with c2:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">💧 Humedad</div>
                    <div class="metric-val">{hum} %</div>
                </div>
                """, unsafe_allow_html=True)
            
            with st.expander("Ver JSON en crudo recibido"):
                st.json(data)
        else:
            st.warning("Se recibió un mensaje, pero no tiene formato JSON.")
            st.code(data)
