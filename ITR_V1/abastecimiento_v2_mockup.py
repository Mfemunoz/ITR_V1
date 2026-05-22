import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
from datetime import datetime
from PIL import Image
from io import BytesIO
from pathlib import Path
from urllib.parse import parse_qs, urlparse

st.set_page_config(
    page_title='Sodimac Colombia | Centro de Control de Abastecimiento',
    layout='wide',
    initial_sidebar_state='expanded'
)

REQUIRED_COLUMNS = [
    'SKU', 'DESC SKU', 'Tienda', 'Nombre Tienda', 'Proyectado_UE', 'Inv_CD', 'Inv_ITR',
    'Stock_Seguridad', 'Capacidad_Tienda', 'Req_Maquila', 'Req_Lote', 'Proyectado_Palets',
    'LT_CD', 'LT_ITR', 'CALENDAR'
]

TMS_COLUMNS = [
    'Shipment', 'Fecha_Despacho', 'Origen', 'Destino', 'Tienda', 'Nombre_Tienda', 'Region',
    'Placa', 'Tipo_Vehiculo', 'Transportadora', 'Conductor', 'Celular_Conductor',
    'Capacidad_Palets', 'Palets_Asignados', 'Peso_Kg', 'Volumen_M3', 'Estado',
    'Hora_Cita', 'Hora_Salida', 'Hora_Llegada', 'Novedad', 'Observacion'
]

TMS_REQUIRED_COLUMNS = [
    'Shipment', 'Tienda', 'Placa', 'Tipo_Vehiculo', 'Capacidad_Palets', 'Palets_Asignados', 'Estado'
]

PLANEACION_COLUMNS = [
    'Semana', 'SKU', 'DESC_SKU', 'Tienda', 'Nombre_Tienda', 'Demanda_Relex',
    'Inv_ITR_Actual', 'Llegada_Proyectada_ITR', 'Inv_CD_Actual', 'Stock_Seguridad',
    'Capacidad_Tienda', 'Palets_Proyectados', 'Fecha_Disponible_ITR', 'Calendario_Tienda',
    'Req_Maquila', 'Req_Lote', 'Prioridad'
]

PLANEACION_REQUIRED_COLUMNS = [
    'Semana', 'SKU', 'Tienda', 'Demanda_Relex', 'Inv_ITR_Actual',
    'Llegada_Proyectada_ITR', 'Stock_Seguridad', 'Capacidad_Tienda',
    'Palets_Proyectados', 'Fecha_Disponible_ITR', 'Calendario_Tienda'
]

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / 'assets' / 'logo_sodimac.png'
logo = Image.open(LOGO_PATH) if LOGO_PATH.exists() else None

st.markdown('''
<style>
.main {background-color:#f8fafc;}
.block-container {padding-top:2.5rem;padding-left:2rem;padding-right:2rem;}
.metric-box {background:white;padding:1rem;border-radius:12px;box-shadow:0 4px 14px rgba(0,0,0,0.08);text-align:center;min-height:96px;}
.metric-title {color:#6b7280;font-size:13px;font-weight:600;}
.metric-value {color:#1f2937;font-size:26px;font-weight:bold;line-height:1.2;}
.status-card {background:#004b8d;color:white;padding:14px;border-radius:12px;text-align:center;}
.footer {text-align:center;color:#6b7280;padding-top:20px;font-size:13px;}
</style>
''', unsafe_allow_html=True)


def normalizar_si_no(valor):
    return str(valor).strip().upper() in ['SI', 'SÍ', 'YES', 'Y', 'TRUE', '1']


def reset_excel_source(source):
    if hasattr(source, 'seek'):
        source.seek(0)
    return source


def normalizar_url_excel(url):
    url = url.strip()
    parsed = urlparse(url)

    if 'drive.google.com' in parsed.netloc and '/file/d/' in parsed.path:
        file_id = parsed.path.split('/file/d/')[1].split('/')[0]
        return f'https://drive.google.com/uc?export=download&id={file_id}'

    if 'docs.google.com' in parsed.netloc and '/spreadsheets/d/' in parsed.path:
        sheet_id = parsed.path.split('/spreadsheets/d/')[1].split('/')[0]
        return f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx'

    if '1drv.ms' in parsed.netloc or 'sharepoint.com' in parsed.netloc:
        query = parse_qs(parsed.query)
        if 'download' not in query:
            separator = '&' if parsed.query else '?'
            return f'{url}{separator}download=1'

    return url


def comparar_lead_time(row):
    lt_itr = row['LT_ITR']
    lt_cd = row['LT_CD']

    if pd.isna(lt_itr) or pd.isna(lt_cd):
        return 'Lead Time incompleto'
    if lt_itr == lt_cd:
        return 'Lead Time equivalente'
    if lt_itr < lt_cd:
        return f"ITR más rápido ({abs(lt_cd - lt_itr):.0f} días)"
    return f"CD más rápido ({abs(lt_cd - lt_itr):.0f} días)"


