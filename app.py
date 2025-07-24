import streamlit as st
import pytesseract
from PIL import Image
import requests
import urllib.parse
import re

# Configuración de la página
st.set_page_config(page_title="Generador de mensaje de reservas", layout="centered")
st.title("📩 Generador de mensaje para reservas")
st.write("Subí una captura de Booking o completá los datos manualmente.")

# Carga de imagen
uploaded_file = st.file_uploader("📷 Subí la captura de pantalla de la reserva", type=["png", "jpg", "jpeg"])

# Variables iniciales
nombre = ""
fecha_llegada = ""
fecha_salida = ""
usd = 0.0
telefono = ""

# Procesar imagen si fue subida
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Captura subida", use_column_width=True)
    texto = pytesseract.image_to_string(image)

    # Extraer datos del texto con expresiones regulares
    nombre_match = re.search(r'Nombre del cliente:\s*(.*)', texto)
    fecha_in_match = re.search(r'Check-in\s*\n([^\n]+)', texto)
    fecha_out_match = re.search(r'Check-out\s*\n([^\n]+)', texto)
    usd_match = re.search(r'US\$([0-9]+[,\.]?[0-9]*)', texto)
    tel_match = re.search(r'\+54\s*[\d\s]+', texto)

    if nombre_match: nombre = nombre_match.group(1).strip()
    if fecha_in_match: fecha_llegada = fecha_in_match.group(1).strip()
    if fecha_out_match: fecha_salida = fecha_out_match.group(1).strip()
    if usd_match:
        usd = float(usd_match.group(1).replace(",", "."))
    if tel_match: telefono = tel_match.group(0).replace(" ", "")

# Entrada manual de datos
st.subheader("📝 Datos de la reserva")
nombre = st.text_input("Nombre del huésped", value=nombre)
fecha_llegada = st.text_input("Fecha de llegada", value=fecha_llegada)
fecha_salida = st.text_input("Fecha de salida", value=fecha_salida)
usd = st.number_input("Precio total en USD", value=usd, format="%.2f")
telefono = st.text_input("Número de WhatsApp del huésped (sin espacios, ej: 541155...)",
                         value=telefono.replace("+", "").replace(" ", ""))

# Obtener cotización actual USD → ARS desde exchangerate.host
def get_usd_ars():
    access_key = "aceb542a130908b4fe0dd21db2e7c4ab"
    url = f"https://api.exchangerate.host/live?access_key={access_key}&source=USD&currencies=ARS"
    try:
        response = requests.get(url)
        data = response.json()
        return data["quotes"]["USDARS"]
    except:
        return 1400  # Valor de respaldo

cotizacion = get_usd_ars()
ars = round(usd * cotizacion)

# Mensaje generado
st.subheader("💬 Mensaje personalizado")

mensaje = f"""Hola {nombre}! ¿Cómo estás? Soy Emilio del alojamiento de Capilla del Monte, ante todo muchas gracias por la reserva. Te comento que la misma está asentada y el total es de ${ars}, que puede abonarse en efectivo o transferencia cuando lleguen. ¡Como les quede más cómodo!

Días antes de que lleguen me voy a comunicar a este Whatsapp para brindarles toda la info del check in, igualmente por cualquier consulta quedo siempre a disposición. ¡Gracias!
"""

st.text_area("Mensaje generado", value=mensaje, height=200)
st.markdown(f"📈 Cotización usada: **1 USD = {cotizacion:.2f} ARS**")

# Link a WhatsApp
if telefono and mensaje:
    mensaje_encoded = urllib.parse.quote(mensaje)
    link = f"https://wa.me/{telefono}?text={mensaje_encoded}"
    st.markdown(f"[📲 Abrir WhatsApp con mensaje]({link})")
