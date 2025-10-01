import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from utils.data_manager import DataManager

st.set_page_config(
    page_title="Dashboard - EcoSmart GPS",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard de Monitoramento")

# Initialize data manager
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()

data_manager = st.session_state.data_manager

# Get data
trucks_data = data_manager.get_trucks_data()
bins_data = data_manager.get_bins_data()
condominiums_data = data_manager.get_condominiums_data()

# Key Performance Indicators
st.header("🎯 Indicadores de Performance")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_bins = len(bins_data)
    st.metric("Total de Lixeiras", total_bins)

with col2:
    active_trucks = len(trucks_data[trucks_data['status'] == 'Ativo'])
    st.metric("Caminhões Ativos", active_trucks)

with col3:
    avg_fill_level = bins_data['fill_level'].mean()
    st.metric("Nível Médio de Enchimento", f"{avg_fill_level:.1f}%")

with col4:
    collections_today = data_manager.get_collections_count_today()
    st.metric("Coletas Hoje", collections_today)

# Charts section
st.header("📈 Análise de Dados")

col1, col2 = st.columns(2)

with col1:
    # Bin fill level distribution
    st.subheader("Distribuição do Nível de Enchimento das Lixeiras")
    
    # Create histogram
    fig_hist = px.histogram(
        bins_data, 
        x='fill_level', 
        nbins=20,
        title="Distribuição dos Níveis de Enchimento",
        labels={'fill_level': 'Nível de Enchimento (%)', 'count': 'Quantidade de Lixeiras'},
        color_discrete_sequence=['#00C851']
    )
    fig_hist.update_layout(showlegend=False)
    st.plotly_chart(fig_hist, use_container_width=False)

with col2:
    # Truck status pie chart
    st.subheader("Status dos Caminhões")
    
    truck_status_counts = trucks_data['status'].value_counts()
    fig_pie = px.pie(
        values=truck_status_counts.values,
        names=truck_status_counts.index,
        title="Distribuição do Status dos Caminhões",
        color_discrete_sequence=['#00C851', '#FF4444']
    )
    st.plotly_chart(fig_pie, use_container_width=False)

# Efficiency metrics
st.header("⚡ Métricas de Eficiência")

col1, col2 = st.columns(2)

with col1:
    # Collection efficiency over time
    st.subheader("Eficiência de Coleta por Dia")
    
    efficiency_data = data_manager.get_efficiency_data()
    fig_efficiency = px.line(
        efficiency_data,
        x='date',
        y='efficiency_percentage',
        title="Eficiência de Coleta (%)",
        labels={'date': 'Data', 'efficiency_percentage': 'Eficiência (%)'},
        color_discrete_sequence=['#00C851']
    )
    fig_efficiency.update_layout(yaxis_range=[0, 100])
    st.plotly_chart(fig_efficiency, use_container_width=False)

with col2:
    # Collections per condominium
    st.subheader("Coletas por Condomínio")
    
    collections_by_condo = data_manager.get_collections_by_condominium()
    fig_bar = px.bar(
        collections_by_condo,
        x='condominium',
        y='collections',
        title="Número de Coletas por Condomínio (Últimos 7 dias)",
        labels={'condominium': 'Condomínio', 'collections': 'Número de Coletas'},
        color_discrete_sequence=['#00C851']
    )
    fig_bar.update_xaxis(tickangle=45)
    st.plotly_chart(fig_bar, use_container_width=False)

# Detailed tables
st.header("📋 Dados Detalhados")

tab1, tab2, tab3 = st.tabs(["🗑️ Lixeiras", "🚛 Caminhões", "🏢 Condomínios"])

with tab1:
    st.subheader("Status das Lixeiras")
    
    # Add color coding for fill levels
    def get_fill_level_color(fill_level):
        if fill_level >= 80:
            return "🔴"
        elif fill_level >= 60:
            return "🟡"
        else:
            return "🟢"
    
    bins_display = bins_data.copy()
    bins_display['Status'] = bins_display['fill_level'].apply(get_fill_level_color)
    bins_display = bins_display[['bin_id', 'condominium', 'location', 'fill_level', 'Status', 'last_updated']]
    bins_display.columns = ['ID da Lixeira', 'Condomínio', 'Localização', 'Nível (%)', 'Status', 'Última Atualização']
    
    st.dataframe(bins_display, width=None)

with tab2:
    st.subheader("Status dos Caminhões")
    
    trucks_display = trucks_data.copy()
    trucks_display = trucks_display[['truck_id', 'status', 'current_location', 'fuel_level', 'last_updated']]
    trucks_display.columns = ['ID do Caminhão', 'Status', 'Localização Atual', 'Combustível (%)', 'Última Atualização']
    
    st.dataframe(trucks_display, width=None)

with tab3:
    st.subheader("Condomínios Cadastrados")
    
    # Calculate bins per condominium
    bins_per_condo = bins_data.groupby('condominium').size().reset_index()
    bins_per_condo.columns = ['condominium', 'total_bins']
    full_bins_per_condo = bins_data[bins_data['fill_level'] >= 80].groupby('condominium').size().reset_index()
    full_bins_per_condo.columns = ['condominium', 'full_bins']
    
    condos_display = condominiums_data.merge(bins_per_condo, left_on='name', right_on='condominium', how='left')
    condos_display = condos_display.merge(full_bins_per_condo, left_on='name', right_on='condominium', how='left')
    condos_display['full_bins'] = condos_display['full_bins'].fillna(0).astype(int)
    condos_display['total_bins'] = condos_display['total_bins'].fillna(0).astype(int)
    
    condos_display = condos_display[['name', 'address', 'total_bins', 'full_bins', 'contact']]
    condos_display.columns = ['Nome', 'Endereço', 'Total de Lixeiras', 'Lixeiras Cheias', 'Contato']
    
    st.dataframe(condos_display, width=None)

# Refresh button
if st.button("🔄 Atualizar Dashboard"):
    data_manager.update_truck_positions()
    data_manager.update_bin_levels()
    st.success("Dados atualizados com sucesso!")
    st.rerun()
