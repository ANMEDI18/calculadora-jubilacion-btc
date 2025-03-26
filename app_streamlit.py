import streamlit as st
import requests
from datetime import datetime
import pandas as pd

# --- FUNCIONES ---
def calcular_pbtc(RI, CP, NH, RF):
    return ((RI * CP) * (2 ** NH)) / RF

def obtener_precio_btc():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        response = requests.get(url, timeout=10)
        data = response.json()
        return data['bitcoin']['usd']
    except:
        return None

def calcular_jubilacion(ahorro_semanal, meta_usd, fecha_nacimiento, años_max=30):
    precio_btc = obtener_precio_btc()
    if not precio_btc:
        return None, "Error al obtener el precio de BTC"

    nacimiento = datetime.strptime(fecha_nacimiento, "%d/%m/%Y")
    edad_actual = datetime.now().year - nacimiento.year
    semanas_por_año = 52
    interes_anual = 0.06
    RI, CP, RF = 50, 20000, 6.25

    resumen = []
    resumen_halvings = []
    btc_total = 0
    ahorro_total = 0
    meta_lograda = False

    for año in range(1, años_max + 1):
        ahorro_anual = ahorro_semanal * semanas_por_año * (1.1 ** (año - 1))
        ahorro_total += ahorro_anual
        btc_comprado = ahorro_anual / precio_btc
        btc_total = (btc_total + btc_comprado) * (1 + interes_anual)

        NH = año // 4
        pbtc = calcular_pbtc(RI, CP, NH, RF)
        valor_proyectado = btc_total * pbtc
        resumen.append({
            "Año": año,
            "Edad": edad_actual + año,
            "BTC Acumulado": btc_total,
            "Valor Proyectado": valor_proyectado
        })

        if año % 4 == 0:
            resumen_halvings.append({
                "Halving Año": 2024 + ((año // 4) * 4),
                "PBTC estimado": pbtc,
                "Valor estimado inversión": valor_proyectado
            })

        if not meta_lograda and valor_proyectado >= meta_usd:
            meta_lograda = True
            año_meta = año
            edad_meta = edad_actual + año

    df = pd.DataFrame(resumen)
    df_halvings = pd.DataFrame(resumen_halvings)
    mensaje_final = ""
    if meta_lograda:
        mensaje_final = f"🎯 ¡Meta de ${meta_usd:,.0f} alcanzada a los {edad_meta} años (en {año_meta} años)!"
    else:
        mensaje_final = f"❌ No se alcanzó la meta de ${meta_usd:,.0f} en {años_max} años."

    return df, mensaje_final, df_halvings

# --- INTERFAZ ---
st.set_page_config(page_title="Calculadora BTC Jubilación", page_icon="🧮")
st.title("🔢 Calculadora de Jubilación con Bitcoin")
st.markdown("Calcula cuánto podrías tener si ahorras semanalmente en BTC aprovechando los halvings")

# --- CONVERSOR USD a BTC ---
with st.expander("💱 Conversor USD a BTC"):
    precio_actual = obtener_precio_btc()
    if precio_actual:
        usd_input = st.number_input("Monto en USD", min_value=0.0, value=25000.0)
        btc_resultado = usd_input / precio_actual
        st.write(f"🔄 Equivale a aproximadamente **{btc_resultado:.6f} BTC** al precio actual de {precio_actual:,.2f} USD/BTC")
    else:
        st.error("No se pudo obtener el precio actual del BTC")

# --- FORMULARIO DE CÁLCULO ---
with st.form("formulario"):
    ahorro_semanal = st.number_input("¿Cuánto vas a ahorrar por semana? (USD)", min_value=1.0, value=25.0)
    meta = st.number_input("¿Cuál es tu meta de jubilación? (USD)", min_value=1000.0, value=6500000.0)
    fecha_nacimiento = st.text_input("¿Cuál es tu fecha de nacimiento? (D/M/AAAA)", value="1/1/2000")
    años_max = st.slider("¿Cuántos años deseas proyectar?", 5, 40, 25)
    submitted = st.form_submit_button("Calcular")

if submitted:
    df, resultado, df_halvings = calcular_jubilacion(ahorro_semanal, meta, fecha_nacimiento, años_max)
    if df is not None:
        st.success(resultado)
        st.subheader("📊 Proyección Anual")
        st.line_chart(df.set_index("Año")["Valor Proyectado"], use_container_width=True)
        st.dataframe(df, use_container_width=True)

        st.subheader("📆 Equivalencia en cada Halving")
        st.dataframe(df_halvings, use_container_width=True)

        st.download_button("📥 Descargar proyección completa", data=df.to_csv(index=False), file_name="proyeccion_jubilacion.csv")
        st.download_button("📥 Descargar tabla de Halvings", data=df_halvings.to_csv(index=False), file_name="proyeccion_halvings.csv")
    else:
        st.error(resultado)

st.markdown("""
---
📖 *Mateo 6:21 — Porque donde esté tu tesoro, allí estará también tu corazón.*
""")
