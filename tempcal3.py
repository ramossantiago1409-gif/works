import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Thermodynamic Analyzer v3.0",
    page_icon="🌡️",
    layout="centered" # Se adapta perfectamente vertical en celulares
)

# Estilo personalizado para emular el Dark Mode moderno
st.markdown("""
    <style>
    .main { background-color: #1e1e24; }
    h1 { color: #ffffff; font-family: 'Segoe UI', sans-serif; }
    .stText { color: #b0b0bc; }
    </style>
    """, unsafe_allow_html=True)

st.title("ANÁLISIS TÉRMICO")
st.caption("Ley de Enfriamiento de Newton — Versión Móvil")

# --- PANEL DE ENTRADAS DE DATOS ---
st.subheader("Parámetros de Entrada")
st.info("Escribe los valores. Deja vacío (o borra el cero) en el parámetro que deseas calcular.")

# Campos de entrada optimizados para pantallas táctiles
t0_in = st.text_input("Temperatura Inicial (T₀) [°C]", value="90.0")
tm_in = st.text_input("Temperatura Ambiente (Tm) [°C]", value="20.0")
k_in = st.text_input("Constante de Enfriamiento (k) [1/s]", value="0.03")
t_in = st.text_input("Tiempo Transcurrido (t) [seg]", value="30.0")
tf_in = st.text_input("Temperatura Final T(t) [°C]", value="")

# --- LÓGICA DE CÁLCULO ---
if st.button("CALCULAR Y GRAFICAR", type="primary", use_container_width=True):
    try:
        # Convertir entradas a float o None si están vacías
        t0 = float(t0_in.strip()) if t0_in.strip() else None
        tm = float(tm_in.strip()) if tm_in.strip() else None
        k = float(k_in.strip()) if k_in.strip() else None
        t = float(t_in.strip()) if t_in.strip() else None
        tf = float(tf_in.strip()) if tf_in.strip() else None

        valores_lista = [t0, tm, k, t, tf]
        nulos = valores_lista.count(None)

        if nulos > 1:
            st.error("Error: Debes rellenar al menos 4 campos para poder calcular el faltante.")
        else:
            # CASO 1: Despejes si falta uno
            if nulos == 1:
                if tf is None:
                    tf = tm + (t0 - tm) * math.exp(-k * t)
                    st.success(f"Temperatura Final Calculada: **{tf:.2f} °C**")
                elif t is None:
                    val_log = (tf - tm) / (t0 - tm)
                    if val_log <= 0: raise ValueError("Límite físico imposible.")
                    t = -math.log(val_log) / k
                    st.success(f"Tiempo Calculado: **{t:.2f} segundos**")
                elif t0 is None:
                    t0 = tm + (tf - tm) / math.exp(-k * t)
                    st.success(f"Temperatura Inicial Calculada: **{t0:.2f} °C**")
                elif tm is None:
                    exp_term = math.exp(-k * t)
                    tm = (tf - t0 * exp_term) / (1 - exp_term)
                    st.success(f"Temperatura Ambiente Calculada: **{tm:.2f} °C**")
                elif k is None:
                    val_log = (tf - tm) / (t0 - tm)
                    if val_log <= 0: raise ValueError("Límite físico imposible.")
                    k = -math.log(val_log) / t
                    st.success(f"Constante k Calculada: **{k:.4f} 1/s**")
            
            # CASO 2: Todos llenos, recalcula Tf
            else:
                tf = tm + (t0 - tm) * math.exp(-k * t)
                st.success(f"Recalculado T(t): **{tf:.2f} °C**")

            # --- GENERACIÓN DE LA GRÁFICA RESPONSIVE ---
            fig, ax = plt.subplots(figsize=(6, 4))
            fig.patch.set_facecolor('#25252d')
            ax.set_facecolor('#1e1e24')
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.title.set_color('white')

            limite_grafica = max(t * 1.5, 10)
            t_axis = np.linspace(0, limite_grafica, 200)
            temp_axis = tm + (t0 - tm) * np.exp(-k * t_axis)

            ax.plot(t_axis, temp_axis, color="#00e676", linewidth=2.5, label="Enfriamiento")
            ax.axhline(tm, color="#ff1744", linestyle="--", label=f"Ambiente ({tm}°C)")
            ax.plot(t, tm + (t0 - tm) * math.exp(-k * t), 'o', color="#29b6f6", markersize=8)

            ax.set_title("Grafica de la Temperatura", weight='bold')
            ax.set_xlabel("Tiempo (segundos)")
            ax.set_ylabel("Temperatura (°C)")
            ax.grid(True, color="#33333d")
            
            legend = ax.legend(facecolor='#25252d', edgecolor='none')
            for text in legend.get_texts():
                text.set_color('white')

            fig.tight_layout()
            
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Error matemático: {str(e)}")