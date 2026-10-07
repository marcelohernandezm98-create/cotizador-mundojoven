import streamlit as st
import io
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import pandas as pd
from google import genai
from google.genai import types

# ==========================================
# CONFIGURACIÓN DE IA (GOOGLE GEMINI)
# ==========================================
# ⚠️ NOTA: Extraemos la API Key de los secretos de Streamlit por seguridad.
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    API_KEY = None

def consultar_asistente_ia(peticion_usuario):
    """
    Se conecta a Google Gemini para sugerir servicios y precios basados en la petición del asesor.
    """
    if not API_KEY:
        st.error("⚠️ No se encontró la API Key. Por favor, configúrala en .streamlit/secrets.toml")
        return None
        
    try:
        cliente = genai.Client(api_key=API_KEY)
        
        instruccion_sistema = """
        Eres un asesor experto de viajes de la agencia 'Mundo Joven'. 
        Tu objetivo es cotizar servicios de viaje (vuelos, cursos de idiomas, seguros, alojamiento) de forma realista en USD.
        Utiliza tu herramienta de búsqueda en Google para encontrar precios actuales en el mercado.
        
        DEBES devolver tu respuesta ÚNICAMENTE como una lista de objetos JSON. No incluyas texto extra, ni saludos.
        El formato estricto debe ser:
        [
            {
                "concepto": "Nombre corto del servicio (ej. Vuelo Redondo)", 
                "descripcion": "Descripción detallada", 
                "precio": 500.00,
                "fuente": "URL exacta de donde obtuviste la información o precio"
            }
        ]
        """
        
        respuesta = cliente.models.generate_content(
            model='gemini-3.8-flash',
            contents=f"Busca en internet los precios actuales y arma una propuesta para: {peticion_usuario}",
            config=types.GenerateContentConfig(
                system_instruction=instruccion_sistema,
                response_mime_type="application/json",
                temperature=0.3,
                tools=[{"google_search": {}}] # 🟢 AQUÍ ESTÁ LA MAGIA: Conectamos Gemini a Internet
            )
        )
        
        # Convertimos el texto de respuesta (que viene en JSON) a una lista de diccionarios de Python
        sugerencias = json.loads(respuesta.text)
        return sugerencias
        
    except Exception as e:
        st.error(f"Error de conexión con la IA: {e}")
        return None

# ==========================================
# GENERACIÓN DE PDF (REPORTLAB)
# ==========================================
def generar_pdf_en_memoria(datos_cliente, servicios):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=18)
    elementos = []
    estilos = getSampleStyleSheet()
    
    estilo_titulo = ParagraphStyle('TituloMundoJoven', parent=estilos['Heading1'], fontSize=24, textColor=colors.HexColor("#0033a0"), spaceAfter=20, alignment=1)
    estilo_subtitulo = ParagraphStyle('Subtitulo', parent=estilos['Normal'], fontSize=12, textColor=colors.HexColor("#333333"), spaceAfter=20, alignment=1)
    
    elementos.append(Paragraph("✈️ <b>MUNDO JOVEN</b>", estilo_titulo))
    elementos.append(Paragraph("<b>¡La aventura de tu vida comienza aquí!</b>", estilo_subtitulo))
    elementos.append(Spacer(1, 12))
    
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    info_cliente = f"""
    <b>Fecha de cotización:</b> {fecha_hoy}<br/>
    <b>Asesor:</b> {datos_cliente.get('asesor', 'Asesor Mundo Joven')}<br/><br/>
    <b>Viajero:</b> {datos_cliente.get('nombre', '')}<br/>
    <b>Destino:</b> {datos_cliente.get('destino', '')}<br/>
    <b>Fechas de viaje:</b> {datos_cliente.get('fechas', '')}
    """
    elementos.append(Paragraph(info_cliente, estilos['Normal']))
    elementos.append(Spacer(1, 20))
    
    datos_tabla = [['Concepto', 'Descripción', 'Precio (MXN)']]
    total = 0
    
    # Creamos un estilo de celda con margen interno para que respire el texto
    estilo_celda = ParagraphStyle('Celda', parent=estilos['Normal'], fontSize=9, leading=11)
    
    for servicio in servicios:
        # Envolvemos los textos en Paragraph para activar el ajuste automático de línea (Word Wrap)
        concepto_p = Paragraph(str(servicio.get('concepto', '')), estilo_celda)
        descripcion_p = Paragraph(str(servicio.get('descripcion', '')), estilo_celda)
        
        datos_tabla.append([concepto_p, descripcion_p, f"${float(servicio['precio']):,.2f}"])
        total += float(servicio['precio'])
    
    datos_tabla.append(['', 'TOTAL ESTIMADO', f"${total:,.2f}"])
    
    tabla = Table(datos_tabla, colWidths=[120, 300, 100])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#ffcc00")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('VALIGN', (0, 1), (-1, -1), 'TOP'), # Alinear el texto hacia arriba
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('GRID', (0, 0), (-1, -2), 1, colors.HexColor("#dddddd")),
        ('FONTNAME', (1, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (1, -1), (-1, -1), colors.HexColor("#0033a0")),
        ('TEXTCOLOR', (1, -1), (-1, -1), colors.white),
        ('ALIGN', (1, -1), (1, -1), 'RIGHT'),
    ]))
    elementos.append(tabla)
    elementos.append(Spacer(1, 30))
    
    terminos = """<font size="8" color="gray"><b>Notas importantes:</b><br/>* Precios en Pesos Mexicanos (MXN).<br/>* Precios sujetos a disponibilidad y cambios sin previo aviso.<br/>* Esta cotización tiene una vigencia de 24 horas.</font>"""
    elementos.append(Paragraph(terminos, estilos['Normal']))
    
    doc.build(elementos)
    buffer.seek(0)
    return buffer

