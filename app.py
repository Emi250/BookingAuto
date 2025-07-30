import streamlit as st
import requests
import urllib.parse
import re

# Configuración
st.set_page_config(page_title="Generador de mensaje de reservas", layout="centered")
st.title("📩 Generador de mensaje para reservas")
st.write("Subí una captura de Booking o completá los datos manualmente.")

# Función de OCR.Space
def ocr_space_text(file, api_key='K88594043488957'):
    url = 'https://api.ocr.space/parse/image'
    payload = {
        'apikey': api_key,
        'language': 'spa',
    }
    with requests.post(url, files={'filename': file}, data=payload) as r:
        result = r.json()
        if result.get("IsErroredOnProcessing"):
            return ""
        return result["ParsedResults"][0]["ParsedText"]

# Subir imagen
uploaded_file = st.file_uploader("📷 Subí la captura de la reserva", type=["png", "jpg", "jpeg"])

nombre = ""
usd = 0.0
telefono_crudo = ""

if uploaded_file:
    st.image(uploaded_file, caption="Imagen subida", use_container_width=True)
    texto = ocr_space_text(uploaded_file)

    # Buscar nombre y monto
    nombre_match = re.search(r'Nombre del cliente:\s*(.*)', texto)
    usd_match = re.search(r'US\$([0-9]+[,\.]?[0-9]*)', texto)

    if nombre_match:
        nombre = nombre_match.group(1).strip()
    if usd_match:
        usd = float(usd_match.group(1).replace(",", "."))

# Formulario manual (editable)
st.subheader("📝 Datos de la reserva")
nombre = st.text_input("Nombre del huésped", value=nombre)
usd = st.number_input("Precio total en USD", value=usd, format="%.2f")
telefono_crudo = st.text_input("Número de WhatsApp del huésped (ej: +54 11 5555 5555)")

# Limpiar teléfono
telefono = telefono_crudo.replace(" ", "").replace("+", "")

# Cotización desde exchangerate.host
# Cotización desde Monedapi.ar (Dólar Blue)
def get_usd_ars():
    url = "https://monedapi.ar/api/usd/bna"
    try:
        response = requests.get(url)
        data = response.json()
        return data["venta"]
    except:
        return 1300  # fallback en caso de error

cotizacion = get_usd_ars()
ars = round(usd * cotizacion)
ars_formateado = f"{ars:,.0f}".replace(",", ".")

# Mensaje
st.subheader("💬 Mensaje personalizado")
mensaje = f"""Hola {nombre}! ¿Cómo estás? Soy Emilio del alojamiento de Capilla del Monte, ante todo muchas gracias por la reserva. Te comento que la misma está asentada y el total es de ${ars_formateado}, que puede abonarse en efectivo o transferencia cuando lleguen. ¡Como les quede más cómodo!

Días antes de que lleguen me voy a comunicar a este Whatsapp para brindarles toda la info del check in, igualmente por cualquier consulta quedo siempre a disposición. ¡Gracias!
"""

st.text_area("Mensaje generado", value=mensaje, height=200)

# Botón para copiar (funciona solo localmente)
st.button("📋 Copiar mensaje", on_click=lambda: st.session_state.update({"_clipboard": mensaje}))

st.markdown(f"📈 Cotización usada: **1 USD = {cotizacion:.2f} ARS**")

# Enlace WhatsApp
if telefono and mensaje:
    mensaje_encoded = urllib.parse.quote(mensaje)
    link = f"https://wa.me/{telefono}?text={mensaje_encoded}"
    st.markdown(f"[📲 Abrir WhatsApp con mensaje]({link})")
