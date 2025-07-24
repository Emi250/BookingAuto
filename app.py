import streamlit as st
import requests
import urllib.parse

# Configuración de la página
st.set_page_config(page_title="Generador de mensaje de reservas", layout="centered")
st.title("📩 Generador de mensaje para reservas")
st.write("Subí una captura de Booking como referencia y completá los datos manualmente.")

# Subida de imagen (opcional)
uploaded_file = st.file_uploader("📷 Subí la captura de pantalla de la reserva (opcional)", type=["png", "jpg", "jpeg"])
if uploaded_file:
    st.image(uploaded_file, caption="Imagen subida", use_container_width=True)

# Entrada manual de datos
st.subheader("📝 Datos de la reserva")
nombre = st.text_input("Nombre del huésped")
usd = st.number_input("Precio total en USD", value=0.0, format="%.2f")
telefono = st.text_input("Número de WhatsApp del huésped (sin espacios, ej: 541155...)")

# Obtener cotización actual USD → ARS desde exchangerate.host
def get_usd_ars():
    access_key = "aceb542a130908b4fe0dd21db2e7c4ab"
    url = f"https://api.exchangerate.host/live?access_key={access_key}&source=USD&currencies=ARS"
    try:
        response = requests.get(url)
        data = response.json()
        return data["quotes"]["USDARS"]
    except:
        return 1400  # Valor por defecto si falla

cotizacion = get_usd_ars()
ars = round(usd * cotizacion)
ars_formateado = f"{ars:,.0f}".replace(",", ".")

# Mensaje generado
st.subheader("💬 Mensaje personalizado")

mensaje = f"""Hola {nombre}! ¿Cómo estás? Soy Emilio del alojamiento de Capilla del Monte, ante todo muchas gracias por la reserva. Te comento que la misma está asentada y el total es de ${ars_formateado}, que puede abonarse en efectivo o transferencia cuando lleguen. ¡Como les quede más cómodo!

Días antes de que lleguen me voy a comunicar a este Whatsapp para brindarles toda la info del check in, igualmente por cualquier consulta quedo siempre a disposición. ¡Gracias!
"""

st.text_area("Mensaje generado", value=mensaje, height=200)
st.markdown(f"📈 Cotización usada: **1 USD = {cotizacion:.2f} ARS**")

# Link a WhatsApp
if telefono and mensaje:
    mensaje_encoded = urllib.parse.quote(mensaje)
    link = f"https://wa.me/{telefono}?text={mensaje_encoded}"
    st.markdown(f"[📲 Abrir WhatsApp con mensaje]({link})")
