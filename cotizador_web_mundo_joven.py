import streamlit as st
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generar_pdf_en_memoria(datos_cliente, servicios):
    """
    Genera el PDF de Mundo Joven y lo devuelve en un buffer de memoria (BytesIO),
    ideal para aplicaciones web como Streamlit.
    """
    buffer = io.BytesIO()
    
    # Configuración básica del documento
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=18)
    
    elementos = []
    estilos = getSampleStyleSheet()
    
    estilo_titulo = ParagraphStyle(
        'TituloMundoJoven',
        parent=estilos['Heading1'],
        fontSize=24,
        textColor=colors.HexColor("#0033a0"), # Azul corporativo Mundo Joven
        spaceAfter=20,
        alignment=1 # Centrado
    )
    
    estilo_subtitulo = ParagraphStyle(
        'Subtitulo',
        parent=estilos['Normal'],
        fontSize=12,
        textColor=colors.HexColor("#333333"),
        spaceAfter=20,
        alignment=1
    )
    
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
    
    datos_tabla = [['Concepto', 'Descripción', 'Precio (USD)']]
    total = 0
    
    for servicio in servicios:
        datos_tabla.append([
            servicio['concepto'], 
            servicio['descripcion'], 
            f"${servicio['precio']:,.2f}"
        ])
        total += servicio['precio']
    
    # Fila de Total
    datos_tabla.append(['', 'TOTAL ESTIMADO', f"${total:,.2f}"])
    
    tabla = Table(datos_tabla, colWidths=[120, 300, 100])
    estilo_tabla = TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#ffcc00")), # Amarillo dinámico
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Cuerpo de la tabla
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'), # Precios a la derecha
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('GRID', (0, 0), (-1, -2), 1, colors.HexColor("#dddddd")),
        
        # Fila de Total
        ('FONTNAME', (1, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (1, -1), (-1, -1), colors.HexColor("#0033a0")),
        ('TEXTCOLOR', (1, -1), (-1, -1), colors.white),
        ('ALIGN', (1, -1), (1, -1), 'RIGHT'),
    ])
    
    tabla.setStyle(estilo_tabla)
    elementos.append(tabla)
    elementos.append(Spacer(1, 30))
    
    terminos = """
    <font size="8" color="gray">
    <b>Notas importantes:</b><br/>
    * Precios en dólares americanos (USD).<br/>
    * Precios sujetos a disponibilidad y cambios sin previo aviso.<br/>
    * La tarifa del vuelo no se garantiza hasta la emisión del boleto.<br/>
    * Esta cotización tiene una vigencia de 24 horas.<br/>
    </font>
    """
    elementos.append(Paragraph(terminos, estilos['Normal']))
    
    # Generar el PDF
    doc.build(elementos)
    buffer.seek(0) # Regresar el puntero al inicio del archivo en memoria
    return buffer

def main():
    # Configuración de la página
    st.set_page_config(page_title="Cotizador Mundo Joven", page_icon="🌎", layout="wide")
    
    st.markdown("<h1 style='text-align: center; color: #0033a0;'>🌎 Generador de Cotizaciones - Mundo Joven</h1>", unsafe_allow_html=True)
    st.write("Completa los datos del viajero, agrega los servicios y descarga el PDF profesional al instante.")
    
    # Inicializar variable de estado para guardar los servicios de la sesión actual
    if 'servicios' not in st.session_state:
        st.session_state.servicios = []

    st.header("1. Datos del Viajero", divider="blue")
    col1, col2 = st.columns(2)
    
    with col1:
        nombre_cliente = st.text_input("Nombre completo del viajero", placeholder="Ej. Carlos Mendoza")
        destino = st.text_input("Destino principal", placeholder="Ej. Vancouver, Canadá")
        
    with col2:
        fechas = st.text_input("Fechas de viaje", placeholder="Ej. 15 Sep 2027 - 15 Dic 2027")
        asesor = st.text_input("Nombre de Asesor y Sucursal", placeholder="Ej. Ana López (Sucursal Roma)")

    st.header("2. Servicios a Cotizar", divider="orange")
    
    # Formulario para agregar un servicio nuevo
    with st.form("form_servicios", clear_on_submit=True):
        st.write("Agrega un nuevo servicio al paquete:")
        col_s1, col_s2, col_s3 = st.columns([1, 2, 1])
        
        with col_s1:
            concepto = st.selectbox("Concepto", [
                "Vuelo Redondo", "Vuelo Sencillo", "Curso de Idiomas", 
                "Alojamiento", "Seguro de Viaje", "Gestión de Visa", "Tour/Excursión", "Otro"
            ])
        with col_s2:
            descripcion = st.text_input("Descripción detallada", placeholder="Ej. Homestay habitación individual...")
        with col_s3:
            precio = st.number_input("Precio (USD)", min_value=0.0, format="%.2f", step=10.0)
            
        btn_agregar = st.form_submit_button("➕ Agregar Servicio")
        
        if btn_agregar:
            if descripcion.strip() == "":
                st.error("Por favor ingresa una descripción para el servicio.")
            else:
                st.session_state.servicios.append({
                    "concepto": concepto,
                    "descripcion": descripcion,
                    "precio": float(precio)
                })
                st.success(f"{concepto} agregado correctamente.")

    if st.session_state.servicios:
        st.subheader("Paquete actual:")
        
        # Mostrar como tabla visual en Streamlit
        import pandas as pd
        df_servicios = pd.DataFrame(st.session_state.servicios)
        # Formatear columna de precio para la vista
        df_servicios_display = df_servicios.copy()
        df_servicios_display['precio'] = df_servicios_display['precio'].apply(lambda x: f"${x:,.2f}")
        st.table(df_servicios_display)
        
        # Botón para limpiar servicios
        if st.button("🗑️ Limpiar lista de servicios"):
            st.session_state.servicios = []
            st.rerun()

    st.header("3. Generar Documento", divider="blue")
    
    # Validación antes de generar
    if st.session_state.servicios and nombre_cliente and destino:
        datos_cliente = {
            "nombre": nombre_cliente,
            "destino": destino,
            "fechas": fechas,
            "asesor": asesor
        }
        
        # Botón de descarga
        pdf_buffer = generar_pdf_en_memoria(datos_cliente, st.session_state.servicios)
        
        nombre_archivo = f"Cotizacion_{nombre_cliente.replace(' ', '_')}_{destino.replace(' ', '')}.pdf"
        
        st.success("¡Cotización lista para descargar!")
        st.download_button(
            label="📥 Descargar Cotización (PDF)",
            data=pdf_buffer,
            file_name=nombre_archivo,
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
    elif not st.session_state.servicios:
        st.info("Agrega al menos un servicio para generar la cotización.")
    else:
        st.info("Completa los datos principales del viajero y destino para habilitar la descarga.")

if __name__ == "__main__":
    main()