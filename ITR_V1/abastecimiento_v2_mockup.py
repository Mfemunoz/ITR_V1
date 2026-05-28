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
    page_title='Sodimac Colombia | Desarrollo Logístico',
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
SECONDARY_LOGO_PATH = BASE_DIR / 'assets' / 'logo_desarrollo_logistico.png'
logo = Image.open(LOGO_PATH) if LOGO_PATH.exists() else None
secondary_logo = Image.open(SECONDARY_LOGO_PATH) if SECONDARY_LOGO_PATH.exists() else None
SODIMAC_COLORS = ['#0072bc', '#ed1c24', '#ffdd00', '#004b8d', '#6b7280']
STORE_COORDS = {
    10: (4.7488, -74.0949), 11: (4.7240, -74.0360), 12: (4.8610, -74.0580),
    30: (3.3900, -76.5400), 31: (3.4700, -76.5200),
    40: (6.2100, -75.5700), 41: (6.2530, -75.5900),
    50: (11.0040, -74.8060), 53: (10.9630, -74.7960),
    54: (10.4230, -75.5250), 57: (11.2408, -74.1990),
    59: (10.3910, -75.4790), 90: (7.8939, -72.5078)
}
ITR_POINTS = pd.DataFrame([
    {'Punto': 'ITR Buenaventura', 'Tipo_Punto': 'ITR', 'Latitud': 3.8801, 'Longitud': -77.0312, 'Casos': 18},
    {'Punto': 'ITR Cartagena - Pasacaballos', 'Tipo_Punto': 'ITR', 'Latitud': 10.3030, 'Longitud': -75.5060, 'Casos': 18},
])

st.markdown('''
<style>
:root {
    --sodimac-red:#ed1c24;
    --sodimac-blue:#0072bc;
    --sodimac-blue-dark:#004b8d;
    --sodimac-yellow:#ffdd00;
    --sodimac-white:#ffffff;
    --sodimac-ink:#1f2937;
    --sodimac-muted:#6b7280;
    --sodimac-bg:#f5f7fb;
    --sodimac-line:#dbeafe;
}
.stApp {background:var(--sodimac-bg);}
.main {background-color:var(--sodimac-bg);}
.block-container {padding-top:1.1rem;padding-left:2rem;padding-right:2rem;max-width:1500px;}
.metric-box {background:var(--sodimac-white);padding:1rem;border-radius:8px;box-shadow:0 4px 14px rgba(0,75,141,0.10);text-align:center;min-height:96px;border-top:4px solid var(--sodimac-blue);}
.metric-title {color:var(--sodimac-muted);font-size:13px;font-weight:700;}
.metric-value {color:var(--sodimac-blue-dark);font-size:26px;font-weight:bold;line-height:1.2;}
.status-card {background:var(--sodimac-blue-dark);color:white;padding:14px;border-radius:8px;text-align:center;border-bottom:4px solid var(--sodimac-yellow);}
.footer {text-align:center;color:var(--sodimac-muted);padding-top:20px;font-size:13px;}
div[data-testid="stFileUploader"] small {display:none!important;}
div[data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] p {display:none!important;}
.upload-formats {color:var(--sodimac-blue-dark);font-size:12px;font-weight:700;margin-top:-10px;margin-bottom:8px;}
section[data-testid="stSidebar"] {background:linear-gradient(180deg, #ffffff 0%, #eef6fc 100%);border-right:1px solid var(--sodimac-line);}
section[data-testid="stSidebar"] > div {padding-left:0.85rem;padding-right:0.85rem;}
div[data-testid="stFileUploader"] section {border:1px dashed var(--sodimac-blue);background:#ffffff;border-radius:8px;}
.stButton > button, .stDownloadButton > button {border-radius:8px;border:1px solid var(--sodimac-blue);color:var(--sodimac-blue-dark);font-weight:700;}
.stButton > button:hover, .stDownloadButton > button:hover {border-color:var(--sodimac-red);color:var(--sodimac-red);}
div[data-testid="stTabs"] button[aria-selected="true"] {color:var(--sodimac-blue-dark);}
span[data-baseweb="tag"] {background-color:var(--sodimac-blue-dark)!important;border-radius:6px!important;}
span[data-baseweb="tag"] span {color:white!important;}
.top-band {background:white;border-left:6px solid var(--sodimac-yellow);padding:14px 18px 14px 18px;border-radius:8px;box-shadow:0 4px 14px rgba(0,75,141,0.08);min-height:112px;}
.app-title {color:var(--sodimac-red)!important;margin-bottom:0;font-size:26px;font-weight:800;letter-spacing:0;white-space:nowrap;line-height:1.1;}
.app-subtitle {color:var(--sodimac-blue-dark);margin-top:0.35rem;font-size:20px;font-weight:700;}
.status-wrap {padding-top:4px;}
.sidebar-title {display:flex;align-items:center;gap:10px;font-size:21px;color:var(--sodimac-ink);line-height:1.15;margin:12px 0 12px 0;padding-bottom:12px;border-bottom:1px solid #cbd5e1;}
.empty-state {background:white;border:1px solid #dbeafe;border-left:6px solid var(--sodimac-blue);border-radius:8px;padding:18px 20px;color:var(--sodimac-blue-dark);box-shadow:0 4px 14px rgba(0,75,141,0.06);}
.empty-title {font-size:18px;font-weight:800;margin-bottom:6px;}
.empty-text {font-size:14px;color:var(--sodimac-muted);}
.login-box {background:white;border:1px solid #dbeafe;border-radius:8px;padding:12px;margin:10px 0 14px 0;}
.login-title {font-weight:800;color:var(--sodimac-blue-dark);font-size:15px;margin-bottom:4px;}
.login-note {font-size:12px;color:var(--sodimac-muted);line-height:1.25;}
hr {border-color:var(--sodimac-line);}
</style>
''', unsafe_allow_html=True)