def decidir(row):
    necesidad = row['Proyectado_UE']
    stock_min = row['Stock_Seguridad']
    capacidad = row['Capacidad_Tienda']
    inv_itr = row['Inv_ITR']
    inv_cd = row['Inv_CD']

    if pd.isna(necesidad):
        return 'DATOS INCOMPLETOS'

    if necesidad <= 0:
        return 'NO GENERAR PEDIDO'

    necesidad_ajustada = min(necesidad, capacidad) if capacidad > 0 else necesidad

    tiene_maquila = normalizar_si_no(row['Req_Maquila'])
    tiene_lote = normalizar_si_no(row['Req_Lote'])

    etiqueta = ''
    if tiene_maquila and tiene_lote:
        etiqueta = ' (MAQUILA + LOTE)'
    elif tiene_maquila:
        etiqueta = ' (MAQUILA)'
    elif tiene_lote:
        etiqueta = ' (LOTE)'

    if inv_itr >= necesidad_ajustada:
        return 'SURTIR DESDE ITR' + etiqueta

    if inv_cd >= necesidad_ajustada:
        return 'SURTIR DESDE CD' + etiqueta

    if inv_itr < stock_min and inv_cd < stock_min:
        return 'SIN INVENTARIO SUFICIENTE'

    return 'SIN INVENTARIO SUFICIENTE'


@st.cache_data(show_spinner=False)
def load_data(excel_source):
    excel_source = reset_excel_source(excel_source)
    df = pd.read_excel(excel_source, sheet_name='Data Analisis', engine='openpyxl')
    df.columns = df.columns.astype(str).str.strip()

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f'Faltan columnas obligatorias: {missing}')

    df['SKU'] = pd.to_numeric(df['SKU'], errors='coerce').fillna(0).astype(int)
    df['Tienda'] = pd.to_numeric(df['Tienda'], errors='coerce').fillna(0).astype(int)

    numeric_cols = [
        'Proyectado_UE', 'Inv_CD', 'Inv_ITR', 'Stock_Seguridad',
        'Capacidad_Tienda', 'Proyectado_Palets', 'LT_CD', 'LT_ITR'
    ]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

    df['Decision_Python'] = df.apply(decidir, axis=1)
    df['Comparativo_LT'] = df.apply(comparar_lead_time, axis=1)
    return df


@st.cache_data(show_spinner=False)
def load_tms_data(excel_source):
    excel_source = reset_excel_source(excel_source)
    excel = pd.ExcelFile(excel_source, engine='openpyxl')
    if 'TMS' not in excel.sheet_names:
        return None, ['No existe la pestaña TMS en el archivo cargado.']

    tms = pd.read_excel(excel, sheet_name='TMS')
    tms.columns = tms.columns.astype(str).str.strip()
    tms = tms.rename(columns={'Nombre Tienda': 'Nombre_Tienda'})

    missing = [c for c in TMS_REQUIRED_COLUMNS if c not in tms.columns]
    if missing:
        return None, [f'Faltan columnas obligatorias en TMS: {missing}']

    for c in TMS_COLUMNS:
        if c not in tms.columns:
            tms[c] = ''

    tms['Shipment'] = tms['Shipment'].astype(str).str.strip()
    tms['Placa'] = tms['Placa'].astype(str).str.strip().str.upper()
    tms['Estado'] = tms['Estado'].astype(str).str.strip().str.upper()
    tms['Novedad'] = tms['Novedad'].fillna('').astype(str).str.strip()
    tms['Tienda'] = pd.to_numeric(tms['Tienda'], errors='coerce').fillna(0).astype(int)

    numeric_cols = ['Capacidad_Palets', 'Palets_Asignados', 'Peso_Kg', 'Volumen_M3']
    for c in numeric_cols:
        tms[c] = pd.to_numeric(tms[c], errors='coerce').fillna(0)

    tms['Fecha_Despacho'] = pd.to_datetime(tms['Fecha_Despacho'], errors='coerce')
    tms['Ocupacion_Pct'] = tms.apply(
        lambda r: (r['Palets_Asignados'] / r['Capacidad_Palets']) if r['Capacidad_Palets'] > 0 else 0,
        axis=1
    )
    tms['Validacion_Capacidad'] = tms.apply(validar_capacidad_tms, axis=1)
    tms['Estado_Operativo'] = tms.apply(validar_estado_tms, axis=1)
    return tms[TMS_COLUMNS + ['Ocupacion_Pct', 'Validacion_Capacidad', 'Estado_Operativo']], []


