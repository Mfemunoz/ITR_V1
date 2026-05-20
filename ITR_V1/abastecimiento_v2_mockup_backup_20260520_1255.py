
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
        ['Inicio', 'Consulta Individual', 'Consulta Masiva', 'Dashboard Ejecutivo', 'Auditoría', 'Reportes'],
        icons=['house', 'search', 'upload', 'bar-chart', 'clipboard-data', 'file-earmark-arrow-down'],
        default_index=0
    )
    uploaded_file = st.file_uploader('Cargar Excel operativo', type=['xlsx'])

df = None
if uploaded_file:
    try:
        df = load_data(uploaded_file)
        st.success(f'Archivo cargado correctamente: {len(df):,} registros procesados.')
    except Exception as e:
        st.error(f'Error cargando archivo: {e}')

if selected == 'Inicio':
    st.subheader('Cockpit Ejecutivo')
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
        st.download_button('Exportar base procesada', to_excel(df), 'base_procesada.xlsx')

st.markdown("<div class='footer'>Sodimac Colombia | Plataforma interna de abastecimiento</div>", unsafe_allow_html=True)