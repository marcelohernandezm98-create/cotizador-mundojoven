import streamlit as st
import urllib.parse
from datetime import datetime

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA (B2C - Modo Cliente)
# ==========================================
st.info("💡 ** Esta pagina es para fines informativos. Todos los costos y precios mostrados son estimaciones aproximadas sujetas a cambios sin previo aviso y no constituyen una oferta comercial definitiva.**")
st.set_page_config(page_title="Arma tu Viaje", page_icon="✈️", layout="centered")

# Simulación de Logo (Centrado)
st.markdown("<h3 style='text-align: center; color: #0033a0;'>¡Arma tu viaje y descubre tu presupuesto ideal! 🌍</h3>", unsafe_allow_html=True)

# Aviso de transparencia Multidestino al inicio
st.info("💡 **Tip para Multidestinos:** Si eliges varios países en tu viaje, nuestro sistema tomará el vuelo base más económico de tu selección y solo sumará un estimado de **$350 USD por cada país adicional** para cubrir tus traslados internos y hospedaje extra.")
st.write("---")

# ==========================================
# 1. DATOS DEL CLIENTE (CAPTURA DE LEADS)
# ==========================================
st.subheader("👤 1. Compártenos tus datos")
st.write("Para poder diseñar tu experiencia a la medida, necesitamos conocerte un poco más.")

col1, col2 = st.columns(2)

with col1:
    nombre = st.text_input("Nombre *")
    apellidos = st.text_input("Apellidos *")
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
datos_completos = bool(nombre.strip() and apellidos.strip() and email.strip() and telefono.strip() and presupuesto != "Selecciona un rango...")

st.write("---")

