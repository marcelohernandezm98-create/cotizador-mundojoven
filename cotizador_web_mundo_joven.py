import streamlit as st
import urllib.parse
from datetime import datetime

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA (B2C - Modo Cliente)
# ==========================================
st.set_page_config(page_title="Arma tu Viaje - Mundo Joven", page_icon="✈️", layout="centered")

# Simulación de Logo (Centrado)
st.markdown("<h1 style='text-align: center; color: #e3001b;'>✈️ MUNDO JOVEN</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #0033a0;'>¡Arma tu viaje y descubre tu presupuesto ideal! 🌍</h3>", unsafe_allow_html=True)
st.write("---")

# ==========================================
# 1. DATOS DEL CLIENTE (CAPTURA DE LEADS)
# ==========================================
st.subheader("👤 1. Compártenos tus datos")
st.write("Para poder diseñar tu experiencia a la medida, necesitamos conocerte un poco más.")

col1, col2 = st.columns(2)

with col1:
    nombre = st.text_input("Nombre *")
    apellido = st.text_input("Apellido *")
    email = st.text_input("Correo Electrónico *")
    telefono = st.text_input("Teléfono / WhatsApp *")
    

with col2:
    adultos = st.number_input("Número de adultos", min_value=1, step=1, help="Campo opcional, por defecto es 1")
    ninos = st.number_input("Número de niños", min_value=0, step=1, help="Campo opcional")
    

presupuesto = st.selectbox(
    "¿Cuál es el presupuesto estimado que tienes en mente? (USD) *", 
    ["Selecciona un rango...", "Menos de $1,000 USD", "$1,000 - $2,000 USD", "$2,000 - $3,500 USD", "$3,500 - $5,000 USD", "Más de $5,000 USD"]
)

# Validación de campos obligatorios
datos_completos = bool(nombre.strip() and apellido.strip() and email.strip() and telefono.strip() and presupuesto != "Selecciona un rango...")

st.write("---")

