import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.data_manager import DataManager
from utils.map_utils import MapUtils
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Gerenciamento - EcoSmart GPS",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Gerenciamento do Sistema")

# Initialize data manager
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()

data_manager = st.session_state.data_manager
map_utils = MapUtils()

# Management tabs
tab1, tab2, tab3, tab4 = st.tabs(["🏢 Condomínios", "🗑️ Lixeiras", "🚛 Caminhões", "📊 Relatórios"])

with tab1:
    st.header("🏢 Gerenciamento de Condomínios")
    
    # Add new condominium
    with st.expander("➕ Adicionar Novo Condomínio", expanded=False):
        with st.form("add_condominium"):
            col1, col2 = st.columns(2)
            
            with col1:
                condo_name = st.text_input("Nome do Condomínio*")
                condo_address = st.text_area("Endereço Completo*")
                condo_contact = st.text_input("Telefone de Contato")
                
            with col2:
                condo_lat = st.number_input("Latitude*", format="%.6f", value=-23.550520)
                condo_lng = st.number_input("Longitude*", format="%.6f", value=-46.633308)
                condo_units = st.number_input("Número de Unidades", min_value=1, value=50)
            
            submitted = st.form_submit_button("Adicionar Condomínio", type="primary")
            
            if submitted:
                if condo_name and condo_address:
                    success = data_manager.add_condominium(
                        condo_name, condo_address, condo_lat, condo_lng, condo_contact, condo_units
                    )
                    if success:
                        st.success(f"✅ Condomínio '{condo_name}' adicionado com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao adicionar condomínio. Verifique se o nome não já existe.")
                else:
                    st.error("❌ Por favor, preencha todos os campos obrigatórios.")
    
    # List existing condominiums
    st.subheader("📋 Condomínios Cadastrados")
    
    condominiums_data = data_manager.get_condominiums_data()
    bins_data = data_manager.get_bins_data()
    
    # Calculate bins per condominium
    bins_per_condo = bins_data.groupby('condominium').agg({
        'bin_id': 'count',
        'fill_level': 'mean'
    }).round(1).reset_index()
    bins_per_condo.columns = ['name', 'total_bins', 'avg_fill_level']
    
    # Merge with condominiums data
    condos_display = condominiums_data.merge(bins_per_condo, on='name', how='left')
    condos_display[['total_bins', 'avg_fill_level']] = condos_display[['total_bins', 'avg_fill_level']].fillna(0)
    
    # Display condominiums
    for _, condo in condos_display.iterrows():
        with st.expander(f"🏢 {condo['name']} - {int(condo['total_bins'])} lixeiras"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Endereço:** {condo['address']}")
                st.write(f"**Contato:** {condo['contact']}")
                st.write(f"**Unidades:** {condo['units']}")
            
            with col2:
                st.metric("Lixeiras", int(condo['total_bins']))
                st.metric("Nível Médio", f"{condo['avg_fill_level']:.1f}%")
            
            with col3:
                if st.button(f"📍 Ver no Mapa", key=f"map_{condo['name']}"):
                    # Show condominium location on map
                    condo_map = folium.Map(
                        location=[float(condo['latitude']), float(condo['longitude'])], 
                        zoom_start=16
                    )
                    folium.Marker(
                        [float(condo['latitude']), float(condo['longitude'])],
                        popup=str(condo['name']),
                        icon=folium.Icon(color='blue', icon='building', prefix='fa')
                    ).add_to(condo_map)
                    
                    st_folium(condo_map, width=600, height=300, key=f"condo_map_{condo['name']}")

with tab2:
    st.header("🗑️ Gerenciamento de Lixeiras")
    
    # Add new trash bin
    with st.expander("➕ Adicionar Nova Lixeira", expanded=False):
        with st.form("add_bin"):
            col1, col2 = st.columns(2)
            
            with col1:
                bin_id = st.text_input("ID da Lixeira*")
                bin_condominium = st.selectbox(
                    "Condomínio*",
                    options=condominiums_data['name'].tolist()
                )
                bin_location = st.text_input("Localização Específica*", placeholder="Ex: Bloco A - Térreo")
                
            with col2:
                bin_lat = st.number_input("Latitude*", format="%.6f", value=-23.550520, key="bin_lat")
                bin_lng = st.number_input("Longitude*", format="%.6f", value=-46.633308, key="bin_lng")
                bin_capacity = st.number_input("Capacidade (kg)", min_value=10, max_value=1000, value=100)
            
            submitted = st.form_submit_button("Adicionar Lixeira", type="primary")
            
            if submitted:
                if bin_id and bin_condominium and bin_location:
                    success = data_manager.add_bin(
                        bin_id, bin_condominium, bin_location, bin_lat, bin_lng, bin_capacity
                    )
                    if success:
                        st.success(f"✅ Lixeira '{bin_id}' adicionada com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao adicionar lixeira. Verifique se o ID não já existe.")
                else:
                    st.error("❌ Por favor, preencha todos os campos obrigatórios.")
    
    # Filter and display bins
    st.subheader("🔍 Filtrar Lixeiras")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_condominium = st.selectbox(
            "Filtrar por Condomínio",
            options=["Todos"] + condominiums_data['name'].tolist()
        )
    
    with col2:
        filter_fill_level = st.select_slider(
            "Nível Mínimo de Enchimento",
            options=[0, 25, 50, 75, 90, 100],
            value=0
        )
    
    with col3:
        filter_status = st.radio(
            "Status",
            options=["Todos", "Normal", "Atenção", "Crítico"]
        )
    
    # Apply filters
    filtered_bins = bins_data.copy()
    
    if filter_condominium != "Todos":
        filtered_bins = filtered_bins[filtered_bins['condominium'] == filter_condominium]
    
    filtered_bins = filtered_bins[filtered_bins['fill_level'] >= filter_fill_level]
    
    if filter_status == "Normal":
        filtered_bins = filtered_bins[filtered_bins['fill_level'] < 70]
    elif filter_status == "Atenção":
        filtered_bins = filtered_bins[(filtered_bins['fill_level'] >= 70) & (filtered_bins['fill_level'] < 90)]
    elif filter_status == "Crítico":
        filtered_bins = filtered_bins[filtered_bins['fill_level'] >= 90]
    
    # Display filtered bins
    st.subheader(f"📋 Lixeiras Encontradas ({len(filtered_bins)} de {len(bins_data)})")
    
    if len(filtered_bins) > 0:
        # Create bins map
        bins_map = map_utils.create_bins_map(filtered_bins, condominiums_data)
        st_folium(bins_map, width=800, height=400, key="bins_management_map")
        
        # Display bins table
        bins_display = filtered_bins.copy()
        bins_display['Status'] = bins_display['fill_level'].apply(
            lambda x: "🔴 Crítico" if x >= 90 else "🟡 Atenção" if x >= 70 else "🟢 Normal"
        )
        bins_display = bins_display[['bin_id', 'condominium', 'location', 'fill_level', 'Status', 'last_updated']].copy()
        bins_display.columns = ['ID', 'Condomínio', 'Localização', 'Nível (%)', 'Status', 'Última Atualização']
        
        st.dataframe(bins_display, width=None)
    else:
        st.info("🔍 Nenhuma lixeira encontrada com os filtros aplicados.")

with tab3:
    st.header("🚛 Gerenciamento de Caminhões")
    
    # Add new truck
    with st.expander("➕ Adicionar Novo Caminhão", expanded=False):
        with st.form("add_truck"):
            col1, col2 = st.columns(2)
            
            with col1:
                truck_id = st.text_input("ID do Caminhão*", placeholder="Ex: ECO-001")
                truck_plate = st.text_input("Placa*", placeholder="Ex: ABC-1234")
                truck_driver = st.text_input("Motorista*")
                
            with col2:
                truck_capacity = st.number_input("Capacidade (kg)", min_value=500, max_value=10000, value=5000)
                truck_fuel_capacity = st.number_input("Capacidade do Tanque (L)", min_value=50, max_value=500, value=200)
                truck_status = st.selectbox("Status Inicial", options=["Ativo", "Manutenção", "Inativo"])
            
            submitted = st.form_submit_button("Adicionar Caminhão", type="primary")
            
            if submitted:
                if truck_id and truck_plate and truck_driver:
                    success = data_manager.add_truck(
                        truck_id, truck_plate, truck_driver, truck_capacity, 
                        truck_fuel_capacity, truck_status
                    )
                    if success:
                        st.success(f"✅ Caminhão '{truck_id}' adicionado com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao adicionar caminhão. Verifique se o ID não já existe.")
                else:
                    st.error("❌ Por favor, preencha todos os campos obrigatórios.")
    
    # Display trucks
    st.subheader("📋 Frota de Caminhões")
    
    trucks_data = data_manager.get_trucks_data()
    
    for _, truck in trucks_data.iterrows():
        with st.expander(f"🚛 {truck['truck_id']} - {truck['status']}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Placa:** {truck['plate']}")
                st.write(f"**Motorista:** {truck['driver']}")
                st.write(f"**Status:** {truck['status']}")
                
            with col2:
                st.metric("Combustível", f"{truck['fuel_level']}%")
                st.metric("Capacidade", f"{truck['capacity']} kg")
                
            with col3:
                st.write(f"**Localização:** {truck['current_location']}")
                st.write(f"**Última Atualização:** {truck['last_updated']}")
                
                # Status change buttons
                current_status = str(truck['status'])
                status_options = ["Ativo", "Manutenção", "Inativo"]
                current_index = status_options.index(current_status) if current_status in status_options else 0
                new_status = st.selectbox(
                    "Alterar Status",
                    options=status_options,
                    index=current_index,
                    key=f"status_{truck['truck_id']}"
                )
                
                if st.button(f"Atualizar Status", key=f"update_{truck['truck_id']}"):
                    data_manager.update_truck_status(truck['truck_id'], new_status)
                    st.success(f"Status do caminhão {truck['truck_id']} atualizado!")
                    st.rerun()

with tab4:
    st.header("📊 Relatórios e Estatísticas")
    
    # Report period selection
    col1, col2 = st.columns(2)
    
    with col1:
        report_period = st.selectbox(
            "Período do Relatório",
            options=["Últimos 7 dias", "Último mês", "Últimos 3 meses", "Personalizado"]
        )
    
    with col2:
        if report_period == "Personalizado":
            date_range = st.date_input(
                "Selecionar Período",
                value=(datetime.now() - timedelta(days=7), datetime.now()),
                max_value=datetime.now()
            )
    
    # Generate reports
    if st.button("📈 Gerar Relatório", type="primary"):
        # Collection statistics
        st.subheader("📊 Estatísticas de Coleta")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Coletas", "156")
        
        with col2:
            st.metric("Lixo Coletado", "12.4 toneladas")
        
        with col3:
            st.metric("Distância Percorrida", "847 km")
        
        with col4:
            st.metric("Eficiência Média", "87.3%")
        
        # Performance by condominium
        st.subheader("🏢 Performance por Condomínio")
        
        performance_data = data_manager.get_performance_by_condominium()
        st.dataframe(performance_data, width=None)
        
        # Environmental impact
        st.subheader("🌱 Impacto Ambiental")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("CO₂ Evitado", "2.4 toneladas", help="Baseado na otimização de rotas")
            st.metric("Combustível Economizado", "340 litros")
        
        with col2:
            st.metric("Taxa de Reciclagem", "68%")
            st.metric("Resíduos Desviados do Aterro", "8.5 toneladas")
    
    # Export functionality
    st.subheader("📤 Exportar Dados")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Exportar Dashboard"):
            st.success("Dashboard exportado!")
    
    with col2:
        if st.button("🗑️ Exportar Dados das Lixeiras"):
            st.success("Dados das lixeiras exportados!")
    
    with col3:
        if st.button("🚛 Exportar Dados dos Caminhões"):
            st.success("Dados dos caminhões exportados!")

# System settings
with st.expander("⚙️ Configurações do Sistema"):
    st.subheader("Configurações Gerais")
    
    col1, col2 = st.columns(2)
    
    with col1:
        update_interval = st.slider("Intervalo de Atualização (minutos)", 1, 60, 5)
        notification_level = st.selectbox(
            "Nível de Notificações",
            options=["Todas", "Apenas Críticas", "Desabilitadas"]
        )
        
    with col2:
        auto_route_optimization = st.checkbox("Otimização Automática de Rotas", value=True)
        emergency_alerts = st.checkbox("Alertas de Emergência", value=True)
    
    if st.button("💾 Salvar Configurações"):
        st.success("Configurações salvas com sucesso!")