# ==========================================
# BASE DE DATOS SIMULADA (Precios Paquete Base USD)
# (Columna Izq = Alta, Columna Der = Baja)
# ==========================================
destinos_por_region = {
    "🇲🇽 Nacionales": {
        "Cancún": {"alta": 1030, "baja": 510, "tours": {"Xcaret Plus": 140, "Catamarán a Isla Mujeres": 75, "Chichén Itzá Clásico": 60}},
        "Los Cabos": {"alta": 1400, "baja": 645, "tours": {"Paseo al Arco en Yate": 60, "Tour en Camello por el desierto": 90, "Avistamiento de Ballenas (Temp)": 75}},
        "Mérida": {"alta": 735, "baja": 400, "tours": {"Tour Uxmal y Kabah": 45, "Cenotes de Cuzamá": 40, "Paseo de Montejo en Calandria": 20}},
        "Otros (Especificar en comentarios)": {"alta": 0, "baja": 0, "tours": {}}
    },
    "🇪🇺 Europa": {
        "Francia": {"alta": 2470, "baja": 1470, "tours": {"Entrada a la Torre Eiffel (Cima)": 40, "Paseo en Barco por el Sena": 20, "Excursión a Versalles": 75}},
        "Italia": {"alta": 2450, "baja": 1550, "tours": {"Coliseo y Foro Romano sin filas": 55, "Paseo en Góndola": 40, "Tour al Vaticano": 65}},
        "España": {"alta": 2060, "baja": 1165, "tours": {"Tour Estadio Bernabéu": 30, "Entrada a la Sagrada Familia": 35, "Show de Flamenco con cena": 60}},
        "Portugal": {"alta": 2100, "baja": 1280, "tours": {"Tour a Sintra y Cascais": 70, "Paseo en barco por el río Tajo": 30}},
        "Suiza": {"alta": 2900, "baja": 1750, "tours": {"Excursión al Monte Titlis": 125, "Tour por los Alpes Suizos": 150}},
        "Grecia": {"alta": 2550, "baja": 1500, "tours": {"Visita Guiada a la Acrópolis": 45, "Crucero de un día por 3 islas": 110}},
        "Turquía": {"alta": 2150, "baja": 1400, "tours": {"Paseo en Globo en Capadocia": 225, "Tour por Santa Sofía y Mezquita Azul": 50}},
        "Otros (Especificar en comentarios)": {"alta": 0, "baja": 0, "tours": {}}
    },
    "🌍 África y Medio Oriente": {
        "Marruecos": {"alta": 2150, "baja": 1400, "tours": {"Noche en el Desierto con Camellos": 100, "Tour por la Medina y Zocos": 30}},
        "Sudáfrica": {"alta": 2950, "baja": 1950, "tours": {"Safari fotográfico de 1 día": 175, "Tour Península y Cabo de Buena Esperanza": 90}},
        "Egipto": {"alta": 2400, "baja": 1550, "tours": {"Pirámides de Giza y Esfinge": 60, "Crucero por el Nilo (Básico)": 200}},
        "Jordania": {"alta": 2600, "baja": 1730, "tours": {"Entrada y Tour por Petra": 125, "Excursión al Mar Muerto": 75}},
        "Otros (Especificar en comentarios)": {"alta": 0, "baja": 0, "tours": {}}
    },
    "🌏 Asia": {
        "Japón": {"alta": 3200, "baja": 2000, "tours": {"Pase JR Pass (1 semana)": 300, "Tour al Monte Fuji": 110, "Ceremonia del Té Tradicional": 40}},
        "Corea del Sur": {"alta": 3100, "baja": 2050, "tours": {"Excursión a la Zona Desmilitarizada (DMZ)": 75, "Alquiler de Hanbok (Traje típico)": 20}},
        "China": {"alta": 2700, "baja": 1700, "tours": {"Excursión a la Gran Muralla": 65, "Crucero por el río Huangpu": 30}},
        "Arabia Saudita": {"alta": 3100, "baja": 2000, "tours": {"Safari en el desierto y cena": 100, "Tour histórico por Diriyah": 75}},
        "Otros (Especificar en comentarios)": {"alta": 0, "baja": 0, "tours": {}}
    },
    "🌎 Sudamérica": {
        "Argentina": {"alta": 1650, "baja": 1030, "tours": {"Show de Tango con Cena": 75, "Excursión al Glaciar Perito Moreno": 150}},
        "Brasil": {"alta": 1700, "baja": 1100, "tours": {"Cristo Redentor y Pan de Azúcar": 90, "Tour a Angra dos Reis": 60}},
        "Colombia": {"alta": 1200, "baja": 750, "tours": {"Excursión a Guatapé y Piedra del Peñol": 40, "Catedral de Sal de Zipaquirá": 35}},
        "Perú": {"alta": 1350, "baja": 800, "tours": {"Tour Machu Picchu (Tren Clásico)": 275, "Montaña de los 7 Colores": 60}},
        "Otros (Especificar en comentarios)": {"alta": 0, "baja": 0, "tours": {}}
    },
    "🌎 Norteamérica y Centroamérica": {
        "Canadá": {"alta": 1540, "baja": 900, "tours": {"Excursión a Cataratas del Niágara": 100, "Puente Colgante de Capilano": 45}},
        "EUA": {"alta": 1540, "baja": 850, "tours": {"CityPass Nueva York": 140, "Tour Estudios Universal Hollywood": 125}},
        "Costa Rica": {"alta": 1290, "baja": 750, "tours": {"Tour Volcán Arenal y Aguas Termales": 125, "Tirolesa en Bosque Nuboso": 75}},
        "Otros (Especificar en comentarios)": {"alta": 0, "baja": 0, "tours": {}}
    }
}

# ==========================================
# 2. INTERFAZ DEL VIAJE
# ==========================================
st.subheader("✈️ 2. ¿A dónde quieres viajar?")
region_seleccionada = st.selectbox("Selecciona tu continente/región:", list(destinos_por_region.keys()))

destinos_seleccionados = st.multiselect(
    f"Selecciona hasta 5 destinos en {region_seleccionada}:", 
    list(destinos_por_region[region_seleccionada].keys()),
    max_selections=5,
    help="Puedes elegir varios países para armar un increíble circuito."
)