@st.cache_data(show_spinner=False)
def load_planeacion_itr(excel_source):
    excel_source = reset_excel_source(excel_source)
    excel = pd.ExcelFile(excel_source, engine='openpyxl')
    if 'Planeacion_ITR' not in excel.sheet_names:
        return None, ['No existe la pestaña Planeacion_ITR en el archivo cargado.']

    plan = pd.read_excel(excel, sheet_name='Planeacion_ITR')
    plan.columns = plan.columns.astype(str).str.strip()
    plan = plan.rename(columns={
        'DESC SKU': 'DESC_SKU',
        'Nombre Tienda': 'Nombre_Tienda',
        'Calendario': 'Calendario_Tienda'
    })

    missing = [c for c in PLANEACION_REQUIRED_COLUMNS if c not in plan.columns]
    if missing:
        return None, [f'Faltan columnas obligatorias en Planeacion_ITR: {missing}']

    for c in PLANEACION_COLUMNS:
        if c not in plan.columns:
            plan[c] = ''

    if plan.empty:
        return plan[PLANEACION_COLUMNS], ['La pestaña Planeacion_ITR existe, pero todavía no tiene registros.']

    plan['SKU'] = pd.to_numeric(plan['SKU'], errors='coerce').fillna(0).astype(int)
    plan['Tienda'] = pd.to_numeric(plan['Tienda'], errors='coerce').fillna(0).astype(int)
    plan['Fecha_Disponible_ITR'] = pd.to_datetime(plan['Fecha_Disponible_ITR'], errors='coerce')

    numeric_cols = [
        'Demanda_Relex', 'Inv_ITR_Actual', 'Llegada_Proyectada_ITR', 'Inv_CD_Actual',
        'Stock_Seguridad', 'Capacidad_Tienda', 'Palets_Proyectados'
    ]
    for c in numeric_cols:
        plan[c] = pd.to_numeric(plan[c], errors='coerce').fillna(0)

    plan['Req_Maquila'] = plan['Req_Maquila'].fillna('').astype(str).str.strip().str.upper()
    plan['Req_Lote'] = plan['Req_Lote'].fillna('').astype(str).str.strip().str.upper()
    plan['Calendario_Tienda'] = plan['Calendario_Tienda'].fillna('').astype(str).str.strip()
    plan['Prioridad'] = plan['Prioridad'].fillna('').astype(str).str.strip().str.upper()
    plan['Inv_ITR_Proyectado'] = plan['Inv_ITR_Actual'] + plan['Llegada_Proyectada_ITR']
    plan['Demanda_Ajustada'] = plan.apply(
        lambda r: min(r['Demanda_Relex'], r['Capacidad_Tienda']) if r['Capacidad_Tienda'] > 0 else r['Demanda_Relex'],
        axis=1
    )
    plan['Potencial_Despacho'] = plan.apply(decidir_planeacion_itr, axis=1)
    plan['Alerta_Planeacion'] = plan.apply(alerta_planeacion_itr, axis=1)
    return plan[PLANEACION_COLUMNS + [
        'Inv_ITR_Proyectado', 'Demanda_Ajustada', 'Potencial_Despacho', 'Alerta_Planeacion'
    ]], []


def decidir_planeacion_itr(row):
    if row['Demanda_Relex'] <= 0:
        return 'NO VIABLE - SIN DEMANDA'
    if row['Demanda_Relex'] < row['Stock_Seguridad']:
        return 'NO VIABLE - NO CUMPLE STOCK MINIMO'
    if row['Inv_ITR_Proyectado'] < row['Demanda_Ajustada']:
        return 'NO VIABLE - SIN INVENTARIO PROYECTADO'
    if pd.isna(row['Fecha_Disponible_ITR']):
        return 'REVISAR - FECHA DISPONIBLE ITR'
    if not row['Calendario_Tienda']:
        return 'REVISAR - CALENDARIO TIENDA'

    etiquetas = []
    if normalizar_si_no(row['Req_Maquila']):
        etiquetas.append('MAQUILA')
    if normalizar_si_no(row['Req_Lote']):
        etiquetas.append('LOTE')
    if etiquetas:
        return 'VIABLE CON REVISION - ' + ' + '.join(etiquetas)
    return 'VIABLE PLANEAR DESPACHO ITR'


def alerta_planeacion_itr(row):
    if row['Potencial_Despacho'].startswith('VIABLE') and row['Palets_Proyectados'] <= 0:
        return 'REVISAR PALETS PROYECTADOS'
    if row['Prioridad'] in ['ALTA', 'URGENTE'] and not row['Potencial_Despacho'].startswith('VIABLE'):
        return 'PRIORIDAD ALTA SIN VIABILIDAD'
    if row['Inv_ITR_Proyectado'] == 0:
        return 'SIN INVENTARIO ITR PROYECTADO'
    return 'OK'


def validar_capacidad_tms(row):
    if row['Capacidad_Palets'] <= 0:
        return 'SIN CAPACIDAD DEFINIDA'
    if row['Palets_Asignados'] > row['Capacidad_Palets']:
        return 'EXCEDE CAPACIDAD'
    if row['Ocupacion_Pct'] >= 0.9:
        return 'CAPACIDAD ALTA'
    if row['Ocupacion_Pct'] >= 0.7:
        return 'CAPACIDAD OK'
    return 'BAJA OCUPACION'


def validar_estado_tms(row):
    if row['Novedad']:
        return 'CON NOVEDAD'
    if row['Estado'] in ['ENTREGADO', 'CERRADO', 'FINALIZADO']:
        return 'ENTREGADO'
    if row['Estado'] in ['EN RUTA', 'TRANSITO', 'TRÁNSITO']:
        return 'EN RUTA'
    if row['Estado'] in ['PLANIFICADO', 'ASIGNADO', 'CARGANDO']:
        return 'PENDIENTE'
    return 'REVISAR ESTADO'


def generar_plantilla_tms():
    plantilla = pd.DataFrame(columns=TMS_COLUMNS)
    ejemplo = {
        'Shipment': 'SH000001',
        'Fecha_Despacho': datetime.now().date(),
        'Origen': 'CD',
        'Destino': 'Tienda',
        'Tienda': 40,
        'Nombre_Tienda': 'Med Industriales',
        'Region': 'Antioquia',
        'Placa': 'ABC123',
        'Tipo_Vehiculo': 'Turbo',
        'Transportadora': 'Transportadora Demo',
        'Conductor': 'Nombre Conductor',
        'Celular_Conductor': '3000000000',
        'Capacidad_Palets': 12,
        'Palets_Asignados': 10,
        'Peso_Kg': 2500,
        'Volumen_M3': 18,
        'Estado': 'PLANIFICADO',
        'Hora_Cita': '08:00',
        'Hora_Salida': '',
        'Hora_Llegada': '',
        'Novedad': '',
        'Observacion': ''
    }
    plantilla = pd.concat([plantilla, pd.DataFrame([ejemplo])], ignore_index=True)
    return to_excel(plantilla)


