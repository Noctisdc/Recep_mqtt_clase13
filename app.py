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

/* Fondo general y fuente */
.stApp {
    background-color: #0f172a;
    background-image: radial-gradient(#1e3a5f 1.5px, transparent 1.5px);
    background-size: 26px 26px;
    font-family: 'Space Grotesk', sans-serif;
    color: #f8fafc;
}

/* Encabezados */
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

/* Contenedores y Cajas de Datos */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(30, 41, 59, 0.85); /* Fondo oscuro translúcido */
    border: 1px solid #38bdf8;
    border-radius: 12px;
    padding: 1.5rem;
}

/* Métricas / Resultados */
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

/* Sobreescritura de elementos nativos de Streamlit para legibilidad */
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
    box-shadow: 0 0