# ==========================================
# BASE DE DATOS SIMULADA (Precios Base Temp Baja vs Alta en USD)
# ==========================================
destinos_por_region = {
    "🇲🇽 Nacionales": {
        "Cancún": {"baja": 510, "alta": 1030, "tours": {"Xcaret Plus": 140, "Catamarán a Isla Mujeres": 75, "Chichén Itzá Clásico": 60}},
        "Los Cabos": {"baja": 645, "alta": 1400, "tours": {"Paseo al Arco en Yate": 60, "Tour en Camello por el desierto": 90, "Avistamiento de Ballenas (Temp)": 75}},
        "Mérida": {"baja": 400, "alta": 735, "tours": {"Tour Uxmal y Kabah": 45, "Cenotes de Cuzamá": 40, "Paseo de Montejo en Calandria": 20}},
        "Otros (Especificar en comentarios)": {"baja": 0, "alta": 0, "tours": {}}
    },
    "🇪🇺 Europa": {
        "Francia": {"baja": 1470, "alta": 2470, "tours": {"Entrada a la Torre Eiffel (Cima)": 40, "Paseo en Barco por el Sena": 20, "Excursión a Versalles": 75}},
        "Italia": {"baja": 1550, "alta": 2450, "tours": {"Coliseo y Foro Romano sin filas": 55, "Paseo en Góndola": 40, "Tour al Vaticano": 65}},
        "España": {"baja": 1165, "alta": 2060, "tours": {"Tour Estadio Bernabéu": 30, "Entrada a la Sagrada Familia": 35, "Show de Flamenco con cena": 60}},
        "Portugal": {"baja": 1280, "alta": 2100, "tours": {"Tour a Sintra y Cascais": 70, "Paseo en barco por el río Tajo": 30}},
        "Suiza": {"baja": 1750, "alta": 2900, "tours": {"Excursión al Monte Titlis": 125, "Tour por los Alpes Suizos": 150}},
        "Grecia": {"baja": 1500, "alta": 2550, "tours": {"Visita Guiada a la Acrópolis": 45, "Crucero de un día por 3 islas": 110}},
        "Turquía": {"baja": 1400, "alta": 2150, "tours": {"Paseo en Globo en Capadocia": 225, "Tour por Santa Sofía y Mezquita Azul": 50}},
        "Otros (Especificar en comentarios)": {"baja": 0, "alta": 0, "tours": {}}
    },
    "🌍 África y Medio Oriente": {
        "Marruecos": {"baja": 1400, "alta": 2150, "tours": {"Noche en el Desierto con Camellos": 100, "Tour por la Medina y Zocos": 30}},
        "Sudáfrica": {"baja": 1950, "alta": 2950, "tours": {"Safari fotográfico de 1 día": 175, "Tour Península y Cabo de Buena Esperanza": 90}},
        "Egipto": {"baja": 1550, "alta": 2400, "tours": {"Pirámides de Giza y Esfinge": 60, "Crucero por el Nilo (Básico)": 200}},
        "Jordania": {"baja": 1730, "alta": 2600, "tours": {"Entrada y Tour por Petra": 125, "Excursión al Mar Muerto": 75}},
        "Otros (Especificar en comentarios)": {"baja": 0, "alta": 0, "tours": {}}
    },
    "🌏 Asia": {
        "Japón": {"baja": 2000, "alta": 3200, "tours": {"Pase JR Pass (1 semana)": 300, "Tour al Monte Fuji": 110, "Ceremonia del Té Tradicional": 40}},
        "Corea del Sur": {"baja": 2050, "alta": 3100, "tours": {"Excursión a la Zona Desmilitarizada (DMZ)": 75, "Alquiler de Hanbok (Traje típico)": 20}},
        "China": {"baja": 1700, "alta": 2700, "tours": {"Excursión a la Gran Muralla": 65, "Crucero por el río Huangpu": 30}},
        "Arabia Saudita": {"baja": 2000, "alta": 3100, "tours": {"Safari en el desierto y cena": 100, "Tour histórico por Diriyah": 75}},
        "Otros (Especificar en comentarios)": {"baja": 0, "alta": 0, "tours": {}}
    },
    "🌎 Sudamérica": {
        "Argentina": {"baja": 1030, "alta": 1650, "tours": {"Show de Tango con Cena": 75, "Excursión al Glaciar Perito Moreno": 150}},
        "Brasil": {"baja": 1100, "alta": 1700, "tours": {"Cristo Redentor y Pan de Azúcar": 90, "Tour a Angra dos Reis": 60}},
        "Colombia": {"baja": 750, "alta": 1200, "tours": {"Excursión a Guatapé y Piedra del Peñol": 40, "Catedral de Sal de Zipaquirá": 35}},
        "Perú": {"baja": 800, "alta": 1350, "tours": {"Tour Machu Picchu (Tren Clásico)": 275, "Montaña de los 7 Colores": 60}},
        "Otros (Especificar en comentarios)": {"baja": 0, "alta": 0, "tours": {}}
    },
    "🌎 Norteamérica y Centroamérica": {
        "Canadá": {"baja": 900, "alta": 1540, "tours": {"Excursión a Cataratas del Niágara": 100, "Puente Colgante de Capilano": 45}},
        "EUA": {"baja": 850, "alta": 1540, "tours": {"CityPass Nueva York": 140, "Tour Estudios Universal Hollywood": 125}},
        "Costa Rica": {"baja": 750, "alta": 1290, "tours": {"Tour Volcán Arenal y Aguas Termales": 125, "Tirolesa en Bosque Nuboso": 75}},
        "Otros (Especificar en comentarios)": {"baja": 0, "alta": 0, "tours": {}}
    }
}

# ==========================================
# 2. INTERFAZ DEL VIAJE
# ==========================================
st.subheader("✈️ 2. ¿A dónde quieres viajar?")
region_seleccionada = st.selectbox("Selecciona tu continente/región:", list(destinos_por_region.keys()))

# Al seleccionar la región, el segundo menú se actualiza solo con los países de esa región
destino_seleccionado = st.selectbox(f"Selecciona tu destino en {region_seleccionada}:", list(destinos_por_region[region_seleccionada].keys()))

st.subheader("📅 3. ¿Cuándo planeas viajar?")
fechas_input = st.date_input("Selecciona tus fechas estimadas (Ida y Regreso)", value=[], format="DD/MM/YYYY")

st.subheader("🗺️ 4. Diseña tu experiencia")
st.info("💡 **Instrucción:** Selecciona hasta 3 tours en orden de importancia. El primero que elijas será tu prioridad máxima para que nuestros asesores aseguren esa experiencia.")

tours_disponibles = destinos_por_region[region_seleccionada][destino_seleccionado]["tours"]
tours_seleccionados = st.multiselect(
    "Top 3 de Actividades/Tours que no te quieres perder:", 
    list(tours_disponibles.keys()),
    max_selections=3
)

st.subheader("✍️ 5. ¿Algo más que debamos saber?")
comentarios_extra = st.text_area(
    "Si buscas un tour diferente que no está en la lista, si viajas por un motivo especial (ej. luna de miel, graduación) escríbelo aquí:", 
    placeholder="Ej. Quiero hacer un tour gastronómico en París..."
)

st.write("---")