def generar_plantilla_planeacion_itr():
    ejemplo = {
        'Semana': '2026-W22',
        'SKU': 132239,
        'DESC_SKU': 'OSB ESTRUCTURAL 9.5mm 122x244cm 630kg/m3',
        'Tienda': 40,
        'Nombre_Tienda': 'Med Industriales',
        'Demanda_Relex': 126,
        'Inv_ITR_Actual': 80,
        'Llegada_Proyectada_ITR': 100,
        'Inv_CD_Actual': 15000,
        'Stock_Seguridad': 126,
        'Capacidad_Tienda': 126,
        'Palets_Proyectados': 2,
        'Fecha_Disponible_ITR': datetime.now().date(),
        'Calendario_Tienda': 'MON/WED',
        'Req_Maquila': 'SI',
        'Req_Lote': 'NO',
        'Prioridad': 'MEDIA'
    }
    plantilla = pd.DataFrame([ejemplo], columns=PLANEACION_COLUMNS)
    return to_excel(plantilla)


def cruzar_tms_abastecimiento(tms, df):
    abastecimiento = df[df['Decision_Python'].str.contains('SURTIR DESDE', na=False)]
    resumen = (
        abastecimiento.groupby('Tienda', as_index=False)['Proyectado_Palets']
        .sum()
        .rename(columns={'Proyectado_Palets': 'Palets_Sugeridos_Abastecimiento'})
    )
    cruzado = tms.merge(resumen, on='Tienda', how='left')
    cruzado['Palets_Sugeridos_Abastecimiento'] = cruzado['Palets_Sugeridos_Abastecimiento'].fillna(0)
    cruzado['Diferencia_Palets'] = cruzado['Capacidad_Palets'] - cruzado['Palets_Asignados']
    return cruzado


def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Resultados')
    return output.getvalue()


def pintar_metricas(metrics):
    cols = st.columns(5)
    for i, (title, value) in enumerate(metrics):
        with cols[i % 5]:
            st.markdown(
                f"<div class='metric-box'><div class='metric-title'>{title}</div><div class='metric-value'>{value}</div></div>",
                unsafe_allow_html=True
            )


col_logo, col_title, col_status = st.columns([1.4, 3.2, 1.4])
with col_logo:
    if logo:
        st.image(logo, width=170)
    else:
        st.markdown("<h2 style='color:#004b8d;'>SODIMAC</h2>", unsafe_allow_html=True)
with col_title:
    st.markdown(
        "<h1 style='color:#1f2937;margin-bottom:0;'>SODIMAC COLOMBIA</h1>"
        "<h3 style='color:#004b8d;margin-top:0;'>Centro de Control de Abastecimiento</h3>",
        unsafe_allow_html=True
    )
with col_status:
    st.markdown(
        f"<div class='status-card'><b>Usuario:</b> Analista Logístico<br>"
        f"<b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br>"
        "<b>Ambiente:</b> PRODUCCIÓN</div>",
        unsafe_allow_html=True
    )

with st.sidebar:
    if logo:
        st.image(logo, width=150)
    selected = option_menu(
        'Centro de Control',
        ['Planeación ITR', 'Ejecución Abastecimiento', 'TMS', 'Consultas', 'Reportes'],
        icons=['calendar-week', 'box-seam', 'truck', 'search', 'file-earmark-arrow-down'],
        default_index=0
    )
    fuente_datos = st.radio('Fuente de datos', ['Archivo local', 'URL en línea'], horizontal=True)
    uploaded_file = None
    excel_source = None
    if fuente_datos == 'Archivo local':
        uploaded_file = st.file_uploader('Cargar Excel operativo', type=['xlsx'])
        excel_source = uploaded_file
        st.caption('Límite configurado para archivos grandes: 1024 MB.')
    else:
        excel_url = st.text_input(
            'URL del Excel',
            placeholder='https://.../archivo.xlsx o enlace compartido de Google Sheets/Drive'
        )
        if excel_url:
            excel_source = normalizar_url_excel(excel_url)
            st.caption('La URL debe permitir descarga directa o acceso público/autorizado desde el servidor.')

df = None
tms_df = None
tms_messages = []
planeacion_df = None
planeacion_messages = []
if excel_source:
    try:
        df = load_data(excel_source)
        planeacion_df, planeacion_messages = load_planeacion_itr(excel_source)
        tms_df, tms_messages = load_tms_data(excel_source)
        st.success(f'Archivo cargado correctamente: {len(df):,} registros procesados.')
    except Exception as e:
        st.error(f'Error cargando archivo: {e}')