def normalizar_si_no(valor):
    return str(valor).strip().upper() in ['SI', 'SÍ', 'YES', 'Y', 'TRUE', '1']


def reset_excel_source(source):
    if hasattr(source, 'seek'):
        source.seek(0)
    return source


def source_name(source):
    if isinstance(source, str):
        return source.split('?')[0].lower()
    return getattr(source, 'name', '').lower()


def source_is_csv(source):
    return source_name(source).endswith('.csv')


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
    if source_is_csv(excel_source):
        df = pd.read_csv(excel_source, sep=None, engine='python', encoding='utf-8-sig')
    else:
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
    if source_is_csv(excel_source):
        return None, ['La fuente CSV solo alimenta Ejecución Abastecimiento. Para TMS usa un XLSX con pestaña TMS.']
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
    if source_is_csv(excel_source):
        return None, ['La fuente CSV solo alimenta Ejecución Abastecimiento. Para Planeación ITR usa un XLSX con pestaña Planeacion_ITR.']
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


def aplicar_tema_grafico(fig):
    fig.update_layout(
        template='plotly_white',
        colorway=SODIMAC_COLORS,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#1f2937'),
        title=dict(font=dict(color='#004b8d', size=18)),
        margin=dict(l=24, r=24, t=60, b=40)
    )
    fig.update_xaxes(showgrid=False, linecolor='#dbeafe')
    fig.update_yaxes(gridcolor='#e5e7eb', linecolor='#dbeafe')
    return fig


def parse_int_list(text):
    values = []
    for part in text.replace(';', ',').replace('\n', ',').split(','):
        part = part.strip()
        if not part:
            continue
        try:
            values.append(int(float(part)))
        except ValueError:
            pass
    return values


def filtrar_por_texto_numerico(df_filtrado, column, text):
    values = parse_int_list(text)
    if values:
        return df_filtrado[df_filtrado[column].isin(values)]
    return df_filtrado


