import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title='Sistema de Abastecimiento PRO', layout='wide')

REQUIRED_COLUMNS = [
    'SKU','DESC SKU','Tienda','Nombre Tienda','Proyectado_UE','Inv_CD','Inv_ITR',
    'Stock_Seguridad','Capacidad_Tienda','Req_Maquila','Req_Lote','Lote_ITR_OK'
]

def decidir(row):
    necesidad = row['Proyectado_UE']
    stock_min = row['Stock_Seguridad']
    capacidad = row['Capacidad_Tienda']
    inv_itr = row['Inv_ITR']
    inv_cd = row['Inv_CD']

    if pd.isna(necesidad):
        return 'DATOS INCOMPLETOS'

    if necesidad <= 0:
        return 'NO PEDIDO'

    if necesidad < stock_min:
        return 'NO PEDIDO (MENOR STOCK SEGURIDAD)'

    necesidad_ajustada = min(necesidad, capacidad)

    reglas_ok = (
        str(row['Req_Maquila']).upper() != 'SI' and
        str(row['Req_Lote']).upper() != 'SI' and
        str(row['Lote_ITR_OK']).upper() == 'OK'
    )

    if not reglas_ok:
        return 'REVISAR RESTRICCIONES'

    if inv_itr >= necesidad_ajustada:
        return 'SURTIR DESDE ITR'

    if inv_cd >= necesidad_ajustada:
        return 'SURTIR DESDE CD'

    return 'SIN INVENTARIO'

@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file, sheet_name='Data Analisis', engine='openpyxl')

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f'Faltan columnas: {missing}')

    df['SKU'] = pd.to_numeric(df['SKU'], errors='coerce').fillna(0).astype(int)
    df['Tienda'] = pd.to_numeric(df['Tienda'], errors='coerce').fillna(0).astype(int)

    numeric_cols = [
        'Proyectado_UE',
        'Inv_CD',
        'Inv_ITR',
        'Stock_Seguridad',
        'Capacidad_Tienda'
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df['Decision_Python'] = df.apply(decidir, axis=1)

    return df

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Resultados')
    return output.getvalue()

if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame()

st.title('📦 Sistema Inteligente de Abastecimiento PRO')

uploaded_file = st.file_uploader('Subir archivo Excel principal (.xlsx)', type=['xlsx'])

if uploaded_file:
    try:
        df = load_data(uploaded_file)

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric('Registros', len(df))
        c2.metric('SKU únicos', df['SKU'].nunique())
        c3.metric('Tiendas', df['Tienda'].nunique())
        c4.metric('Inventario ITR', f"{df['Inv_ITR'].sum():,.0f}")
        c5.metric('Inventario CD', f"{df['Inv_CD'].sum():,.0f}")

        tab1, tab2, tab3 = st.tabs([
            'Consulta Individual',
            'Consulta Masiva',
            'Dashboard'
        ])

        with tab1:
            st.subheader('Consulta Individual')
            col1, col2 = st.columns(2)

            sku = col1.number_input('SKU', min_value=0, step=1)
            tienda = col2.number_input('Tienda', min_value=0, step=1)

            if st.button('Consultar'):
                resultado = df[(df['SKU'] == sku) & (df['Tienda'] == tienda)]

                if resultado.empty:
                    st.error('No se encontró información')
                else:
                    fila = resultado.iloc[0]
                    st.success(f"Decisión: {fila['Decision_Python']}")
                    st.dataframe(resultado[[
                        'SKU','DESC SKU','Tienda','Nombre Tienda',
                        'Proyectado_UE','Inv_ITR','Inv_CD','Decision_Python'
                    ]], use_container_width=True)

        with tab2:
            st.subheader('Consulta Masiva')
            texto = st.text_area('Formato: SKU,Tienda (uno por línea)')

            if st.button('Procesar consultas'):
                consultas = []
                for linea in texto.splitlines():
                    if ',' in linea:
                        sku_txt, tienda_txt = linea.split(',')
                        consultas.append((int(sku_txt.strip()), int(tienda_txt.strip())))

                resultados = []
                for sku_val, tienda_val in consultas:
                    temp = df[(df['SKU'] == sku_val) & (df['Tienda'] == tienda_val)]
                    if not temp.empty:
                        resultados.append(temp)

                if resultados:
                    final = pd.concat(resultados)
                    st.dataframe(final, use_container_width=True)
                    st.download_button(
                        'Descargar Excel',
                        to_excel(final),
                        file_name='resultado_abastecimiento.xlsx'
                    )
                else:
                    st.warning('Sin resultados')

        with tab3:
            st.subheader('Dashboard')

            fig = px.pie(df, names='Decision_Python', title='Distribución de decisiones')
            st.plotly_chart(fig, use_container_width=True)

            top = df.groupby('Nombre Tienda').size().reset_index(name='Total')
            top = top.sort_values('Total', ascending=False).head(10)

            fig2 = px.bar(top, x='Nombre Tienda', y='Total', title='Top tiendas')
            st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f'Error: {e}')
else:
    st.info('Carga tu archivo Excel para comenzar')