if selected == 'Ejecución Abastecimiento':
    st.subheader('Ejecución Abastecimiento')
    if df is None:
        st.info('Carga el archivo Excel operativo desde el menú lateral.')
    else:
        metrics = [
            ('SKU evaluados', f'{len(df):,}'),
            ('Tiendas activas', f'{df["Tienda"].nunique():,}'),
            ('Reposición ITR', f'{df["Decision_Python"].str.contains("SURTIR DESDE ITR", na=False).sum():,}'),
            ('Reposición CD', f'{df["Decision_Python"].str.contains("SURTIR DESDE CD", na=False).sum():,}'),
            ('Sin inventario', f'{df["Decision_Python"].eq("SIN INVENTARIO SUFICIENTE").sum():,}'),
            ('Inv Total ITR', f'{df["Inv_ITR"].sum():,.0f}'),
            ('Inv Total CD', f'{df["Inv_CD"].sum():,.0f}'),
            ('Palets sugeridos', f'{df["Proyectado_Palets"].sum():,.0f}'),
            ('LT Prom ITR', f'{df["LT_ITR"].mean():.1f}'),
            ('LT Prom CD', f'{df["LT_CD"].mean():.1f}'),
        ]
        pintar_metricas(metrics)
        st.divider()
        st.dataframe(
            df[['SKU', 'DESC SKU', 'Tienda', 'Nombre Tienda', 'Proyectado_Palets', 'LT_ITR', 'LT_CD', 'CALENDAR', 'Comparativo_LT', 'Decision_Python']].head(100),
            use_container_width=True
        )

elif selected == 'Consultas':
    st.subheader('Consultas')
    if df is None:
        st.warning('Carga primero el archivo Excel.')
    else:
        tab_individual, tab_masiva = st.tabs(['Consulta individual', 'Consulta masiva'])

        with tab_individual:
            st.markdown('Consulta por SKU y tienda')
            c1, c2, c3 = st.columns([1, 1, 1])
            with c1:
                sku = st.number_input('SKU', min_value=0, step=1, format='%d')
            with c2:
                tienda = st.number_input('Tienda', min_value=0, step=1, format='%d')
            with c3:
                buscar = st.button('Buscar', use_container_width=True)

            if buscar:
                resultado = df[(df['SKU'] == int(sku)) & (df['Tienda'] == int(tienda))]
                if resultado.empty:
                    st.warning('Sin coincidencias para ese SKU y tienda.')
                else:
                    st.dataframe(
                        resultado[['SKU', 'DESC SKU', 'Tienda', 'Nombre Tienda', 'Proyectado_Palets', 'LT_ITR', 'LT_CD', 'CALENDAR', 'Comparativo_LT', 'Decision_Python']],
                        use_container_width=True
                    )
                    st.download_button('Descargar resultado', to_excel(resultado), 'resultado_individual.xlsx')

        with tab_masiva:
            st.caption('Puedes pegar pares SKU,Tienda uno por línea o cargar un Excel con columnas SKU y Tienda.')
            texto = st.text_area('Consultas manuales', placeholder='132239,40\n274734,40')
            qfile = st.file_uploader('Cargar archivo de consultas', type=['xlsx'], key='consulta_masiva')
            ejecutar = st.button('Ejecutar consulta masiva', use_container_width=True)

            if ejecutar:
                queries = []
                for line in texto.splitlines():
                    parts = [p.strip() for p in line.replace(';', ',').split(',')]
                    if len(parts) >= 2 and parts[0] and parts[1]:
                        try:
                            queries.append((int(float(parts[0])), int(float(parts[1]))))
                        except ValueError:
                            st.warning(f'Línea ignorada por formato inválido: {line}')

                if qfile:
                    qdf = pd.read_excel(qfile, engine='openpyxl')
                    qdf.columns = qdf.columns.astype(str).str.strip()
                    if {'SKU', 'Tienda'}.issubset(qdf.columns):
                        qdf['SKU'] = pd.to_numeric(qdf['SKU'], errors='coerce')
                        qdf['Tienda'] = pd.to_numeric(qdf['Tienda'], errors='coerce')
                        qdf = qdf.dropna(subset=['SKU', 'Tienda'])
                        queries.extend([(int(s), int(t)) for s, t in zip(qdf['SKU'], qdf['Tienda'])])
                    else:
                        st.error('El archivo de consultas debe tener columnas SKU y Tienda.')

                if not queries:
                    st.warning('No hay consultas válidas para ejecutar.')
                else:
                    key_df = pd.DataFrame(queries, columns=['SKU', 'Tienda']).drop_duplicates()
                    final = df.merge(key_df, on=['SKU', 'Tienda'], how='inner')
                    if final.empty:
                        st.warning('Sin coincidencias.')
                    else:
                        st.dataframe(
                            final[['SKU', 'DESC SKU', 'Tienda', 'Nombre Tienda', 'Proyectado_Palets', 'LT_ITR', 'LT_CD', 'CALENDAR', 'Comparativo_LT', 'Decision_Python']],
                            use_container_width=True
                        )
                        st.download_button('Descargar Excel', to_excel(final), 'resultado_abastecimiento.xlsx')