# ==========================================
# CÁLCULO DEL PRESUPUESTO Y ESTACIONALIDAD
# ==========================================
if len(fechas_input) == 2: # Nos aseguramos de que seleccionen ida y vuelta
    mes_salida = fechas_input[0].month
    
    # Temporada alta: Junio, Julio, Agosto, Diciembre
    meses_temporada_alta = [6, 7, 8, 12] 
    
    precios = destinos_por_region[region_seleccionada][destino_seleccionado]

    if mes_salida in meses_temporada_alta:
        costo_base = precios["alta"]
        etiqueta_temporada = "☀️ Tarifa Estimada (Temporada Alta)"
        color_alerta = "error"
    else:
        costo_base = precios["baja"]
        etiqueta_temporada = "🍃 Tarifa Estimada (Temporada Baja)"
        color_alerta = "success"
        
    costo_total = costo_base
    
    resumen_servicios = f"- ✈️🏨 Paquete Base (Vuelo redondo + Hospedaje): ${costo_base:,.2f} USD\n"
        
    if tours_seleccionados:
        resumen_servicios += "- 🗺️ Top Tours seleccionados (En orden de prioridad):\n"
        for i, tour in enumerate(tours_seleccionados, 1):
            costo_t = precios["tours"][tour]
            costo_total += costo_t
            resumen_servicios += f"   {i}. {tour}: ${costo_t:,.2f} USD\n"

    # ==========================================
    # MOSTRAR RESULTADOS
    # ==========================================
    st.header("Tu Presupuesto Estimado 💸")
    
    if color_alerta == "error":
        st.error(f"¡Atención! Viajas en verano o diciembre. Mostrando {etiqueta_temporada}")
    else:
        st.success(f"¡Genial! Tienes flexibilidad de fechas. Mostrando {etiqueta_temporada}")
        
    if destino_seleccionado == "Otros (Especificar en comentarios)":
        st.info("📌 Como elegiste un destino no listado, uno de nuestros expertos diseñará tu presupuesto a la medida. ¡Envíanos tus datos en el botón de abajo!")
    else:
        st.metric(label="Inversión total aproximada (USD)", value=f"${costo_total:,.2f}")
    
    with st.expander("Ver desglose de tu viaje"):
        st.text(resumen_servicios)
        st.caption("* Estos precios son estimaciones 'Desde', volando de CDMX en USD, sujetos a disponibilidad al reservar.")
        st.caption("🎒 **Nota de servicio:** El vuelo considerado incluye 25 kg de equipaje documentado y 10 kg en mano. El hospedaje contemplado es en hoteles categoría 3 estrellas.")

    # ==========================================
    # GENERACIÓN DE ENLACE A WHATSAPP
    # ==========================================
    st.write("---")
    st.subheader("¡Hazlo realidad! 🚀")
    
    if not datos_completos:
        st.warning("⚠️ Por favor, completa tus datos personales en la sección superior (Nombre, Apellido, Email, Teléfono y Presupuesto) para poder enviar tu cotización a nuestros asesores.")
    else:
        st.write(f"¡Todo listo, {nombre}! Da clic en el botón para enviar tu itinerario a WhatsApp. Un asesor experto de la **Sucursal Villahermosa** te contactará con tu tarifa final.")
        
        # Número de teléfono de Villahermosa
        numero_whatsapp = "529931234567" 
        
        comentarios_texto = f"\n\n*Comentarios extra:* {comentarios_extra}" if comentarios_extra.strip() else ""
        
        # El mensaje ahora incluye todos los datos del cliente
        mensaje = f"¡Hola Mundo Joven Villahermosa! 👋\n\nArmé mi viaje en la web y me gustaría cotizarlo formalmente.\n\n*👤 MIS DATOS*\nNombre: {nombre} {apellido}\nEmail: {email}\nTeléfono: {telefono}\nPasajeros: {adultos} Adulto(s), {ninos} Niño(s)\nPresupuesto estimado: {presupuesto}\n\n*✈️ MI VIAJE*\nDestino: {destino_seleccionado} ({region_seleccionada})\nTemporada: {etiqueta_temporada}\nServicios que busco:\n{resumen_servicios}\n*Presupuesto Estimado Web:* ${costo_total:,.2f} USD{comentarios_texto}\n\n*Nota:* Cotización basada en vuelos con 25kg + 10kg y hospedaje 3 estrellas.\n\n¿Me ayudan a cerrarlo?"
        
        mensaje_codificado = urllib.parse.quote(mensaje)
        link_whatsapp = f"https://wa.me/{522281310507}?text={mensaje_codificado}"
        
        st.markdown(f"""
            <a href="{link_whatsapp}" target="_blank">
                <button style="background-color: #25D366; color: white; border: none; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 8px; width: 100%; font-weight: bold; box-shadow: 0px 4px 6px rgba(0,0,0,0.1);">
                    📲 Enviar Itinerario por WhatsApp
                </button>
            </a>
        """, unsafe_allow_html=True)

else:
    st.info("👆 Por favor, selecciona las fechas exactas (Ida y Regreso) en el calendario para calcular tu presupuesto.")