st.subheader("📅 3. ¿Cuándo planeas viajar?")
fechas_input = st.date_input("Selecciona tus fechas estimadas (Ida y Regreso)", value=[], format="DD/MM/YYYY")

st.subheader("🗺️ 4. Diseña tu experiencia")
st.info("💡 **Instrucción:** Selecciona hasta 3 tours en orden de importancia. El primero que elijas será tu prioridad máxima para que nuestros asesores aseguren esa experiencia.")

# Agrupamos los tours de todos los destinos seleccionados
tours_disponibles = {}
if destinos_seleccionados:
    for dest in destinos_seleccionados:
        tours_destino = destinos_por_region[region_seleccionada][dest]["tours"]
        for nombre_tour, precio_tour in tours_destino.items():
            tours_disponibles[f"{dest} - {nombre_tour}"] = precio_tour

tours_seleccionados = st.multiselect(
    "Top 3 de Actividades/Tours que no te quieres perder:", 
    list(tours_disponibles.keys()),
    max_selections=3
)

st.subheader("✍️ 5. ¿Algo más que debamos saber?")
comentarios_extra = st.text_area(
    "Si buscas un tour diferente que no está en la lista o tienes alguna petición especial, escríbelo aquí:", 
    placeholder="Ej. Quiero hacer un tour gastronómico en París..."
)

st.write("---")