def preparar_mapa_tiendas(df_base):
    mapa = (
        df_base.groupby(['Tienda', 'Nombre Tienda'], as_index=False)
        .size()
        .rename(columns={'size': 'Casos'})
        .sort_values('Casos', ascending=False)
        .head(10)
    )
    mapa['Latitud'] = mapa['Tienda'].map(lambda t: STORE_COORDS.get(int(t), (None, None))[0] if pd.notna(t) else None)
    mapa['Longitud'] = mapa['Tienda'].map(lambda t: STORE_COORDS.get(int(t), (None, None))[1] if pd.notna(t) else None)
    mapa['Punto'] = mapa['Tienda'].astype(str) + ' - ' + mapa['Nombre Tienda'].astype(str)
    mapa['Tipo_Punto'] = 'Tienda'
    return mapa


if 'uploader_version' not in st.session_state:
    st.session_state.uploader_version = 0
if 'url_version' not in st.session_state:
    st.session_state.url_version = 0
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ''


col_title, col_status = st.columns([4.1, 1.6])
with col_title:
    st.markdown(
        "<div class='top-band'>"
        "<h1 class='app-title'>SODIMAC COLOMBIA - DESARROLLO LOGISTICO</h1>"
        "<div class='app-subtitle'>Centro de Control de Abastecimiento</div>"
        "</div>",
        unsafe_allow_html=True
    )