elif selected == 'Consulta Individual':
    st.subheader('Consulta Individual')
    if df is None:
        st.warning('Carga primero el archivo Excel.')
    else:
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            sku = st.number_input('SKU', min_value=0, step=1, format='%d')
        with c2:
            tienda = st.number_input('Tienda', min_value=0, step=1, format='%d')
        with c3:
            buscar = st.button('Buscar', use_container_width=True)

        if buscar:
            resultado = df[(df['SKU'] == int(sku)) & (df['Tienda'] == int(tienda))]
            if resultado.empty:
                st.warning('Sin coincidencias para ese SKU y tienda.')
            else:
                st.dataframe(
                    resultado[['SKU', 'DESC SKU', 'Tienda', 'Nombre Tienda', 'Proyectado_Palets', 'LT_ITR', 'LT_CD', 'CALENDAR', 'Comparativo_LT', 'Decision_Python']],
                    use_container_width=True
                )
                st.download_button('Descargar resultado', to_excel(resultado), 'resultado_individual.xlsx')

elif selected == 'Consulta Masiva':
    st.subheader('Consulta Masiva')
    if df is None:
        st.warning('Carga primero el archivo Excel.')
    else:
        st.caption('Puedes pegar pares SKU,Tienda uno por línea o cargar un Excel con columnas SKU y Tienda.')
        texto = st.text_area('Consultas manuales', placeholder='132239,40\n274734,40')
        qfile = st.file_uploader('Cargar archivo de consultas', type=['xlsx'], key='consulta_masiva')
        ejecutar = st.button('Ejecutar consulta masiva', use_container_width=True)

        if ejecutar:
            queries = []
            for line in texto.splitlines():
                parts = [p.strip() for p in line.replace(';', ',').split(',')]
                if len(parts) >= 2 and parts[0] and parts[1]:
                    try:
                        queries.append((int(float(parts[0])), int(float(parts[1]))))
                    except ValueError:
                        st.warning(f'Línea ignorada por formato inválido: {line}')

            if qfile:
                qdf = pd.read_excel(qfile, engine='openpyxl')
                qdf.columns = qdf.columns.astype(str).str.strip()
                if {'SKU', 'Tienda'}.issubset(qdf.columns):
                    qdf['SKU'] = pd.to_numeric(qdf['SKU'], errors='coerce')
                    qdf['Tienda'] = pd.to_numeric(qdf['Tienda'], errors='coerce')
                    qdf = qdf.dropna(subset=['SKU', 'Tienda'])
                    queries.extend([(int(s), int(t)) for s, t in zip(qdf['SKU'], qdf['Tienda'])])
                else:
                    st.error('El archivo de consultas debe tener columnas SKU y Tienda.')

            if not queries:
                st.warning('No hay consultas válidas para ejecutar.')
            else:
                key_df = pd.DataFrame(queries, columns=['SKU', 'Tienda']).drop_duplicates()
                final = df.merge(key_df, on=['SKU', 'Tienda'], how='inner')
                if final.empty:
                    st.warning('Sin coincidencias.')
                else:
                    st.dataframe(
                        final[['SKU', 'DESC SKU', 'Tienda', 'Nombre Tienda', 'Proyectado_Palets', 'LT_ITR', 'LT_CD', 'CALENDAR', 'Comparativo_LT', 'Decision_Python']],
                        use_container_width=True
                    )
                    st.download_button('Descargar Excel', to_excel(final), 'resultado_abastecimiento.xlsx')

elif selected == 'Dashboard Ejecutivo':
    st.subheader('Dashboard Ejecutivo')
    if df is None:
        st.warning('Carga primero el archivo Excel.')
    else:
        decisiones = df['Decision_Python'].value_counts().reset_index()
        decisiones.columns = ['Decision_Python', 'Casos']
        fig1 = px.bar(decisiones, x='Decision_Python', y='Casos', title='Distribución de decisiones')
        st.plotly_chart(fig1, use_container_width=True)

        top = df.groupby('Nombre Tienda').size().reset_index(name='Casos').sort_values('Casos', ascending=False).head(10)
        fig2 = px.bar(top, x='Nombre Tienda', y='Casos', title='Top tiendas con registros')
        st.plotly_chart(fig2, use_container_width=True)