# ==========================================
# CÁLCULO DEL PRESUPUESTO Y ESTACIONALIDAD
# ==========================================
if len(fechas_input) == 2 and destinos_seleccionados: 
    mes_salida = fechas_input[0].month
    
    # Temporada alta: Junio, Julio, Agosto, Diciembre
    meses_temporada_alta = [6, 7, 8, 12] 
    es_temporada_alta = mes_salida in meses_temporada_alta
    
    if es_temporada_alta:
        etiqueta_temporada = "☀️ Tarifa Estimada (Temporada Alta)"
        color_alerta = "error"
    else:
        etiqueta_temporada = "🍃 Tarifa Estimada (Temporada Baja)"
        color_alerta = "success"
        
    # --- NUEVA LÓGICA DE CÁLCULO MULTIDESTINO ($350) ---
    precios_base_seleccionados = []
    
    for dest in destinos_seleccionados:
        precios = destinos_por_region[region_seleccionada][dest]
        precio_actual = precios["alta"] if es_temporada_alta else precios["baja"]
        if precio_actual > 0: # Evitar procesar "Otros" matemáticamente aquí
            precios_base_seleccionados.append(precio_actual)
            
    costo_base_total = 0
    desglose_multidestino_texto = ""
    
    if precios_base_seleccionados:
        # Tomamos el destino más barato como "Paquete Base" (Incluye vuelo transatlántico)
        costo_base_principal = min(precios_base_seleccionados)
        # Calculamos cuántos países adicionales hay
        paises_extra = len(precios_base_seleccionados) - 1
        # Sumamos $350 USD por cada país extra
        suplemento = paises_extra * 350
        
        costo_base_total = costo_base_principal + suplemento
        
        if paises_extra > 0:
            desglose_multidestino_texto = f" (Incluye vuelo principal + suplemento por {paises_extra} país(es) adicional(es))"
            
    costo_total = costo_base_total
    
    # Preparamos el texto del resumen
    destinos_str = ", ".join(destinos_seleccionados)
    resumen_servicios = f"- ✈️🏨 Paquete Base ({destinos_str}): ${costo_base_total:,.2f} USD{desglose_multidestino_texto}\n"
        
    if tours_seleccionados:
        resumen_servicios += "- 🗺️ Top Tours seleccionados (En orden de prioridad):\n"
        for i, tour_key in enumerate(tours_seleccionados, 1):
            costo_t = tours_disponibles[tour_key]
            costo_total += costo_t
            resumen_servicios += f"   {i}. {tour_key}: ${costo_t:,.2f} USD\n"

    # ==========================================
    # MOSTRAR RESULTADOS
    # ==========================================
    st.header("Tu Presupuesto Estimado 💸")
    
    if color_alerta == "error":
        st.error(f"¡Atención! Viajas en verano o diciembre. Mostrando {etiqueta_temporada}")
    else:
        st.success(f"¡Genial! Tienes flexibilidad de fechas. Mostrando {etiqueta_temporada}")
        
    if "Otros (Especificar en comentarios)" in destinos_seleccionados:
        st.info("📌 Como incluiste un destino no listado, uno de nuestros expertos diseñará tu presupuesto a la medida. ¡Envíanos tus datos en el botón de abajo!")
    
    st.metric(label="Inversión total aproximada (USD)", value=f"${costo_total:,.2f}")
    
    with st.expander("Ver desglose de tu viaje y términos"):
        st.text(resumen_servicios)
        st.caption("🎒 **Nota de servicio:** El vuelo considerado incluye 25 kg de equipaje documentado y 10 kg en mano. El hospedaje contemplado es en hoteles categoría 3 estrellas.")
        st.caption("🗺️ **Lógica Multidestino:** Para brindarte un estimado realista, los viajes a más de un país calculan el vuelo internacional al destino más económico de tu selección y suman un estimado de $350 USD por cada país adicional por conceptos de movilidad interna y/u hospedaje.")

    # ==========================================
    # GENERACIÓN DE ENLACE A WHATSAPP
    # ==========================================
    st.write("---")
    st.subheader("¡Hazlo realidad! 🚀")
    
    if not datos_completos:
        st.warning("⚠️ Por favor, completa tus datos personales en la sección superior (Nombre, Apellido, Email, Teléfono y Presupuesto) para poder enviar tu cotización a nuestros asesores.")
    else:
        st.write(f"¡Todo listo, {nombre}! Da clic en el botón para enviar tu itinerario a WhatsApp. Un asesor experto de la **Sucursal Villahermosa** te contactará con tu tarifa final.")
        
        numero_whatsapp = "529931234567" # REEMPLAZAR CON EL DE VILLAHERMOSA
        
        comentarios_texto = f"\n\n*Comentarios extra:* {comentarios_extra}" if comentarios_extra.strip() else ""
        
        mensaje = f"¡Hola Mundo Joven Villahermosa! 👋\n\nArmé mi viaje en la web y me gustaría cotizarlo formalmente.\n\n*👤 MIS DATOS*\nNombre: {nombre} {apellidos}\nEmail: {email}\nTeléfono: {telefono}\nPasajeros: {adultos} Adulto(s), {ninos} Niño(s)\nPresupuesto estimado: {presupuesto}\n\n*✈️ MI VIAJE*\nDestinos: {destinos_str} ({region_seleccionada})\nTemporada: {etiqueta_temporada}\nServicios que busco:\n{resumen_servicios}\n*Presupuesto Estimado Web:* ${costo_total:,.2f} USD{comentarios_texto}\n\n*Nota:* Cotización basada en vuelos con equipaje (25kg+10kg), hospedaje 3 estrellas y lógica de suplemento multidestino ($350 USD por país extra).\n\n¿Me ayudan a cerrarlo?"
        
        mensaje_codificado = urllib.parse.quote(mensaje)
        link_whatsapp = f"https://wa.me/{522281310507}?text={mensaje_codificado}"
        
        st.markdown(f"""
            <a href="{link_whatsapp}" target="_blank">
                <button style="background-color: #25D366; color: white; border: none; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 8px; width: 100%; font-weight: bold; box-shadow: 0px 4px 6px rgba(0,0,0,0.1);">
                    📲 Enviar Itinerario por WhatsApp
                </button>
            </a>
        """, unsafe_allow_html=True)

elif len(fechas_input) < 2:
    st.info("👆 Por favor, selecciona las fechas exactas (Ida y Regreso) en el calendario para calcular tu presupuesto.")
else:
    st.info("👆 Por favor, selecciona al menos un destino de la lista para calcular tu presupuesto.")