with col_status:
    st.markdown("<div class='status-wrap'>", unsafe_allow_html=True)
    if secondary_logo:
        st.image(secondary_logo, width=110)
    usuario_activo = st.session_state.user_email if st.session_state.authenticated else 'Sin sesión'
    st.markdown(
        f"<div class='status-card'><b>Usuario:</b> {usuario_activo}<br>"
        f"<b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br>"
        "<b>Ambiente:</b> PRODUCCIÓN</div>",
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

with st.sidebar:
    if logo:
        st.image(logo, width=150)
    st.markdown("<div class='sidebar-title'>▤<span>Centro de Control</span></div>", unsafe_allow_html=True)
    selected = option_menu(
        None,
        ['Planeación ITR', 'Ejecución Abastecimiento', 'TMS', 'Consultas', 'Reportes'],
        icons=['calendar-week', 'box-seam', 'truck', 'search', 'file-earmark-arrow-down'],
        default_index=0,
        styles={
            'container': {'padding': '0!important', 'background-color': 'transparent', 'width': '100%'},
            'icon': {'color': '#004b8d', 'font-size': '18px'},
            'nav-link': {
                'font-size': '14px',
                'font-weight': '500',
                'text-align': 'left',
                'margin': '3px 0',
                'padding': '11px 12px',
                'border-radius': '6px',
                '--hover-color': '#eef6fc',
            },
            'nav-link-selected': {'background-color': '#004b8d', 'color': 'white', 'font-weight': '700'},
        }
    )
    uploaded_file = None
    excel_source = None

    st.markdown("<div class='login-box'><div class='login-title'>Acceso plataforma</div><div class='login-note'>Ingresa con correo corporativo Homecenter para habilitar carga de datos y reportes.</div></div>", unsafe_allow_html=True)
    if not st.session_state.authenticated:
        login_email = st.text_input('Correo', placeholder='usuario@homecenter.co', key='login_email')
        login_password = st.text_input('Clave', type='password', key='login_password')
        if st.button('Ingresar', use_container_width=True):
            email_ok = login_email.strip().lower().endswith('@homecenter.co')
            password_ok = login_password == '12345678'
            if email_ok and password_ok:
                st.session_state.authenticated = True
                st.session_state.user_email = login_email.strip().lower()
                st.rerun()
            else:
                st.error('Correo o clave inválidos para el ambiente de prueba.')
    else:
        st.success(f'Sesión activa: {st.session_state.user_email}')
        if st.button('Cerrar sesión', use_container_width=True):
            st.cache_data.clear()
            st.session_state.authenticated = False
            st.session_state.user_email = ''
            st.session_state.uploader_version += 1
            st.session_state.url_version += 1
            st.rerun()

        fuente_datos = st.radio('Fuente de datos', ['Archivo local', 'URL en línea'], horizontal=True)
        if fuente_datos == 'Archivo local':
            uploaded_file = st.file_uploader(
                'Cargar archivo operativo',
                type=['xlsx', 'csv'],
                key=f'archivo_operativo_{st.session_state.uploader_version}'
            )
            excel_source = uploaded_file
            st.markdown("<div class='upload-formats'>XLSX, CSV</div>", unsafe_allow_html=True)
        else:
            excel_url = st.text_input(
                'URL del archivo',
                placeholder='https://.../archivo.xlsx, archivo.csv o enlace compartido de Google Sheets/Drive',
                key=f'online_url_{st.session_state.url_version}'
            )
            if excel_url:
                excel_source = normalizar_url_excel(excel_url)
                st.caption('La URL debe permitir descarga directa o acceso público/autorizado desde el servidor.')
        if excel_source:
            if st.button('X Quitar archivo cargado', use_container_width=True):
                st.cache_data.clear()
                st.session_state.uploader_version += 1
                st.session_state.url_version += 1
                st.rerun()

df = None
tms_df = None
tms_messages = []
planeacion_df = None
planeacion_messages = []
if excel_source and st.session_state.authenticated:
    try:
        df = load_data(excel_source)
        planeacion_df, planeacion_messages = load_planeacion_itr(excel_source)
        tms_df, tms_messages = load_tms_data(excel_source)
        st.success(f'Archivo cargado correctamente: {len(df):,} registros procesados.')
        if source_is_csv(excel_source):
            st.info('CSV cargado como Data Analisis. Planeación ITR y TMS requieren un XLSX con sus pestañas respectivas.')
    except Exception as e:
        st.error(f'Error cargando archivo: {e}')

if not st.session_state.authenticated:
    st.markdown(
        "<div class='empty-state'><div class='empty-title'>Acceso requerido</div>"
        "<div class='empty-text'>Inicia sesión con un correo terminado en @homecenter.co para habilitar el importador, consultar datos y visualizar reportes.</div></div>",
        unsafe_allow_html=True
    )
elif selected == 'Ejecución Abastecimiento':
    st.subheader('Ejecución Abastecimiento')
    if df is None:
        st.markdown(
            "<div class='empty-state'><div class='empty-title'>Carga un archivo operativo para iniciar</div>"
            "<div class='empty-text'>Usa el panel izquierdo para cargar un XLSX o CSV. El tablero activará filtros, métricas y consulta de SKU una vez procesado el archivo.</div></div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown('Filtros operativos')
        tienda_options = (
            df[['Tienda', 'Nombre Tienda']]
            .drop_duplicates()
            .sort_values(['Nombre Tienda', 'Tienda'])
            .assign(label=lambda x: x['Tienda'].astype(str) + ' - ' + x['Nombre Tienda'].astype(str))
        )
        decision_options = sorted(df['Decision_Python'].dropna().unique())
        calendar_options = sorted([c for c in df['CALENDAR'].dropna().astype(str).unique() if c])
        f1, f2, f3, f4 = st.columns([1.3, 1.2, 1.1, 1.0])
        with f1:
            tiendas_sel = st.multiselect('Tiendas', tienda_options['label'].tolist())
        with f2:
            decisiones_sel = st.multiselect('Decisión', decision_options)
        with f3:
            sku_text = st.text_input('SKU específicos', placeholder='132239, 274734')
        with f4:
            calendarios_sel = st.multiselect('Calendario', calendar_options)

        filtrado_ejecucion = df.copy()
        if tiendas_sel:
            tienda_ids = [int(t.split(' - ')[0]) for t in tiendas_sel]
            filtrado_ejecucion = filtrado_ejecucion[filtrado_ejecucion['Tienda'].isin(tienda_ids)]
        if decisiones_sel:
            filtrado_ejecucion = filtrado_ejecucion[filtrado_ejecucion['Decision_Python'].isin(decisiones_sel)]
        if calendarios_sel:
            filtrado_ejecucion = filtrado_ejecucion[filtrado_ejecucion['CALENDAR'].astype(str).isin(calendarios_sel)]
        filtrado_ejecucion = filtrar_por_texto_numerico(filtrado_ejecucion, 'SKU', sku_text)

        metrics = [
            ('Registros filtrados', f'{len(filtrado_ejecucion):,}'),
            ('SKU evaluados', f'{filtrado_ejecucion["SKU"].nunique():,}'),
            ('Tiendas activas', f'{filtrado_ejecucion["Tienda"].nunique():,}'),
            ('Reposición ITR', f'{filtrado_ejecucion["Decision_Python"].str.contains("SURTIR DESDE ITR", na=False).sum():,}'),
            ('Reposición CD', f'{filtrado_ejecucion["Decision_Python"].str.contains("SURTIR DESDE CD", na=False).sum():,}'),
            ('Sin inventario', f'{filtrado_ejecucion["Decision_Python"].eq("SIN INVENTARIO SUFICIENTE").sum():,}'),
            ('Inv Total ITR', f'{filtrado_ejecucion["Inv_ITR"].sum():,.0f}'),
            ('Inv Total CD', f'{filtrado_ejecucion["Inv_CD"].sum():,.0f}'),
            ('Palets sugeridos', f'{filtrado_ejecucion["Proyectado_Palets"].sum():,.0f}'),
            ('LT Prom ITR', f'{filtrado_ejecucion["LT_ITR"].mean():.1f}' if len(filtrado_ejecucion) else '0.0'),
        ]
        pintar_metricas(metrics)
        st.divider()
        if filtrado_ejecucion.empty:
            st.warning('No hay registros para los filtros seleccionados.')
        else:
            decisiones = filtrado_ejecucion['Decision_Python'].value_counts().reset_index()
            decisiones.columns = ['Decision_Python', 'Casos']
            fig_dec = aplicar_tema_grafico(px.bar(decisiones, x='Decision_Python', y='Casos', title='Decisiones filtradas', color='Decision_Python'))
            st.plotly_chart(fig_dec, use_container_width=True)
            st.caption(f'Mostrando hasta 500 registros de {len(filtrado_ejecucion):,}. Usa los filtros o descarga el resultado completo.')
            st.dataframe(
                filtrado_ejecucion[['SKU', 'DESC SKU', 'Tienda', 'Nombre Tienda', 'Proyectado_Palets', 'LT_ITR', 'LT_CD', 'CALENDAR', 'Comparativo_LT', 'Decision_Python']]
                .sort_values(['Nombre Tienda', 'SKU'])
                .head(500),
                use_container_width=True
            )
            st.download_button('Exportar ejecución filtrada', to_excel(filtrado_ejecucion), 'ejecucion_abastecimiento_filtrada.xlsx')

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
        fig1 = aplicar_tema_grafico(px.bar(decisiones, x='Decision_Python', y='Casos', title='Distribución de decisiones', color='Decision_Python'))
        st.plotly_chart(fig1, use_container_width=True)

        top = df.groupby('Nombre Tienda').size().reset_index(name='Casos').sort_values('Casos', ascending=False).head(10)
        fig2 = aplicar_tema_grafico(px.bar(top, x='Nombre Tienda', y='Casos', title='Top tiendas con registros', color_discrete_sequence=['#0072bc']))
        st.plotly_chart(fig2, use_container_width=True)

elif selected == 'Planeación ITR':
    st.subheader('Planeación ITR - Potencial de Despacho')
    if df is None:
        st.markdown(
            "<div class='empty-state'><div class='empty-title'>Planeación pendiente de archivo</div>"
            "<div class='empty-text'>Carga un XLSX con la hoja Planeacion_ITR para activar potencial de despacho, alertas y gráficos filtrables.</div></div>",
            unsafe_allow_html=True
        )
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
        alerta_options = sorted([a for a in plan['Alerta_Planeacion'].dropna().astype(str).unique() if a])
        tienda_plan_options = (
            plan[['Tienda', 'Nombre_Tienda']]
            .drop_duplicates()
            .sort_values(['Nombre_Tienda', 'Tienda'])
            .assign(label=lambda x: x['Tienda'].astype(str) + ' - ' + x['Nombre_Tienda'].astype(str))
        )

        f1, f2, f3 = st.columns(3)
        with f1:
            semana_filtro = st.multiselect('Semana', semana_options, default=semana_options)
        with f2:
            decision_filtro = st.multiselect('Potencial despacho', decision_options, default=decision_options)
        with f3:
            prioridad_filtro = st.multiselect('Prioridad', prioridad_options, default=prioridad_options)
        f4, f5, f6 = st.columns(3)
        with f4:
            tienda_plan_filtro = st.multiselect('Tiendas', tienda_plan_options['label'].tolist())
        with f5:
            alerta_filtro = st.multiselect('Alertas', alerta_options, default=alerta_options)
        with f6:
            sku_plan_text = st.text_input('SKU específicos', placeholder='132239, 274734', key='sku_planeacion')

        filtrado = plan.copy()
        if semana_filtro:
            filtrado = filtrado[filtrado['Semana'].astype(str).isin(semana_filtro)]
        if decision_filtro:
            filtrado = filtrado[filtrado['Potencial_Despacho'].isin(decision_filtro)]
        if prioridad_filtro:
            filtrado = filtrado[filtrado['Prioridad'].astype(str).isin(prioridad_filtro)]
        if tienda_plan_filtro:
            tienda_plan_ids = [int(t.split(' - ')[0]) for t in tienda_plan_filtro]
            filtrado = filtrado[filtrado['Tienda'].isin(tienda_plan_ids)]
        if alerta_filtro:
            filtrado = filtrado[filtrado['Alerta_Planeacion'].astype(str).isin(alerta_filtro)]
        filtrado = filtrar_por_texto_numerico(filtrado, 'SKU', sku_plan_text)

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
            fig_decision = aplicar_tema_grafico(px.bar(decision_chart, x='Potencial_Despacho', y='Casos', title='Potencial de despacho ITR', color='Potencial_Despacho'))
            st.plotly_chart(fig_decision, use_container_width=True)
        with g2:
            semana_chart = (
                filtrado.groupby('Semana', as_index=False)['Palets_Proyectados']
                .sum()
                .sort_values('Semana')
            )
            fig_semana = aplicar_tema_grafico(px.bar(semana_chart, x='Semana', y='Palets_Proyectados', title='Palets proyectados por semana', color_discrete_sequence=['#0072bc']))
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
            fig_estado = aplicar_tema_grafico(px.bar(estado_chart, x='Estado_Operativo', y='Shipments', title='Shipments por estado operativo', color='Estado_Operativo'))
            st.plotly_chart(fig_estado, use_container_width=True)
        with g2:
            vehiculo_chart = (
                filtrado.groupby('Tipo_Vehiculo', as_index=False)['Palets_Asignados']
                .sum()
                .sort_values('Palets_Asignados', ascending=False)
            )
            fig_vehiculo = aplicar_tema_grafico(px.bar(vehiculo_chart, x='Tipo_Vehiculo', y='Palets_Asignados', title='Palets por tipo de vehículo', color_discrete_sequence=['#004b8d']))
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
            st.markdown('Filtros de indicadores')
            tienda_reporte_options = (
                df[['Tienda', 'Nombre Tienda']]
                .drop_duplicates()
                .sort_values(['Nombre Tienda', 'Tienda'])
                .assign(label=lambda x: x['Tienda'].astype(str) + ' - ' + x['Nombre Tienda'].astype(str))
            )
            decision_reporte_options = sorted(df['Decision_Python'].dropna().unique())
            calendario_reporte_options = sorted([c for c in df['CALENDAR'].dropna().astype(str).unique() if c])
            r1, r2, r3, r4 = st.columns([1.3, 1.2, 1.1, 1.0])
            with r1:
                tiendas_reporte_sel = st.multiselect('Tiendas', tienda_reporte_options['label'].tolist(), key='reporte_tiendas')
            with r2:
                decisiones_reporte_sel = st.multiselect('Decisión', decision_reporte_options, default=decision_reporte_options, key='reporte_decision')
            with r3:
                calendarios_reporte_sel = st.multiselect('Calendario', calendario_reporte_options, key='reporte_calendario')
            with r4:
                sku_reporte_text = st.text_input('SKU específicos', placeholder='132239, 274734', key='reporte_sku')

            df_reportes = df.copy()
            if tiendas_reporte_sel:
                tienda_reporte_ids = [int(t.split(' - ')[0]) for t in tiendas_reporte_sel]
                df_reportes = df_reportes[df_reportes['Tienda'].isin(tienda_reporte_ids)]
            if decisiones_reporte_sel:
                df_reportes = df_reportes[df_reportes['Decision_Python'].isin(decisiones_reporte_sel)]
            if calendarios_reporte_sel:
                df_reportes = df_reportes[df_reportes['CALENDAR'].astype(str).isin(calendarios_reporte_sel)]
            df_reportes = filtrar_por_texto_numerico(df_reportes, 'SKU', sku_reporte_text)

            if df_reportes.empty:
                st.warning('No hay registros para los filtros seleccionados.')
                st.stop()

            c1, c2, c3, c4 = st.columns(4)
            c1.metric('Registros', f'{len(df_reportes):,}')
            c2.metric('Tiendas', f'{df_reportes["Tienda"].nunique():,}')
            c3.metric('SKU', f'{df_reportes["SKU"].nunique():,}')
            c4.metric('Palets', f'{df_reportes["Proyectado_Palets"].sum():,.0f}')

            decisiones = df_reportes['Decision_Python'].value_counts().reset_index()
            decisiones.columns = ['Decision_Python', 'Casos']
            fig1 = aplicar_tema_grafico(px.bar(decisiones, x='Decision_Python', y='Casos', title='Distribución de decisiones', color='Decision_Python'))
            st.plotly_chart(fig1, use_container_width=True)

            mapa_tiendas = preparar_mapa_tiendas(df_reportes)
            mapa_ok = mapa_tiendas.dropna(subset=['Latitud', 'Longitud'])
            st.markdown('Top 10 tiendas filtradas en mapa interactivo')
            if mapa_ok.empty:
                st.warning('No hay coordenadas disponibles para las tiendas del top 10.')
            else:
                puntos_itr = ITR_POINTS.copy()
                mapa_plot = pd.concat([
                    mapa_ok[['Punto', 'Tipo_Punto', 'Latitud', 'Longitud', 'Casos']],
                    puntos_itr[['Punto', 'Tipo_Punto', 'Latitud', 'Longitud', 'Casos']]
                ], ignore_index=True)
                fig_mapa = px.scatter_mapbox(
                    mapa_plot,
                    lat='Latitud',
                    lon='Longitud',
                    size='Casos',
                    color='Tipo_Punto',
                    hover_name='Punto',
                    hover_data={'Tipo_Punto': True, 'Casos': True, 'Latitud': False, 'Longitud': False},
                    title='Top tiendas e ITR de referencia',
                    color_discrete_map={'Tienda': '#0072bc', 'ITR': '#ed1c24'},
                )
                fig_mapa.update_layout(
                    mapbox_style='open-street-map',
                    mapbox=dict(center=dict(lat=5.5, lon=-74.5), zoom=4.6),
                    paper_bgcolor='white',
                    plot_bgcolor='white',
                    title=dict(font=dict(color='#004b8d', size=18)),
                    margin=dict(l=10, r=10, t=55, b=10),
                    height=560,
                )
                st.plotly_chart(fig_mapa, use_container_width=True)
                st.caption('Mapa basado en OpenStreetMap. Los puntos rojos son ITR de referencia: Buenaventura y Cartagena/Pasacaballos.')
            pendientes_coord = mapa_tiendas[mapa_tiendas['Latitud'].isna() | mapa_tiendas['Longitud'].isna()]
            if not pendientes_coord.empty:
                st.caption('Tiendas sin coordenadas configuradas')
                st.dataframe(pendientes_coord[['Tienda', 'Nombre Tienda', 'Casos']], use_container_width=True)

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