elif selected == 'Planeación ITR':
    st.subheader('Planeación ITR - Potencial de Despacho')
    if df is None:
        st.warning('Carga primero el archivo Excel.')
    elif planeacion_df is None:
        for msg in planeacion_messages:
            st.info(msg)
        st.markdown('La pestaña `Planeacion_ITR` debe tener como mínimo estas columnas obligatorias:')
        st.dataframe(pd.DataFrame({'Columnas obligatorias': PLANEACION_REQUIRED_COLUMNS}), use_container_width=True)
        st.download_button(
            'Descargar plantilla Planeacion_ITR',
            generar_plantilla_planeacion_itr(),
            'plantilla_planeacion_itr.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    elif planeacion_df.empty:
        for msg in planeacion_messages:
            st.info(msg)
        st.markdown('La hoja ya existe. Puedes alimentarla con estas columnas:')
        st.dataframe(pd.DataFrame({'Columnas': PLANEACION_COLUMNS}), use_container_width=True)
        st.download_button(
            'Descargar ejemplo Planeacion_ITR',
            generar_plantilla_planeacion_itr(),
            'plantilla_planeacion_itr.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    else:
        plan = planeacion_df.copy()
        semana_options = sorted([str(s) for s in plan['Semana'].dropna().unique()])
        decision_options = sorted(plan['Potencial_Despacho'].dropna().unique())
        prioridad_options = sorted([p for p in plan['Prioridad'].dropna().astype(str).unique() if p])

        f1, f2, f3 = st.columns(3)
        with f1:
            semana_filtro = st.multiselect('Semana', semana_options, default=semana_options)
        with f2:
            decision_filtro = st.multiselect('Potencial despacho', decision_options, default=decision_options)
        with f3:
            prioridad_filtro = st.multiselect('Prioridad', prioridad_options, default=prioridad_options)

        filtrado = plan.copy()
        if semana_filtro:
            filtrado = filtrado[filtrado['Semana'].astype(str).isin(semana_filtro)]
        if decision_filtro:
            filtrado = filtrado[filtrado['Potencial_Despacho'].isin(decision_filtro)]
        if prioridad_filtro:
            filtrado = filtrado[filtrado['Prioridad'].astype(str).isin(prioridad_filtro)]

        viable_mask = filtrado['Potencial_Despacho'].str.startswith('VIABLE', na=False)
        metrics = [
            ('Registros planeados', f'{len(filtrado):,}'),
            ('Tiendas', f'{filtrado["Tienda"].nunique():,}'),
            ('SKU', f'{filtrado["SKU"].nunique():,}'),
            ('Viables ITR', f'{viable_mask.sum():,}'),
            ('No viables', f'{(~viable_mask).sum():,}'),
            ('Demanda Relex', f'{filtrado["Demanda_Relex"].sum():,.0f}'),
            ('Inv ITR proyectado', f'{filtrado["Inv_ITR_Proyectado"].sum():,.0f}'),
            ('Palets proyectados', f'{filtrado["Palets_Proyectados"].sum():,.0f}'),
            ('Alertas', f'{filtrado["Alerta_Planeacion"].ne("OK").sum():,}'),
            ('Prioridad alta', f'{filtrado["Prioridad"].isin(["ALTA", "URGENTE"]).sum():,}'),
        ]
        pintar_metricas(metrics)
        st.divider()

        g1, g2 = st.columns(2)
        with g1:
            decision_chart = filtrado['Potencial_Despacho'].value_counts().reset_index()
            decision_chart.columns = ['Potencial_Despacho', 'Casos']
            fig_decision = px.bar(decision_chart, x='Potencial_Despacho', y='Casos', title='Potencial de despacho ITR')
            st.plotly_chart(fig_decision, use_container_width=True)
        with g2:
            semana_chart = (
                filtrado.groupby('Semana', as_index=False)['Palets_Proyectados']
                .sum()
                .sort_values('Semana')
            )
            fig_semana = px.bar(semana_chart, x='Semana', y='Palets_Proyectados', title='Palets proyectados por semana')
            st.plotly_chart(fig_semana, use_container_width=True)

        columnas_plan = [
            'Semana', 'SKU', 'DESC_SKU', 'Tienda', 'Nombre_Tienda', 'Demanda_Relex',
            'Inv_ITR_Actual', 'Llegada_Proyectada_ITR', 'Inv_ITR_Proyectado',
            'Demanda_Ajustada', 'Stock_Seguridad', 'Capacidad_Tienda',
            'Palets_Proyectados', 'Fecha_Disponible_ITR', 'Calendario_Tienda',
            'Req_Maquila', 'Req_Lote', 'Prioridad', 'Potencial_Despacho', 'Alerta_Planeacion'
        ]
        st.dataframe(
            filtrado[columnas_plan].sort_values(['Semana', 'Potencial_Despacho', 'Tienda', 'SKU']),
            use_container_width=True
        )
        st.download_button(
            'Exportar planeación filtrada',
            to_excel(filtrado),
            'planeacion_itr_filtrada.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

elif selected == 'TMS':
    st.subheader('TMS - Gestión de Transporte')
    if df is None:
        st.warning('Carga primero el archivo Excel.')
    elif tms_df is None:
        for msg in tms_messages:
            st.info(msg)
        st.markdown('La pestaña `TMS` debe tener como mínimo estas columnas obligatorias:')
        st.dataframe(pd.DataFrame({'Columnas obligatorias': TMS_REQUIRED_COLUMNS}), use_container_width=True)
        st.download_button(
            'Descargar plantilla TMS',
            generar_plantilla_tms(),
            'plantilla_tms.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    else:
        tms_vista = cruzar_tms_abastecimiento(tms_df, df)

        estado_options = sorted([e for e in tms_vista['Estado_Operativo'].dropna().unique()])
        region_options = sorted([r for r in tms_vista['Region'].dropna().astype(str).unique() if r])
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            estado_filtro = st.multiselect('Estado operativo', estado_options, default=estado_options)
        with c2:
            region_filtro = st.multiselect('Región', region_options, default=region_options)
        with c3:
            placa_busqueda = st.text_input('Buscar placa o shipment')

        filtrado = tms_vista.copy()
        if estado_filtro:
            filtrado = filtrado[filtrado['Estado_Operativo'].isin(estado_filtro)]
        if region_filtro:
            filtrado = filtrado[filtrado['Region'].astype(str).isin(region_filtro)]
        if placa_busqueda:
            q = placa_busqueda.strip().upper()
            filtrado = filtrado[
                filtrado['Placa'].astype(str).str.upper().str.contains(q, na=False)
                | filtrado['Shipment'].astype(str).str.upper().str.contains(q, na=False)
            ]

        metrics = [
            ('Shipments', f'{filtrado["Shipment"].nunique():,}'),
            ('Vehículos', f'{filtrado["Placa"].nunique():,}'),
            ('Palets asignados', f'{filtrado["Palets_Asignados"].sum():,.0f}'),
            ('Capacidad palets', f'{filtrado["Capacidad_Palets"].sum():,.0f}'),
            ('Ocupación prom.', f'{filtrado["Ocupacion_Pct"].mean() * 100:.1f}%' if len(filtrado) else '0.0%'),
            ('Con novedad', f'{filtrado["Estado_Operativo"].eq("CON NOVEDAD").sum():,}'),
            ('Excede capacidad', f'{filtrado["Validacion_Capacidad"].eq("EXCEDE CAPACIDAD").sum():,}'),
            ('En ruta', f'{filtrado["Estado_Operativo"].eq("EN RUTA").sum():,}'),
            ('Entregado', f'{filtrado["Estado_Operativo"].eq("ENTREGADO").sum():,}'),
            ('Pendiente', f'{filtrado["Estado_Operativo"].eq("PENDIENTE").sum():,}'),
        ]
        pintar_metricas(metrics)
        st.divider()

        g1, g2 = st.columns(2)
        with g1:
            estado_chart = filtrado['Estado_Operativo'].value_counts().reset_index()
            estado_chart.columns = ['Estado_Operativo', 'Shipments']
            fig_estado = px.bar(estado_chart, x='Estado_Operativo', y='Shipments', title='Shipments por estado operativo')
            st.plotly_chart(fig_estado, use_container_width=True)
        with g2:
            vehiculo_chart = (
                filtrado.groupby('Tipo_Vehiculo', as_index=False)['Palets_Asignados']
                .sum()
                .sort_values('Palets_Asignados', ascending=False)
            )
            fig_vehiculo = px.bar(vehiculo_chart, x='Tipo_Vehiculo', y='Palets_Asignados', title='Palets por tipo de vehículo')
            st.plotly_chart(fig_vehiculo, use_container_width=True)

        columnas_tms = [
            'Shipment', 'Fecha_Despacho', 'Origen', 'Destino', 'Tienda', 'Nombre_Tienda', 'Region',
            'Placa', 'Tipo_Vehiculo', 'Transportadora', 'Capacidad_Palets', 'Palets_Asignados',
            'Ocupacion_Pct', 'Validacion_Capacidad', 'Estado', 'Estado_Operativo', 'Novedad',
            'Palets_Sugeridos_Abastecimiento', 'Diferencia_Palets'
        ]
        st.dataframe(
            filtrado[columnas_tms].sort_values(['Estado_Operativo', 'Fecha_Despacho', 'Shipment']),
            use_container_width=True
        )
        st.download_button(
            'Exportar TMS filtrado',
            to_excel(filtrado),
            'tms_filtrado.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

elif selected == 'Auditoría':
    st.subheader('Auditoría')
    if df is None:
        st.warning('Carga primero el archivo Excel.')
    else:
        columnas = ['SKU', 'Tienda', 'Decision', 'Decision_Python'] if 'Decision' in df.columns else ['SKU', 'Tienda', 'Decision_Python']
        st.dataframe(df[columnas].head(200), use_container_width=True)

elif selected == 'Reportes':
    st.subheader('Centro de Reportes')
    if df is None:
        st.warning('Carga primero el archivo Excel.')
    else:
        tab_indicadores, tab_validacion, tab_descargas = st.tabs(['Indicadores', 'Validación', 'Descargas'])

        with tab_indicadores:
            decisiones = df['Decision_Python'].value_counts().reset_index()
            decisiones.columns = ['Decision_Python', 'Casos']
            fig1 = px.bar(decisiones, x='Decision_Python', y='Casos', title='Distribución de decisiones')
            st.plotly_chart(fig1, use_container_width=True)

            top = df.groupby('Nombre Tienda').size().reset_index(name='Casos').sort_values('Casos', ascending=False).head(10)
            fig2 = px.bar(top, x='Nombre Tienda', y='Casos', title='Top tiendas con registros')
            st.plotly_chart(fig2, use_container_width=True)

        with tab_validacion:
            columnas = ['SKU', 'Tienda', 'Decision', 'Decision_Python'] if 'Decision' in df.columns else ['SKU', 'Tienda', 'Decision_Python']
            st.dataframe(df[columnas].head(300), use_container_width=True)

            if 'Decision' in df.columns:
                diferencias = df[df['Decision'].astype(str).str.strip() != df['Decision_Python'].astype(str).str.strip()]
                st.metric('Diferencias decisión archivo vs app', f'{len(diferencias):,}')
                if not diferencias.empty:
                    st.dataframe(diferencias[columnas].head(300), use_container_width=True)

        with tab_descargas:
            st.download_button('Exportar base procesada', to_excel(df), 'base_procesada.xlsx')
            if planeacion_df is not None and not planeacion_df.empty:
                st.download_button('Exportar Planeación ITR', to_excel(planeacion_df), 'planeacion_itr_procesada.xlsx')
            if tms_df is not None and not tms_df.empty:
                st.download_button('Exportar TMS procesado', to_excel(tms_df), 'tms_procesado.xlsx')

st.markdown("<div class='footer'>Sodimac Colombia | Plataforma interna de abastecimiento</div>", unsafe_allow_html=True)