# ==========================================
# INTERFAZ WEB (STREAMLIT)
# ==========================================
def main():
    st.set_page_config(page_title="Cotizador AI - Mundo Joven", page_icon="🌎", layout="wide")
    st.markdown("<h1 style='text-align: center; color: #0033a0;'>🌎 Asistente Inteligente de Cotizaciones</h1>", unsafe_allow_html=True)
    
    if 'servicios' not in st.session_state:
        st.session_state.servicios = []
    if 'sugerencias_temporales' not in st.session_state:
        st.session_state.sugerencias_temporales = []

    st.header("1. Datos del Viajero", divider="blue")
    col1, col2 = st.columns(2)
    with col1:
        nombre_cliente = st.text_input("Nombre completo del viajero")
        destino = st.text_input("Destino principal")
    with col2:
        fechas = st.text_input("Fechas de viaje")
        asesor = st.text_input("Nombre de Asesor y Sucursal")

    st.header("2. Servicios a Cotizar", divider="orange")
    
    # Sistema de Pestañas para elegir entre IA o Manual
    tab_ia, tab_manual = st.tabs(["🤖 Asistente de IA (Nuevo)", "✍️ Captura Manual"])
    
    with tab_ia:
        st.info("Describe lo que busca el cliente y la IA estimará los precios y armará los conceptos automáticamente.")
        peticion = st.text_area("¿Qué paquete necesitas armar?", placeholder="Ej. Vuelo redondo a Londres en junio, 2 semanas de curso de inglés y seguro médico.")
        
        if st.button("✨ Generar sugerencia con Gemini"):
            if peticion:
                with st.spinner("La IA está analizando opciones y precios del mercado..."):
                    sugerencias = consultar_asistente_ia(peticion)
                    if sugerencias:
                        st.session_state.sugerencias_temporales = sugerencias
            else:
                st.warning("Escribe algo para que la IA pueda ayudarte.")
                
        # Mostrar sugerencias de la IA si existen
        if st.session_state.sugerencias_temporales:
            st.success("¡Sugerencias generadas con éxito! Revisa la propuesta:")
            df_sug = pd.DataFrame(st.session_state.sugerencias_temporales)
            st.dataframe(df_sug, use_container_width=True)
            
            if st.button("✅ Agregar estos servicios a la cotización final"):
                for item in st.session_state.sugerencias_temporales:
                    st.session_state.servicios.append(item)
                st.session_state.sugerencias_temporales = [] # Limpiamos
                st.rerun()

    with tab_manual:
        with st.form("form_servicios", clear_on_submit=True):
            c1, c2, c3 = st.columns([1, 2, 1])
            with c1: concepto = st.selectbox("Concepto", ["Vuelo Redondo", "Vuelo Sencillo", "Curso de Idiomas", "Alojamiento", "Seguro de Viaje", "Otro"])
            with c2: descripcion = st.text_input("Descripción detallada")
            with c3: precio = st.number_input("Precio (USD)", min_value=0.0, format="%.2f", step=10.0)
            
            fuente = st.text_input("Enlace de referencia / Proveedor (Opcional)", placeholder="Ej. https://kayak.com/...")
            
            if st.form_submit_button("➕ Agregar Manualmente"):
                if descripcion:
                    st.session_state.servicios.append({
                        "concepto": concepto, 
                        "descripcion": descripcion, 
                        "precio": float(precio),
                        "fuente": fuente if fuente else "Captura Manual"
                    })
                    st.success("Agregado.")

    # Mostrar la tabla final
    if st.session_state.servicios:
        st.subheader("🛒 Paquete actual a cotizar:")
        df_servicios = pd.DataFrame(st.session_state.servicios)
        
        # Si existe la columna fuente, la mostramos como un enlace bonito en la interfaz
        if 'fuente' in df_servicios.columns:
            st.dataframe(
                df_servicios, 
                use_container_width=True,
                column_config={
                    "fuente": st.column_config.LinkColumn("🔗 Enlace / Proveedor"),
                    "precio": st.column_config.NumberColumn("Precio (USD)", format="$%.2f")
                }
            )
        else:
            st.dataframe(df_servicios, use_container_width=True)
            
        if st.button("🗑️ Limpiar carrito"):
            st.session_state.servicios = []
            st.rerun()

    st.header("3. Generar Documento", divider="blue")
    if st.session_state.servicios and nombre_cliente and destino:
        datos_cliente = {"nombre": nombre_cliente, "destino": destino, "fechas": fechas, "asesor": asesor}
        pdf_buffer = generar_pdf_en_memoria(datos_cliente, st.session_state.servicios)
        st.download_button("📥 Descargar PDF Oficial", data=pdf_buffer, file_name=f"Cotizacion_{nombre_cliente.replace(' ', '_')}.pdf", mime="application/pdf", type="primary", use_container_width=True)
    else:
        st.info("Completa los datos del viajero y agrega al menos un servicio para habilitar la descarga del PDF.")

if __name__ == "__main__":
    main()
